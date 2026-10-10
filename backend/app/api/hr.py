import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from werkzeug.utils import secure_filename

from app.models.models import CandidateResume, JobDescription, ResumeMatch, Team, db
from app.services.ai import AIUnavailableError
from app.services.resumes import (
    allowed_file,
    generate_resume_summary_gemini,
    match_resume_to_jd_gemini,
    process_single_resume,
)

logger = logging.getLogger(__name__)

hr_bp = Blueprint('hr', __name__)



MAX_RESUME_SIZE = 16 * 1024 * 1024  # 16 MB


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

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported: PDF, DOCX, TXT'}), 400

    filename = secure_filename(file.filename)
    file_content = file.read()
    if len(file_content) > MAX_RESUME_SIZE:
        return jsonify({'error': 'File size exceeds maximum limit of 16MB'}), 413

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

    except AIUnavailableError:
        db.session.rollback()
        return jsonify({'error': 'AI service is not available right now'}), 503
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process resume: {e!s}'}), 500


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
            if not allowed_file(file.filename):
                return {'success': False, 'filename': file.filename, 'error': 'Invalid file type'}
            filename = secure_filename(file.filename)
            file_content = file.read()
            if len(file_content) > MAX_RESUME_SIZE:
                return {'success': False, 'filename': filename, 'error': 'File exceeds 16MB limit'}
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
            'error': f'Failed to save candidates to database: {e!s}',
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
        return jsonify({'error': f'Failed to generate summary: {e!s}'}), 500


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

        except AIUnavailableError:
            raise
        except Exception as e:
            logger.warning("Error matching candidate %s: %s", candidate.id, e)
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
