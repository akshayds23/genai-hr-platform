from datetime import date

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user

from app.models.models import User

birthday_tracker_bp = Blueprint('birthday_tracker', __name__)

DEFAULT_BIRTHDAY_WINDOW = 30
MAX_LOOKAHEAD_DAYS = 90


class ScopeError(Exception):
    """Raised when a requested scope cannot be satisfied."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def _is_manager(user: User) -> bool:
    return (getattr(user, 'employment_role', '') or '').lower() == 'manager'


def _display_name(user: User | None) -> str:
    if not user:
        return 'Team member'
    parts = [user.first_name, user.last_name]
    fallback = user.username or user.email or f'User {user.id}'
    return ' '.join(part for part in parts if part) or fallback


def _clean_scope_param(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.strip().lower()
    return cleaned or None


def _clean_team_param(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.strip()
    return cleaned or None


def _coerce_days(raw: str | None, default: int) -> int:
    try:
        if raw is None:
            raise ValueError
        value = int(raw)
    except (TypeError, ValueError):
        value = default
    return max(1, min(MAX_LOOKAHEAD_DAYS, value))


def _resolve_user_scope(scope_param: str | None, team_param: str | None) -> tuple:
    scope = _clean_scope_param(scope_param)
    team_number = _clean_team_param(team_param) or _clean_team_param(getattr(current_user, 'team_number', None))

    base = User.query.filter(User.active.is_(True))

    if scope == 'organization':
        if not current_user.is_admin():
            raise ScopeError('Only administrators can view organization birthdays.', 403)
        return base, 'organization', None

    if scope == 'team':
        if not (current_user.is_admin() or _is_manager(current_user)):
            raise ScopeError('Team birthdays are visible to managers or administrators.', 403)
        if not team_number:
            raise ScopeError('team_number is required for team scope.', 400)
        return base.filter(User.team_number == team_number), 'team', team_number

    if scope == 'self':
        return base.filter(User.id == current_user.id), 'self', None

    if current_user.is_admin():
        return base, 'organization', None

    if team_number:
        return base.filter(User.team_number == team_number), 'team', team_number

    return base.filter(User.id == current_user.id), 'self', None


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


@birthday_tracker_bp.route('/birthday-tracker', methods=['GET'])
@auth_required()
def birthday_tracker():
    try:
        scoped_query, resolved_scope, resolved_team = _resolve_user_scope(
            request.args.get('scope'),
            request.args.get('team_number'),
        )
    except ScopeError as exc:
        return jsonify({'error': str(exc)}), exc.status_code

    window_days = _coerce_days(request.args.get('days'), DEFAULT_BIRTHDAY_WINDOW)
    today = date.today()

    users = (
        scoped_query
        .filter(User.birth_date.isnot(None))
        .order_by(User.birth_date.asc())
        .all()
    )

    upcoming = []
    for user in users:
        next_birthday = _safe_next_birthday(user.birth_date, today)
        days_until = (next_birthday - today).days
        if days_until < 0 or days_until > window_days:
            continue
        turning = next_birthday.year - user.birth_date.year
        upcoming.append({
            'employee_id': user.id,
            'employee_name': _display_name(user),
            'birth_date': user.birth_date.isoformat(),
            'next_birthday': next_birthday.isoformat(),
            'days_until': days_until,
            'turning': turning,
            'team_number': user.team_number,
        })

    upcoming.sort(key=lambda entry: (entry['days_until'], entry['employee_name']))

    today_birthdays = [entry for entry in upcoming if entry['days_until'] == 0]
    within_seven = sum(1 for entry in upcoming if entry['days_until'] <= 7)
    within_thirty = sum(1 for entry in upcoming if entry['days_until'] <= 30)

    return jsonify({
        'scope': resolved_scope,
        'team_number': resolved_team,
        'window_days': window_days,
        'today': today_birthdays,
        'upcoming': upcoming,
        'summary': {
            'total_upcoming': len(upcoming),
            'birthdays_today': len(today_birthdays),
            'within_7_days': within_seven,
            'within_30_days': within_thirty,
        }
    })
