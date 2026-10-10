from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from sqlalchemy import func, or_

from app.models.models import (
    Conversation,
    LeaveRequest,
    Message,
    ProjectAnnouncement,
    Team,
    TeamEvent,
    User,
)
from app.services.leave_balance import build_balance_snapshot
from app.services.notifications import recent_notifications_for_user, serialize_notification

ANNUAL_LEAVE_ALLOWANCE = 20
MAX_NOTIFICATIONS = 5
MAX_UPCOMING_EVENTS = 5
MAX_PENDING_LEAVES = 25
MAX_TEAM_OFFBOARDING = 12
ANALYTICS_MONTH_SPAN = 2
MAX_RECENT_LEAVES = 5
DEFAULT_TEAM_BIRTHDAY_WINDOW = 30
MAX_TEAM_BIRTHDAY_LOOKAHEAD = 90

OFFBOARDING_LEAVE_TYPES = {'resignation', 'offboarding'}


def ensure_manager_access(user: User) -> bool:
    if getattr(user, 'is_admin', lambda: False)():
        return True
    return getattr(user, 'employment_role', '').lower() == 'manager'


def safe_next_birthday(birth_date: date, today: date) -> date:
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


def display_name(user: User | None) -> str:
    if not user:
        return 'Team member'
    parts = [user.first_name, user.last_name]
    fallback = user.username or user.email or f'User {user.id}'
    return ' '.join(part for part in parts if part) or fallback


def collect_team_birthdays(team: Team | None, window_days: int = DEFAULT_TEAM_BIRTHDAY_WINDOW) -> dict:
    window_days = max(1, min(window_days, MAX_TEAM_BIRTHDAY_LOOKAHEAD))
    today = date.today()

    if not team:
        return {
            'window_days': window_days,
            'today': [],
            'upcoming': [],
        }

    members = (
        User.query
        .filter(User.team_id == team.id)
        .filter(User.active.is_(True))
        .filter(User.birth_date.isnot(None))
        .order_by(User.first_name.asc(), User.last_name.asc())
        .all()
    )

    upcoming = []
    for member in members:
        if not member.birth_date:
            continue
        next_birthday = safe_next_birthday(member.birth_date, today)
        days_until = (next_birthday - today).days
        if days_until < 0 or days_until > window_days:
            continue
        upcoming.append({
            'employee_id': member.id,
            'employee_name': display_name(member),
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


def build_profile_snapshot(user: User, today: date) -> dict:
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

    tenure = None
    if user.hire_date:
        delta_days = max((today - user.hire_date).days, 0)
        years = delta_days // 365
        months = (delta_days % 365) // 30
        parts = []
        if years:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months:
            parts.append(f"{months} month{'s' if months != 1 else ''}")
        tenure = {
            'years': years,
            'months': months,
            'label': ' '.join(parts) or 'Joined recently',
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
        },
    }


def resolve_user_team(user: User) -> Team | None:
    """Return the team associated with the user or the team they manage."""
    if getattr(user, 'employment_role', '').lower() == 'manager':
        managed_team = Team.query.filter_by(manager_id=user.id).first()
        if managed_team:
            return managed_team

    team: Team | None = None
    if user.team_id:
        team = Team.query.get(user.team_id)
    if team:
        return team

    return Team.query.filter_by(manager_id=user.id).first()


def collect_team_overview(user: User, *, team: Team | None = None) -> dict:
    team = team or resolve_user_team(user)
    team_name = team.name if team else user.team_number

    base = {
        'team_number': team_name,
        'members': [],
        'total_members': 1,
        'has_more': False,
        'empty_message': 'Assign teammates to this squad to manage them here.',
        'birthday_window': DEFAULT_TEAM_BIRTHDAY_WINDOW,
        'birthdayWindow': DEFAULT_TEAM_BIRTHDAY_WINDOW,
        'birthdays': {
            'window_days': DEFAULT_TEAM_BIRTHDAY_WINDOW,
            'today': [],
            'upcoming': [],
        },
    }

    if not team:
        base['team_number'] = team_name
        return base

    query = (
        User.query
        .filter(User.team_id == team.id)
        .filter(User.active.is_(True))
        .order_by(User.first_name.asc(), User.last_name.asc())
    )

    total_members = query.count()
    members = []
    for member in query.limit(20).all():
        full_name_parts = [part for part in (member.first_name, member.last_name) if part]
        members.append({
            'id': member.id,
            'name': ' '.join(full_name_parts) or member.username or member.email,
            'job_title': member.job_title,
            'employment_role': member.employment_role,
            'email': member.email,
            'is_self': member.id == user.id,
        })

    if not members and team.manager_id == user.id:
        full_name_parts = [part for part in (user.first_name, user.last_name) if part]
        members.append({
            'id': user.id,
            'name': ' '.join(full_name_parts) or user.username or user.email,
            'job_title': user.job_title,
            'employment_role': user.employment_role,
            'email': user.email,
            'is_self': True,
        })
        total_members = max(total_members, 1)

    birthday_window = DEFAULT_TEAM_BIRTHDAY_WINDOW
    birthdays = collect_team_birthdays(team, birthday_window)

    return {
        'team_number': team_name,
        'members': members,
        'total_members': total_members or len(members) or 1,
        'has_more': total_members > len(members),
        'empty_message': None if members else 'No teammates recorded yet.',
        'birthday_window': birthday_window,
        'birthdayWindow': birthday_window,
        'birthdays': birthdays,
    }


def build_leave_summary(user_id: int) -> dict:
    rows = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == user_id)
        .filter(~LeaveRequest.leave_type.in_(OFFBOARDING_LEAVE_TYPES))
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


def build_team_leave_summary(team_id: int | None, *, exclude_user_id: int | None = None) -> dict:
    if not team_id:
        return {'total': 0, 'by_status': {}}

    query = (
        LeaveRequest.query
        .join(User, User.id == LeaveRequest.user_id)
        .filter(User.team_id == team_id)
        .filter(~LeaveRequest.leave_type.in_(OFFBOARDING_LEAVE_TYPES))
    )
    if exclude_user_id is not None:
        query = query.filter(LeaveRequest.user_id != exclude_user_id)

    rows = (
        query
        .with_entities(LeaveRequest.status, func.count(LeaveRequest.id))
        .group_by(LeaveRequest.status)
        .all()
    )
    by_status = {status.lower(): count for status, count in rows}
    return {
        'total': sum(by_status.values()),
        'by_status': by_status,
    }


def collect_pending_team_leaves(user: User, *, team_id: int | None = None, status_param: str = 'pending') -> list[dict]:
    if team_id is None:
        team = resolve_user_team(user)
        team_id = team.id if team else None
    if not team_id:
        return []

    statuses = {value.strip().lower() for value in (status_param or 'pending').split(',') if value.strip()}
    if not statuses:
        statuses = {'pending'}

    query = (
        LeaveRequest.query
        .join(User, LeaveRequest.user_id == User.id)
        .filter(User.team_id == team_id)
        .filter(LeaveRequest.status.in_(statuses))
        .filter(~LeaveRequest.leave_type.in_(OFFBOARDING_LEAVE_TYPES))
        .order_by(LeaveRequest.start_date.asc())
    )

    if getattr(user, 'employment_role', '').lower() == 'manager':
        query = query.filter(LeaveRequest.user_id != user.id)

    leaves: list[dict] = []
    for leave in query.limit(MAX_PENDING_LEAVES).all():
        employee = leave.user
        if employee:
            full_name_parts = [part for part in (employee.first_name, employee.last_name) if part]
            employee_name = ' '.join(full_name_parts) or employee.username or employee.email
        else:
            employee_name = 'Team member'

        leaves.append({
            'id': leave.id,
            'employee_id': leave.user_id,
            'employee_name': employee_name,
            'leave_type': leave.leave_type,
            'start_date': leave.start_date.isoformat() if leave.start_date else None,
            'end_date': leave.end_date.isoformat() if leave.end_date else None,
            'status': leave.status,
            'reason': leave.reason,
            'submitted_at': leave.created_at.isoformat() if leave.created_at else None,
        })
    return leaves


def load_notifications(user_id: int) -> list[dict]:
    notifications = recent_notifications_for_user(
        user_id,
        limit=MAX_NOTIFICATIONS,
        unread_only=True,
    )
    return [
        serialize_notification(notification)
        for notification in notifications
    ]


def build_chatbot_summary(user_id: int) -> dict:
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
        trimmed = last_message.content.strip()
        snippet = trimmed if len(trimmed) <= 160 else trimmed[:159].rstrip() + '…'

    return {
        'has_history': True,
        'headline': latest_conversation.title or 'Latest chat with HR bot',
        'subtitle': 'Jump back into your conversation or start something new.',
        'snippet': snippet,
        'last_interaction': last_interaction.isoformat() if last_interaction else None,
    }


def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    month_total = month + offset
    year += (month_total - 1) // 12
    month = ((month_total - 1) % 12) + 1
    return year, month


def generate_month_series(months: int = ANALYTICS_MONTH_SPAN) -> list[dict]:
    today = date.today()
    series: list[dict] = []
    for offset in range(months - 1, -1, -1):
        year, month = shift_month(today.year, today.month, -offset)
        label = date(year, month, 1).strftime('%b')
        key = f'{year}-{month:02d}'
        series.append({
            'key': key,
            'label': label,
            'approved': 0,
            'pending': 0,
            'rejected': 0,
        })
    return series


def build_leave_analytics(user: User, team_summary: dict) -> dict:
    series = generate_month_series()
    indexed = {entry['key']: entry for entry in series}

    oldest_key = series[0]['key']
    oldest_year, oldest_month = map(int, oldest_key.split('-'))
    start_date = date(oldest_year, oldest_month, 1)

    user_leaves = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == user.id)
        .filter(LeaveRequest.start_date >= start_date)
        .all()
    )
    status_counts = defaultdict(int)
    for leave in user_leaves:
        status = (leave.status or '').lower()
        status_counts[status] += 1
        if leave.start_date:
            key = f'{leave.start_date.year}-{leave.start_date.month:02d}'
            if key in indexed:
                bucket = indexed[key]
                if status in bucket:
                    bucket[status] += 1

    return {
        'monthly': series,
        'status_breakdown': dict(status_counts),
        'team_status_breakdown': dict(team_summary.get('by_status', {})),
    }


def format_event_time(event: TeamEvent) -> str:
    start = event.start_datetime
    end = event.end_datetime

    if not start:
        return ''

    if end:
        if start.date() == end.date():
            return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
        return f"{start.strftime('%b %d %I:%M %p')} - {end.strftime('%b %d %I:%M %p')}"

    return start.strftime('%b %d %I:%M %p')


def load_upcoming_events(team_id: int | None) -> list[dict]:
    now = datetime.utcnow()
    query = TeamEvent.query.filter(TeamEvent.start_datetime >= now)

    team_name = None
    if team_id:
        team = Team.query.get(team_id)
        if team:
            team_name = team.name

    if team_name:
        query = query.filter(
            or_(
                TeamEvent.team_number == team_name,
                TeamEvent.team_number.is_(None),
            )
        )
    events = []
    for event in query.order_by(TeamEvent.start_datetime.asc()).limit(MAX_UPCOMING_EVENTS).all():
        events.append({
            'id': event.id,
            'title': event.title,
            'month': event.start_datetime.strftime('%b') if event.start_datetime else '',
            'date': event.start_datetime.strftime('%d') if event.start_datetime else '',
            'time': format_event_time(event),
            'location': event.location,
            'description': event.description,
        })
    return events


def collect_team_offboarding(user: User, *, team_id: int | None = None) -> list[dict]:
    if team_id is None:
        team = resolve_user_team(user)
        team_id = team.id if team else None
    if not team_id:
        return []

    members = (
        User.query
        .filter(User.team_id == team_id)
        .filter(User.id != user.id)
        .order_by(User.first_name.asc(), User.last_name.asc())
        .limit(MAX_TEAM_OFFBOARDING)
        .all()
    )

    items: list[dict] = []
    for member in members:
        full_name_parts = [part for part in (member.first_name, member.last_name) if part]
        name = ' '.join(full_name_parts) or member.username or member.email
        status = 'active'
        stage = 'Active'
        details = 'No exit activity recorded.'

        resignation_leave = (
            LeaveRequest.query
            .filter(LeaveRequest.user_id == member.id)
            .filter(LeaveRequest.leave_type.in_(['resignation', 'offboarding']))
            .order_by(LeaveRequest.created_at.desc())
            .first()
        )

        if not member.active:
            status = 'completed'
            stage = 'Completed exit'
            details = 'Offboarding completed.'
        elif resignation_leave:
            status = resignation_leave.status.lower()
            if status == 'pending':
                stage = 'Awaiting approval'
                details = 'Exit request pending review.'
            elif status == 'approved':
                stage = 'Exit scheduled'
                details = (
                    f"Exit planned for {resignation_leave.start_date.isoformat() if resignation_leave.start_date else 'TBD'}."
                )
            elif status == 'rejected':
                stage = 'Declined'
                details = 'Most recent exit request was declined.'
            else:
                stage = status.capitalize()
                details = 'Exit request updated.'

        items.append({
            'member_id': member.id,
            'name': name,
            'job_title': member.job_title,
            'status': status,
            'stage': stage,
            'last_updated': member.updated_at.isoformat() if member.updated_at else None,
            'details': details,
        })
    return items


def serialize_project_announcement(record: ProjectAnnouncement | None) -> dict | None:
    if not record:
        return None
    return {
        'id': record.id,
        'manager_id': record.manager_id,
        'title': record.title,
        'description': record.description,
        'createdAt': record.created_at.isoformat() if record.created_at else None,
        'lastUpdated': record.updated_at.isoformat() if record.updated_at else None,
    }


def get_manager_project_announcement(manager_id: int) -> dict | None:
    if not manager_id:
        return None
    record = ProjectAnnouncement.query.filter_by(manager_id=manager_id).first()
    return serialize_project_announcement(record)


def build_resignation_snapshot(user: User) -> dict | None:
    if user.active:
        return None

    return {
        'status_label': 'Awaiting HR confirmation',
        'message': 'Your resignation has been logged. HR will guide you through the final steps.',
        'last_day': None,
        'notice_period': None,
        'handover_plan': None,
        'notes': None,
    }


def build_manager_dashboard_data(user: User, status_param: str = 'pending') -> dict:
    today = date.today()
    profile = build_profile_snapshot(user, today)
    leave_summary = build_leave_summary(user.id)
    leave_balance = leave_summary.get('balance')
    leave_balance_details = leave_balance or {}
    allowance_days = leave_balance_details.get('allowance_days')
    managed_team = resolve_user_team(user)
    managed_team_id = managed_team.id if managed_team else None
    team_overview = collect_team_overview(user, team=managed_team)
    exclude_self = user.id if getattr(user, 'employment_role', '').lower() == 'manager' else None
    team_leave_summary = build_team_leave_summary(
        managed_team_id,
        exclude_user_id=exclude_self,
    )
    pending_leaves = collect_pending_team_leaves(user, team_id=managed_team_id, status_param=status_param)
    team_offboarding = collect_team_offboarding(user, team_id=managed_team_id)

    stats = [
        {
            'id': 'pending-approvals',
            'title': 'Pending approvals',
            'value': team_leave_summary.get('by_status', {}).get('pending', 0),
            'subtext': 'Waiting on manager decision',
            'icon': 'PA',
        },
        {
            'id': 'leave-balance',
            'title': 'Leave balance',
            'value': leave_balance_details.get('remaining_days', 0),
            'subtext': (
                f"of {allowance_days} days" if allowance_days is not None else 'Remaining days'
            ),
            'icon': 'LB',
        },
        {
            'id': 'team-members',
            'title': 'Team members',
            'value': max(team_overview.get('total_members', 1) - 1, 0) + 1,
            'subtext': 'Active teammates',
            'icon': 'TM',
        },
    ]

    recent_leaves = [
        {
            'id': leave.id,
            'leave_type': leave.leave_type or 'General',
            'request_type': getattr(leave, 'request_type', None),
            'start_date': leave.start_date.isoformat() if leave.start_date else None,
            'end_date': leave.end_date.isoformat() if leave.end_date else None,
            'status': (leave.status or '').capitalize(),
            'reason': leave.reason,
            'days': (
                (leave.end_date - leave.start_date).days + 1
                if leave.start_date and leave.end_date else None
            ),
            'submitted_at': leave.created_at.isoformat() if leave.created_at else None,
        }
        for leave in (
            LeaveRequest.query
            .filter(LeaveRequest.user_id == user.id)
            .filter(~LeaveRequest.leave_type.in_(OFFBOARDING_LEAVE_TYPES))
            .order_by(LeaveRequest.created_at.desc())
            .limit(MAX_RECENT_LEAVES)
            .all()
        )
    ]

    analytics = build_leave_analytics(user, team_leave_summary)
    notifications = load_notifications(user.id)
    chatbot_summary = build_chatbot_summary(user.id)
    upcoming_events = load_upcoming_events(managed_team_id)
    resignation_snapshot = build_resignation_snapshot(user)

    return {
        'profile': profile,
        'stats': stats,
        'leave_summary': leave_summary,
        'leave_balance': leave_balance,
        'leave_analytics': analytics,
        'team_overview': team_overview,
        'team_leave_summary': team_leave_summary,
        'pending_team_leaves': pending_leaves,
        'team_offboarding': team_offboarding,
        'upcoming_events': upcoming_events,
        'notifications': notifications,
        'chatbot': chatbot_summary,
        'resignation': resignation_snapshot,
        'project_announcement': get_manager_project_announcement(user.id),
        'recent_leaves': recent_leaves,
    }
