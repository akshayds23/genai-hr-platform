"""
API endpoints for employee offboarding processes.

This blueprint exposes operations for employees to initiate a resignation,
administrators to view and update offboarding tasks, and managers to track
the exit status of their team members. Offboarding tasks are created when
an employee resigns and must be completed by various roles (HR, admin,
IT, etc.) before the process is considered complete.
"""

from datetime import datetime, date
from typing import List, Optional

from flask import Blueprint, jsonify, request, Response
from flask_security import auth_required, current_user

from app.models.models import db, OffboardingTask, User, LeaveRequest, Role, GeneratedLetter, LetterTemplate
from app.services.notifications import determine_manager_ids, notify_users
from app.services.offboarding import start_offboarding_for_user, generate_offboarding_letter


offboarding_bp = Blueprint('offboarding', __name__)


# Default tasks generated for every offboarding event. These tasks represent
# the responsibilities of different departments to ensure a smooth exit.
DEFAULT_OFFBOARDING_TASKS: List[dict] = [
    {
        'assignee_role': 'manager',
        'description': 'Collect company assets (laptop, ID card, etc.)',
    },
    {
        'assignee_role': 'it',
        'description': 'Revoke system and email access',
    },
    {
        'assignee_role': 'hr',
        'description': 'Conduct exit interview and finalize paperwork',
    },
]


def _is_admin_or_manager(user: User) -> bool:
    """Return True if the user has an admin or manager role."""
    if hasattr(user, 'is_admin') and user.is_admin():
        return True
    return (getattr(user, 'employment_role', '') or '').lower() == 'manager'


def _normalize_status(value: Optional[str]) -> str:
    """Normalize a status string for comparison."""
    return (value or '').strip().lower()


def _find_incomplete_predecessor(task: OffboardingTask) -> Optional[OffboardingTask]:
    """
    Return the earliest prior task for the same user that is not completed.

    Tasks are ordered by their primary key which reflects the creation order,
    matching how the frontend renders the timeline.
    """
    return (
        OffboardingTask.query
        .filter(OffboardingTask.user_id == task.user_id)
        .filter(OffboardingTask.id < task.id)
        .filter(OffboardingTask.status != 'completed')
        .order_by(OffboardingTask.id.asc())
        .first()
    )


def _find_other_in_progress_task(task: OffboardingTask) -> Optional[OffboardingTask]:
    """Return another task for the same user that is currently running."""
    return (
        OffboardingTask.query
        .filter(OffboardingTask.user_id == task.user_id)
        .filter(OffboardingTask.status == 'in_progress')
        .filter(OffboardingTask.id != task.id)
        .first()
    )


def _validate_status_transition(task: OffboardingTask, new_status: str) -> Optional[str]:
    """Enforce sequential task progression rules."""
    current = _normalize_status(task.status)
    if new_status == current:
        return None

    if new_status == 'pending':
        if current != 'pending':
            return 'Tasks cannot be moved back to pending once started.'
        return None

    if new_status == 'in_progress':
        if current not in {'pending', 'in_progress'}:
            return 'Only pending tasks may be started.'
        predecessor = _find_incomplete_predecessor(task)
        if predecessor:
            return f'Complete "{predecessor.description}" before starting this task.'
        other_running = _find_other_in_progress_task(task)
        if other_running:
            return 'Another task is already in progress for this employee.'
        return None

    if new_status == 'completed':
        if current != 'in_progress':
            return 'Start the task before marking it complete.'
        predecessor = _find_incomplete_predecessor(task)
        if predecessor:
            return f'Complete "{predecessor.description}" before closing this task.'
        return None

    return 'Unsupported status transition.'


def _should_deactivate_user_on_completion(task: OffboardingTask) -> bool:
    """
    Determine if completing this task should deactivate the employee.

    We currently treat IT revocation tasks as the trigger point, since the
    employee should retain access up until accounts are revoked.
    """
    role = (task.assignee_role or '').strip().lower()
    description = (task.description or '').strip().lower()
    if role == 'it':
        return True
    return 'revoke' in description and 'access' in description


@offboarding_bp.route('/offboarding/resign', methods=['POST'])
@auth_required()
def submit_resignation():
    """
    Initiate an offboarding process for the authenticated employee.

    The employee's account will be marked inactive and a resignation leave
    request will be created. Default offboarding tasks are generated and
    notifications are sent to managers and HR.
    """
    data = request.get_json() or {}
    # Determine final working day; default to today if not provided
    last_day_raw = (data.get('last_day') or data.get('final_day') or '').strip()
    if last_day_raw:
        try:
            final_day = datetime.strptime(last_day_raw, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid last_day format. Expected YYYY-MM-DD.'}), 400
    else:
        final_day = date.today()

    # Check for existing resignation/offboarding leave requests
    existing = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == current_user.id)
        .filter(LeaveRequest.leave_type.in_(['resignation', 'offboarding']))
        .filter(LeaveRequest.status.in_(['pending', 'approved']))
        .first()
    )
    if existing:
        return jsonify({'error': 'An offboarding request is already in progress.'}), 400

    # Delegate to the shared offboarding service which centralises
    # leave creation, task creation and notifications. This keeps
    # behaviour consistent with admin-triggered offboarding.
    result = start_offboarding_for_user(current_user, final_day=final_day, initiator_id=current_user.id, reason=data.get('reason'))
    return jsonify({'message': 'Resignation submitted successfully.', 'leave': result.get('leave'), 'tasks': result.get('tasks')}), 200


@offboarding_bp.route('/offboarding/tasks', methods=['GET'])
@auth_required()
def list_offboarding_tasks():
    """
    Retrieve offboarding tasks relevant to the current user.

    - Employees see only their own tasks.
    - Managers see tasks for their team members.
    - Admins and super admins see tasks across the organisation.
    Optional query parameters:
      - user_id: filter by a specific employee
      - status: comma separated list of statuses
    """
    # Determine scope
    user_id_param = request.args.get('user_id')
    status_param = request.args.get('status', '')
    statuses = {s.strip().lower() for s in status_param.split(',') if s.strip()}
    tasks_query = OffboardingTask.query

    # Filter by user id if provided
    if user_id_param:
        try:
            uid = int(user_id_param)
        except ValueError:
            return jsonify({'error': 'user_id must be an integer'}), 400
        tasks_query = tasks_query.filter(OffboardingTask.user_id == uid)
    else:
        if _is_admin_or_manager(current_user):
            # Managers/Admins see tasks for their team or all
            if not current_user.is_admin():
                team_number = getattr(current_user, 'team_number', None)
                if team_number:
                    team_member_ids = [
                        member.id
                        for member in User.query
                        .filter(User.team_number == team_number)
                        .filter(User.active.is_(False))
                        .all()
                    ]
                    tasks_query = tasks_query.filter(OffboardingTask.user_id.in_(team_member_ids))
        else:
            # Regular employees only see their own tasks
            tasks_query = tasks_query.filter(OffboardingTask.user_id == current_user.id)

    if statuses:
        tasks_query = tasks_query.filter(OffboardingTask.status.in_(list(statuses)))

    tasks = [task.to_dict() for task in tasks_query.order_by(OffboardingTask.due_date.asc()).limit(100).all()]
    return jsonify({'tasks': tasks})


@offboarding_bp.route('/offboarding/tasks/<int:task_id>/reopen', methods=['POST'])
@auth_required()
def reopen_offboarding_task(task_id: int):
    """
    Reopen a completed offboarding task.

    This endpoint allows HR/admins to reopen completed tasks by bypassing
    the normal status transition validation. The task will be set back to
    'in_progress' status and the completed_at timestamp will be cleared.
    """
    if not _is_admin_or_manager(current_user):
        return jsonify({'error': 'Only managers or administrators may reopen offboarding tasks.'}), 403

    task = OffboardingTask.query.get_or_404(task_id)
    
    # Only allow reopening completed tasks
    if task.status != 'completed':
        return jsonify({'error': 'Only completed tasks can be reopened.'}), 400
    
    # Reopen the task by setting it to in_progress and clearing completion timestamp
    task.status = 'in_progress'
    task.completed_at = None
    
    # If this task completion had deactivated the user, reactivate them
    if _should_deactivate_user_on_completion(task):
        user = User.query.get(task.user_id)
        if user and not user.active:
            user.active = True
            db.session.add(user)
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({'task': task.to_dict(), 'message': 'Task reopened successfully'})


@offboarding_bp.route('/offboarding/tasks/<int:task_id>', methods=['PATCH'])
@auth_required()
def update_offboarding_task(task_id: int):
    """
    Update the status or due date of an offboarding task.

    Only managers, admins or super admins are allowed to modify tasks. The
    assignee_role field is not editable via this endpoint.
    Request body may include:
      - status: one of pending, in_progress, completed, cancelled
      - due_date: date in YYYY-MM-DD format
    """
    if not _is_admin_or_manager(current_user):
        return jsonify({'error': 'Only managers or administrators may update offboarding tasks.'}), 403

    task = OffboardingTask.query.get_or_404(task_id)
    data = request.get_json() or {}
    allowed_statuses = {'pending', 'in_progress', 'completed'}
    status = _normalize_status(data.get('status'))
    user_to_deactivate = None
    if status:
        if status not in allowed_statuses:
            return jsonify({'error': f'Invalid status. Allowed: {", ".join(sorted(allowed_statuses))}'}), 400
        transition_error = _validate_status_transition(task, status)
        if transition_error:
            return jsonify({'error': transition_error}), 400
        task.status = status
        if status == 'completed':
            if not task.completed_at:
                task.completed_at = datetime.utcnow()
            if _should_deactivate_user_on_completion(task):
                user_to_deactivate = User.query.get(task.user_id)
                if user_to_deactivate and user_to_deactivate.active:
                    user_to_deactivate.active = False
        else:
            task.completed_at = None
    due_date_raw = data.get('due_date')
    if due_date_raw:
        try:
            task.due_date = datetime.strptime(due_date_raw, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid due_date format. Expected YYYY-MM-DD.'}), 400
    db.session.add(task)
    if user_to_deactivate:
        db.session.add(user_to_deactivate)
    db.session.commit()
    return jsonify({'task': task.to_dict()})



@offboarding_bp.route('/offboarding/report', methods=['GET'])
@auth_required()
def offboarding_report():
    """Return a simple progress report for active offboardings.

    For each user with offboarding tasks, return counts and percent complete.
    Admins and managers see wider scopes; employees see only their own progress.
    """
    tasks_query = OffboardingTask.query
    if not _is_admin_or_manager(current_user):
        tasks_query = tasks_query.filter(OffboardingTask.user_id == current_user.id)

    rows = tasks_query.with_entities(OffboardingTask.user_id).distinct().all()
    user_ids = [r[0] for r in rows]
    report = []
    for uid in user_ids:
        total = OffboardingTask.query.filter(OffboardingTask.user_id == uid).count()
        completed = OffboardingTask.query.filter(OffboardingTask.user_id == uid, OffboardingTask.status == 'completed').count()
        user = User.query.get(uid)
        percent = int((completed / total) * 100) if total else 0
        report.append({'user': user.to_dict() if user else {'id': uid}, 'total_tasks': total, 'completed_tasks': completed, 'percent_complete': percent})
    return jsonify({'report': report})



@offboarding_bp.route('/offboarding/generate-letter', methods=['POST'])
@auth_required()
def generate_letter():
    """Generate a letter for a user from a named template.

    Request JSON should include:
      - template_name: string (required)
      - user_id: integer (optional; defaults to current user). Admins may generate for others.
    """
    data = request.get_json() or {}
    template_name = data.get('template_name')
    if not template_name:
        return jsonify({'error': 'template_name is required.'}), 400

    target_user_id = data.get('user_id')
    if target_user_id:
        if not _is_admin_or_manager(current_user):
            return jsonify({'error': 'Only managers/admins may generate letters for other users.'}), 403
        target_user = User.query.get_or_404(int(target_user_id))
    else:
        target_user = current_user

    try:
        generated = generate_offboarding_letter(target_user, template_name)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to generate letter', 'details': str(e)}), 500

    return jsonify({'letter': {'id': generated.id, 'content': generated.content}})



@offboarding_bp.route('/offboarding/run-reminders', methods=['POST'])
@auth_required()
def run_offboarding_reminders():
    """Trigger reminder scan. Admins/managers only."""
    if not _is_admin_or_manager(current_user):
        return jsonify({'error': 'Only managers or administrators may run reminders.'}), 403
    from app.services.offboarding import run_reminders
    try:
        result = run_reminders()
    except Exception as e:
        return jsonify({'error': 'Failed to run reminders', 'details': str(e)}), 500
    return jsonify({'message': 'Reminders run', 'result': result})



@offboarding_bp.route('/offboarding/letters', methods=['GET'])
@auth_required()
def list_generated_letters():
    """List generated letters for a user (or current user by default)."""
    user_id = request.args.get('user_id')
    if user_id:
        if not _is_admin_or_manager(current_user):
            return jsonify({'error': 'Only managers or admins may list letters for other users.'}), 403
        target_user = User.query.get_or_404(int(user_id))
    else:
        target_user = current_user

    letters = GeneratedLetter.query.filter(GeneratedLetter.user_id == target_user.id).order_by(GeneratedLetter.created_at.desc()).limit(50).all()
    return jsonify({'letters': [{'id': l.id, 'template_id': l.template_id, 'created_at': l.created_at.isoformat(), 'snippet': (l.content or '')[:240]} for l in letters]})



@offboarding_bp.route('/offboarding/letters/<int:letter_id>', methods=['GET'])
@auth_required()
def get_generated_letter(letter_id: int):
    letter = GeneratedLetter.query.get_or_404(letter_id)
    # permission: admins/managers or owner
    if letter.user_id != current_user.id and not _is_admin_or_manager(current_user):
        return jsonify({'error': 'Not allowed to view this letter.'}), 403
    return jsonify({'id': letter.id, 'template_id': letter.template_id, 'content': letter.content, 'created_at': letter.created_at.isoformat()})



@offboarding_bp.route('/offboarding/letters/<int:letter_id>/download', methods=['GET'])
@auth_required()
def download_generated_letter(letter_id: int):
    letter = GeneratedLetter.query.get_or_404(letter_id)
    if letter.user_id != current_user.id and not _is_admin_or_manager(current_user):
        return jsonify({'error': 'Not allowed to download this letter.'}), 403
    # Return plain text for now with attachment headers
    content = letter.content or ''
    resp = Response(content, mimetype='text/plain')
    resp.headers.set('Content-Disposition', f'attachment', filename=f'letter_{letter.id}.txt')
    return resp
