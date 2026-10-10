# app/api/utils.py
from __future__ import annotations

from collections.abc import Iterable

from flask import current_app


def _get_security_datastore():
    security_ext = current_app.extensions.get('security')
    if not security_ext:
        raise RuntimeError('Flask-Security extension is not initialized')
    if not hasattr(security_ext, 'datastore') or security_ext.datastore is None:
        raise RuntimeError('Flask-Security datastore is not available')
    return security_ext.datastore


def set_user_roles(user, role_names: Iterable[str] | None, *, ensure_default: bool = True):
    """Assign a single role to a user. Users can only have one role at a time."""
    from app.models.models import db

    datastore = _get_security_datastore()

    # Convert to list for validation
    role_list = list(role_names) if role_names else []

    # Remove empty/None values
    role_list = [str(role).strip() for role in role_list if role and str(role).strip()]

    # Enforce single role constraint
    if len(role_list) > 1:
        raise ValueError(f"Users can only have one role. Provided: {role_list}")

    # Get the single role name
    role_name = role_list[0] if role_list else None

    if not role_name and ensure_default:
        role_name = 'employee'

    # Clear ALL existing roles first
    for existing_role in user.roles[:]:  # Create a copy to avoid modification during iteration
        datastore.remove_role_from_user(user, existing_role)

    # Assign the new single role
    if role_name:
        role = datastore.find_role(role_name)
        if role:
            datastore.add_role_to_user(user, role)
        else:
            raise ValueError(f"Role '{role_name}' not found")

    # Ensure changes are flushed to database
    db.session.flush()
