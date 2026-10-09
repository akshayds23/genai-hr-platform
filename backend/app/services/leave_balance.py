from datetime import date
from typing import Iterable, Optional

from app.models.models import LeaveRequest

DEFAULT_ALLOWANCE_DAYS = 20
BALANCE_STATUSES = {'pending', 'approved'}


def inclusive_day_count(start: date, end: date) -> int:
    if not start or not end:
        return 0
    return (end - start).days + 1


def overlap_in_range(start: date, end: date, range_start: date, range_end: date) -> int:
    if not start or not end:
        return 0
    effective_start = max(start, range_start)
    effective_end = min(end, range_end)
    if effective_end < effective_start:
        return 0
    return (effective_end - effective_start).days + 1


def used_leave_days_for_year(
    user_id: int,
    year: int,
    *,
    statuses: Optional[Iterable[str]] = None,
) -> int:
    status_filter = {status.lower() for status in (statuses or BALANCE_STATUSES)}
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    leave_rows = (
        LeaveRequest.query
        .filter(LeaveRequest.user_id == user_id)
        .filter(LeaveRequest.status.in_(list(status_filter)))
        .filter(LeaveRequest.start_date.isnot(None))
        .filter(LeaveRequest.end_date.isnot(None))
        .filter(LeaveRequest.start_date <= year_end)
        .filter(LeaveRequest.end_date >= year_start)
        .all()
    )

    total_days = 0
    for leave in leave_rows:
        total_days += overlap_in_range(leave.start_date, leave.end_date, year_start, year_end)
    return total_days


def remaining_leave_days(
    user_id: int,
    year: int,
    *,
    allowance_days: int = DEFAULT_ALLOWANCE_DAYS,
    statuses: Optional[Iterable[str]] = None,
) -> int:
    used_days = used_leave_days_for_year(user_id, year, statuses=statuses)
    remaining = allowance_days - used_days
    return remaining if remaining > 0 else 0


def build_balance_snapshot(
    user_id: int,
    *,
    reference_date: Optional[date] = None,
    allowance_days: int = DEFAULT_ALLOWANCE_DAYS,
    statuses: Optional[Iterable[str]] = None,
) -> dict:
    reference_date = reference_date or date.today()
    year = reference_date.year
    used_days = used_leave_days_for_year(user_id, year, statuses=statuses)
    remaining_days = allowance_days - used_days
    if remaining_days < 0:
        remaining_days = 0
    return {
        'year': year,
        'allowance_days': allowance_days,
        'used_days': used_days,
        'remaining_days': remaining_days,
    }
