from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from sqlalchemy import func

from app.models.models import LeaveRequest, User, db
from app.services.leave_balance import (
    build_balance_snapshot,
    inclusive_day_count,
    overlap_in_range,
    remaining_leave_days,
)
from app.services.notifications import determine_manager_ids, notify_users

leave_bp = Blueprint('leave', __name__)

DATE_FORMAT = '%Y-%m-%d'
ALLOWED_STATUSES = {'pending', 'approved', 'rejected', 'cancelled'}
ANNUAL_LEAVE_ALLOWANCE = 20


def _parse_date(value, label):
    if not value:
        raise ValueError(f'{label} is required')
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Invalid {label}. Expected format YYYY-MM-DD.') from exc


def _is_manager_or_admin(user):
    if hasattr(user, 'is_admin') and user.is_admin():
        return True
    return getattr(user, 'employment_role', '') == 'manager'


@leave_bp.route('/leave/apply', methods=['POST'])
@auth_required()
def apply_for_leave():
    data = request.get_json() or {}

    try:
        start_date = _parse_date(data.get('start_date'), 'start_date')
        end_date = _parse_date(data.get('end_date'), 'end_date')
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    if start_date > end_date:
        return jsonify({'error': 'start_date cannot be after end_date.'}), 400

    requested_days = inclusive_day_count(start_date, end_date)
    if requested_days <= 0:
        return jsonify({'error': 'Requested leave duration must be at least one day.'}), 400

    for year in range(start_date.year, end_date.year + 1):
        span_days = overlap_in_range(start_date, end_date, date(year, 1, 1), date(year, 12, 31))
        remaining_days = remaining_leave_days(
            current_user.id,
            year,
            allowance_days=ANNUAL_LEAVE_ALLOWANCE,
        )
        if span_days > remaining_days:
            return jsonify({
                'error': (
                    f'Request exceeds remaining balance for {year}. '
                    f'You have {remaining_days} day{"s" if remaining_days != 1 else ""} left.'
                )
            }), 400

    conflicting_leave = (
        LeaveRequest.query.filter(LeaveRequest.user_id == current_user.id)
        .filter(LeaveRequest.status.in_(['pending', 'approved']))
        .filter(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= start_date)
        .first()
    )
    if conflicting_leave:
        return jsonify({
            'error': (
                'You already have a leave request covering these dates. '
                'Please modify the dates or cancel the existing request.'
            )
        }), 400

    leave_type = (data.get('leave_type') or 'general').strip()
    reason = (data.get('reason') or '').strip() or None

    leave_request = LeaveRequest(
        user_id=current_user.id,
        leave_type=leave_type or 'general',
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status='pending'
    )

    db.session.add(leave_request)
    db.session.flush()

    # Do not notify managers for resignation/offboarding leave types
    if leave_type.lower() not in {'resignation', 'offboarding'}:
        manager_ids = determine_manager_ids(current_user)
        if manager_ids:
            notify_users(
                manager_ids,
                category='leave',
                title='New leave request pending review',
                message=f'{current_user.first_name or current_user.email} requested leave {start_date} - {end_date}.',
                metadata={
                    'leave_id': leave_request.id,
                    'employee_id': current_user.id,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'status': 'pending',
                },
            )

    db.session.commit()

    return jsonify({
        'message': 'Leave request submitted successfully.',
        'leave': leave_request.to_dict(),
        'balance': build_balance_snapshot(
            current_user.id,
            reference_date=start_date,
            allowance_days=ANNUAL_LEAVE_ALLOWANCE,
        )
    }), 200


@leave_bp.route('/leave/mine', methods=['GET'])
@auth_required()
def get_my_leaves():
    status_filter = (request.args.get('status') or '').strip().lower()

    query = current_user.leave_requests.order_by(LeaveRequest.created_at.desc())
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    leaves = [leave.to_dict() for leave in query.all()]
    return jsonify({'leaves': leaves})


@leave_bp.route('/leave/team/requests', methods=['GET'])
@auth_required()
def get_team_leave_requests():
    if not _is_manager_or_admin(current_user):
        return jsonify({'error': 'Only managers or admins can view team leave requests.'}), 403

    team_number = (request.args.get('team_number') or getattr(current_user, 'team_number', None) or '').strip()
    if not team_number:
        return jsonify({'leaves': []})

    status_param = (request.args.get('status') or 'pending').lower()
    statuses = {value.strip().lower() for value in status_param.split(',') if value.strip()}
    if not statuses:
        statuses = {'pending'}

    query = (
        LeaveRequest.query
        .join(User, LeaveRequest.user_id == User.id)
        .filter(User.team_number == team_number)
        .filter(LeaveRequest.status.in_(statuses))
        .filter(LeaveRequest.leave_type.notin_(['resignation', 'offboarding']))  # <<< hide resign/offboarding
        .order_by(LeaveRequest.start_date.asc())
    )

    leaves = []
    for leave in query.limit(50).all():
        employee = leave.user
        if employee:
            full_name_parts = [part for part in (employee.first_name, employee.last_name) if part]
            employee_name = ' '.join(full_name_parts) or employee.username or employee.email
        else:
            employee_name = 'Team member'

        leaves.append({
            'id': leave.id,
            'employee_id': leave.user_id,
            'employee_name': employee_name,
            'leave_type': leave.leave_type,
            'start_date': leave.start_date.isoformat() if leave.start_date else None,
            'end_date': leave.end_date.isoformat() if leave.end_date else None,
            'status': leave.status,
            'reason': leave.reason,
            'submitted_at': leave.created_at.isoformat() if leave.created_at else None,
        })

    return jsonify({'leaves': leaves})


@leave_bp.route('/leave/<int:leave_id>', methods=['GET'])
@auth_required()
def get_leave_detail(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)

    if (
        leave.user_id != current_user.id
        and not _is_manager_or_admin(current_user)
    ):
        return jsonify({'error': 'Not authorized to view this leave request.'}), 403

    return jsonify({'leave': leave.to_dict()})


@leave_bp.route('/leave/<int:leave_id>/cancel', methods=['POST'])
@auth_required()
def cancel_my_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)

    if leave.user_id != current_user.id:
        return jsonify({'error': 'You can only cancel your own leave requests.'}), 403

    status = (leave.status or '').lower()
    if status not in {'pending', 'approved'}:
        return jsonify({'error': 'Only pending or approved requests can be cancelled.'}), 400

    if status == 'approved' and leave.start_date and leave.start_date <= date.today():
        return jsonify({'error': 'Approved leave that has already started cannot be cancelled.'}), 400

    leave.status = 'cancelled'
    leave.decision_reason = 'Cancelled by requester'
    leave.updated_at = datetime.utcnow()

    db.session.add(leave)
    manager_ids = determine_manager_ids(current_user)
    if manager_ids:
        notify_users(
            manager_ids,
            category='leave',
            title='Leave request cancelled',
            message=(
                f'{current_user.first_name or current_user.email} cancelled leave '
                f'for {leave.start_date.isoformat() if leave.start_date else ""} '
                f'- {leave.end_date.isoformat() if leave.end_date else ""}.'
            ),
            metadata={
                'leave_id': leave.id,
                'status': leave.status,
            },
        )

    db.session.commit()

    return jsonify({
        'message': 'Leave request cancelled.',
        'leave': leave.to_dict()
    })


@leave_bp.route('/leave/<int:leave_id>/status', methods=['PATCH'])
@auth_required()
def update_leave_status(leave_id):
    if not _is_manager_or_admin(current_user):
        return jsonify({'error': 'Only managers or admins can update leave status.'}), 403

    leave = LeaveRequest.query.get_or_404(leave_id)
    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip().lower()

    if new_status not in ALLOWED_STATUSES:
        return jsonify({'error': f'Invalid status. Allowed values: {", ".join(sorted(ALLOWED_STATUSES))}'}), 400

    leave.status = new_status
    leave.decision_reason = (data.get('comment') or '').strip() or None
    leave.approver_id = current_user.id
    leave.updated_at = datetime.utcnow()

    db.session.add(leave)

    notify_users(
        [leave.user_id],
        category='leave',
        title='Leave request updated',
        message=(
            f'Your leave request for {leave.start_date.isoformat() if leave.start_date else ""} '
            f'- {leave.end_date.isoformat() if leave.end_date else ""} was {new_status}.'
        ),
        metadata={
            'leave_id': leave.id,
            'status': new_status,
            'comment': leave.decision_reason,
        },
    )

    db.session.commit()

    return jsonify({
        'message': 'Leave status updated.',
        'leave': leave.to_dict()
    })


@leave_bp.route('/leave/summary', methods=['GET'])
@auth_required()
def leave_summary():
    scope = (request.args.get('scope') or 'self').lower()
    query = LeaveRequest.query

    # Exclude resignation/offboarding from leave stats and balance
    query = query.filter(LeaveRequest.leave_type.notin_(['resignation', 'offboarding']))  # <<<

    if scope == 'team' and _is_manager_or_admin(current_user):
        team_number = getattr(current_user, 'team_number', None)
        if not team_number:
            return jsonify({'error': 'Manager is not assigned to a team.'}), 400
        query = query.join(User, LeaveRequest.user_id == User.id).filter(User.team_number == team_number)
    elif scope == 'all' and current_user.is_admin():
        pass  # Already querying all leave requests (except resignation/offboarding)
    else:
        query = query.filter(LeaveRequest.user_id == current_user.id)

    status_counts = dict(
        query.with_entities(LeaveRequest.status, func.count(LeaveRequest.id)).group_by(LeaveRequest.status).all()
    )
    total = sum(status_counts.values())

    response = {
        'summary': status_counts,
        'total': total
    }

    if scope not in {'team', 'all'} or not current_user.is_admin():
        response['balance'] = build_balance_snapshot(
            current_user.id,
            allowance_days=ANNUAL_LEAVE_ALLOWANCE,
        )

    return jsonify(response)
