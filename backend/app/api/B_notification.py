from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.models import LeaveRequest, User, Notification
from app.services.notifications import recent_notifications_for_user, serialize_notification, mark_read


notification_bp = Blueprint('notification', __name__)

DEFAULT_LEAVE_WINDOW_DAYS = 21
MAX_LOOKAHEAD_DAYS = 120
MAX_UPCOMING_LEAVES = 10
MAX_TOP_EMPLOYEES = 5


class ScopeError(Exception):
    """Raised when a requested scope cannot be satisfied."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def _is_manager(user: User) -> bool:
    return (getattr(user, 'employment_role', '') or '').lower() == 'manager'


def _display_name(user: Optional[User]) -> str:
    if not user:
        return 'Team member'
    parts = [user.first_name, user.last_name]
    fallback = user.username or user.email or f'User {user.id}'
    return ' '.join(part for part in parts if part) or fallback


def _clean_scope_param(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    cleaned = raw.strip().lower()
    return cleaned or None


def _clean_team_param(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    cleaned = raw.strip()
    return cleaned or None


def _coerce_days(raw: Optional[str], default: int) -> int:
    try:
        if raw is None:
            raise ValueError
        value = int(raw)
    except (TypeError, ValueError):
        value = default
    return max(1, min(MAX_LOOKAHEAD_DAYS, value))


def _leave_duration_days(leave: LeaveRequest) -> int:
    if not leave.start_date or not leave.end_date:
        return 0
    return (leave.end_date - leave.start_date).days + 1


def _resolve_leave_scope(scope_param: Optional[str], team_param: Optional[str]) -> Tuple:
    scope = _clean_scope_param(scope_param)
    team_number = _clean_team_param(team_param) or _clean_team_param(getattr(current_user, 'team_number', None))

    if scope == 'organization':
        if not current_user.is_admin():
            raise ScopeError('Only administrators can view organization leave analytics.', 403)
        query = LeaveRequest.query.options(selectinload(LeaveRequest.user))
        return query, 'organization', None

    if scope == 'team':
        if not (current_user.is_admin() or _is_manager(current_user)):
            raise ScopeError('Team analytics are available to managers or administrators.', 403)
        if not team_number:
            raise ScopeError('team_number is required for team scope.', 400)
        query = (
            LeaveRequest.query
            .join(User, LeaveRequest.user_id == User.id)
            .filter(User.team_number == team_number)
            .options(selectinload(LeaveRequest.user))
        )
        return query, 'team', team_number

    if scope == 'self':
        query = (
            LeaveRequest.query
            .filter(LeaveRequest.user_id == current_user.id)
            .options(selectinload(LeaveRequest.user))
        )
        return query, 'self', None

    if current_user.is_admin():
        query = LeaveRequest.query.options(selectinload(LeaveRequest.user))
        return query, 'organization', None

    if _is_manager(current_user) and team_number:
        query = (
            LeaveRequest.query
            .join(User, LeaveRequest.user_id == User.id)
            .filter(User.team_number == team_number)
            .options(selectinload(LeaveRequest.user))
        )
        return query, 'team', team_number

    query = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == current_user.id)
        .options(selectinload(LeaveRequest.user))
    )
    return query, 'self', None


@notification_bp.route('/notifications', methods=['GET'])
@auth_required()
def list_notifications():
    try:
        limit = int(request.args.get('limit', 20))
    except (TypeError, ValueError):
        limit = 20
    limit = max(1, min(limit, 100))
    unread_only = (request.args.get('unread_only', 'false').lower() == 'true')

    notifications = recent_notifications_for_user(
        current_user.id,
        limit=limit,
        unread_only=unread_only,
    )
    return jsonify({
        'notifications': [
            serialize_notification(notification)
            for notification in notifications
        ]
    })


@notification_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@auth_required()
def mark_notification(notification_id: int):
    notification = (
        Notification.query
        .filter(Notification.id == notification_id)
        .filter(Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        return jsonify({'error': 'Notification not found.'}), 404

    mark_read(notification)
    return jsonify({'notification': serialize_notification(notification)})


@notification_bp.route('/notifications/leave-analytics', methods=['GET'])
@auth_required()
def leave_analytics():
    try:
        scoped_query, resolved_scope, resolved_team = _resolve_leave_scope(
            request.args.get('scope'),
            request.args.get('team_number'),
        )
    except ScopeError as exc:
        return jsonify({'error': str(exc)}), exc.status_code

    today = date.today()
    upcoming_days = _coerce_days(request.args.get('upcoming_days'), DEFAULT_LEAVE_WINDOW_DAYS)
    upcoming_cutoff = today + timedelta(days=upcoming_days)
    recent_cutoff = datetime.combine(today - timedelta(days=30), datetime.min.time())
    year_start = date(today.year, 1, 1)

    status_rows = (
        scoped_query
        .with_entities(LeaveRequest.status, func.count(LeaveRequest.id))
        .group_by(LeaveRequest.status)
        .all()
    )
    status_totals = defaultdict(int)
    for status, count in status_rows:
        key = (status or 'unknown').lower()
        status_totals[key] += count
    total_requests = sum(status_totals.values())

    recent_rows = (
        scoped_query
        .filter(LeaveRequest.created_at >= recent_cutoff)
        .with_entities(LeaveRequest.status, func.count(LeaveRequest.id))
        .group_by(LeaveRequest.status)
        .all()
    )
    recent_totals = defaultdict(int)
    for status, count in recent_rows:
        key = (status or 'unknown').lower()
        recent_totals[key] += count

    approved_samples = (
        scoped_query
        .filter(LeaveRequest.status == 'approved')
        .filter(LeaveRequest.created_at.isnot(None))
        .filter(LeaveRequest.updated_at.isnot(None))
        .order_by(LeaveRequest.updated_at.desc())
        .limit(250)
        .all()
    )
    approval_durations = []
    for leave in approved_samples:
        if leave.updated_at >= leave.created_at:
            delta = leave.updated_at - leave.created_at
            approval_durations.append(delta.total_seconds() / 86400)
    average_approval_days = round(sum(approval_durations) / len(approval_durations), 1) if approval_durations else None

    upcoming_leaves = (
        scoped_query
        .filter(LeaveRequest.start_date.isnot(None))
        .filter(LeaveRequest.start_date >= today)
        .filter(LeaveRequest.start_date <= upcoming_cutoff)
        .order_by(LeaveRequest.start_date.asc())
        .limit(MAX_UPCOMING_LEAVES)
        .all()
    )
    upcoming_payload = []
    for leave in upcoming_leaves:
        duration_days = _leave_duration_days(leave)
        upcoming_payload.append({
            'id': leave.id,
            'employee_id': leave.user_id,
            'employee_name': _display_name(leave.user),
            'leave_type': leave.leave_type,
            'status': leave.status,
            'start_date': leave.start_date.isoformat() if leave.start_date else None,
            'end_date': leave.end_date.isoformat() if leave.end_date else None,
            'duration_days': duration_days if duration_days else None,
        })

    year_leaves = (
        scoped_query
        .filter(LeaveRequest.start_date.isnot(None))
        .filter(LeaveRequest.start_date >= year_start)
        .options(selectinload(LeaveRequest.user))
        .all()
    )
    per_employee = defaultdict(lambda: {'days': 0, 'count': 0, 'user': None})
    for leave in year_leaves:
        duration = _leave_duration_days(leave)
        if duration <= 0:
            continue
        bucket = per_employee[leave.user_id]
        bucket['days'] += duration
        bucket['count'] += 1
        bucket['user'] = leave.user
    top_employees = sorted(
        per_employee.values(),
        key=lambda item: (item['days'], item['count']),
        reverse=True
    )[:MAX_TOP_EMPLOYEES]
    top_employees_payload = [
        {
            'employee_id': bucket['user'].id if bucket['user'] else None,
            'employee_name': _display_name(bucket['user']),
            'total_days': bucket['days'],
            'request_count': bucket['count'],
        }
        for bucket in top_employees
    ]

    sampled_leaves = (
        scoped_query
        .filter(LeaveRequest.start_date.isnot(None))
        .filter(LeaveRequest.end_date.isnot(None))
        .limit(500)
        .all()
    )
    duration_values = []
    for leave in sampled_leaves:
        duration = _leave_duration_days(leave)
        if duration > 0:
            duration_values.append(duration)
    average_duration_days = round(sum(duration_values) / len(duration_values), 1) if duration_values else None

    return jsonify({
        'scope': resolved_scope,
        'team_number': resolved_team,
        'total_requests': total_requests,
        'status_breakdown': status_totals,
        'recent_30_day_breakdown': recent_totals,
        'average_approval_days': average_approval_days,
        'average_duration_days': average_duration_days,
        'upcoming_window_days': upcoming_days,
        'upcoming_leaves': upcoming_payload,
        'top_employee_absences': top_employees_payload,
    })
