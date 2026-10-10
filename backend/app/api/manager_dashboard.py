from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user

from app.api.genai.chatbot import hr_chatbot_service
from app.models.models import ProjectAnnouncement, Team, User, db
from app.services.manager_dashboard import (
    build_manager_dashboard_data,
    collect_team_overview,
    ensure_manager_access,
    get_manager_project_announcement,
    resolve_user_team,
    serialize_project_announcement,
)

manager_dashboard_bp = Blueprint('manager_dashboard', __name__)


@manager_dashboard_bp.route('/manager/debug-team', methods=['GET'])
@auth_required()
def debug_team_info():
    """Debug endpoint to check team information"""
    if not ensure_manager_access(current_user):
        return jsonify({'error': 'Only managers or admins can access this dashboard.'}), 403

    user = current_user
    user_team_id = user.team_id
    managed_team = Team.query.filter_by(manager_id=user.id).first()
    team_from_user_id = Team.query.get(user_team_id) if user_team_id else None

    managed_team_members = []
    if managed_team:
        managed_team_members = User.query.filter(User.team_id == managed_team.id).all()

    all_teams = Team.query.all()

    return jsonify({
        'current_user': {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'team_id': user_team_id,
            'employment_role': user.employment_role,
        },
        'user_team_id': user_team_id,
        'team_from_user_id': team_from_user_id.to_dict() if team_from_user_id else None,
        'managed_team': managed_team.to_dict() if managed_team else None,
        'managed_team_members': [
            {
                'id': member.id,
                'name': f"{member.first_name} {member.last_name}",
                'email': member.email,
                'team_id': member.team_id,
                'employment_role': member.employment_role,
            }
            for member in managed_team_members
        ],
        'resolved_team': resolve_user_team(user).to_dict() if resolve_user_team(user) else None,
        'team_overview': collect_team_overview(user),
        'all_teams': [team.to_dict() for team in all_teams],
    })


@manager_dashboard_bp.route('/manager/dashboard', methods=['GET'])
@auth_required()
def manager_dashboard():
    if not ensure_manager_access(current_user):
        return jsonify({'error': 'Only managers or admins can access this dashboard.'}), 403

    status_param = request.args.get('status') or 'pending'
    data = build_manager_dashboard_data(current_user, status_param=status_param)

    if hr_chatbot_service:
        hr_chatbot_service.ensure_profile_indexed(current_user.id)

    return jsonify(data)


@manager_dashboard_bp.route('/manager/project-announcement', methods=['GET', 'PUT', 'DELETE'])
@auth_required()
def manage_project_announcement():
    if not ensure_manager_access(current_user):
        return jsonify({'error': 'Only managers or admins can update the project announcement.'}), 403

    manager_id = current_user.id

    if request.method == 'GET':
        return jsonify({'project_announcement': get_manager_project_announcement(manager_id)})

    if request.method == 'DELETE':
        record = ProjectAnnouncement.query.filter_by(manager_id=manager_id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
        return jsonify({'project_announcement': None})

    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or '').strip()
    description = (payload.get('description') or '').strip()

    if not title or not description:
        return jsonify({'error': 'Title and description are required.'}), 400

    record = ProjectAnnouncement.query.filter_by(manager_id=manager_id).first()
    now = datetime.utcnow()

    if not record:
        record = ProjectAnnouncement(
            manager_id=manager_id,
            title=title,
            description=description,
        )
        db.session.add(record)
    else:
        record.title = title
        record.description = description
    record.updated_at = now

    db.session.commit()
    return jsonify({'project_announcement': serialize_project_announcement(record)})
