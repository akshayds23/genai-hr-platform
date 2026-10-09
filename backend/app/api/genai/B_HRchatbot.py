import json
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import numpy as np
from flask import Blueprint, current_app, jsonify, request
from flask_security import auth_required, current_user
from pypdf import PdfReader

# NEW: Groq (OpenAI-compatible) client
from openai import OpenAI

from app.models.models import (
    db,
    AuditLog,
    Conversation,
    HRKnowledge,
    HRQuestionLog,
    Message,
    User,
)
from app.services.notifications import (
    determine_hr_user_ids,
    determine_manager_ids,
    notify_users,
)


hr_chatbot_bp = Blueprint('hr_chatbot', __name__)


class HRChatbotService:
    """Encapsulates Gemini powered RAG workflow for the HR virtual assistant."""

    def __init__(self):
        self._knowledge_cache: List[dict] = []
        self._client_ready = False
        self._model = None
        self._similarity_model = None
        self._embedding_model_name = 'models/text-embedding-004'
        self._generator_model_name = 'gemini-2.5-flash'
        self._similarity_model_name = 'gemini-2.5-flash'
        self._knowledge_last_refreshed_at: Optional[datetime] = None
        # Track how many HRKnowledge records are currently indexed
        self._knowledge_record_count: int = 0

    def _latest_knowledge_modified_at(self) -> Optional[datetime]:
        """Return the timestamp of the most recently modified knowledge entry."""
        try:
            result = (
                db.session.query(
                    db.func.max(
                        db.func.coalesce(HRKnowledge.updated_at, HRKnowledge.created_at)
                    )
                )
                .scalar()
            )
            return result
        except Exception:
            return None

    # --------------------------------------------------------------------- #
    # Initialisation helpers
    # --------------------------------------------------------------------- #
    def _ensure_client(self):
        if self._client_ready:
            return
        api_key = (
            os.getenv('GEMINI_API_KEY')
            or current_app.config.get('GEMINI_API_KEY')
        )
        if not api_key:
            raise RuntimeError('GEMINI_API_KEY is not configured.')
        genai.configure(api_key=api_key)
        if not self._model:
            generator_name = current_app.config.get(
                'HR_CHATBOT_MODEL',
                self._generator_model_name,
            )
            self._model = genai.GenerativeModel(generator_name)
        if not self._similarity_model:
            similarity_name = current_app.config.get(
                'HR_CHATBOT_SIMILARITY_MODEL',
                self._similarity_model_name,
            )
            self._similarity_model = genai.GenerativeModel(similarity_name)
        self._client_ready = True

    # NEW: Groq fallback
    def _generate_with_groq(self, prompt: str) -> str:
        """
        Fallback to Groq if Gemini is unavailable or fails.
        Requires GROQ_API_KEY in environment or Flask config.
        """
        api_key = (
            os.getenv('GROQ_API_KEY')
            or current_app.config.get('GROQ_API_KEY')
        )
        if not api_key:
            current_app.logger.error("GROQ_API_KEY is not configured.")
            return ""

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )

            response = client.responses.create(
                input=prompt,
                model="openai/gpt-oss-20b",
            )

            text = getattr(response, "output_text", "") or ""
            return text.strip()
        except Exception as exc:
            current_app.logger.exception("HRChatbot Groq fallback failed: %s", exc)
            return ""

    # NEW: shared helper – try Gemini, then Groq
    def _generate_llm_answer(
        self,
        prompt: str,
        temperature: float = 0.2,
        top_p: float = 0.8,
        max_tokens: int = 700,
    ) -> str:
        text = ""
        try:
            self._ensure_client()
            response = self._model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=temperature,
                    top_p=top_p,
                    candidate_count=1,
                    max_output_tokens=max_tokens,
                ),
            )
            text = (response.text or "").strip()
        except Exception as exc:
            current_app.logger.exception("HRChatbot Gemini generation failed: %s", exc)

        if not text:
            groq_text = self._generate_with_groq(prompt)
            if groq_text:
                return groq_text

        return text

    def _ensure_knowledge(self, force: bool = False):
        """
        Ensure that the in-memory knowledge cache is up to date.

        It reloads when:
        - forced, OR
        - record count changed, OR
        - latest (updated_at/created_at) is newer than last refresh.
        """
        latest_update = self._latest_knowledge_modified_at()
        try:
            current_count = HRKnowledge.query.count()
        except Exception:
            current_count = 0

        if self._knowledge_cache and not force:
            nothing_new_by_time = (
                (latest_update is None and self._knowledge_last_refreshed_at is None)
                or (
                    latest_update is not None
                    and self._knowledge_last_refreshed_at is not None
                    and latest_update <= self._knowledge_last_refreshed_at
                )
            )
            if current_count == self._knowledge_record_count and nothing_new_by_time:
                return

        records = HRKnowledge.query.order_by(HRKnowledge.id.asc()).all()
        if not records:
            self._ingest_pdf()
            records = HRKnowledge.query.order_by(HRKnowledge.id.asc()).all()

        knowledge_cache: List[dict] = []
        updated = False
        for record in records:
            embedding_vector: Optional[List[float]] = None
            if record.embedding:
                try:
                    embedding_vector = json.loads(record.embedding)
                except (ValueError, TypeError):
                    embedding_vector = None
            if embedding_vector is None:
                try:
                    embedding_vector = self._embed_text(
                        f"{record.question}\n{record.answer}"
                    )
                except Exception as exc:
                    current_app.logger.exception(
                        "HRChatbot embedding refresh failed for id=%s: %s",
                        record.id,
                        exc,
                    )
                    continue
                record.embedding = json.dumps(embedding_vector)
                updated = True
            vector = np.array(embedding_vector, dtype=np.float32)
            knowledge_cache.append(
                {
                    'id': record.id,
                    'question': record.question,
                    'answer': record.answer,
                    'source': record.source,
                    'embedding': vector,
                    'norm': float(np.linalg.norm(vector)),
                }
            )

        if updated:
            db.session.commit()

        self._knowledge_cache = knowledge_cache
        self._knowledge_record_count = len(knowledge_cache)

        if latest_update is None:
            latest_update = self._latest_knowledge_modified_at()
        self._knowledge_last_refreshed_at = latest_update or datetime.utcnow()

    def _get_pdf_path(self) -> Path:
        base_dir = Path(current_app.root_path).parent.parent
        return base_dir / 'Hr questions.pdf'

    def _ingest_pdf(self):
        pdf_path = self._get_pdf_path()
        if not pdf_path.exists():
            current_app.logger.warning('HR questions PDF not found at %s', pdf_path)
            return
        reader = PdfReader(str(pdf_path))
        lines: List[str] = []
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ''
            except Exception:  # pragma: no cover - defensive
                page_text = ''
            lines.extend(page_text.splitlines())

        qa_pairs = self._parse_qa_pairs(lines)
        for question, answer in qa_pairs:
            if not question or not answer:
                continue
            existing = HRKnowledge.query.filter(
                HRKnowledge.question == question.strip()
            ).first()
            if existing:
                continue
            record = HRKnowledge(
                question=question.strip(),
                answer=answer.strip(),
                source=pdf_path.name,
            )
            db.session.add(record)
        db.session.commit()

    @staticmethod
    def _parse_qa_pairs(lines: List[str]) -> List[Tuple[str, str]]:
        qa_pairs: List[Tuple[str, str]] = []
        current_question: Optional[str] = None
        current_answer_lines: List[str] = []

        for raw_line in lines:
            line = (raw_line or '').strip()
            if not line:
                continue

            normalized = line.lower()
            is_question = (
                line.endswith('?')
                or normalized.startswith('q:')
                or normalized.startswith('question')
            )

            if is_question:
                if current_question:
                    answer_text = ' '.join(current_answer_lines).strip()
                    qa_pairs.append((current_question.strip(), answer_text))
                    current_answer_lines = []

                if ':' in line:
                    current_question = line.split(':', 1)[1].strip() or line
                else:
                    current_question = line
            else:
                cleaned = (
                    line.split(':', 1)[1].strip()
                    if normalized.startswith(('answer', 'a:'))
                    else line
                )
                current_answer_lines.append(cleaned)

        if current_question:
            answer_text = ' '.join(current_answer_lines).strip()
            qa_pairs.append((current_question.strip(), answer_text))

        if qa_pairs:
            return qa_pairs

        buffer: List[str] = []
        for raw_line in lines:
            line = (raw_line or '').strip()
            if not line:
                continue
            buffer.append(line)
            joined = ' '.join(buffer)
            if len(joined) >= 600:
                qa_pairs.append((joined[:120] + '...', joined))
                buffer = []
        if buffer:
            joined = ' '.join(buffer)
            qa_pairs.append((joined[:120] + '...', joined))
        return qa_pairs

    def ensure_profile_indexed(self, user_id: int) -> None:
        """
        Warm up the chatbot retrieval caches for a specific user.
        """
        try:
            self._ensure_client()
            self._ensure_knowledge()
        except Exception as error:  # pragma: no cover - defensive
            current_app.logger.warning(
                'HR chatbot pre-indexing skipped for user %s: %s',
                user_id,
                error,
            )

    # --------------------------------------------------------------------- #
    # Embedding & retrieval helpers
    # --------------------------------------------------------------------- #
    def _embed_text(self, text: str) -> List[float]:
        self._ensure_client()
        response = genai.embed_content(
            model=self._embedding_model_name,
            content=text,
        )
        embedding = response.get('embedding') or response.get('values')
        if not embedding:
            raise RuntimeError('Unable to compute embedding for text.')
        return embedding

    def _retrieve_top_matches(self, question_vector: np.ndarray, top_k: int = 3) -> List[dict]:
        if not self._knowledge_cache:
            return []
        query_norm = float(np.linalg.norm(question_vector))
        if query_norm == 0:
            return []

        scored_records: List[dict] = []
        for record in self._knowledge_cache:
            denom = query_norm * record['norm']
            if denom == 0:
                continue
            score = float(np.dot(question_vector, record['embedding']) / denom)
            scored_records.append({'record': record, 'score': score})

        scored_records.sort(key=lambda item: item['score'], reverse=True)
        return scored_records[:top_k]

    def _semantic_similarity_score(self, query: str, candidate: str) -> float:
        self._ensure_client()
        if not query or not candidate:
            return 0.0
        prompt = (
            "You are comparing HR related questions. "
            "Rate how similar Question A is to Question B on a scale from 0 to 1. "
            "Respond with only the decimal number.\n"
            f"Question A: {query.strip()}\n"
            f"Question B: {candidate.strip()}\n"
            "Score:"
        )
        try:
            response = self._similarity_model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.0,
                    top_p=0.0,
                    candidate_count=1,
                ),
            )
            text = (response.text or '').strip()
            match = re.search(r'1(?:\.0+)?|0(?:\.\d+)?', text)
            if not match:
                return 0.0
            score = float(match.group(0))
            if score < 0:
                return 0.0
            if score > 1:
                return 1.0
            return score
        except Exception:
            return 0.0

    def _semantic_rerank(self, question: str, matches: List[dict]) -> List[dict]:
        reranked: List[dict] = []
        for item in matches:
            candidate_question = item['record']['question']
            similarity = self._semantic_similarity_score(question, candidate_question)
            updated = {
                'record': item['record'],
                'score': similarity,
            }
            reranked.append(updated)
        reranked.sort(key=lambda entry: entry['score'], reverse=True)
        return reranked

    @staticmethod
    def _build_history(conversation: Optional[Conversation], limit: int = 6) -> str:
        if not conversation:
            return ''

        messages = (
            conversation.messages
            .order_by(Message.created_at.asc())
            .limit(limit * 2)
            .all()
        )
        if not messages:
            return ''

        history_lines: List[str] = []
        for message in messages[-limit * 2:]:
            history_lines.append(f"{message.content}")
        return '\n'.join(history_lines)

    def _build_prompt(
        self,
        question: str,
        context_snippets: List[str],
        history: str,
        user: Optional[User],
    ) -> str:
        instructions = (
            "You are Ava, the HR assistant for the Employee Engagement Portal. "
            "Use the supplied HR reference material to provide concise and accurate answers. "
            "Always cite policies when possible, and if the answer is uncertain say that you will escalate the query.\n\n"
            "Formatting rules:\n"
            "- Do NOT use markdown tables or the '|' character for layout.\n"
            "- Avoid headings like '### Title'; just use plain sentences or short bullet lists.\n"
            "- Bullet points are allowed (start lines with '-' or '1.' etc.).\n"
            "- Keep the answer short, clear, and easy to read in plain text."
        )

        profile_line = ''
        if user:
            profile_line = (
                f"Employee context: role={user.employment_role}, "
                f"department={user.department or 'N/A'}, team={user.team_number or 'N/A'}."
            )

        context_block = '\n'.join(f"- {snippet}" for snippet in context_snippets if snippet)
        sections = [
            instructions,
            profile_line,
        ]
        if history:
            sections.append(f"Conversation history:\n{history}")
        sections.append(f"HR reference material:\n{context_block or 'No direct reference provided.'}")
        sections.append(f"Employee question: {question}")
        sections.append("Provide an empathetic and actionable answer.")
        return '\n\n'.join(filter(None, sections))

    def _is_in_domain(self, question: str) -> bool:
        """
        Decide if a question is in scope for the HR assistant.

        If the question already exists in HRKnowledge, treat it as in-domain
        regardless of keywords or classifier output.
        """
        if not question:
            return False

        normalized = question.strip().lower()

        # 1) Explicit KB entry => always in-domain
        explicit_match = HRKnowledge.query.filter(
            db.func.lower(HRKnowledge.question) == normalized
        ).first()
        if explicit_match:
            return True

        # 2) Keyword-based heuristic
        keywords = [
            'leave', 'pto', 'vacation', 'sick', 'policy', 'benefit', 'payroll', 'salary',
            'hr', 'manager', 'team', 'employee', 'onboarding', 'offboarding', 'feedback',
            'career', 'training', 'promotion', 'appraisal', 'timesheet'
        ]
        if any(keyword in normalized for keyword in keywords):
            return True

        # 3) Classifier for everything else
        classification_prompt = (
            "Classify the employee question to decide if it relates to HR policies, "
            "employee benefits, time off, workplace processes, or manager support. "
            "Respond with exactly 'HR' for relevant questions or 'OTHER' if the question is outside that scope.\n\n"
            f"Question: {question}"
        )
        try:
            self._ensure_client()
            response = self._model.generate_content(
                classification_prompt,
                generation_config=GenerationConfig(
                    temperature=0.0,
                    candidate_count=1,
                    top_p=0.0,
                    max_output_tokens=10,
                ),
            )
            label = (response.text or '').strip().lower()
            return 'hr' in label
        except Exception:
            # If classifier fails, default to in-domain so we can still try to help
            return True

    @staticmethod
    def _sanitize_response_text(text: Optional[str]) -> str:
        if not text:
            return ""

        # Remove bold markers
        cleaned = text.replace("**", "")

        lines = cleaned.splitlines()
        out_lines: List[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip markdown horizontal rules
            if stripped in ("---", "***", "___"):
                continue

            # Turn markdown headings into plain text: "### Title" -> "Title"
            if stripped.startswith("#"):
                stripped = stripped.lstrip("#").strip()
                if not stripped:
                    continue

            # Convert simple markdown table rows into plain text
            # Example: | Col1 | Col2 | Col3 |
            if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
                # header/separator row detection: |----|----|
                if re.fullmatch(r"\|\s*-+\s*(\|\s*-+\s*)+\|", stripped):
                    # skip separator row
                    continue

                parts = [p.strip() for p in stripped.strip("|").split("|")]
                # Join columns with " – " so it's readable
                stripped = " – ".join([p for p in parts if p])

            out_lines.append(stripped)

        # Collapse extra blank lines
        result = "\n".join(l for l in out_lines if l.strip())
        return result

    def answer_question(
        self,
        user: Optional[User],
        question: str,
        conversation: Optional[Conversation],
        auto_escalate: bool = True,
    ):
        # Normalized tokens for quick DB lookups
        normalized_q = (question or '').strip().lower()
        tokens = re.findall(r'\w+', normalized_q)

        history_text = self._build_history(conversation)

        # -----------------------------------------------------------------
        # 0) Direct single-word / exact DB match (case-insensitive)
        #    If a single word matches any HRKnowledge.question, answer from it.
        # -----------------------------------------------------------------
        direct_record = None
        if tokens:
            # Exact match on full question (any length)
            direct_record = HRKnowledge.query.filter(
                db.func.lower(HRKnowledge.question) == normalized_q
            ).first()

            # If question is a single word, allow partial match inside question text
            if not direct_record and len(tokens) == 1:
                token = tokens[0]
                direct_record = HRKnowledge.query.filter(
                    HRKnowledge.question.ilike(f"%{token}%")
                ).first()

        if direct_record:
            context_snippets = [
                f"Q: {direct_record.question}\nA: {direct_record.answer}"
            ]
            prompt = self._build_prompt(question, context_snippets, history_text, user)
            answer_text = self._generate_llm_answer(prompt)
            final_answer = (
                answer_text
                or direct_record.answer
                or 'I found relevant guidance in our policy documents.'
            )
            final_answer = self._sanitize_response_text(final_answer)
            reference_source = direct_record.source or 'knowledge_base'
            log_entry = HRQuestionLog(
                user_id=user.id if user else None,
                manager_id=getattr(user, 'manager_id', None),
                conversation_id=conversation.id if conversation else None,
                question=question,
                normalized_question=normalized_q,
                answer=final_answer,
                status='auto_answered',
                source=reference_source,
                confidence=1.0,
            )
            db.session.add(log_entry)
            db.session.commit()
            return {
                'answer': final_answer,
                'status': 'auto_answered',
                'question_log_id': log_entry.id,
                'reference': direct_record.question,
                'reference_source': reference_source,
            }

        # -----------------------------------------------------------------
        # 1) Embedding + RAG path
        # -----------------------------------------------------------------
        try:
            self._ensure_client()
        except Exception as exc:
            current_app.logger.exception("HRChatbot client init failed: %s", exc)

        try:
            self._ensure_knowledge()
        except Exception as exc:
            current_app.logger.exception("HRChatbot knowledge ensure failed: %s", exc)
            self._knowledge_cache = []

        top_matches: List[dict] = []
        try:
            if self._knowledge_cache:
                question_vector = np.array(self._embed_text(question), dtype=np.float32)
                top_matches = self._retrieve_top_matches(question_vector)
        except Exception as exc:
            current_app.logger.exception("HRChatbot retrieval failed: %s", exc)
            top_matches = []

        similarity_threshold = current_app.config.get('HR_RAG_MIN_SIMILARITY', 0.72)
        fallback_threshold = current_app.config.get('HR_RAG_FALLBACK_SIMILARITY', 0.55)
        confident_matches = [match for match in top_matches if match['score'] >= similarity_threshold]

        if not confident_matches and top_matches:
            reranked_subset = self._semantic_rerank(question, top_matches[:5])
            if reranked_subset:
                remainder = top_matches[5:]
                top_matches = reranked_subset + remainder
                confident_matches = [
                    match for match in reranked_subset if match['score'] >= fallback_threshold
                ]

        # 2) If we have a confident KB match, answer from it (with Groq fallback)
        if confident_matches:
            primary_match = confident_matches[0]['record']
            reference_question = primary_match['question']
            reference_source = primary_match['source'] or 'knowledge_base'
            context_snippets = [
                f"Q: {match['record']['question']}\nA: {match['record']['answer']}"
                for match in confident_matches
            ]
            prompt = self._build_prompt(question, context_snippets, history_text, user)

            answer_text = self._generate_llm_answer(prompt)
            final_answer = (
                answer_text
                or primary_match['answer']
                or 'I found relevant guidance in our policy documents.'
            )
            final_answer = self._sanitize_response_text(final_answer)
            log_entry = HRQuestionLog(
                user_id=user.id if user else None,
                manager_id=getattr(user, 'manager_id', None),
                conversation_id=conversation.id if conversation else None,
                question=question,
                normalized_question=normalized_q,
                answer=final_answer,
                status='auto_answered',
                source=reference_source,
                confidence=confident_matches[0]['score'],
            )
            db.session.add(log_entry)
            db.session.commit()
            return {
                'answer': final_answer,
                'status': 'auto_answered',
                'question_log_id': log_entry.id,
                'reference': reference_question,
                'reference_source': reference_source,
            }

        # 3) No KB match: apply domain filter
        if not self._is_in_domain(question):
            return {
                'answer': (
                    "I'm designed to help with HR and employee portal questions. "
                    "This one looks outside that scope, so I can't answer it."
                ),
                'status': 'out_of_scope',
                'question_log_id': None,
                'reference': None,
                'reference_source': None,
            }

        # 4) In-domain but no documented answer: escalate or ask to confirm
        fallback_message = (
            "I couldn't find a documented answer. Would you like me to forward this to HR for a manual response?"
        )
        if not auto_escalate:
            return {
                'answer': fallback_message,
                'status': 'needs_confirmation',
                'question_log_id': None,
                'reference': None,
                'reference_source': None,
            }

        log_entry = self._log_pending_question(user, conversation, question, top_matches)

        return {
            'answer': (
                "Thanks for the question! I couldn't find a documented answer, so I've "
                "escalated it to HR and your manager. We'll follow up with guidance shortly."
            ),
            'status': 'pending',
            'question_log_id': log_entry.id,
            'reference': None,
            'reference_source': log_entry.source,
        }

    def escalate_question(
        self,
        user: Optional[User],
        question: str,
        conversation: Optional[Conversation] = None,
    ):
        """Explicitly forward a question to HR after the employee confirms."""
        try:
            self._ensure_client()
            self._ensure_knowledge()
        except Exception:
            pass
        try:
            question_vector = np.array(self._embed_text(question), dtype=np.float32)
            top_matches = self._retrieve_top_matches(question_vector)
        except Exception:
            top_matches = []

        log_entry = self._log_pending_question(
            user,
            conversation,
            question,
            top_matches,
        )
        return log_entry

    def _log_pending_question(
        self,
        user: Optional[User],
        conversation: Optional[Conversation],
        question: str,
        top_matches: Optional[List[dict]],
    ) -> HRQuestionLog:
        log_entry = HRQuestionLog(
            user_id=user.id if user else None,
            manager_id=getattr(user, 'manager_id', None),
            conversation_id=conversation.id if conversation else None,
            question=question,
            normalized_question=(question or "").lower(),
            status='pending',
            source='manual_review',
            confidence=top_matches[0]['score'] if top_matches else None,
        )
        db.session.add(log_entry)
        db.session.flush()

        details_payload = {
            'question_id': log_entry.id,
            'question': question,
            'submitted_by': user.id if user else None,
        }

        if getattr(user, 'manager_id', None):
            audit_entry = AuditLog(
                actor_id=user.id if user else None,
                action='hr-question-pending',
                object_type='hr_question',
                object_id=str(user.manager_id),
                details=json.dumps(details_payload),
            )
            db.session.add(audit_entry)

        if user:
            hr_user_ids = determine_hr_user_ids(exclude_id=user.id)
            if hr_user_ids:
                notify_users(
                    hr_user_ids,
                    category='hr_question',
                    title='New HR question awaiting review',
                    message=(
                        f'{user.first_name or user.email} submitted an HR '
                        'question that needs attention.'
                    ),
                    metadata={
                        'question_id': log_entry.id,
                        'employee_id': user.id,
                        'question': question,
                        'status': 'pending',
                    },
                )
            notify_users(
                [user.id],
                category='hr_question',
                title='Question escalated to HR',
                message='We have sent your question to HR for a manual response.',
                metadata={
                    'question_id': log_entry.id,
                    'status': 'pending',
                },
            )

        db.session.commit()
        return log_entry

    def add_manual_knowledge(
        self,
        question: str,
        answer: str,
        source: str = 'manager_response',
    ):
        """Store manually curated answers so future RAG calls can reuse them."""
        vector = self._embed_text(f"{question}\n{answer}")
        trimmed_question = question.strip()
        normalized_question = trimmed_question.lower()
        existing = (
            HRKnowledge.query.filter(
                db.func.lower(HRKnowledge.question) == normalized_question
            ).first()
        )
        if existing:
            existing.answer = answer.strip()
            existing.source = source
            existing.embedding = json.dumps(vector)
        else:
            record = HRKnowledge(
                question=trimmed_question,
                answer=answer.strip(),
                source=source,
                embedding=json.dumps(vector),
            )
            db.session.add(record)
        db.session.commit()
        # refresh cache on next call
        self._knowledge_cache = []
        self._knowledge_last_refreshed_at = None
        self._knowledge_record_count = 0


hr_chatbot_service = HRChatbotService()


# ------------------------------------------------------------------------- #
# API routes
# ------------------------------------------------------------------------- #


@hr_chatbot_bp.route('/hr/questions', methods=['GET'])
@auth_required()
def list_hr_questions():
    status_filter = request.args.get('status', 'pending').lower()
    statuses = {status.strip() for status in status_filter.split(',') if status.strip()}
    if not statuses:
        statuses = {'pending'}

    query = HRQuestionLog.query
    if 'all' not in statuses:
        query = query.filter(HRQuestionLog.status.in_(list(statuses)))

    if current_user.is_admin():
        pass
    elif current_user.employment_role == 'manager':
        team_number = getattr(current_user, 'team_number', None)
        team_user_ids = []
        if team_number:
            team_user_ids = [
                member.id
                for member in User.query
                .filter(User.team_number == team_number)
                .filter(User.active.is_(True))
                .all()
            ]
        query = query.filter(
            (HRQuestionLog.manager_id == current_user.id)
            | (HRQuestionLog.user_id.in_(team_user_ids) if team_user_ids else False)
        )
    else:
        query = query.filter(HRQuestionLog.user_id == current_user.id)

    questions = [
        {
            'id': item.id,
            'question': item.question,
            'answer': item.answer,
            'status': item.status,
            'source': item.source,
            'confidence': item.confidence,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            'resolved_at': item.resolved_at.isoformat() if item.resolved_at else None,
            'user_id': item.user_id,
            'manager_id': item.manager_id,
        }
        for item in query.order_by(HRQuestionLog.created_at.desc()).limit(100).all()
    ]
    return jsonify({'questions': questions})


@hr_chatbot_bp.route('/hr/questions/<int:question_id>/answer', methods=['POST'])
@auth_required()
def resolve_hr_question(question_id: int):
    if not (current_user.is_admin() or current_user.employment_role == 'manager'):
        return jsonify({'error': 'Only managers or HR can resolve questions.'}), 403

    payload = request.get_json() or {}
    answer = (payload.get('answer') or '').strip()
    if not answer:
        return jsonify({'error': 'Answer is required.'}), 400

    question = HRQuestionLog.query.get_or_404(question_id)
    question.answer = answer
    question.status = 'resolved'
    question.resolved_by = current_user.id
    question.resolved_at = db.func.now()
    question.source = question.source or 'manual_review'
    question.updated_at = db.func.now()

    if not question.manager_id:
        question.manager_id = current_user.id

    hr_chatbot_service.add_manual_knowledge(
        question.question,
        answer,
        source='manual_review',
    )

    details_payload = {
        'question_id': question.id,
        'question': question.question,
        'answer': answer,
        'resolved_by': current_user.id,
    }
    if question.user_id:
        audit_entry = AuditLog(
            actor_id=current_user.id,
            action='hr-question-resolved',
            object_type='hr_question',
            object_id=str(question.user_id),
            details=json.dumps(details_payload),
        )
        db.session.add(audit_entry)

        notify_users(
            [question.user_id],
            category='hr_question',
            title='HR question answered',
            message='HR has responded to your question. Tap to read the reply.',
            metadata={
                'question_id': question.id,
                'status': question.status,
            },
        )
        if question.manager_id and question.manager_id != question.user_id:
            notify_users(
                [question.manager_id],
                category='hr_question',
                title='HR question answered',
                message='HR has responded to the escalated question from your team.',
                metadata={
                    'question_id': question.id,
                    'status': question.status,
                    'resolved_for': 'manager',
                },
            )

    db.session.commit()

    return jsonify({'message': 'Question resolved and knowledge base updated.'})


@hr_chatbot_bp.route('/genai/chat/knowledge', methods=['GET'])
@auth_required()
def get_knowledge_base():
    """Get all questions in the HR knowledge base (for debugging/reference)."""
    try:
        records = HRKnowledge.query.order_by(HRKnowledge.id.asc()).all()
        questions = [
            {
                'id': record.id,
                'question': record.question,
                'source': record.source,
            }
            for record in records[:20]  # Limit to first 20
        ]
        return jsonify({
            'total': len(records),
            'questions': questions,
        }), 200
    except Exception as error:
        current_app.logger.exception('Error fetching knowledge base: %s', error)
        return jsonify({'error': str(error)}), 500


@hr_chatbot_bp.route('/genai/chat', methods=['POST'])
@auth_required()
def chat():
    """Send a message to the HR chatbot and get a response."""
    payload = request.get_json() or {}
    user_message = (payload.get('message') or '').strip()
    raw_auto_escalate = payload.get('auto_escalate')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    if isinstance(raw_auto_escalate, str):
        normalized = raw_auto_escalate.strip().lower()
        auto_escalate = normalized not in {'false', '0', 'no'}
    elif raw_auto_escalate is None:
        auto_escalate = True
    else:
        auto_escalate = bool(raw_auto_escalate)

    try:
        conversation = Conversation.query.filter_by(
            user_id=current_user.id,
        ).first()
        if not conversation:
            conversation = Conversation(user_id=current_user.id)
            db.session.add(conversation)
            db.session.commit()

        user_msg = Message(
            conversation_id=conversation.id,
            sender='user',
            content=user_message,
        )
        db.session.add(user_msg)
        db.session.commit()

        result = hr_chatbot_service.answer_question(
            current_user,
            user_message,
            conversation,
            auto_escalate=auto_escalate,
        )

        ai_msg = Message(
            conversation_id=conversation.id,
            sender='assistant',
            content=result['answer'],
        )
        db.session.add(ai_msg)
        db.session.commit()

        return jsonify({
            'response': result['answer'],
            'status': result.get('status', 'answered'),
            'question_id': result.get('question_log_id'),
            'reference': result.get('reference'),
            'reference_source': result.get('reference_source'),
            'conversation_id': conversation.id,
        }), 200
    except Exception as error:
        current_app.logger.exception('Chat error: %s', error)
        return jsonify({'error': str(error)}), 500
