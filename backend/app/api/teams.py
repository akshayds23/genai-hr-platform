from flask import Blueprint, jsonify, request
from flask_security import auth_required, roles_accepted

from app.models.models import Role, Team, User, db

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/admin/teams', methods=['GET'])
@auth_required()
@roles_accepted('manager', 'hr')
def get_teams():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)  # Default 9 for 3x3 grid
    search = request.args.get('search', '', type=str)
    manager_filter = request.args.get('manager_filter', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_direction = request.args.get('sort_direction', 'asc', type=str)

    # Build query
    query = Team.query

    # Apply search filter
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            db.or_(
                Team.name.ilike(search_term),
                Team.description.ilike(search_term)
            )
        )

    # Apply manager filter
    if manager_filter:
        if manager_filter == 'assigned':
            query = query.filter(Team.manager_id.isnot(None))
        elif manager_filter == 'unassigned':
            query = query.filter(Team.manager_id.is_(None))

    # Apply sorting
    if sort_by == 'name':
        sort_column = Team.name
    elif sort_by == 'created_at':
        sort_column = Team.created_at
    else:
        sort_column = Team.name  # default fallback

    if sort_direction == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    teams = pagination.items

    return jsonify({
        'teams': [team.to_dict() for team in teams],
        'total_items': pagination.total,
        'total_pages': pagination.pages,
        'current_page': page,
        'has_next': pagination.has_next
    }), 200

@teams_bp.route('/admin/teams', methods=['POST'])
@auth_required()
@roles_accepted('manager', 'hr')
def create_team():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    manager_id = data.get('manager_id')

    if not name:
        return jsonify({'error': 'Team name is required'}), 400

    if Team.query.filter_by(name=name).first():
        return jsonify({'error': 'Team name already exists'}), 400

    # Require manager_id when creating a team
    if not manager_id:
        return jsonify({'error': 'Manager is required to create a team'}), 400

    manager = User.query.get(manager_id)
    if not manager:
        return jsonify({'error': 'Manager not found'}), 404

    # Check if manager is already assigned to another team
    existing_team = Team.query.filter_by(manager_id=manager_id).first()
    if existing_team:
        return jsonify({'error': f'Manager is already assigned to team "{existing_team.name}"'}), 400

    # Check if manager has 'manager' role
    if not manager.has_role('manager'):
        return jsonify({'error': 'Selected user does not have manager role'}), 400

    team = Team(name=name, description=description, manager=manager)
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team created successfully', 'team': team.to_dict()}), 200

@teams_bp.route('/admin/teams/<int:team_id>', methods=['PUT'])
@auth_required()
@roles_accepted('manager', 'hr')
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    data = request.get_json()

    if 'name' in data:
        name = data['name']
        if name != team.name and Team.query.filter_by(name=name).first():
            return jsonify({'error': 'Team name already exists'}), 400
        team.name = name

    if 'description' in data:
        team.description = data['description']

    if 'manager_id' in data:
        manager_id = data['manager_id']
        if not manager_id:
            return jsonify({'error': 'Manager is required. Cannot unassign manager from a team'}), 400

        manager = User.query.get(manager_id)
        if not manager:
            return jsonify({'error': 'Manager not found'}), 404

        # Check if manager has 'manager' role
        if not manager.has_role('manager'):
            return jsonify({'error': 'Selected user does not have manager role'}), 400

        # Check if manager is already assigned to another team (excluding current team)
        existing_team = Team.query.filter(
            Team.manager_id == manager_id,
            Team.id != team_id
        ).first()
        if existing_team:
            return jsonify({'error': f'Manager is already assigned to team "{existing_team.name}"'}), 400

        # If manager is changing, update all team members' manager_id
        old_manager_id = team.manager_id
        team.manager = manager

        # Update all team members' manager_id to the new manager
        if old_manager_id != manager_id:
            for member in team.members:
                member.manager_id = manager_id

    db.session.commit()
    db.session.refresh(team)
    return jsonify({'message': 'Team updated successfully', 'team': team.to_dict()}), 200

@teams_bp.route('/admin/teams/<int:team_id>', methods=['DELETE'])
@auth_required()
@roles_accepted('manager', 'hr')
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)

    # Remove team_id and manager_id from all members
    for member in team.members:
        member.team_id = None
        member.manager_id = None

    db.session.delete(team)
    db.session.commit()
    return jsonify({'message': 'Team deleted successfully'}), 200

@teams_bp.route('/admin/teams/<int:team_id>/members', methods=['POST'])
@auth_required()
@roles_accepted('manager', 'hr')
def add_team_member(team_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    team = Team.query.get_or_404(team_id)

    # Ensure team has a manager (should always be true now, but check for safety)
    if not team.manager_id:
        return jsonify({'error': 'Team must have a manager assigned before adding members'}), 400

    user = User.query.get_or_404(user_id)
    user.team_id = team.id
    # Update employee's manager_id to match team's manager
    user.manager_id = team.manager_id
    db.session.commit()

    return jsonify({'message': 'Member added successfully', 'team': team.to_dict()}), 200

@teams_bp.route('/admin/teams/<int:team_id>/members/<int:user_id>', methods=['DELETE'])
@auth_required()
@roles_accepted('manager', 'hr')
def remove_team_member(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    user = User.query.get_or_404(user_id)

    if user.team_id != team.id:
        return jsonify({'error': 'User is not in this team'}), 400

    # Remove user from team and clear their manager_id
    user.team_id = None
    user.manager_id = None
    db.session.commit()

    return jsonify({'message': 'Member removed successfully', 'team': team.to_dict()}), 200

@teams_bp.route('/admin/teams/<int:team_id>/members', methods=['GET'])
@auth_required()
@roles_accepted('manager', 'hr')
def get_team_members(team_id):
    team = Team.query.get_or_404(team_id)
    # Existing members
    member_objs = team.members[:]
    # Add manager if they're not already in the list
    manager_obj = None
    if team.manager_id:
        # Avoid duplicate if manager is also a member
        if not any(u.id == team.manager_id for u in member_objs):
            manager_obj = team.manager
    members = []
    for user in member_objs:
        udict = user.to_dict()
        udict['is_manager'] = user.id == team.manager_id
        members.append(udict)
    if manager_obj:
        udict = manager_obj.to_dict()
        udict['is_manager'] = True
        members.insert(0, udict)  # or append to end, as needed
    return jsonify({'members': members}), 200

@teams_bp.route('/admin/teams/<int:team_id>/unassign-manager', methods=['POST'])
@auth_required()
@roles_accepted('manager', 'hr')
def unassign_team_manager(team_id):
    """This endpoint is deprecated. Teams must always have a manager assigned."""
    return jsonify({'error': 'Cannot unassign manager. Teams must always have a manager assigned. Please assign a new manager instead.'}), 400

@teams_bp.route('/admin/available-managers', methods=['GET'])
@auth_required()
@roles_accepted('manager', 'hr')
def get_available_managers():
    """Get all managers who are not currently assigned to any team"""
    team_id = request.args.get('exclude_team_id', type=int)  # Exclude current team when editing

    # Get all users with manager role
    managers_with_role = User.query.join(User.roles).filter(Role.name == 'manager').all()

    # Get managers who are already assigned to teams (excluding specified team if editing)
    assigned_manager_ids_query = db.session.query(Team.manager_id).filter(
        Team.manager_id.isnot(None)
    )

    if team_id:
        assigned_manager_ids_query = assigned_manager_ids_query.filter(Team.id != team_id)

    assigned_manager_ids = [id[0] for id in assigned_manager_ids_query.all()]

    # Filter out already assigned managers
    available_managers = [
        manager for manager in managers_with_role
        if manager.id not in assigned_manager_ids
    ]

    return jsonify({
        'managers': [manager.to_dict() for manager in available_managers]
    }), 200
