import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import PyPDF2
import google.generativeai as genai
from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from werkzeug.utils import secure_filename

# NEW: Groq (OpenAI-compatible) client
from openai import OpenAI

from app.models.models import db, CandidateResume, JobDescription, ResumeMatch, Team


hr_bp = Blueprint('hr', __name__)


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

generation_config = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 8192,
}

_working_model_name = None


# ---------------------------------------------------------------------------
# LLM helpers (Gemini + Groq fallback)
# ---------------------------------------------------------------------------

def _get_gemini_model(generation_cfg: Optional[dict] = None):
    """Get a working Gemini model, trying different model names."""
    global _working_model_name

    if not generation_cfg:
        generation_cfg = {}

    # If we already found a working model, use it
    if _working_model_name:
        try:
            return genai.GenerativeModel(
                model_name=_working_model_name,
                generation_config=generation_cfg,
            )
        except Exception:
            # Model name might have changed, reset cache
            _working_model_name = None

    # Try gemini-2.5-flash first (direct)
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=generation_cfg,
        )
        _working_model_name = 'gemini-2.5-flash'
        print("Using Gemini model: gemini-2.5-flash")
        return model
    except Exception as e:
        print(f"gemini-2.5-flash not available, trying alternatives: {e}")

    # Try to list available models first (most reliable)
    try:
        available_models = genai.list_models()
        generate_models = [
            m.name
            for m in available_models
            if 'generateContent' in m.supported_generation_methods
        ]
        if generate_models:
            preferred_order = [
                'gemini-2.5-flash',
                'models/gemini-2.5-flash',
                'gemini-2.5-pro',
                'models/gemini-2.5-pro',
                'gemini-1.5-pro',
                'models/gemini-1.5-pro',
                'gemini-1.5-flash',
                'models/gemini-1.5-flash',
                'gemini-pro',
                'models/gemini-pro',
            ]
            for preferred in preferred_order:
                for available in generate_models:
                    if preferred in available or available.endswith(
                        preferred.replace('models/', '')
                    ):
                        _working_model_name = available
                        print(f"Using Gemini model: {available}")
                        return genai.GenerativeModel(
                            model_name=available,
                            generation_config=generation_cfg,
                        )

            _working_model_name = generate_models[0]
            print(f"Using first available Gemini model: {generate_models[0]}")
            return genai.GenerativeModel(
                model_name=generate_models[0],
                generation_config=generation_cfg,
            )
    except Exception as e:
        print(f"Could not list models: {e}")

    # Fallback: try common names
    model_names = [
        'gemini-2.5-flash',
        'models/gemini-2.5-flash',
        'gemini-2.5-pro',
        'models/gemini-2.5-pro',
        'gemini-pro',
        'models/gemini-pro',
        'gemini-1.5-pro',
        'models/gemini-1.5-pro',
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
    ]

    last_error: Optional[Exception] = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_cfg,
            )
            _working_model_name = model_name
            print(f"Using Gemini model: {model_name}")
            return model
        except Exception as e:
            last_error = e
            continue

    raise ValueError(
        f"No working Gemini model found. Last error: {last_error}. "
        "Please check your API key and model availability."
    )


def _generate_with_groq(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.8,
) -> str:
    """Fallback to Groq if Gemini is unavailable or fails."""
    if not GROQ_API_KEY:
        print("GROQ_API_KEY is not configured.")
        return ""

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.responses.create(
            input=prompt,
            model="openai/gpt-oss-20b",
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        text = getattr(response, "output_text", "") or ""
        return text.strip()
    except Exception as exc:
        print(f"Groq fallback failed: {exc}")
        return ""


def _generate_llm_text(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.8,
) -> str:
    """Try Gemini first, then Groq, returning plain text."""
    text = ""

    # Gemini path
    try:
        if GEMINI_API_KEY:
            model_cfg = {
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            }
            model = _get_gemini_model(model_cfg)
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
    except Exception as exc:
        print(f"Gemini text generation failed: {exc}")
        text = ""

    # Groq fallback
    if not text:
        text = _generate_with_groq(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

    return text.strip()


def _generate_llm_json(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    top_p: float = 0.0,
) -> Dict:
    """
    Try Gemini first, then Groq, and parse result as JSON.
    Assumes the prompt strictly asks for JSON.
    """
    raw = _generate_llm_text(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    if not raw:
        raise RuntimeError("Empty LLM response.")

    # Strip common code fences
    cleaned = re.sub(r"```json\n?", "", raw)
    cleaned = re.sub(r"```\n?", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception as exc:
        print(f"Failed to parse LLM JSON: {exc} | raw={cleaned[:200]}")
        raise


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def extract_text_from_resume(file_content: bytes, filename: str) -> str:
    """Extract text from resume file. Supports PDF, DOCX, TXT."""
    try:
        if filename.lower().endswith('.pdf'):
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
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
        print(f"Error extracting text: {str(e)}")
        return ""


def extract_resume_data_gemini(resume_text: str) -> Dict:
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
            max_tokens=1200,
            temperature=0.0,
            top_p=0.0,
        )
        return data
    except Exception as e:
        print(f"Error in resume data extraction: {str(e)}")
        raise


def generate_resume_summary_gemini(resume_text: str) -> str:
    """Generate a concise summary of the resume using Gemini + Groq fallback."""
    prompt = f"""
Provide a concise professional summary (2-3 sentences) of this resume focusing on:
- Key qualifications
- Years of experience
- Main skills or expertise
- Current or most recent role

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
        print(f"Error generating summary: {str(e)}")
        return "Unable to generate summary"


def match_resume_to_jd_gemini(resume_data: Dict, jd_data: Dict) -> Dict:
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
        print(f"Error in resume-JD matching: {str(e)}")
        raise


def infer_gender_from_name(name: str) -> Optional[str]:
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
        print(f"Error inferring gender from name: {str(e)}")
    return None


# ---------------------------------------------------------------------------
# API Routes / Handlers
# ---------------------------------------------------------------------------

def process_single_resume(file_content: bytes, filename: str, source: str = 'Manual') -> Dict:
    """
    Process a single resume file and return candidate data.
    This is extracted for reuse in bulk upload.
    """
    resume_text = extract_text_from_resume(file_content, filename)

    if not resume_text or len(resume_text.strip()) < 50:
        raise ValueError('Unable to extract meaningful content from file')

    extracted_data = extract_resume_data_gemini(resume_text)
    summary = generate_resume_summary_gemini(resume_text)

    if 'gender' not in extracted_data or not extracted_data['gender']:
        if 'name' in extracted_data:
            extracted_data['gender'] = infer_gender_from_name(extracted_data['name'])

    candidate_data = {
        'filename': filename,
        'name': extracted_data.get('name'),
        'email': extracted_data.get('email'),
        'phone': extracted_data.get('phone'),
        'skills': json.dumps(extracted_data.get('skills', [])),
        'experience': json.dumps(extracted_data.get('experience', [])),
        'education': json.dumps(extracted_data.get('education', [])),
        'summary': summary,
        'total_experience': extracted_data.get('total_experience'),
        'current_role': extracted_data.get('current_role'),
        'current_company': extracted_data.get('current_company'),
        'source': source,
        'status': 'New',
        'gender': extracted_data.get('gender'),
        'resume_text': resume_text,
    }

    return candidate_data


@hr_bp.route('/hr/resume/upload', methods=['POST'])
@auth_required()
def upload_resume():
    """
    Upload and extract data from a resume file.
    Supports PDF, DOCX, TXT files.
    """
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    file_content = file.read()
    source = request.form.get('source') or 'Manual'

    try:
        candidate_data = process_single_resume(file_content, filename, source)

        candidate = CandidateResume(**candidate_data)
        db.session.add(candidate)
        db.session.commit()

        return jsonify({
            'message': 'Resume uploaded and processed successfully',
            'candidate': candidate.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process resume: {str(e)}'}), 500


@hr_bp.route('/hr/resume/bulk-upload', methods=['POST'])
@auth_required()
def bulk_upload_resumes():
    """
    Bulk upload and process multiple resume files in parallel.
    Supports PDF, DOCX, TXT files.
    """
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    source = request.form.get('source') or 'Manual'
    max_workers = int(request.form.get('max_workers', 10))

    results = {
        'successful': [],
        'failed': [],
        'total': len(files),
        'processed': 0,
    }

    def process_file(file):
        try:
            filename = secure_filename(file.filename)
            file_content = file.read()
            candidate_data = process_single_resume(file_content, filename, source)
            return {'success': True, 'filename': filename, 'data': candidate_data}
        except Exception as e:
            return {'success': False, 'filename': file.filename, 'error': str(e)}

    candidates_to_add = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in files}

        for future in as_completed(future_to_file):
            result = future.result()
            results['processed'] += 1

            if result['success']:
                candidates_to_add.append(result['data'])
                results['successful'].append({
                    'filename': result['filename'],
                    'name': result['data'].get('name', 'N/A'),
                })
            else:
                results['failed'].append({
                    'filename': result['filename'],
                    'error': result['error'],
                })

    try:
        for candidate_data in candidates_to_add:
            candidate = CandidateResume(**candidate_data)
            db.session.add(candidate)

        db.session.commit()

        return jsonify({
            'message': (
                f'Bulk upload completed: {len(results["successful"])} successful, '
                f'{len(results["failed"])} failed'
            ),
            'results': results,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to save candidates to database: {str(e)}',
            'results': results,
        }), 500


@hr_bp.route('/hr/resume/summarize/<int:resume_id>', methods=['POST'])
@auth_required()
def summarize_resume(resume_id):
    """Generate a concise summary for a specific resume."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    candidate = CandidateResume.query.get_or_404(resume_id)

    if not candidate.resume_text:
        return jsonify({'error': 'Resume text not available'}), 400

    try:
        summary = generate_resume_summary_gemini(candidate.resume_text)
        candidate.summary = summary
        db.session.commit()

        return jsonify({
            'message': 'Summary generated successfully',
            'summary': summary,
            'candidate_id': resume_id,
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate summary: {str(e)}'}), 500


@hr_bp.route('/hr/resumes', methods=['GET'])
@auth_required()
def get_all_resumes():
    """Get all uploaded resumes with filtering and pagination."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    source = request.args.get('source')

    query = CandidateResume.query

    if status:
        query = query.filter_by(status=status)
    if source:
        query = query.filter_by(source=source)

    candidates = query.order_by(
        CandidateResume.uploaded_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'resumes': [c.to_dict() for c in candidates.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': candidates.total,
            'pages': candidates.pages,
        },
    }), 200


@hr_bp.route('/hr/resume/<int:resume_id>', methods=['GET'])
@auth_required()
def get_resume(resume_id):
    """Get detailed information about a specific resume."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    candidate = CandidateResume.query.get_or_404(resume_id)
    return jsonify(candidate.to_dict()), 200


@hr_bp.route('/hr/resume/<int:resume_id>/status', methods=['PUT'])
@auth_required()
def update_resume_status(resume_id):
    """Update the status of a resume (e.g., Shortlisted, Interviewed, Rejected)."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    candidate = CandidateResume.query.get_or_404(resume_id)
    data = request.get_json() or {}

    if 'status' in data:
        candidate.status = data['status']

    db.session.commit()

    return jsonify({
        'message': 'Status updated successfully',
        'candidate': candidate.to_dict(),
    }), 200


@hr_bp.route('/hr/jd/upload_removed', methods=['POST'])
@auth_required()
def upload_job_description_removed():
    """Deprecated endpoint - use /api/genai/jd endpoints instead."""
    return jsonify({
        'error': 'This endpoint has been removed. Use /api/genai/jd/generate and /api/genai/jd/save instead.'
    }), 410


@hr_bp.route('/hr/jd/generate_removed', methods=['POST'])
@auth_required()
def generate_job_description_removed():
    """Deprecated endpoint - use /api/genai/jd/generate instead."""
    return jsonify({
        'error': 'This endpoint has been removed. Use /api/genai/jd/generate instead.'
    }), 410


@hr_bp.route('/hr/jd/match', methods=['POST'])
@auth_required()
def match_candidates_to_jd():
    """
    Match all candidates to a specific job description.
    Returns top matches sorted by score.
    """
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    data = request.get_json() or {}

    if 'job_description_id' not in data:
        return jsonify({'error': 'job_description_id is required'}), 400

    jd = JobDescription.query.get_or_404(data['job_description_id'])

    candidates = CandidateResume.query.all()
    matches = []

    for candidate in candidates:
        try:
            candidate_data = {
                'skills': json.loads(candidate.skills) if candidate.skills else [],
                'experience': json.loads(candidate.experience) if candidate.experience else [],
                'education': json.loads(candidate.education) if candidate.education else [],
                'total_experience': candidate.total_experience,
                'current_role': candidate.current_role,
                'summary': candidate.summary,
            }

            jd_data = {
                'requirements': json.loads(jd.requirements) if jd.requirements else [],
                'skills_required': json.loads(jd.skills_required) if jd.skills_required else [],
                'experience_required': jd.experience_required,
                'description': jd.description,
                'title': jd.title,
            }

            match_result = match_resume_to_jd_gemini(candidate_data, jd_data)

            match = ResumeMatch(
                job_description_id=jd.id,
                candidate_resume_id=candidate.id,
                match_score=match_result['match_score'],
                reasoning=match_result['reasoning'],
            )
            db.session.add(match)

            matches.append({
                'candidate': candidate.to_dict(),
                'match_score': match_result['match_score'],
                'reasoning': match_result['reasoning'],
            })

        except Exception as e:
            print(f"Error matching candidate {candidate.id}: {str(e)}")
            continue

    db.session.commit()

    matches.sort(key=lambda x: x['match_score'], reverse=True)
    top_n = data.get('top_n', 10)
    matches = matches[:top_n]

    return jsonify({
        'message': f'Matched {len(matches)} candidates',
        'job_description': jd.to_dict(),
        'matches': matches,
    }), 200


@hr_bp.route('/hr/jd', methods=['GET'])
@auth_required()
def get_all_job_descriptions():
    """Get all job descriptions."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    jds = JobDescription.query.order_by(JobDescription.uploaded_at.desc()).all()

    return jsonify({
        'job_descriptions': [jd.to_dict() for jd in jds],
    }), 200


@hr_bp.route('/hr/analytics/applicants-gender', methods=['GET'])
@auth_required()
def get_applicants_by_gender():
    """Get analytics for applicants by gender."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    from sqlalchemy import func

    results = db.session.query(
        CandidateResume.gender,
        func.count(CandidateResume.id).label('count'),
    ).group_by(CandidateResume.gender).all()

    analytics = {
        'Male': 0,
        'Female': 0,
        'Other': 0,
    }

    for gender, count in results:
        if gender in analytics:
            analytics[gender] = count

    return jsonify(analytics), 200


@hr_bp.route('/hr/analytics/applicants-source', methods=['GET'])
@auth_required()
def get_applicants_by_source():
    """Get analytics for applicants by source."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    from sqlalchemy import func

    results = db.session.query(
        CandidateResume.source,
        func.count(CandidateResume.id).label('count'),
    ).group_by(CandidateResume.source).all()

    analytics = {source: count for source, count in results if source}

    return jsonify(analytics), 200


@hr_bp.route('/hr/analytics/applicants-status', methods=['GET'])
@auth_required()
def get_applicants_by_status():
    """Get analytics for applicants by status."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    from sqlalchemy import func

    results = db.session.query(
        CandidateResume.status,
        func.count(CandidateResume.id).label('count'),
    ).group_by(CandidateResume.status).all()

    analytics = {status: count for status, count in results if status}

    return jsonify(analytics), 200


@hr_bp.route('/hr/analytics/overview', methods=['GET'])
@auth_required()
def get_analytics_overview():
    """Get comprehensive analytics overview."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    total_candidates = CandidateResume.query.count()
    total_jds = JobDescription.query.count()

    from sqlalchemy import func

    avg_experience = (
        db.session.query(func.avg(CandidateResume.total_experience)).scalar() or 0
    )

    return jsonify({
        'total_candidates': total_candidates,
        'total_job_descriptions': total_jds,
        'average_experience': round(avg_experience, 1),
        'top_skills': _get_top_skills(limit=10),
        'recent_applications': _get_recent_applications(limit=5),
    }), 200


def _get_top_skills(limit=10):
    """Helper to get top skills from resumes."""
    from collections import Counter

    candidates = CandidateResume.query.all()
    all_skills = []

    for candidate in candidates:
        if candidate.skills:
            skills = json.loads(candidate.skills)
            all_skills.extend(skill.lower().strip() for skill in skills)

    skill_counts = Counter(all_skills)
    return [
        {'skill': skill, 'count': count}
        for skill, count in skill_counts.most_common(limit)
    ]


@hr_bp.route('/hr/teams', methods=['GET'])
@auth_required()
def get_all_teams():
    """Get all teams from the team table for selection in UI."""
    if not current_user.has_role('hr'):
        return jsonify({'error': 'Unauthorized - HR access required'}), 403

    teams = Team.query.order_by(Team.name.asc()).all()
    return jsonify({
        'teams': [t.to_dict() for t in teams],
    }), 200


def _get_recent_applications(limit=5):
    """Helper to get recent applications."""
    candidates = CandidateResume.query.order_by(
        CandidateResume.uploaded_at.desc()
    ).limit(limit).all()

    return [{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'current_role': c.current_role,
        'uploaded_at': c.uploaded_at.isoformat() if c.uploaded_at else None,
    } for c in candidates]
