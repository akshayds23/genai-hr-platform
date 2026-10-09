from datetime import date, datetime
from typing import Dict, Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_security import auth_required, roles_required, current_user
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import joinedload

from app.models.models import (
    CandidateResume,
    HRQuestionLog,
    LeaveRequest,
    Role,
    Team,
    User,
    db,
)
from app.services.notifications import notify_users
from app.api.genai.B_HRchatbot import hr_chatbot_service


admin_portal_bp = Blueprint('admin_portal', __name__)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _parse_pagination(param: str, default: int, minimum: int = 1, maximum: int = 100) -> int:
    try:
        value = int(request.args.get(param, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def _determine_employee_status(user: User) -> str:
    status = 'active' if user.active else 'inactive'
    today = date.today()
    current_leave_exists = (
        db.session.query(LeaveRequest.id)
        .filter(
            LeaveRequest.user_id == user.id,
            func.lower(LeaveRequest.status) == 'approved',
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        )
        .limit(1)
        .scalar()
        is not None
    )
    if current_leave_exists:
        status = 'on_leave'
    return status


def _serialize_user(user: User) -> Dict:
    if user.has_role('hr'):
        role_label = 'hr'
    elif user.has_role('manager'):
        role_label = 'manager'
    else:
        role_label = user.employment_role

    return {
        'id': user.id,
        'full_name': ' '.join(
            part for part in [user.first_name, user.last_name] if part
        ) or user.username or user.email,
        'email': user.email,
        'employee_id': user.employee_id,
        'department': user.department,
        'employment_role': user.employment_role,
        'role': role_label,
        'manager_id': user.manager_id,
        'team_number': user.team_number,
        'status': _determine_employee_status(user),
        'active': user.active,
    }


def _apply_leave_decision(leave: LeaveRequest, new_status: str, comment: Optional[str] = None) -> None:
    leave.status = new_status
    leave.decision_reason = (comment or '').strip() or None
    leave.approver_id = current_user.id
    leave.updated_at = datetime.utcnow()
    db.session.add(leave)

    notify_users(
        [leave.user_id],
        category='leave',
        title='Leave request updated',
        message=(
            f'Your leave request for '
            f'{leave.start_date.isoformat() if leave.start_date else ""} - '
            f'{leave.end_date.isoformat() if leave.end_date else ""} was {new_status}.'
        ),
        metadata={
            'leave_id': leave.id,
            'status': new_status,
            'comment': leave.decision_reason,
        },
    )


# ---------------------------------------------------------------------------
# Departments & employee search
# ---------------------------------------------------------------------------


@admin_portal_bp.route('/admin/departments', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_departments():
    departments = (
        db.session.query(User.department)
        .filter(User.department.isnot(None))
        .filter(User.department != '')
        .distinct()
        .order_by(User.department.asc())
        .all()
    )
    return jsonify({
        'departments': [department for (department,) in departments]
    })


@admin_portal_bp.route('/admin/employees/search', methods=['GET'])
@auth_required()
@roles_required('hr')
def search_employees():
    query_text = (request.args.get('query') or '').strip().lower()
    employee_id = (request.args.get('employee_id') or '').strip()
    department = (request.args.get('department') or '').strip()
    role = (request.args.get('role') or '').strip().lower()
    status = (request.args.get('status') or '').strip().lower()

    page = _parse_pagination('page', default=1, maximum=250)
    page_size = _parse_pagination('page_size', default=10, maximum=250)

    query = User.query.filter(
        ~User.roles.any(Role.name.in_(['manager', 'hr']))
    )

    if query_text:
        like_pattern = f'%{query_text}%'
        query = query.filter(
            or_(
                func.lower(func.coalesce(User.first_name, '')).like(like_pattern),
                func.lower(func.coalesce(User.last_name, '')).like(like_pattern),
                func.lower(func.coalesce(User.email, '')).like(like_pattern),
            )
        )

    if employee_id:
        query = query.filter(User.employee_id.ilike(f'%{employee_id}%'))

    if department:
        query = query.filter(User.department == department)

    if role:
        query = query.filter(func.lower(User.employment_role) == role)

    if status == 'active':
        query = query.filter(User.active.is_(True))
    elif status == 'inactive':
        query = query.filter(User.active.is_(False))
    elif status == 'on_leave':
        today = date.today()
        query = query.join(
            LeaveRequest,
            and_(
                LeaveRequest.user_id == User.id,
                LeaveRequest.status == 'approved',
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today,
            ),
        )
    elif status == 'offboarded':
        query = query.filter(User.active.is_(False))

    total = query.count()
    results = (
        query.order_by(func.lower(func.coalesce(User.first_name, User.username)))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return jsonify({
        'results': [_serialize_user(user) for user in results],
        'total': total,
        'page': page,
        'page_size': page_size,
    })


# ---------------------------------------------------------------------------
# Leave approvals
# ---------------------------------------------------------------------------


def _serialize_leave(leave: LeaveRequest) -> Dict:
    user = leave.user
    return {
        'id': leave.id,
        'status': leave.status,
        'leave_type': leave.leave_type,
        'reason': leave.reason,
        'start_date': leave.start_date.isoformat() if leave.start_date else None,
        'end_date': leave.end_date.isoformat() if leave.end_date else None,
        'submitted_at': leave.created_at.isoformat() if leave.created_at else None,
        'manager_name': (
            f'{user.first_name} {user.last_name}'.strip()
            if user and (user.first_name or user.last_name)
            else user.email if user else None
        ),
        'manager_id': user.id if user else None,
        'decision_reason': leave.decision_reason,
    }


@admin_portal_bp.route('/admin/leaves', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_manager_leaves():
    submitted_by = (request.args.get('submitted_by') or '').strip().lower()
    status_filter = (request.args.get('status') or '').strip().lower()

    # Join users and optionally their team to understand manager assignment.
    query = (
        LeaveRequest.query
        .join(User, LeaveRequest.user_id == User.id)
        .outerjoin(Team, User.team_id == Team.id)
    )

    if submitted_by == 'manager':
        query = query.filter(func.lower(User.employment_role) == 'manager')
    elif submitted_by == 'employee':
        
        query = query.filter(func.lower(User.employment_role) == 'employee')
        query = query.filter(
            and_(
                User.manager_id.is_(None),
                or_(
                    User.team_id.is_(None),
                    Team.manager_id.is_(None),
                ),
            )
        )

    if status_filter:
        statuses = [status.strip() for status in status_filter.split(',') if status.strip()]
        if statuses:
            query = query.filter(LeaveRequest.status.in_(statuses))

   
    query = query.filter(LeaveRequest.leave_type.notin_(['resignation', 'offboarding']))

    leaves = query.order_by(LeaveRequest.created_at.desc()).limit(200).all()
    return jsonify({
        'leaves': [_serialize_leave(leave) for leave in leaves]
    })


@admin_portal_bp.route('/admin/leaves/<int:leave_id>/approve', methods=['POST'])
@auth_required()
@roles_required('hr')
def approve_leave(leave_id: int):
    leave = LeaveRequest.query.get_or_404(leave_id)
    if leave.status == 'approved':
        return jsonify({'message': 'Leave request already approved.'}), 200

    _apply_leave_decision(leave, 'approved')
    db.session.commit()
    return jsonify({'message': 'Leave request approved.'})


@admin_portal_bp.route('/admin/leaves/<int:leave_id>/reject', methods=['POST'])
@auth_required()
@roles_required('hr')
def reject_leave(leave_id: int):
    payload = request.get_json() or {}
    comment = payload.get('reason') or payload.get('comment')

    leave = LeaveRequest.query.get_or_404(leave_id)
    if leave.status == 'rejected':
        return jsonify({'message': 'Leave request already rejected.'}), 200

    _apply_leave_decision(leave, 'rejected', comment=comment)
    db.session.commit()
    return jsonify({'message': 'Leave request rejected.'})


# ---------------------------------------------------------------------------
# Escalated questions
# ---------------------------------------------------------------------------


def _serialize_question(question: HRQuestionLog) -> Dict:
    return {
        'id': question.id,
        'question': question.question,
        'answer': question.answer,
        'status': question.status,
        'confidence': question.confidence,
        'source': question.source,
        'created_at': question.created_at.isoformat() if question.created_at else None,
        'updated_at': question.updated_at.isoformat() if question.updated_at else None,
        'resolved_at': question.resolved_at.isoformat() if question.resolved_at else None,
        'user_id': question.user_id,
        'manager_id': question.manager_id,
        'asked_by': f"{question.requester.first_name or ''} {question.requester.last_name or ''}".strip() or question.requester.email if question.requester else 'Unknown',
    }


@admin_portal_bp.route('/admin/hr/questions', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_escalated_questions():
    status_filter = (request.args.get('status') or 'pending').lower()
    statuses = [status.strip() for status in status_filter.split(',') if status.strip()]

    query = HRQuestionLog.query.options(joinedload(HRQuestionLog.requester))
    if statuses and 'all' not in statuses:
        query = query.filter(HRQuestionLog.status.in_(statuses))

    questions = query.order_by(HRQuestionLog.created_at.desc()).limit(200).all()
    return jsonify({
        'questions': [_serialize_question(question) for question in questions]
    })


@admin_portal_bp.route('/admin/hr/questions/<int:question_id>/answer', methods=['POST'])
@auth_required()
@roles_required('hr')
def answer_escalated_question(question_id: int):
    payload = request.get_json() or {}
    answer = (payload.get('answer') or '').strip()
    if not answer:
        return jsonify({'error': 'Answer is required.'}), 400

    question = HRQuestionLog.query.get_or_404(question_id)
    question.answer = answer
    question.status = 'resolved'
    question.source = question.source or 'manual_review'
    question.resolved_by = current_user.id
    question.resolved_at = datetime.utcnow()
    question.updated_at = datetime.utcnow()
    if not question.manager_id:
        question.manager_id = current_user.id

    hr_chatbot_service.add_manual_knowledge(question.question, answer, source='manual_review')

    db.session.add(question)
    db.session.commit()

    if question.user_id:
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

    return jsonify({'message': 'Question answered and knowledge base updated.'})


# ---------------------------------------------------------------------------
# Resume summary
# ---------------------------------------------------------------------------


def _aggregate_resume_statuses() -> Tuple[Dict[str, int], int]:
    rows = (
        db.session.query(
            func.coalesce(func.lower(CandidateResume.status), 'pending').label('status'),
            func.count(CandidateResume.id),
        )
        .group_by('status')
        .all()
    )
    summary: Dict[str, int] = {}
    total = 0
    for status, count in rows:
        summary[status] = count
        total += count
    return summary, total


@admin_portal_bp.route('/admin/resumes/summary', methods=['GET'])
@auth_required()
@roles_required('hr')
def resume_summary():
    summary, total = _aggregate_resume_statuses()
    recent_uploads = (
        CandidateResume.query.order_by(CandidateResume.uploaded_at.desc())
        .limit(5)
        .all()
    )
    return jsonify({
        'summary': summary,
        'total': total,
        'recent_uploads': [resume.to_dict() for resume in recent_uploads],
    })
