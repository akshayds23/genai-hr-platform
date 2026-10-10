import json
import logging
import re
from io import BytesIO

from pypdf import PdfReader

from app.services.ai import AIUnavailableError, generate_text

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _generate_llm_text(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    top_p: float = 0.8,
) -> str:
    """Generate text using AI service."""
    return generate_text(prompt, max_tokens=max_tokens)


def _generate_llm_json(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    top_p: float = 0.0,
) -> dict:
    """Generate JSON using AI service and parse result."""
    raw = generate_text(prompt, json_output=True, max_tokens=max_tokens)
    if not raw:
        raise RuntimeError("Empty LLM response.")

    cleaned = re.sub(r"```json\n?", "", raw)
    cleaned = re.sub(r"```\n?", "", cleaned)
    cleaned = cleaned.strip()

    return json.loads(cleaned)


def extract_text_from_resume(file_content: bytes, filename: str) -> str:
    """Extract text from resume file. Supports PDF, DOCX, TXT."""
    try:
        if filename.lower().endswith('.pdf'):
            pdf_file = BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ''
                text += page_text
            return text
        elif filename.lower().endswith('.docx'):
            from docx import Document
            doc_file = BytesIO(file_content)
            doc = Document(doc_file)
            return '\n'.join(para.text for para in doc.paragraphs)
        elif filename.lower().endswith('.txt'):
            return file_content.decode('utf-8', errors='ignore')
        else:
            return file_content.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.warning("Error extracting text from %s: %s", filename, e)
        return ""


def extract_resume_data_gemini(resume_text: str) -> dict:
    """Use LLM (Gemini + Groq fallback) to extract structured data from resume text."""
    prompt = f"""
Extract the following information from this resume in JSON format.
Return ONLY valid JSON with these exact fields:
{{
    "name": "full name",
    "email": "email address",
    "phone": "phone number",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "company": "company name",
            "role": "job title",
            "duration": "years or date range",
            "responsibilities": "brief description"
        }}
    ],
    "education": [
        {{
            "institution": "university/school name",
            "degree": "degree type",
            "field": "field of study",
            "year": "graduation year"
        }}
    ],
    "summary": "brief professional summary",
    "total_experience": number of years as a float,
    "current_role": "current job title",
    "current_company": "current company name",
    "gender": "Male/Female/Other if inferable from name or content"
}}

Resume Text:
{resume_text}

Return ONLY the JSON object, no additional text.
""".strip()

    try:
        data = _generate_llm_json(
            prompt,
            max_tokens=1500,
            temperature=0.1,
            top_p=0.8,
        )
        return data
    except AIUnavailableError:
        raise
    except Exception as e:
        logger.warning("Error in structured resume data extraction: %s", e)
        return {
            'name': 'Unknown Candidate',
            'email': '',
            'phone': '',
            'skills': [],
            'experience': [],
            'education': [],
            'summary': resume_text[:300] if resume_text else 'No summary available',
            'total_experience': 0.0,
            'current_role': 'Candidate',
            'current_company': '',
            'gender': None,
        }


def generate_resume_summary_gemini(resume_text: str) -> str:
    """Use LLM to generate a concise, professional summary of a resume."""
    prompt = f"""
Provide a concise, professional summary (3-4 sentences) of this candidate's resume.
Highlight:
- Core expertise and years of experience
- Key technical/professional skills
- Notable career achievements
- Best-fit roles

Resume Text:
{resume_text}

Summary:
""".strip()

    try:
        summary = _generate_llm_text(
            prompt,
            max_tokens=256,
            temperature=0.3,
            top_p=0.8,
        )
        return summary or "Resume summary not available"
    except Exception as e:
        logger.warning("Error generating resume summary: %s", e)
        return "Unable to generate summary"


def match_resume_to_jd_gemini(resume_data: dict, jd_data: dict) -> dict:
    """Use LLM to match a resume to job description and return score + reasoning."""
    resume_str = json.dumps(resume_data, indent=2)
    jd_str = json.dumps(jd_data, indent=2)

    prompt = f"""
Analyze how well this candidate matches the job description.
Return ONLY a JSON object with these exact fields:
{{
    "match_score": numerical score 0-100,
    "reasoning": "detailed explanation of match"
}}

Candidate Resume:
{resume_str}

Job Description:
{jd_str}

Consider:
- Skills overlap
- Experience level
- Education requirements
- Role relevance
- Cultural fit indicators

Return ONLY the JSON object, no additional text.
""".strip()

    try:
        match_data = _generate_llm_json(
            prompt,
            max_tokens=800,
            temperature=0.0,
            top_p=0.0,
        )
        match_data['match_score'] = float(match_data.get('match_score', 0.0))
        return match_data
    except Exception as e:
        logger.warning("Error in resume-JD matching: %s", e)
        raise


def infer_gender_from_name(name: str) -> str | None:
    """Infer gender from name using LLM (Gemini + Groq)."""
    if not name:
        return None

    prompt = (
        f"From the name '{name}', infer the most likely gender. "
        "Return only one word: Male, Female, or Other"
    )

    try:
        text = _generate_llm_text(
            prompt,
            max_tokens=16,
            temperature=0.0,
            top_p=0.0,
        )
        gender = text.strip()
        if gender in ['Male', 'Female', 'Other']:
            return gender
    except Exception as e:
        logger.warning("Error inferring gender from name: %s", e)
    return None


def process_single_resume(file_content: bytes, filename: str, source: str = 'Manual') -> dict:
    """
    Process a single resume file and return candidate data.
    This is extracted for reuse in bulk upload.
    """
    resume_text = extract_text_from_resume(file_content, filename)

    if not resume_text or len(resume_text.strip()) < 50:
        raise ValueError('Unable to extract meaningful content from file')

    candidate_data = extract_resume_data_gemini(resume_text)

    if not candidate_data.get('gender') and candidate_data.get('name'):
        candidate_data['gender'] = infer_gender_from_name(candidate_data['name'])

    summary = generate_resume_summary_gemini(resume_text)

    return {
        'filename': filename,
        'name': candidate_data.get('name', 'Unknown Candidate'),
        'email': candidate_data.get('email', ''),
        'phone': candidate_data.get('phone', ''),
        'skills': json.dumps(candidate_data.get('skills', [])),
        'experience': json.dumps(candidate_data.get('experience', [])),
        'education': json.dumps(candidate_data.get('education', [])),
        'summary': summary,
        'total_experience': candidate_data.get('total_experience', 0.0),
        'current_role': candidate_data.get('current_role', 'Candidate'),
        'current_company': candidate_data.get('current_company', ''),
        'gender': candidate_data.get('gender'),
        'source': source,
        'status': 'New',
        'resume_text': resume_text,
    }
