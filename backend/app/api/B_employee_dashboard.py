import json
from datetime import date, datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request, current_app
from flask_security import auth_required, current_user
from sqlalchemy import func, or_

from app.api.genai.B_HRchatbot import hr_chatbot_service
from app.models.models import (
    AuditLog,
    Conversation,
    LeaveRequest,
    Message,
    ProjectAnnouncement,
    Team,
    TeamEvent,
    User,
    Experience,
    db,
)
from app.services.leave_balance import build_balance_snapshot
from app.services.notifications import recent_notifications_for_user, serialize_notification


employee_dashboard_bp = Blueprint('employee_dashboard', __name__)

ANNUAL_LEAVE_ALLOWANCE = 20
CAREER_TARGET_SKILLS = 8
MAX_RECENT_LEAVES = 5
MAX_UPCOMING_EVENTS = 5
MAX_NOTIFICATIONS = 5
MAX_CAREER_SKILLS = 6
MAX_NOTIFICATION_DETAILS_LEN = 160
MAX_CHATBOT_SNIPPET = 160
MAX_TEAM_MEMBERS = 8
DEFAULT_TEAM_BIRTHDAY_WINDOW = 30
MAX_TEAM_BIRTHDAY_LOOKAHEAD = 90
MAX_PROJECT_ASSIGNMENTS = 6


def _safe_parse_json(raw_value):
    if not raw_value:
        return None
    try:
        return json.loads(raw_value)
    except (TypeError, ValueError):
        return None


def _truncate(text: str, max_length: int = MAX_NOTIFICATION_DETAILS_LEN) -> str:
    if not text:
        return ''
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + '...'


def _safe_next_birthday(birth_date: date, today: date) -> date:
    try:
        candidate = date(today.year, birth_date.month, birth_date.day)
    except ValueError:
        candidate = date(today.year, 2, 28)

    if candidate < today:
        year = today.year + 1
        try:
            return date(year, birth_date.month, birth_date.day)
        except ValueError:
            return date(year, 2, 28)
    return candidate


def _display_name(user: Optional[User]) -> str:
    if not user:
        return 'Team member'
    parts = [user.first_name, user.last_name]
    fallback = user.username or user.email or f'User {user.id}'
    return ' '.join(part for part in parts if part) or fallback


def _collect_team_birthdays(
    user: User,
    window_days: int = DEFAULT_TEAM_BIRTHDAY_WINDOW,
    *,
    team: Team | None = None,
) -> dict:
    window_days = max(1, min(window_days, MAX_TEAM_BIRTHDAY_LOOKAHEAD))
    today = date.today()

    if not team and not user.team_number:
        return {'window_days': window_days, 'today': [], 'upcoming': []}

    query = (
        User.query
        .filter(User.active.is_(True))
        .filter(User.birth_date.isnot(None))
    )
    if team:
        query = query.filter(User.team_id == team.id)
    else:
        query = query.filter(User.team_number == user.team_number)
    members = (
        query
        .order_by(User.first_name.asc(), User.last_name.asc())
        .all()
    )

    upcoming = []
    for member in members:
        if not member.birth_date:
            continue
        next_birthday = _safe_next_birthday(member.birth_date, today)
        days_until = (next_birthday - today).days
        if days_until < 0 or days_until > window_days:
            continue
        upcoming.append({
            'employee_id': member.id,
            'employee_name': _display_name(member),
            'birth_date': member.birth_date.isoformat(),
            'next_birthday': next_birthday.isoformat(),
            'days_until': days_until,
            'turning': next_birthday.year - member.birth_date.year,
            'team_number': member.team_number,
        })

    upcoming.sort(key=lambda entry: (entry['days_until'], entry['employee_name']))
    today_birthdays = [entry for entry in upcoming if entry['days_until'] == 0]

    return {
        'window_days': window_days,
        'today': today_birthdays,
        'upcoming': upcoming,
    }

def _leave_days_in_year(leave: LeaveRequest, year: int) -> int:
    """Return the number of days of a leave request that fall within the given year."""
    if not leave.start_date or not leave.end_date:
        return 0

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    effective_start = max(leave.start_date, year_start)
    effective_end = min(leave.end_date, year_end)

    if effective_end < effective_start:
        return 0

    return (effective_end - effective_start).days + 1


def _load_manager_project_announcement_for_employee(user: User) -> dict | None:
    manager_ids = []

    if getattr(user, 'manager_id', None):
        manager_ids.append(user.manager_id)

    if user.team_number:
        team_manager_ids = (
            User.query
            .with_entities(User.id)
            .filter(User.team_number == user.team_number)
            .filter(func.lower(func.coalesce(User.employment_role, '')) == 'manager')
            .all()
        )
        manager_ids.extend(manager_id for (manager_id,) in team_manager_ids)

    manager_ids = [mid for mid in {mid for mid in manager_ids if mid}]

    query = ProjectAnnouncement.query.order_by(ProjectAnnouncement.updated_at.desc())
    if manager_ids:
        query = query.filter(ProjectAnnouncement.manager_id.in_(manager_ids))

    record = query.first()
    if not record:
        return None
    return {
        'manager_id': record.manager_id,
        'title': record.title,
        'description': record.description,
        'createdAt': record.created_at.isoformat() if record.created_at else None,
        'lastUpdated': record.updated_at.isoformat() if record.updated_at else None,
    }


def _format_event_time(event: TeamEvent) -> str:
    """Return a human readable range for the event timeframe."""
    start = event.start_datetime
    end = event.end_datetime

    if not start:
        return ''

    if end:
        if start.date() == end.date():
            return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
        return f"{start.strftime('%b %d %I:%M %p')} - {end.strftime('%b %d %I:%M %p')}"

    return start.strftime('%b %d %I:%M %p')


def _format_tenure_label(years: int, months: int) -> str:
    if not years and not months:
        return 'Joined recently'
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    return ' '.join(parts)


def _build_profile_snapshot(user: User, today: date) -> dict:
    full_name_parts = [part for part in (user.first_name, user.last_name) if part]
    full_name = ' '.join(full_name_parts) or (user.username or user.email)

    manager_info = None
    if user.manager_id:
        manager = User.query.get(user.manager_id)
        if manager:
            manager_name_parts = [manager.first_name, manager.last_name]
            manager_info = {
                'id': manager.id,
                'name': ' '.join(part for part in manager_name_parts if part) or manager.username,
                'email': manager.email,
            }
    if manager_info is None and user.team_number:
        fallback_manager = (
            User.query
            .filter(User.team_number == user.team_number)
            .filter(User.id != user.id)
            .filter(User.employment_role == 'manager')
            .filter(User.active.is_(True))
            .order_by(User.first_name.asc(), User.last_name.asc())
            .first()
        )
        if fallback_manager:
            fallback_name_parts = [fallback_manager.first_name, fallback_manager.last_name]
            manager_info = {
                'id': fallback_manager.id,
                'name': ' '.join(part for part in fallback_name_parts if part) or fallback_manager.username,
                'email': fallback_manager.email,
            }

    tenure = None
    if user.hire_date:
        delta_days = max((today - user.hire_date).days, 0)
        years = delta_days // 365
        months = (delta_days % 365) // 30
        tenure = {
            'years': years,
            'months': months,
            'label': _format_tenure_label(years, months)
        }

    return {
        'full_name': full_name,
        'job_title': user.job_title,
        'department': user.department,
        'employment_role': user.employment_role,
        'employee_id': user.employee_id,
        'team_number': user.team_number,
        'hire_date': user.hire_date.isoformat() if user.hire_date else None,
        'tenure': tenure,
        'manager': manager_info,
        'contact': {
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
        }
    }


def _resolve_employee_team(user: User) -> Team | None:
    if user.team_id:
        team = Team.query.get(user.team_id)
        if team:
            return team
    if user.team_number:
        team = Team.query.filter_by(team_number=user.team_number).first()
        if team:
            return team
    return Team.query.filter_by(manager_id=user.id).first()


def _build_team_overview(user: User) -> dict:
    team = _resolve_employee_team(user)
    team_label = (team.name if team else user.team_number) or 'Team'
    
    base = {
        'team_number': team_label,
        'team_name': team_label,
        'members': [],
        'total_members': 1,
        'has_more': False,
        'empty_message': 'You are not yet assigned to a team.',
        'birthday_window': DEFAULT_TEAM_BIRTHDAY_WINDOW,
        'birthdayWindow': DEFAULT_TEAM_BIRTHDAY_WINDOW,
        'birthdays': {
            'window_days': DEFAULT_TEAM_BIRTHDAY_WINDOW,
            'today': [],
            'upcoming': [],
        },
        'manager': None,
    }
    if not team and not user.team_number:
        return base

    if team:
        member_filter = User.team_id == team.id
    else:
        member_filter = User.team_number == user.team_number

    query = (
        User.query
        .filter(member_filter)
        .filter(User.active.is_(True))
        .order_by(User.first_name.asc(), User.last_name.asc())
    )

    total_members = query.count()
    members = []
    for member in query.limit(MAX_TEAM_MEMBERS).all():
        full_name_parts = [part for part in (member.first_name, member.last_name) if part]
        members.append({
            'id': member.id,
            'name': ' '.join(full_name_parts) or member.username or member.email,
            'job_title': member.job_title,
            'employment_role': member.employment_role,
            'email': member.email,
            'is_self': member.id == user.id,
            'team_number': member.team_number,
        })
    birthday_window = DEFAULT_TEAM_BIRTHDAY_WINDOW
    birthdays = _collect_team_birthdays(user, birthday_window, team=team)

    manager_user = None
    if team and team.manager_id:
        manager_user = User.query.get(team.manager_id)
    if not manager_user and user.team_number:
        manager_user = (
            User.query
            .filter(User.team_number == user.team_number)
            .filter(User.active.is_(True))
            .filter(func.lower(func.coalesce(User.employment_role, '')) == 'manager')
            .order_by(User.first_name.asc(), User.last_name.asc())
            .first()
        )
    manager = None
    if manager_user:
        mgr_parts = [part for part in (manager_user.first_name, manager_user.last_name) if part]
        manager = {
            'id': manager_user.id,
            'name': ' '.join(mgr_parts) or manager_user.username or manager_user.email,
            'job_title': manager_user.job_title,
            'employment_role': manager_user.employment_role,
            'email': manager_user.email,
        }

    return {
        'team_number': team_label,
        'team_name': team_label,
        'members': members,
        'total_members': total_members or len(members) or 1,
        'has_more': total_members > len(members),
        'empty_message': None if members else 'No teammates recorded yet.',
        'birthday_window': birthday_window,
        'birthdayWindow': birthday_window,
        'birthdays': birthdays,
        'manager': manager,
    }


def _collect_project_assignments(user: User) -> dict:
    raw_entries = []
    parsed = _safe_parse_json(user.experience_json)
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                raw_entries.append(item)

    if not raw_entries:
        qs = (
            user.experiences
            .order_by(Experience.start_date.desc().nullslast())
            .limit(MAX_PROJECT_ASSIGNMENTS)
        )
        for exp in qs:
            raw_entries.append({
                'project_name': getattr(exp, 'role', None),
                'client': getattr(exp, 'company', None),
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'description': exp.responsibilities,
                'role': exp.role,
            })

    assignments = []
    for entry in raw_entries[:MAX_PROJECT_ASSIGNMENTS]:
        name = (
            entry.get('project_name')
            or entry.get('name')
            or entry.get('title')
            or entry.get('company')
            or 'Project'
        )
        role = entry.get('role') or entry.get('position')
        client = entry.get('client') or entry.get('company')
        summary = entry.get('description') or entry.get('responsibilities')
        start_date = entry.get('start_date')
        end_date = entry.get('end_date')

        assignments.append({
            'name': name,
            'role': role,
            'client': client,
            'summary': summary,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': not bool(end_date),
        })

    active_count = sum(1 for item in assignments if item['is_active'])

    return {
        'assignments': assignments,
        'active_count': active_count,
        'history_count': len(assignments),
        'has_history': bool(assignments),
    }


def _build_leave_summary(user_id: int) -> dict:
    rows = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == user_id)
        .with_entities(LeaveRequest.status, func.count(LeaveRequest.id))
        .group_by(LeaveRequest.status)
        .all()
    )
    by_status = {status.lower(): count for status, count in rows}
    total = sum(by_status.values())
    return {
        'total': total,
        'by_status': by_status,
        'balance': build_balance_snapshot(
            user_id,
            allowance_days=ANNUAL_LEAVE_ALLOWANCE,
        ),
    }


def _load_notifications(user_id: int) -> list[dict]:
    notifications = recent_notifications_for_user(
        user_id,
        limit=MAX_NOTIFICATIONS,
        unread_only=True,
    )
    return [
        serialize_notification(notification)
        for notification in notifications
    ]


def _build_chatbot_summary(user_id: int) -> dict:
    latest_conversation = (
        Conversation.query
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.started_at.desc())
        .first()
    )

    if not latest_conversation:
        return {
            'has_history': False,
            'headline': 'Meet Ava, your HR copilot',
            'subtitle': 'Ask policy questions or request help any time.',
            'snippet': None,
            'last_interaction': None,
        }

    last_message = (
        latest_conversation.messages
        .order_by(Message.created_at.desc())
        .first()
    )

    last_interaction = last_message.created_at if last_message else latest_conversation.started_at

    snippet = None
    if last_message and last_message.content:
        snippet = _truncate(last_message.content, MAX_CHATBOT_SNIPPET)

    return {
        'has_history': True,
        'headline': latest_conversation.title or 'Latest chat with HR bot',
        'subtitle': f"{latest_conversation.messages.count()} message(s) exchanged.",
        'snippet': snippet,
        'last_interaction': last_interaction.isoformat() if last_interaction else None,
    }


def _generate_career_tip(progress_pct: int, skills: list[dict]) -> str:
    if progress_pct >= 90:
        return "You're ready for the next milestone. Consider mentoring teammates."
    if progress_pct >= 60:
        return "Keep your momentum and add two new leadership-focused skills this quarter."
    if progress_pct >= 30 and skills:
        return f"Deepen expertise in {skills[0]['name']} to unlock your next promotion."
    if skills:
        return f"Pin at least three core skills to tailor your growth plan. Start with {skills[0]['name']}."
    return "Add your skills to receive personalized learning suggestions."


def _collect_career_insights(user: User, progress_pct: int) -> dict:
    skills: list[dict] = []
    parsed_skills = _safe_parse_json(user.skills_json)

    if isinstance(parsed_skills, list):
        for item in parsed_skills:
            if isinstance(item, dict):
                name = item.get('name') or item.get('skill')
                if not name:
                    continue
                skills.append({
                    'name': name,
                    'progress': item.get('progress') or item.get('proficiency') or item.get('level'),
                    'years_experience': item.get('years_experience'),
                })
            else:
                skills.append({'name': str(item), 'progress': None, 'years_experience': None})
            if len(skills) >= MAX_CAREER_SKILLS:
                break

    if len(skills) < MAX_CAREER_SKILLS:
        remaining = MAX_CAREER_SKILLS - len(skills)
        for user_skill in user.user_skills.limit(remaining).all():
            if not getattr(user_skill, 'skill', None):
                continue
            skills.append({
                'name': user_skill.skill.name,
                'progress': getattr(user_skill, 'proficiency', None),
                'years_experience': getattr(user_skill, 'years_experience', None),
            })
            if len(skills) >= MAX_CAREER_SKILLS:
                break

    return {
        'progress_pct': progress_pct,
        'target_skills': CAREER_TARGET_SKILLS,
        'skills': skills,
        'recommendation': _generate_career_tip(progress_pct, skills),
    }


def _build_offboarding_snapshot(user: User) -> dict:
    if user.active:
        status = 'active'
        status_label = 'Active employee'
        message = 'No offboarding tasks in progress.'
        pending_tasks = 0
    else:
        status = 'offboarding'
        status_label = 'Exit in progress'
        message = 'Coordinate with HR to complete remaining offboarding steps.'
        pending_tasks = 3

    return {
        'status': status,
        'status_label': status_label,
        'message': message,
        'pending_tasks': pending_tasks,
        'last_updated': user.updated_at.isoformat() if user.updated_at else None,
    }


def _build_quick_actions(profile: dict, career: dict, chatbot: dict, offboarding: dict, leave_summary: dict, pending_requests: int) -> list[dict]:
    leave_total = leave_summary.get('total', 0) if leave_summary else 0
    pending_label = f"{pending_requests} pending approval" if pending_requests else "Submit time-off request"

    chatbot_description = chatbot.get('snippet') or chatbot.get('subtitle')
    career_description = f"{career.get('progress_pct', 0)}% journey complete" if career else "Plan your next role"
    offboarding_description = offboarding.get('status_label', 'Track your exit tasks')

    return [
        {
            'key': 'profile',
            'label': 'My Profile',
            'icon': 'bi bi-person-badge',
            'description': profile.get('job_title') or 'Review your personal details'
        },
        {
            'key': 'leave',
            'label': 'New Leave Request',
            'icon': 'bi bi-calendar2-plus',
            'description': pending_label
        },
        {
            'key': 'leave-history',
            'label': 'Leave History',
            'icon': 'bi bi-card-checklist',
            'description': f'{leave_total} total requests logged' if leave_total else 'View past leave submissions'
        },
        {
            'key': 'career',
            'label': 'Career Path',
            'icon': 'bi bi-graph-up-arrow',
            'description': career_description
        },
        {
            'key': 'learning',
            'label': 'Learning Hub',
            'icon': 'bi bi-mortarboard',
            'description': 'Upskill with curated learning tracks'
        },
        {
            'key': 'chatbot',
            'label': 'Ask HR Bot',
            'icon': 'bi bi-robot',
            'description': chatbot_description
        },
        {
            'key': 'offboarding',
            'label': 'Offboarding',
            'icon': 'bi bi-box-arrow-right',
            'description': offboarding_description
        },
        {
            'key': 'feedback',
            'label': 'Share Feedback',
            'icon': 'bi bi-chat-left-text',
            'description': 'Help improve the workplace experience'
        },
    ]


def _generate_chatbot_response(message: str) -> str:
    text = (message or '').strip().lower()
    if not text:
        return "I'm here whenever you need assistance with HR or policy questions."
    if any(keyword in text for keyword in ('leave', 'vacation', 'time off', 'pto')):
        return "Need time off? Submit a leave request and track approvals in the Leave Overview card."
    if any(keyword in text for keyword in ('policy', 'handbook', 'guideline')):
        return "You can browse HR policies in the knowledge base. Let me know the topic and I can point you to the right section."
    if any(keyword in text for keyword in ('salary', 'payroll', 'compensation', 'payslip')):
        return "Compensation queries are handled by Finance. I can log a ticket for you or connect you with the payroll team."
    if any(keyword in text for keyword in ('feedback', 'complaint', 'issue', 'concern')):
        return "Thanks for sharing. Please also consider submitting the feedback form so HR can follow up promptly."
    if any(keyword in text for keyword in ('hello', 'hi', 'thanks', 'thank you')):
        return "Happy to help! Ask me anything about leaves, policies, or HR contacts."
    return "I'll record this for HR to review. If it's urgent, please raise a ticket or ping your HR partner directly."


def _get_or_create_chat_conversation() -> Conversation:
    cutoff = datetime.utcnow() - timedelta(hours=4)
    conversation = (
        Conversation.query
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
        .first()
    )

    if not conversation or (conversation.ended_at and conversation.ended_at < cutoff):
        conversation = Conversation(
            user_id=current_user.id,
            title='HR Virtual Assistant',
            started_at=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.flush()

    return conversation


def _get_chat_conversation(conversation_id: Optional[int]) -> Conversation:
    if not conversation_id:
        return _get_or_create_chat_conversation()
    conversation = (
        Conversation.query.filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        ).first()
    )
    if conversation:
        return conversation
    return _get_or_create_chat_conversation()


@employee_dashboard_bp.route('/employee/dashboard', methods=['GET'])
@auth_required()
def get_employee_dashboard():
    """Return aggregated dashboard data for the authenticated employee."""
    today = date.today()

    approved_leaves = (
        LeaveRequest.query
        .filter_by(user_id=current_user.id, status='approved')
        .all()
    )
    approved_days_this_year = sum(
        _leave_days_in_year(leave, today.year) for leave in approved_leaves
    )
    remaining_leave = max(ANNUAL_LEAVE_ALLOWANCE - approved_days_this_year, 0)

    pending_requests = (
        LeaveRequest.query
        .filter_by(user_id=current_user.id, status='pending')
        .count()
    )

    team_size = 1
    team_subtext = 'You are the only member assigned'
    if current_user.team_number:
        team_members_query = (
            User.query
            .filter(User.team_number == current_user.team_number)
            .filter(User.active.is_(True))
        )
        team_size = team_members_query.count()
        team_subtext = f"Team {current_user.team_number}"

    skills_count = current_user.user_skills.count()
    career_progress_pct = 0
    if CAREER_TARGET_SKILLS > 0:
        career_progress_pct = min(
            int(round((skills_count / CAREER_TARGET_SKILLS) * 100)),
            100
        )

    stats = [
        {
            'title': 'Leave Balance',
            'value': f'{remaining_leave} Days',
            'subtext': f'Out of {ANNUAL_LEAVE_ALLOWANCE} annual days',
            'icon': 'bi bi-calendar'
        },
        {
            'title': 'Pending Requests',
            'value': str(pending_requests),
            'subtext': 'Awaiting approval',
            'icon': 'bi bi-clock'
        },
        {
            'title': 'Team Size',
            'value': str(team_size),
            'subtext': team_subtext,
            'icon': 'bi bi-people'
        },
        {
            'title': 'Career Progress',
            'value': f'{career_progress_pct}%',
            'subtext': 'Skill development progress',
            'icon': 'bi bi-graph-up'
        }
    ]

    recent_leaves = [
        {
            'id': leave.id,
            'leave_type': leave.leave_type or 'General',
            'start_date': leave.start_date.isoformat() if leave.start_date else None,
            'end_date': leave.end_date.isoformat() if leave.end_date else None,
            'status': leave.status.capitalize(),
            'reason': leave.reason,
            'days': (
                (leave.end_date - leave.start_date).days + 1
                if leave.start_date and leave.end_date else None
            ),
            'submitted_at': leave.created_at.isoformat() if leave.created_at else None,
        }
        for leave in (
            LeaveRequest.query
            .filter_by(user_id=current_user.id)
            .order_by(LeaveRequest.created_at.desc())
            .limit(MAX_RECENT_LEAVES)
            .all()
        )
    ]

    leave_summary = _build_leave_summary(current_user.id)

    now = datetime.utcnow()
    event_query = TeamEvent.query.filter(TeamEvent.start_datetime >= now)
    if current_user.team_number:
        event_query = event_query.filter(
            or_(
                TeamEvent.team_number == current_user.team_number,
                TeamEvent.team_number.is_(None)
            )
        )
    else:
        event_query = event_query.filter(TeamEvent.team_number.is_(None))

    upcoming_events = [
        {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'time': _format_event_time(event),
            'month': event.start_datetime.strftime('%b').upper(),
            'date': event.start_datetime.strftime('%d'),
            'location': event.location,
            'start_datetime': event.start_datetime.isoformat() if event.start_datetime else None,
            'end_datetime': event.end_datetime.isoformat() if event.end_datetime else None,
            'team_number': event.team_number,
        }
        for event in (
            event_query
            .order_by(TeamEvent.start_datetime.asc())
            .limit(MAX_UPCOMING_EVENTS)
            .all()
        )
    ]

    profile = _build_profile_snapshot(current_user, today)
    team_overview = _build_team_overview(current_user)
    career = _collect_career_insights(current_user, career_progress_pct)
    notifications = _load_notifications(current_user.id)
    chatbot = _build_chatbot_summary(current_user.id)
    offboarding = _build_offboarding_snapshot(current_user)
    quick_actions = _build_quick_actions(profile, career, chatbot, offboarding, leave_summary, pending_requests)
    projects = _collect_project_assignments(current_user)
    project_announcement = _load_manager_project_announcement_for_employee(current_user)

    return jsonify({
        'profile': profile,
        'team_overview': team_overview,
        'project_assignments': projects,
        'project_announcement': project_announcement,
        'stats': stats,
        'leave_summary': leave_summary,
        'recent_leaves': recent_leaves,
        'upcoming_events': upcoming_events,
        'quick_actions': quick_actions,
        'notifications': notifications,
        'chatbot': chatbot,
        'offboarding': offboarding,
        'career': career
    })


@employee_dashboard_bp.route('/employee/project-announcement', methods=['GET'])
@auth_required()
def get_employee_project_announcement():
    """Return the manager project announcement for the current employee."""
    announcement = _load_manager_project_announcement_for_employee(current_user)
    return jsonify({'project_announcement': announcement})


@employee_dashboard_bp.route('/employee/feedback', methods=['POST'])
@auth_required()
def submit_dashboard_feedback():
    data = request.get_json() or {}

    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Feedback message is required'}), 400

    subject = (data.get('subject') or 'General').strip()
    rating = data.get('rating')

    payload = {
        'subject': subject,
        'rating': rating,
        'message': message,
    }

    audit_entry = AuditLog(
        actor_id=current_user.id,
        action='feedback-submitted',
        object_type='feedback',
        object_id=str(current_user.id),
        details=json.dumps(payload),
    )
    db.session.add(audit_entry)
    db.session.commit()

    return jsonify({'message': 'Thank you for sharing your feedback!'}), 200


@employee_dashboard_bp.route('/employee/chatbot', methods=['POST'])
@auth_required()
def interact_with_chatbot():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    conversation = _get_or_create_chat_conversation()

    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        sender='user',
        content=message,
        created_at=datetime.utcnow()
    )
    db.session.add(user_message)

    try:
        rag_result = hr_chatbot_service.answer_question(
            current_user,
            message,
            conversation,
            auto_escalate=False,
        )
        response_text = rag_result.get('answer') or "I'm still looking into that and will follow up soon."
        chatbot_status = rag_result.get('status')
        knowledge_reference = rag_result.get('reference')
        knowledge_source = rag_result.get('reference_source')
        question_log_id = rag_result.get('question_log_id')
    except Exception as error:  # pragma: no cover - defensive
        current_app.logger.exception('HR chatbot failed to process query: {0}'.format(error))
        response_text = (
            "I ran into a technical issue while fetching the answer. "
            "Please try again shortly or reach out to HR directly."
        )
        chatbot_status = 'error'
        knowledge_reference = None
        knowledge_source = None
        question_log_id = None

    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=None,
        sender='assistant',
        content=response_text,
        created_at=datetime.utcnow()
    )
    db.session.add(assistant_message)

    conversation.ended_at = datetime.utcnow()
    db.session.add(conversation)

    db.session.commit()

    return jsonify({
        'conversation_id': conversation.id,
        'response': response_text,
        'status': chatbot_status,
        'reference': knowledge_reference,
        'reference_source': knowledge_source,
        'question_log_id': question_log_id,
        'messages': [
            {
                'sender': 'user',
                'content': message,
                'timestamp': user_message.created_at.isoformat(),
            },
            {
                'sender': 'assistant',
                'content': response_text,
                'timestamp': assistant_message.created_at.isoformat(),
            }
        ]
    }), 200


@employee_dashboard_bp.route('/employee/chatbot/escalate', methods=['POST'])
@auth_required()
def escalate_chatbot_question():
    payload = request.get_json() or {}
    question = (payload.get('message') or '').strip()
    conversation_id = payload.get('conversation_id')

    if not question:
        return jsonify({'error': 'Question is required'}), 400

    conversation = _get_chat_conversation(conversation_id)

    try:
        log_entry = hr_chatbot_service.escalate_question(current_user, question, conversation)
    except Exception as error:  # pragma: no cover - defensive
        current_app.logger.exception('Unable to escalate chatbot question: %s', error)
        return jsonify({'error': 'Failed to forward the question to HR.'}), 500

    acknowledgement = (
        "Thanks! I've sent this to HR for review. You'll receive a notification once someone responds."
    )

    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=None,
        sender='assistant',
        content=acknowledgement,
        created_at=datetime.utcnow(),
    )
    db.session.add(assistant_message)
    conversation.ended_at = datetime.utcnow()
    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        'conversation_id': conversation.id,
        'response': acknowledgement,
        'status': 'pending',
        'question_log_id': log_entry.id,
        'reference': None,
        'reference_source': log_entry.source,
        'messages': [
            {
                'sender': 'assistant',
                'content': acknowledgement,
                'timestamp': assistant_message.created_at.isoformat(),
            }
        ]
    }), 200

