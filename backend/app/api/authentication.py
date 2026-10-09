# app/api/authentication.py
from flask import Blueprint, request, jsonify, current_app
from flask_security import auth_required, current_user, login_user, logout_user, roles_required
from flask_security.utils import verify_password, hash_password
from app.models.models import User, db
from flask import send_file, Response
from io import BytesIO
from datetime import datetime
import re
from sqlalchemy import func
from app.api.utils import set_user_roles

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Email/username and password required'}), 400

    requested_role = (data.get('role') or '').strip().lower()
    if not requested_role:
        return jsonify({'error': 'Role selection required'}), 400

    # TechCorp India three-role hierarchy
    role_aliases = {
        'hr': 'hr',           # Super Administrator level
        'manager': 'manager', # Administrative level  
        'employee': 'employee' # User level
    }
    canonical_role = role_aliases.get(requested_role)
    if not canonical_role:
        return jsonify({'error': f"Invalid role. Expected one of: {', '.join(sorted(role_aliases))}"}), 400

    identifier = (data.get('username') or data.get('email') or data.get('identifier') or '').strip()
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'error': 'Email/username and password required'}), 400

    user = User.query.filter_by(username=identifier).first()
    if not user and identifier:
        user = User.query.filter(func.lower(User.email) == identifier.lower()).first()

    if user and verify_password(password, user.password):
        # Double-check: Explicit role validation 
        user_roles = [role.name.lower() for role in user.roles]
        if canonical_role not in user_roles:
            return jsonify({'error': 'Account does not have the requested role access.'}), 403
        
        if not _user_matches_selected_role(user, canonical_role):
            return jsonify({'error': 'Current account does not exist.'}), 403

        login_user(user)
        token = user.get_auth_token()
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token,
            'selected_role': canonical_role,
            'requested_role': requested_role
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/logout', methods=['POST'])
@auth_required()
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/api/me', methods=['GET'])
@auth_required()
def get_current_user():
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/api/me', methods=['PUT'])
@auth_required()
def update_current_user_profile():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or not data:
        return jsonify({'error': 'No profile details provided'}), 400

    editable_fields = (
        'first_name',
        'last_name',
        'phone',
        'address',
        'organization',
        'job_title',
        'department',
        'team_number',
        'employee_id',
    )

    updated = False
    for field in editable_fields:
        if field in data:
            value = data.get(field)
            if isinstance(value, str):
                value = value.strip()
            setattr(current_user, field, value or None)
            updated = True

    date_fields = ('hire_date', 'birth_date')
    for field in date_fields:
        if field in data:
            date_value = data.get(field)
            if date_value:
                try:
                    parsed = datetime.strptime(date_value, '%Y-%m-%d').date()
                except (TypeError, ValueError):
                    return jsonify({'error': f'Invalid {field} format. Expected YYYY-MM-DD.'}), 400
                setattr(current_user, field, parsed)
            else:
                setattr(current_user, field, None)
            updated = True

    if not updated:
        return jsonify({'error': 'No editable profile fields were provided'}), 400

    db.session.add(current_user)
    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict(),
    }), 200


@auth_bp.route('/api/register', methods=['POST'])
def register():
    from flask import current_app
    # Only allow registration if enabled in config
    if not current_app.config.get('SECURITY_REGISTERABLE', True):
        return jsonify({'error': 'Registration is disabled'}), 403

    data = request.get_json()

    if not data or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Email and password required'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Get user_datastore from flask_security
    user_datastore = current_app.extensions['security'].datastore

    # Create user with 'employee' role
    # Support additional optional profile fields
    user_kwargs = {
        'email': data['email'],
        'password': hash_password(data['password'])
    }

    optional_fields = (
        'first_name',
        'last_name',
        'phone',
        'address',
        'organization',
        'employee_id',
        'job_title',
        'department',
        'team_number'
    )

    for field in optional_fields:
        value = data.get(field)
        if isinstance(value, str):
            value = value.strip()
        if value:
            user_kwargs[field] = value

    requested_username = (data.get('username') or '').strip()
    if not requested_username:
        first = (data.get('first_name') or '').strip()
        last = (data.get('last_name') or '').strip()
        if first or last:
            requested_username = '.'.join(part for part in (first, last) if part)
        else:
            requested_username = data['email'].split('@', 1)[0]

    base_username = re.sub(r'[^a-z0-9]+', '', requested_username.lower())
    if not base_username:
        base_username = 'user'

    unique_username = base_username
    suffix = 1
    while User.query.filter(func.lower(User.username) == unique_username.lower()).first():
        unique_username = f"{base_username}{suffix}"
        suffix += 1

    user_kwargs['username'] = unique_username

    role_value = data.get('employment_role') or data.get('role') or 'employee'
    if isinstance(role_value, str):
        role_value = role_value.strip().lower()

    # Only manager and employee roles can be created via registration
    # HR role is reserved for default user created in auth.py
    allowed_roles = {'employee', 'manager'}
    if role_value not in allowed_roles:
        return jsonify({'error': f"Invalid role. Expected one of: {', '.join(sorted(allowed_roles))}"}), 400

    user_kwargs['employment_role'] = role_value

    date_fields = ('hire_date', 'birth_date')
    for field in date_fields:
        date_value = data.get(field)
        if date_value:
            try:
                user_kwargs[field] = datetime.strptime(date_value, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return jsonify({'error': f'Invalid {field} format. Expected YYYY-MM-DD.'}), 400

    user = user_datastore.create_user(**user_kwargs)
    # Assign the role based on employment_role (manager or employee)
    try:
        set_user_roles(user, [role_value])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/api/me/resume', methods=['POST'])
@auth_required()
def upload_my_resume():
    """Upload or replace the current user's resume file.

    Expects multipart/form-data with a file field named 'file'.
    """
    if 'file' not in request.files:
        return jsonify({'error': "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    content = file.read()
    # store binary blob directly on the user model
    current_user.resume_file = content
    db.session.add(current_user)
    db.session.commit()

    return jsonify({'message': 'Resume uploaded successfully', 'has_resume': bool(current_user.resume_file)}), 200


@auth_bp.route('/api/me/resume', methods=['GET'])
@auth_required()
def download_my_resume():
    """Download the current user's resume if present."""
    if not getattr(current_user, 'resume_file', None):
        return jsonify({'error': 'No resume uploaded'}), 404

    data = current_user.resume_file
    # Return as an octet-stream; client can handle filename/mimetype if needed.
    return Response(data, mimetype='application/octet-stream', headers={
        'Content-Disposition': 'attachment; filename="resume.bin"'
    })


@auth_bp.route('/api/admin/users/<int:user_id>/resume', methods=['GET'])
@auth_required()
@roles_required('hr')  # Only HR users can access admin endpoints
def admin_download_user_resume(user_id):
    """Admin endpoint to download any user's resume."""
    user = User.query.get_or_404(user_id)
    if not getattr(user, 'resume_file', None):
        return jsonify({'error': 'User has no resume uploaded'}), 404

    return Response(user.resume_file, mimetype='application/octet-stream', headers={
        'Content-Disposition': f'attachment; filename="user_{user_id}_resume.bin"'
    })


def _user_matches_selected_role(user, selected_role):
    """Validate that the authenticated user can act as the requested role.
    
    With single role constraint: users can only login with their exactly assigned role.
    No role hierarchy or cross-role access is allowed.
    """
    from flask import current_app
    
    normalized_role = (selected_role or '').strip().lower()
    user_id = getattr(user, 'id', None)
    if not user_id or not normalized_role:
        current_app.logger.warning(f"Role check failed: invalid user_id={user_id} or role='{normalized_role}'")
        return False

    # Always verify against the latest database state for safety
    fresh_user = User.query.get(user_id)
    if not fresh_user:
        current_app.logger.warning(f"Role check failed: user {user_id} not found in database")
        return False

    # Get all current roles for the user
    user_roles = [role.name.lower() for role in fresh_user.roles]
    has_requested_role = normalized_role in user_roles
    
    current_app.logger.info(f"Role check: user {fresh_user.email} has roles {user_roles}, requesting '{normalized_role}', result: {has_requested_role}")
    
    # Users can only login with their exact assigned role - no cross-role access
    return has_requested_role
