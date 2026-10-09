# app/api/admin.py
from flask import Blueprint, jsonify, request
from flask_security import auth_required, roles_required, roles_accepted, current_user
from datetime import datetime
from app.models.models import User, Role, db
from app.services.offboarding import start_offboarding_for_user
from app.api.utils import set_user_roles

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users', methods=['GET'])
@auth_required()
@roles_accepted('manager', 'hr')
def get_all_users():
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200


@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@auth_required()
@roles_accepted('manager', 'hr')
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)

    def _parse_iso_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(str(value), '%Y-%m-%d').date()
        except Exception:
            return None

    # Only hr can assign hr role and enforce single role constraint
    if 'roles' in data:
        roles = data['roles']
        if len(roles) > 1:
            return jsonify({'error': 'Users can only be assigned one role at a time.'}), 400
        if 'hr' in roles and not current_user.has_role('hr'):
            return jsonify({'error': 'Only hr can assign hr role'}), 403

    # Update user fields
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'active' in data:
        prev_active = user.active
        user.active = data['active']
    # Optional profile fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    if 'organization' in data:
        user.organization = data['organization']
    if 'hire_date' in data:
        user.hire_date = _parse_iso_date(data.get('hire_date'))
    if 'birth_date' in data:
        user.birth_date = _parse_iso_date(data.get('birth_date'))

    # Update roles
    if 'roles' in data:
        try:
            set_user_roles(user, data['roles'])
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

    db.session.commit()

    # If admin deactivated the user, trigger offboarding automation
    try:
        if 'active' in data and prev_active and data['active'] is False:
            final_day_raw = data.get('final_day') or data.get('last_day')
            final_day = None
            if final_day_raw:
                try:
                    from datetime import datetime
                    final_day = datetime.strptime(final_day_raw, '%Y-%m-%d').date()
                except Exception:
                    final_day = None
            # Reason can be provided by admin
            reason = data.get('reason')
            # Call service to start offboarding
            start_offboarding_for_user(user, final_day=final_day, initiator_id=current_user.id, reason=reason)
    except Exception:
        # Do not block user update if offboarding automation fails; administrator can retry
        pass

    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@auth_required()
@roles_required('hr')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent self-deletion
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200