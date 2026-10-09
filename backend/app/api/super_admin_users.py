# app/api/super_admin_users.py
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app
from flask_security import auth_required, roles_required, current_user
from flask_security.utils import hash_password
from sqlalchemy import or_, func, case

from app.models.models import db, User, Role, OffboardingTask
from app.services.offboarding import DEFAULT_FULL_OFFBOARDING_TASKS
from app.api.utils import set_user_roles


super_admin_users_bp = Blueprint('super_admin_users', __name__)


def _safe_strip(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_iso_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except Exception:
        return None


def _get_departments_from_dataset():
    root_path = Path(current_app.root_path).parent
    dataset_path = root_path / 'data_ingestion' / 'datasets' / 'company' / 'departments.json'
    if not dataset_path.exists():
        return []
    try:
        with dataset_path.open('r', encoding='utf-8') as fh:
            payload = json.load(fh)
    except Exception:
        return []
    departments = payload.get('departments', [])
    cleaned = []
    seen = set()
    for dept in departments:
        name = _safe_strip(dept.get('name'))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cleaned.append(
            {
                'name': name,
                'description': _safe_strip(dept.get('description')),
                'team_code': _safe_strip(dept.get('team_code')),
                'location': _safe_strip(dept.get('location')),
            }
        )
    return cleaned


def _collect_departments():
    dataset_departments = _get_departments_from_dataset()
    dataset_names = {dept['name'].lower(): dept for dept in dataset_departments}
    db_departments = (
        db.session.query(User.department)
        .filter(User.department.isnot(None))
        .distinct()
        .order_by(func.lower(User.department))
        .all()
    )
    for (dept_name,) in db_departments:
        if not dept_name:
            continue
        key = dept_name.lower()
        if key not in dataset_names:
            dataset_names[key] = {
                'name': dept_name,
                'description': None,
                'team_code': None,
                'location': None,
            }
    return sorted(dataset_names.values(), key=lambda item: item['name'])


def _prepare_user_dict(user: User):
    payload = user.to_dict()
    payload['roles'] = [role.name for role in user.roles]
    return payload


def _gather_offboarding_task_stats(user_ids: list[int]) -> dict[int, tuple[int, int]]:
    """
    Return a mapping of user_id to (total_tasks, completed_tasks) for the provided IDs.
    """
    if not user_ids:
        return {}

    rows = (
        db.session.query(
            OffboardingTask.user_id.label('user_id'),
            func.count(OffboardingTask.id).label('total'),
            func.sum(case((OffboardingTask.status == 'completed', 1), else_=0)).label('completed'),
        )
        .filter(OffboardingTask.user_id.in_(user_ids))
        .group_by(OffboardingTask.user_id)
        .all()
    )
    return {row.user_id: (int(row.total or 0), int(row.completed or 0)) for row in rows}


@super_admin_users_bp.route('/super-admin/users', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_users():
    search = _safe_strip(request.args.get('query'))
    department = _safe_strip(request.args.get('department'))
    role_filter = _safe_strip(request.args.get('role'))
    status = _safe_strip(request.args.get('status'))
    page = max(int(request.args.get('page', 1)), 1)
    per_page = int(request.args.get('per_page', request.args.get('page_size', 5)))
    per_page = min(max(per_page, 1), 100)

    query = User.query
    
    # Exclude current user and other HR users from the list
    query = query.filter(User.id != current_user.id)
    query = query.filter(~User.roles.any(Role.name == 'hr'))
    
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(User.username).like(like),
                func.lower(User.email).like(like),
                func.lower(User.first_name).like(like),
                func.lower(User.last_name).like(like),
                func.lower(User.employee_id).like(like),
            )
        )
    if department:
        query = query.filter(func.lower(User.department) == department.lower())
    if status == 'active':
        query = query.filter(User.active.is_(True))
    elif status == 'inactive':
        query = query.filter(User.active.is_(False))
    if role_filter:
        query = query.join(User.roles).filter(func.lower(Role.name) == role_filter.lower())

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    users = [_prepare_user_dict(user) for user in pagination.items]
    task_stats = _gather_offboarding_task_stats([u.get('id') for u in users if u.get('id')])
    required_tasks = max(len(DEFAULT_FULL_OFFBOARDING_TASKS), 1)
    for user in users:
        total, completed = task_stats.get(user.get('id'), (0, 0))
        user['offboarding_task_total'] = total
        user['offboarding_task_completed'] = completed
        user['offboarding_complete'] = (
            not user.get('active', True)
            and total >= required_tasks
            and completed >= required_tasks
            and total == completed
        )

    return jsonify(
        {
            'results': users,
            'meta': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
            },
        }
    ), 200


@super_admin_users_bp.route('/super-admin/users', methods=['POST'])
@auth_required()
@roles_required('hr')
def create_user():
    data = request.get_json(silent=True) or {}
    username = _safe_strip(data.get('username'))
    email = _safe_strip(data.get('email'))
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({'error': 'username, email, and password are required.'}), 400

    # Prevent HR users from creating other HR users and enforce single role
    roles = data.get('roles') or ['employee']
    if len(roles) > 1:
        return jsonify({'error': 'Users can only be assigned one role at a time.'}), 400
    if 'hr' in roles:
        return jsonify({'error': 'HR users cannot create other HR users.'}), 403

    existing = User.query.filter(
        or_(func.lower(User.username) == username.lower(), func.lower(User.email) == email.lower())
    ).first()
    if existing:
        return jsonify({'error': 'A user with that username or email already exists.'}), 400

    user_datastore = current_app.extensions['security'].datastore
    try:
        user = user_datastore.create_user(
            username=username,
            email=email,
            password=hash_password(password),
            first_name=_safe_strip(data.get('first_name')),
            last_name=_safe_strip(data.get('last_name')),
            employee_id=_safe_strip(data.get('employee_id')),
            department=_safe_strip(data.get('department')),
            job_title=_safe_strip(data.get('job_title')),
            phone=_safe_strip(data.get('phone')),
            employment_role=_safe_strip(data.get('employment_role')) or 'employee',
            hire_date=_parse_iso_date(data.get('hire_date')),
            birth_date=_parse_iso_date(data.get('birth_date')),
            active=bool(data.get('active', True)),
        )
        try:
            set_user_roles(user, roles)
        except ValueError as ve:
            db.session.rollback()
            return jsonify({'error': str(ve)}), 400
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Unable to create user', 'details': str(exc)}), 500

    return jsonify({'message': 'User created successfully', 'user': _prepare_user_dict(user)}), 200


@super_admin_users_bp.route('/super-admin/users/<int:user_id>', methods=['GET'])
@auth_required()
@roles_required('hr')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent accessing current user or other HR users
    if user.id == current_user.id or user.has_role('hr'):
        return jsonify({'error': 'Access denied.'}), 403
    
    return jsonify({'user': _prepare_user_dict(user)}), 200


@super_admin_users_bp.route('/super-admin/users/<int:user_id>', methods=['PUT'])
@auth_required()
@roles_required('hr')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    # Prevent editing current user or other HR users
    if user.id == current_user.id:
        return jsonify({'error': 'You cannot edit your own account.'}), 400
    
    if user.has_role('hr'):
        return jsonify({'error': 'You cannot edit other HR users.'}), 403

    # Prevent HR users from assigning HR roles and enforce single role
    if 'roles' in data:
        roles = data.get('roles') or []
        if len(roles) > 1:
            return jsonify({'error': 'Users can only be assigned one role at a time.'}), 400
        if 'hr' in roles:
            return jsonify({'error': 'You cannot assign HR roles to users.'}), 403

    if 'username' in data:
        new_username = _safe_strip(data.get('username'))
        if not new_username:
            return jsonify({'error': 'username cannot be empty.'}), 400
        conflict = User.query.filter(func.lower(User.username) == new_username.lower(), User.id != user.id).first()
        if conflict:
            return jsonify({'error': 'Username already in use.'}), 400
        user.username = new_username

    if 'email' in data:
        new_email = _safe_strip(data.get('email'))
        if not new_email:
            return jsonify({'error': 'email cannot be empty.'}), 400
        conflict = User.query.filter(func.lower(User.email) == new_email.lower(), User.id != user.id).first()
        if conflict:
            return jsonify({'error': 'Email already in use.'}), 400
        user.email = new_email

    simple_fields = [
        'first_name',
        'last_name',
        'phone',
        'employee_id',
        'job_title',
        'department',
        'employment_role',
        'team_number',
        'organization',
        'address',
    ]
    for field in simple_fields:
        if field in data:
            setattr(user, field, _safe_strip(data.get(field)))

    if 'hire_date' in data:
        user.hire_date = _parse_iso_date(data.get('hire_date'))
    if 'birth_date' in data:
        user.birth_date = _parse_iso_date(data.get('birth_date'))

    if 'active' in data:
        user.active = bool(data.get('active'))

    if 'roles' in data:
        roles = data.get('roles') or []
        try:
            set_user_roles(user, roles)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

    if data.get('password'):
        user.password = hash_password(data['password'])

    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'user': _prepare_user_dict(user)}), 200


@super_admin_users_bp.route('/super-admin/users/<int:user_id>', methods=['DELETE'])
@auth_required()
@roles_required('hr')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'You cannot delete your own account.'}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@super_admin_users_bp.route('/super-admin/departments', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_departments():
    departments = _collect_departments()
    return jsonify({'departments': departments}), 200


@super_admin_users_bp.route('/super-admin/roles', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_roles():
    roles = (
        Role.query.filter(Role.name != 'hr').order_by(func.lower(Role.name)).all()
    )
    return (
        jsonify(
            {
                'roles': [
                    {
                        'name': role.name,
                        'description': role.description,
                    }
                    for role in roles
                ]
            }
        ),
        200,
    )
