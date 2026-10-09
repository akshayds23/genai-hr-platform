"""
Public endpoint for creating a new HR account.

This endpoint allows an external HR representative to create a hr
user if one does not already exist for the provided email. It collects
minimal information (name, email, password and organisation) and assigns
the ``hr`` role. This route is intentionally not protected by
authentication so that a company can bootstrap its first HR user.

Security considerations:

* If a user is already logged in (and not a manager), the request is
  rejected to prevent privilege escalation.
* Email addresses are normalised to lower-case to avoid duplicates.
* Usernames are derived from the email prefix with a numeric suffix if
  necessary to ensure uniqueness.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_security.utils import hash_password
from flask_security import current_user

from app.models.models import User, db
from app.api.utils import set_user_roles


# Define blueprint for HR signup
hr_signup_bp = Blueprint('hr_signup', __name__)


@hr_signup_bp.route('/auth/signup/hr', methods=['POST'])
def signup_hr():
    """
    Create a new HR user. This route is open to
    unauthenticated users. A hr account with the given email
    must not already exist. If a user is currently authenticated and not
    a manager, they cannot create another HR account.

    Request JSON body should include:
      - email: the HR's email address (required)
      - password: the desired password (required)
      - first_name: optional first name
      - last_name: optional last name
      - organization/organisation: optional organisation name

    Returns a success message and the created user's public fields.
    """
    # Prevent non-admin authenticated users from creating HR users
    if current_user.is_authenticated and not current_user.is_admin():
        return jsonify({'error': 'You are already logged in'}), 403

    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    organisation = (data.get('organization') or data.get('organisation') or '').strip()
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    # Check for existing user by email
    if User.query.filter(User.email.ilike(email)).first():
        return jsonify({'error': 'A user with that email already exists.'}), 400

    user_datastore = current_app.extensions['security'].datastore
    # Derive a unique username from the email prefix
    username_base = email.split('@', 1)[0]
    username = username_base
    suffix = 1
    while User.query.filter(User.username.ilike(username)).first():
        username = f"{username_base}{suffix}"
        suffix += 1
    # Create user
    new_user = user_datastore.create_user(
        email=email,
        username=username,
        password=hash_password(password),
        first_name=first_name or None,
        last_name=last_name or None,
        organization=organisation or None,
    )
    # Assign the hr role
    try:
        set_user_roles(new_user, ['hr'])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    db.session.commit()
    return jsonify({'message': 'HR user created successfully', 'user': new_user.to_dict()}), 200