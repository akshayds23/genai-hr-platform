import json
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, List

from app.models.models import Notification, User, db


IST = timezone(timedelta(hours=5, minutes=30))


def _encode_metadata(metadata: Optional[dict]) -> Optional[str]:
    if metadata is None:
        return None
    try:
        return json.dumps(metadata)
    except (TypeError, ValueError):
        return None


def _to_ist_iso(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert a naive/UTC datetime to an ISO string in Asia/Kolkata.

    The database timestamps are stored without timezone information and
    effectively behave like UTC. We normalise them to UTC first and then
    convert to IST so that all frontends see consistent local times.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        return dt.astimezone(IST).isoformat()
    except (OverflowError, ValueError):
        # Fallback to original ISO format if conversion somehow fails
        return dt.isoformat()


def create_notification(
    *,
    user_id: Optional[int],
    category: str,
    title: str,
    message: Optional[str] = None,
    metadata: Optional[dict] = None,
    commit: bool = False,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        category=category,
        title=title,
        message=message,
        metadata_json=_encode_metadata(metadata),
    )
    db.session.add(notification)
    if commit:
        db.session.commit()
    return notification


def notify_users(
    user_ids: Iterable[int],
    *,
    category: str,
    title: str,
    message: Optional[str] = None,
    metadata: Optional[dict] = None,
    commit: bool = False,
) -> list[Notification]:
    notifications: list[Notification] = []
    for user_id in user_ids:
        notifications.append(
            create_notification(
                user_id=user_id,
                category=category,
                title=title,
                message=message,
                metadata=metadata,
                commit=False,
            )
        )
    if commit and notifications:
        db.session.commit()
    return notifications


def determine_manager_ids(user: User) -> list[int]:
    """
    Resolve the appropriate escalation targets for workflow notifications.

    Employees route to their direct manager or team managers, falling back
    to super admins. Managers route directly to HR (super admins) so their
    own requests do not bounce back to themselves.
    """

    def _active_users_with_role(role_name: str) -> list[User]:
        return (
            User.query
            .filter(User.active.is_(True))
            .filter(User.roles.any(name=role_name))
            .all()
        )

    role = (getattr(user, 'employment_role', '') or '').lower()
    if role == 'manager':
        recipients = [candidate.id for candidate in _active_users_with_role('hr') if candidate.id != user.id]
        if recipients:
            return recipients
        # Fallback: escalate to managers if no hr exists.
        recipients = [candidate.id for candidate in _active_users_with_role('manager') if candidate.id != user.id]
        if recipients:
            return recipients

def _active_users_with_role(role_name: str, exclude_id: Optional[int] = None) -> List[User]:
    query = (
        User.query
        .filter(User.active.is_(True))
        .filter(User.roles.any(name=role_name))
    )
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.all()

def determine_hr_user_ids(exclude_id: Optional[int] = None) -> list[int]:
    return [user.id for user in _active_users_with_role('hr', exclude_id=exclude_id)]

def determine_manager_ids(user: User) -> list[int]:
    """
    Resolve the appropriate escalation targets for workflow notifications.

    Employees route to their direct manager or team managers, falling back
    to super admins. Managers route directly to HR (super admins) so their
    own requests do not bounce back to themselves.
    """

    role = (getattr(user, 'employment_role', '') or '').lower()
    if role == 'manager':
        recipients = [candidate.id for candidate in _active_users_with_role('hr', exclude_id=user.id)]
        if recipients:
            return recipients
        # Fallback: escalate to managers if no hr exists.
        recipients = [candidate.id for candidate in _active_users_with_role('manager', exclude_id=user.id)]
        if recipients:
            return recipients

    recipient_ids: list[int] = []
    if getattr(user, 'manager_id', None):
        recipient_ids.append(user.manager_id)

    if not recipient_ids and getattr(user, 'team_number', None):
        team_managers = (
            User.query
            .filter(User.team_number == user.team_number)
            .filter(User.employment_role == 'manager')
            .filter(User.active.is_(True))
            .all()
        )
        recipient_ids.extend(manager.id for manager in team_managers if manager.id != user.id)

    if not recipient_ids:
        recipient_ids.extend(
            admin.id for admin in _active_users_with_role('hr', exclude_id=user.id)
        )

    return list(dict.fromkeys(recipient_ids))


def serialize_notification(notification: Notification) -> dict:
    metadata = None
    if notification.metadata_json:
        try:
            metadata = json.loads(notification.metadata_json)
        except (TypeError, ValueError):
            metadata = notification.metadata_json
    return {
        'id': notification.id,
        'category': notification.category,
        'title': notification.title,
        'message': notification.message,
        'is_read': notification.is_read,
        'created_at': _to_ist_iso(notification.created_at),
        'read_at': _to_ist_iso(notification.read_at),
        'metadata': metadata,
    }


def recent_notifications_for_user(
    user_id: int,
    *,
    limit: int = 20,
    unread_only: bool = False,
) -> list[Notification]:
    query = Notification.query.filter(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.limit(limit).all()


def mark_read(notification: Notification, commit: bool = True) -> Notification:
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = db.func.now()
        db.session.add(notification)
        if commit:
            db.session.commit()
    return notification
