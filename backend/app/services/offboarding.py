from datetime import date

from app.models.models import GeneratedLetter, LeaveRequest, LetterTemplate, OffboardingTask, User, db
from app.services.notifications import determine_manager_ids, notify_users

DEFAULT_FULL_OFFBOARDING_TASKS: list[dict] = [
    {'assignee_role': 'manager', 'description': 'Collect company assets (laptop, ID card, keys).'},
    {'assignee_role': 'it', 'description': 'Revoke system and email access and remove from groups.'},
    {'assignee_role': 'hr', 'description': 'Conduct exit interview and finalize paperwork.'},
    {'assignee_role': 'finance', 'description': 'Process final payroll and benefits settlement.'},
    {'assignee_role': 'manager', 'description': 'Handover responsibilities and update team docs.'},
]


def _create_leave_if_missing(user: User, final_day: date, reason: str | None = None) -> LeaveRequest:
    existing = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == user.id)
        .filter(LeaveRequest.leave_type.in_(['resignation', 'offboarding']))
        .filter(LeaveRequest.status.in_(['pending', 'approved']))
        .first()
    )
    if existing:
        return existing

    leave_request = LeaveRequest(
        user_id=user.id,
        leave_type='resignation',
        start_date=final_day,
        end_date=final_day,
        reason=reason or 'Resignation',
        status='pending',
    )
    db.session.add(leave_request)
    db.session.flush()
    return leave_request


def start_offboarding_for_user(
    user: User,
    final_day: date | None = None,
    initiator_id: int | None = None,
    reason: str | None = None,
) -> dict:
    """
    Begin the offboarding workflow for a user.

    Creates a resignation leave (if missing), marks the user inactive, creates
    default offboarding tasks for relevant departments and notifies relevant
    recipients (managers, HR, finance).

    Returns a dict with created leave and tasks information.
    """
    final_day = final_day or date.today()
    # Create leave if not present
    leave = _create_leave_if_missing(user, final_day, reason=reason)

    # Create tasks
    tasks: list[OffboardingTask] = []
    for spec in DEFAULT_FULL_OFFBOARDING_TASKS:
        task = OffboardingTask(
            user_id=user.id,
            assignee_role=spec['assignee_role'],
            description=spec['description'],
            due_date=final_day,
            status='pending',
        )
        db.session.add(task)
        tasks.append(task)

    # Notify managers and HR/finance
    manager_ids = determine_manager_ids(user)
    # find HR/finance/super_admins
    hr_finance_admins = (
        User.query
        .filter(User.active.is_(True))
        .filter(User.roles.any())
        .all()
    )
    # collect admins with roles that match hr/finance/super_admin
    recipient_ids = list(dict.fromkeys(manager_ids))
    for u in hr_finance_admins:
        role_names = {r.name for r in getattr(u, 'roles', [])}
        if 'hr' in role_names or 'finance' in role_names:
            if u.id != user.id:
                recipient_ids.append(u.id)

    if recipient_ids:
        notify_users(
            recipient_ids,
            category='offboarding',
            title='Offboarding initiated',
            message=f'Offboarding started for {user.first_name or user.email} effective {final_day.isoformat()}.',
            metadata={'employee_id': user.id, 'final_day': final_day.isoformat(), 'initiator_id': initiator_id},
            commit=True,
        )

    db.session.commit()

    return {'leave': leave.to_dict(), 'tasks': [t.to_dict() for t in tasks]}


def _render_template_placeholders(template: str, user: User) -> str:
    # Basic placeholder replacement for common fields
    mapping = {
        '{{first_name}}': user.first_name or '',
        '{{last_name}}': user.last_name or '',
        '{{full_name}}': f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip(),
        '{{job_title}}': user.job_title or '',
        '{{department}}': user.department or '',
        '{{employee_id}}': user.employee_id or '',
        '{{hire_date}}': user.hire_date.isoformat() if getattr(user, 'hire_date', None) else '',
        '{{company_name}}': '',
        '{{hr_representative_name}}': '',
        '{{hr_title}}': '',
        '{{last_day}}': '',
    }
    content = template
    for k, v in mapping.items():
        content = content.replace(k, v)
    return content


def generate_offboarding_letter(user: User, template_name: str) -> GeneratedLetter:
    """
    Generate a letter for a user from a named template. If GenAI is
    available, use it to rewrite and polish the generated letter.
    """
    template = LetterTemplate.query.filter(LetterTemplate.name == template_name).first()
    if not template:
        raise ValueError('Template not found')

    content = _render_template_placeholders(template.content, user)

    try:
        from app.services.ai import generate_text
        prompt = (
            f"Polish and formalise the following HR letter. Preserve meaning, keep it concise:\n\n{content}\n\n"
        )
        polished = generate_text(prompt, max_tokens=1024)
        if polished:
            content = polished
    except Exception:
        # Fall back to template content if AI call fails or is unavailable
        pass

    generated = GeneratedLetter(user_id=user.id, template_id=template.id, content=content)
    db.session.add(generated)
    db.session.commit()
    return generated


def run_reminders() -> dict:
    """
    Scan for due/offboarding tasks and send reminder notifications.

    Returns a summary dict with counts.
    """
    today = date.today()
    due_tasks = OffboardingTask.query.filter(OffboardingTask.due_date <= today).filter(OffboardingTask.status.in_(['pending', 'in_progress'])).all()
    notified = 0
    for task in due_tasks:
        # find active users who have the role or employment_role
        candidates = (
            User.query
            .filter(User.active.is_(True))
            .all()
        )
        recipients = []
        for u in candidates:
            roles = {r.name for r in getattr(u, 'roles', [])}
            if task.assignee_role in roles or task.assignee_role == getattr(u, 'employment_role', ''):
                recipients.append(u.id)
        if recipients:
            notify_users(
                recipients,
                category='offboarding_reminder',
                title='Offboarding task reminder',
                message=(f"Reminder: Task '{task.description}' for employee id {task.user_id} is due {task.due_date.isoformat() if task.due_date else 'soon'}"),
                metadata={'task_id': task.id, 'user_id': task.user_id, 'due_date': task.due_date.isoformat() if task.due_date else None},
                commit=False,
            )
            notified += len(recipients)
    if notified:
        db.session.commit()
    return {'tasks_checked': len(due_tasks), 'recipients_notified': notified}
