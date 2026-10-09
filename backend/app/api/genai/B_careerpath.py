import os
import textwrap
from io import BytesIO

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_security import auth_required, current_user

# NEW: Groq (OpenAI-compatible) client
from openai import OpenAI

career_bp = Blueprint('careerpath', __name__)


class CareerPathService:
    """Simple GenAI-backed career path recommendation service.

    Generates a concise personalised recommendation based on the employee's
    inputs and produces a downloadable PDF.
    """

    def __init__(self):
        self._client_ready = False
        self._generator_model_name = 'gemini-2.0-flash'

    def _ensure_client(self):
        if self._client_ready:
            return
        api_key = os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            # This will be caught and will trigger Groq fallback
            raise RuntimeError('GEMINI_API_KEY is not configured.')
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(self._generator_model_name)
        self._client_ready = True

    def _build_prompt(self, payload: dict) -> str:
        parts = []
        parts.append(
            "You are an expert career coach. Read the employee information and produce a short, "
            "practical career development recommendation.\n"
        )
        fields = [
            ('Current role', 'current_role'),
            ('Target role', 'target_role'),
            ('Strengths', 'strengths'),
            ('Focus areas', 'focus_areas'),
            ('Preferred learning style', 'learning_style'),
            ('Timeline', 'timeline'),
            ('Support needed', 'support_needed'),
        ]
        for label, key in fields:
            value = (payload.get(key) or '').strip()
            parts.append(f"{label}: {value}")

        instructions = (
            "Produce a well-structured career development recommendation with the following sections:\n\n"
            "**Summary:**\n"
            "Write a 2-3 sentence personalized overview of the employee's career transition goals and feasibility.\n\n"
            "**Recommended Actions:**\n"
            "List 3-4 specific, actionable steps as numbered items (1. 2. 3. 4.).\n\n"
            "**Suggested Learning Resources:**\n"
            "Provide a brief list of specific courses, books, or platforms as bullet points (* or -).\n\n"
            "**Measurable Milestones & Timeline:**\n"
            "Break down the timeline with specific milestones as bullet points, clearly indicating what should be achieved in each period.\n\n"
            "Formatting rules:\n"
            "- Use **bold** for section headers\n"
            "- Use numbered lists (1. 2. 3.) for actions\n"
            "- Use bullet points (* or -) for resources and milestones\n"
            "- Keep overall length ~300-500 words\n"
            "- Make the tone encouraging, actionable, and professional"
        )
        parts.append('')
        parts.append(instructions)
        return '\n'.join(parts)

    # NEW: Groq fallback implementation (using the snippet you provided)
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

            # Groq helper from your example
            text = getattr(response, "output_text", "") or ""
            return text.strip()

        except Exception as exc:
            current_app.logger.exception("CareerPath Groq fallback failed: %s", exc)
            return ""

    def generate_recommendation(self, payload: dict) -> str:
        prompt = self._build_prompt(payload)

        # Try Gemini first
        text = ''
        try:
            self._ensure_client()
            response = self._model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    top_p=0.9,
                    candidate_count=1,
                    max_output_tokens=700,
                ),
            )
            text = (response.text or '').strip()
        except Exception as exc:  # pragma: no cover - fail gracefully
            current_app.logger.exception('CareerPath Gemini generation failed: %s', exc)

        # If Gemini failed or returned empty, fall back to Groq
        if not text:
            groq_text = self._generate_with_groq(prompt)
            if groq_text:
                return groq_text

            # If Groq also fails, return a friendly error
            return (
                'Sorry — I was unable to generate a personalised recommendation at this time. '
                'Please try again later.'
            )

        return text


service = CareerPathService()


def _text_to_pdf_bytes(title: str, body: str) -> BytesIO:
    # Delayed import so reportlab requirement is optional until endpoint used
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT
    import re
    import unicodedata

    # --- NEW: helper to normalize & replace problematic characters ---
    def _clean_text(s: str) -> str:
        if not s:
            return ""

        # Normalize accents etc.
        s = unicodedata.normalize("NFKC", s)

        # Normalise weird spaces, dashes and bullets that LLMs often emit
        translate_map = {
            ord("\u00A0"): " ",   # non-breaking space
            ord("\u2009"): " ",   # thin space
            ord("\u200A"): " ",
            ord("\u202F"): " ",
            ord("\u200B"): "",    # zero-width space

            ord("\u2010"): "-",   # hyphen
            ord("\u2011"): "-",   # non-breaking hyphen
            ord("\u2012"): "-",
            ord("\u2013"): "-",
            ord("\u2014"): "-",
            ord("\u2015"): "-",

            # bullets / squares → nice bullet or plain space
            ord("\u2022"): "• ",
            ord("\u2023"): "• ",
            ord("\u25AA"): "• ",
            ord("\u25CF"): "• ",
            ord("\u25A0"): " ",   # solid square
            ord("\u25AB"): " ",   # hollow square
        }
        s = s.translate(translate_map)

        # Drop any remaining control / unprintable chars that might show as boxes
        cleaned_chars = []
        for ch in s:
            cat = unicodedata.category(ch)
            if cat.startswith("C") and ch not in ("\n", "\t"):
                cleaned_chars.append(" ")
            else:
                cleaned_chars.append(ch)
        s = "".join(cleaned_chars)

        # Collapse multiple spaces
        s = re.sub(r"[ \t]+", " ", s)
        return s.strip()

    # Clean title & body once up front
    title = _clean_text(title)
    body = _clean_text(body)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Styles (left-aligned)
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        alignment=TA_LEFT,
        fontSize=16,
        textColor="#0f172a",
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor="#0f172a",
        spaceAfter=12,
        spaceBefore=18,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=10,
        textColor="#475569",
        spaceAfter=12,
        leading=15,
        fontName="Helvetica",
        alignment=TA_LEFT,
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=styles["BodyText"],
        fontSize=10,
        textColor="#475569",
        leftIndent=20,
        spaceAfter=6,
        leading=15,
        fontName="Helvetica",
        alignment=TA_LEFT,
    )

    numbered_style = ParagraphStyle(
        "NumberedStyle",
        parent=styles["BodyText"],
        fontSize=10,
        textColor="#475569",
        leftIndent=15,
        spaceAfter=6,
        leading=15,
        fontName="Helvetica",
        alignment=TA_LEFT,
    )

    story = []
    story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Spacer(1, 0.3 * inch))

    lines = body.split("\n")
    current_bullet_list = []
    current_numbered_list = []
    paragraph_buffer = []

    def flush_lists():
        nonlocal current_bullet_list, current_numbered_list
        if current_bullet_list:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, bullet_style)) for item in current_bullet_list],
                    bulletType="bullet",
                    leftIndent=10,
                    spaceBefore=6,
                    spaceAfter=12,
                )
            )
            current_bullet_list = []
        if current_numbered_list:
            numbered_items = []
            for i, item in enumerate(current_numbered_list, 1):
                numbered_items.append(ListItem(Paragraph(item, numbered_style), value=i))
            story.append(
                ListFlowable(
                    numbered_items,
                    bulletType="1",
                    leftIndent=10,
                    spaceBefore=6,
                    spaceAfter=12,
                )
            )
            current_numbered_list = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            para_text = " ".join(paragraph_buffer)
            # Clean again just to be safe
            para_text = _clean_text(para_text)
            # Convert **bold** markdown to <b>
            para_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", para_text)
            story.append(Paragraph(para_text, body_style))
            paragraph_buffer = []

    for raw_line in lines:
        line = _clean_text(raw_line.strip())

        if not line:
            flush_paragraph()
            flush_lists()
            continue

        # Section headers (**Summary**, **Recommended Actions:** etc.)
        if re.match(r"^\*\*[^*]+\*\*:?$", line):
            flush_paragraph()
            flush_lists()
            header_text = line.strip("*").strip(":")
            story.append(Paragraph(f"<b>{header_text}</b>", heading_style))
            continue

        # Bullet points (* or - or •)
        bullet_match = re.match(r"^[*\-•]\s+(.+)$", line)
        if bullet_match:
            flush_paragraph()
            if current_numbered_list:
                flush_lists()
            item_text = bullet_match.group(1)
            item_text = _clean_text(item_text)
            item_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", item_text)
            current_bullet_list.append(item_text)
            continue

        # Numbered list (1. 2. 3.)
        numbered_match = re.match(r"^(\d+)\.\s+(.+)$", line)
        if numbered_match:
            flush_paragraph()
            if current_bullet_list:
                flush_lists()
            num_text = numbered_match.group(2)
            num_text = _clean_text(num_text)
            num_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", num_text)
            current_numbered_list.append(num_text)
            continue

        # Regular paragraph text
        flush_lists()
        paragraph_buffer.append(line)

    flush_paragraph()
    flush_lists()

    doc.build(story)
    buffer.seek(0)
    return buffer


@career_bp.route('/genai/careerpath', methods=['POST'])
@auth_required()
def generate_careerpath():
    payload = request.get_json() or {}
    # Minimal validation — frontend should send these keys
    # Accept both snake_case and camelCase just in case

    def get_field(k):
        return payload.get(k) or payload.get(k.replace('_', '')) or payload.get(k.replace('_', ''))

    data = {
        'current_role': payload.get('current_role') or payload.get('currentRole') or '',
        'target_role': payload.get('target_role') or payload.get('targetRole') or '',
        'strengths': payload.get('strengths') or '',
        'focus_areas': payload.get('focus_areas') or payload.get('focusAreas') or '',
        'learning_style': payload.get('learning_style') or payload.get('preferredLearningStyle') or '',
        'timeline': payload.get('timeline') or '',
        'support_needed': payload.get('support_needed') or payload.get('supportNeeded') or '',
    }

    recommendation = service.generate_recommendation(data)

    return jsonify({
        'recommendation': recommendation,
        'pdf_endpoint': '/api/genai/careerpath/pdf',
    })


@career_bp.route('/genai/careerpath/pdf', methods=['POST'])
@auth_required()
def careerpath_pdf():
    payload = request.get_json() or {}
    recommendation = payload.get('recommendation')
    title = 'Career Development Plan'

    # If recommendation not provided, generate it from the payload fields.
    if not recommendation:
        data = {
            'current_role': payload.get('current_role') or payload.get('currentRole') or '',
            'target_role': payload.get('target_role') or payload.get('targetRole') or '',
            'strengths': payload.get('strengths') or '',
            'focus_areas': payload.get('focus_areas') or payload.get('focusAreas') or '',
            'learning_style': payload.get('learning_style') or payload.get('preferredLearningStyle') or '',
            'timeline': payload.get('timeline') or '',
            'support_needed': payload.get('support_needed') or payload.get('supportNeeded') or '',
        }
        recommendation = service.generate_recommendation(data)

    pdf_io = _text_to_pdf_bytes(title, recommendation)
    filename = f"careerplan_{current_user.id if current_user else 'anon'}.pdf"
    return send_file(
        pdf_io,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )


@career_bp.route('/genai/debug', methods=['GET'])
def career_debug():
    """Unauthenticated debug endpoint to verify backend reachability and key/dependency health."""
    info = {
        'status': 'ok',
        'gemini_key_present': bool(os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')),
        # NEW: Groq key presence
        'groq_key_present': bool(
            os.getenv('GROQ_API_KEY') or current_app.config.get('GROQ_API_KEY')
        ),
        'reportlab_importable': True,
        'google_generativeai_importable': True,
    }
    # Check imports without failing the endpoint
    try:
        import reportlab  # type: ignore
    except Exception:
        info['reportlab_importable'] = False

    try:
        # google.generativeai already imported at module import time but double-check
        _ = genai  # noqa: F841
    except Exception:
        info['google_generativeai_importable'] = False

    return jsonify(info)
