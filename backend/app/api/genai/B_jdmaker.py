import json
import os
import re
from io import BytesIO

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_security import auth_required, current_user

# Groq (OpenAI-compatible) client
from openai import OpenAI

from app.models.models import db, JobDescription


jd_bp = Blueprint('jdmaker', __name__)


class JDMakerService:
    """GenAI-powered professional job description generator."""

    def __init__(self):
        self._client_ready = False
        self._generator_model_name = 'gemini-2.5-flash'
        self._model = None

    # ------------------ LLM client helpers ------------------ #

    def _ensure_client(self):
        if self._client_ready:
            return
        api_key = os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            # This will trigger Groq fallback
            raise RuntimeError('GEMINI_API_KEY is not configured.')
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(self._generator_model_name)
        self._client_ready = True

    def _generate_with_groq(self, prompt: str) -> str:
        """
        Fallback to Groq if Gemini is unavailable or fails.
        Requires GROQ_API_KEY in environment or Flask config.
        """
        api_key = os.getenv('GROQ_API_KEY') or current_app.config.get('GROQ_API_KEY')
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
            current_app.logger.exception("JD Groq fallback failed: %s", exc)
            return ""

    def _generate_llm_answer(
        self,
        prompt: str,
        temperature: float = 0.3,
        top_p: float = 0.8,
        max_tokens: int = 1200,
    ) -> str:
        """Try Gemini first, then Groq."""
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
            current_app.logger.exception("JD Gemini generation failed: %s", exc)

        if not text:
            groq_text = self._generate_with_groq(prompt)
            if groq_text:
                return groq_text

        return text

    # ------------------ Prompt building / sanitising ------------------ #

    def _build_jd_prompt(self, inputs: dict) -> str:
        """Build a comprehensive prompt for professional JD generation."""
        parts = []
        parts.append("You are an expert HR professional and job description writer.")
        parts.append("Create a professional, comprehensive job description based on these inputs:\n")

        fields = [
            ('Job Title', 'title'),
            ('Department', 'department'),
            ('Location', 'location'),
            ('Employment Type', 'employment_type'),
            ('Experience Level', 'experience_level'),
            ('Salary Range', 'salary_range'),
            ('Company Info', 'company_info'),
        ]
        for label, key in fields:
            value = (inputs.get(key) or '').strip()
            if value:
                parts.append(f"{label}: {value}")

        skills = inputs.get('key_skills', '')
        if skills:
            parts.append(f"Key Skills Required: {skills}")

        resp = inputs.get('responsibilities', '')
        if resp:
            parts.append(f"Key Responsibilities: {resp}")

        qual = inputs.get('qualifications', '')
        if qual:
            parts.append(f"Qualifications: {qual}")

        notes = inputs.get('additional_notes', '')
        if notes:
            parts.append(f"Additional Notes: {notes}")

        parts.append("\n\nGenerate a professional job description with these sections:")
        parts.append("1. Position Overview (compelling 2-3 sentence summary)")
        parts.append("2. About The Role (2-3 paragraphs on the position)")
        parts.append("3. Key Responsibilities (6-8 clear bullet points)")
        parts.append("4. Required Qualifications (education, experience, skills as bullet points)")
        parts.append("5. Preferred Qualifications (additional desirable skills/experience)")
        parts.append("6. What We Offer (benefits, culture, growth opportunities)")
        parts.append("7. Application Process (brief note)")
        parts.append(
            "\nFormatting rules:\n"
            "- Use plain text paragraphs and bullet points.\n"
            "- Do NOT use markdown tables or the '|' character for layout.\n"
            "- Do NOT wrap the answer in code fences.\n"
            "- You may use simple bullets like '- ' or numbered lists '1.' etc.\n"
        )
        parts.append("IMPORTANT: All salary values must be expressed in Indian Rupees (₹ or Rs.) — never in dollars.")

        parts.append("Make it professional, engaging, and compelling. Use industry-standard language.")
        parts.append("Return ONLY the formatted job description text, no markdown code blocks.")

        return '\n'.join(parts)

    @staticmethod
    def _sanitize_description_text(text: str) -> str:
        """Strip code fences and flatten any table-style markdown into plain text."""
        if not text:
            return ""

        # Remove code fences if present
        cleaned = re.sub(r"```[a-zA-Z]*\n?", "", text)
        cleaned = cleaned.replace("```", "")

        lines = cleaned.splitlines()
        out_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                out_lines.append("")
                continue

            # Remove horizontal rules
            if stripped in ("---", "***", "___"):
                continue

            # Convert headings like "### Title" to "Title"
            if stripped.startswith("#"):
                stripped = stripped.lstrip("#").strip()
                if not stripped:
                    continue

            # Convert simple markdown table rows to text
            if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
                # Skip pure separator row like |----|----|
                if re.fullmatch(r"\|\s*-+\s*(\|\s*-+\s*)+\|", stripped):
                    continue
                cols = [c.strip() for c in stripped.strip("|").split("|")]
                stripped = " – ".join([c for c in cols if c])

            out_lines.append(stripped)

        # Collapse extra blank lines
        result = "\n".join(l for l in out_lines if l is not None)
        return result.strip()

    # ------------------ Public JD generation ------------------ #

    def generate_jd(self, inputs: dict) -> dict:
        """Generate a professional job description using Gemini with Groq fallback."""
        if not inputs.get('title'):
            raise ValueError('Job title is required.')

        prompt = self._build_jd_prompt(inputs)
        description = self._generate_llm_answer(
            prompt,
            temperature=0.3,
            top_p=0.8,
            max_tokens=1200,
        )

        if not description:
            raise RuntimeError('Failed to generate JD text.')

        # Clean up any unwanted markdown/table artefacts
        description = self._sanitize_description_text(description)

        # Extract structured info (requirements, skills) from the generated description
        extraction_prompt = f"""
Extract structured data from this job description. Return ONLY valid JSON:
{{
    "requirements": ["requirement1", "requirement2", ...],
    "skills_required": ["skill1", "skill2", ...],
    "experience_required": <number of years as integer, or null>
}}

Job Description:
{description}
""".strip()

        try:
            extraction_text = self._generate_llm_answer(
                extraction_prompt,
                temperature=0.0,
                top_p=0.0,
                max_tokens=500,
            )
            extraction_text = (extraction_text or "").strip()
            # Clean markdown code blocks if present
            extraction_text = re.sub(r'```json\n?', '', extraction_text)
            extraction_text = re.sub(r'```\n?', '', extraction_text)
            extracted = json.loads(extraction_text)
        except Exception as exc:
            current_app.logger.warning('Failed to extract JD structure: %s', exc)
            extracted = {'requirements': [], 'skills_required': [], 'experience_required': None}

        return {
            'description': description,
            'requirements': extracted.get('requirements', []),
            'skills_required': extracted.get('skills_required', []),
            'experience_required': extracted.get('experience_required'),
        }


service = JDMakerService()


def _generate_jd_pdf(title: str, description: str) -> BytesIO:
    """Generate a professional PDF from a job description."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import unicodedata

    # Helper to normalise / clean problematic Unicode so we don't see boxes/locks
    def _clean_text(s: str) -> str:
        if not s:
            return ""

        s = unicodedata.normalize("NFKC", s)

        translate_map = {
            # spaces
            ord("\u00A0"): " ",   # non-breaking space
            ord("\u2009"): " ",
            ord("\u200A"): " ",
            ord("\u202F"): " ",
            ord("\u200B"): "",    # zero-width space
            # dashes
            ord("\u2010"): "-",
            ord("\u2011"): "-",
            ord("\u2012"): "-",
            ord("\u2013"): "-",
            ord("\u2014"): "-",
            ord("\u2015"): "-",
            # bullets / squares
            ord("\u2022"): "• ",
            ord("\u2023"): "• ",
            ord("\u25AA"): "• ",
            ord("\u25CF"): "• ",
            ord("\u25A0"): " ",
            ord("\u25AB"): " ",
        }
        s = s.translate(translate_map)

        cleaned_chars = []
        for ch in s:
            cat = unicodedata.category(ch)
            if cat.startswith("C") and ch not in ("\n", "\t"):
                cleaned_chars.append(" ")
            else:
                cleaned_chars.append(ch)
        s = "".join(cleaned_chars)

        s = re.sub(r"[ \t]+", " ", s)
        return s.strip()

    # Clean title and description once
    title = _clean_text(title or "")
    description = _clean_text(description or "")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1f2937',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor='#374151',
        spaceAfter=10,
        alignment=TA_LEFT,
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Split description into paragraphs for better formatting
    paragraphs = description.split('\n\n')
    bullet_prefixes = ('* ', '- ', '• ')

    for raw_para in paragraphs:
        para_text = _clean_text(raw_para)
        if not para_text.strip():
            continue

        lines = para_text.split('\n')
        # Check if this block is a list of bullet points
        is_bullet_block = all(
            line.strip().startswith(bullet_prefixes)
            for line in lines
            if line.strip()
        )

        if is_bullet_block:
            # Render each bullet line as its own bullet point
            for line in lines:
                txt = _clean_text(line.strip())
                if not txt:
                    continue
                if txt.startswith('* ') or txt.startswith('- '):
                    txt = '• ' + txt[2:]

                # Convert **bold** to <b>bold</b> and remove stray **
                txt = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', txt)
                txt = txt.replace('**', '')

                story.append(Paragraph(txt, body_style))
                story.append(Spacer(1, 0.05 * inch))

            story.append(Spacer(1, 0.1 * inch))
        else:
            # Normal paragraph: handle bold and line breaks
            para_text_clean = para_text

            # Convert **bold** to <b>bold</b>
            para_text_clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para_text_clean)
            # Remove any remaining **
            para_text_clean = para_text_clean.replace('**', '')

            # Preserve line breaks within the paragraph
            para_text_clean = para_text_clean.replace('\n', '<br/>')

            story.append(Paragraph(para_text_clean, body_style))
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer


@jd_bp.route('/genai/jd/generate', methods=['POST'])
@auth_required()
def generate_jd():
    """Generate a professional job description using GenAI."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    payload = request.get_json() or {}

    if not payload.get('title'):
        return jsonify({'error': 'Job title is required'}), 400

    try:
        generated = service.generate_jd(payload)

        return jsonify({
            'description': generated['description'],
            'requirements': generated['requirements'],
            'skills_required': generated['skills_required'],
            'experience_required': generated['experience_required'],
        })
    except Exception as error:
        current_app.logger.exception('JD generation failed: %s', error)
        return jsonify({'error': str(error)}), 500


@jd_bp.route('/genai/jd/pdf', methods=['POST'])
@auth_required()
def download_jd_pdf():
    """Download generated JD as a professional PDF."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    payload = request.get_json() or {}
    description = payload.get('description')
    title = payload.get('title', 'Job Description')

    if not description:
        # If description not provided, generate it first
        if not payload.get('title'):
            return jsonify({'error': 'Title is required to generate JD'}), 400
        try:
            generated = service.generate_jd(payload)
            description = generated['description']
        except Exception as error:
            current_app.logger.exception('JD text generation for PDF failed: %s', error)
            return jsonify({'error': 'Failed to generate JD text'}), 500

    try:
        pdf_buffer = _generate_jd_pdf(title, description)
        filename = f"jd_{title.replace(' ', '_').lower()}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf',
        )
    except Exception as error:
        current_app.logger.exception('PDF generation failed: %s', error)
        return jsonify({'error': 'Failed to generate PDF'}), 500


@jd_bp.route('/genai/jd/save', methods=['POST'])
@auth_required()
def save_jd():
    """Save generated JD to database."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    payload = request.get_json() or {}

    if not payload.get('title') or not payload.get('description'):
        return jsonify({'error': 'Title and description are required'}), 400

    try:
        jd = JobDescription(
            title=payload['title'],
            department=payload.get('department'),
            description=payload['description'],
            salary_range=payload.get('salary_range'),
            requirements=json.dumps(payload.get('requirements', [])),
            skills_required=json.dumps(payload.get('skills_required', [])),
            experience_required=payload.get('experience_required'),
        )
        db.session.add(jd)
        db.session.commit()

        return jsonify({
            'message': 'Job description saved successfully',
            'id': jd.id,
        }), 200
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Failed to save JD: %s', error)
        return jsonify({'error': str(error)}), 500
