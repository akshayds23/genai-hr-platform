"""Anonymous Feedback API endpoints for employees and HR"""
from flask import Blueprint, current_app, jsonify, request
from flask_security import auth_required, current_user

from app.models.models import AnonymousFeedback, db

feedback_bp = Blueprint('feedback', __name__)


def _can_moderate_feedback(user) -> bool:
    """Return True when the caller is allowed to moderate anonymous feedback."""
    if not user:
        return False
    if user.has_role('hr') or user.has_role('manager'):
        return True
    return (getattr(user, 'employment_role', '') or '').lower() in {'manager', 'hr'}


@feedback_bp.route('/feedback/submit', methods=['POST'])
@auth_required()
def submit_feedback():
    """Submit anonymous feedback from employee"""
    payload = request.get_json() or {}

    title = (payload.get('title') or '').strip()
    category = (payload.get('category') or '').strip()
    feedback_text = (payload.get('feedback_text') or '').strip()
    rating = payload.get('rating')

    # Validation
    if not title:
        return jsonify({'error': 'Feedback title is required'}), 400
    if not category:
        return jsonify({'error': 'Category is required'}), 400
    if not feedback_text:
        return jsonify({'error': 'Feedback text is required'}), 400

    if rating is not None:
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Rating must be a number'}), 400

    try:
        feedback = AnonymousFeedback(
            user_id=current_user.id,  # Store user_id for internal tracking but don't display it
            title=title,
            category=category,
            feedback_text=feedback_text,
            rating=rating
        )
        db.session.add(feedback)
        db.session.commit()

        return jsonify({
            'message': 'Thank you! Your anonymous feedback has been submitted.',
            'feedback_id': feedback.id
        }), 200
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error submitting feedback: %s', error)
        return jsonify({'error': str(error)}), 500


@feedback_bp.route('/feedback/all', methods=['GET'])
@auth_required()
def get_all_feedbacks():
    """Get all feedbacks (HR only)"""
    if not _can_moderate_feedback(current_user):
        return jsonify({'error': 'Unauthorized - HR/Manager access required'}), 403

    # Filter by status if provided
    is_read = request.args.get('is_read')
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = AnonymousFeedback.query

    if is_read is not None:
        is_read = is_read.lower() == 'true'
        query = query.filter_by(is_read=is_read)

    if category:
        query = query.filter_by(category=category)

    feedbacks = query.order_by(AnonymousFeedback.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'feedbacks': [f.to_dict(anonymous=True) for f in feedbacks.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': feedbacks.total,
            'pages': feedbacks.pages
        }
    }), 200


@feedback_bp.route('/feedback/<int:feedback_id>/mark-read', methods=['PUT'])
@auth_required()
def mark_feedback_read(feedback_id):
    """Mark feedback as read (HR only)"""
    if not _can_moderate_feedback(current_user):
        return jsonify({'error': 'Unauthorized - HR/Manager access required'}), 403

    feedback = AnonymousFeedback.query.get_or_404(feedback_id)
    feedback.is_read = True
    db.session.commit()

    return jsonify({
        'message': 'Feedback marked as read',
        'feedback': feedback.to_dict(anonymous=True)
    }), 200


@feedback_bp.route('/feedback/stats', methods=['GET'])
@auth_required()
def get_feedback_stats():
    """Get feedback statistics (HR only)"""
    if not _can_moderate_feedback(current_user):
        return jsonify({'error': 'Unauthorized - HR/Manager access required'}), 403

    total_feedbacks = AnonymousFeedback.query.count()
    unread_feedbacks = AnonymousFeedback.query.filter_by(is_read=False).count()

    # Category breakdown
    category_breakdown = {}
    from sqlalchemy import func
    results = db.session.query(
        AnonymousFeedback.category,
        func.count(AnonymousFeedback.id).label('count')
    ).group_by(AnonymousFeedback.category).all()

    for category, count in results:
        category_breakdown[category] = count

    # Average rating
    avg_rating = db.session.query(func.avg(AnonymousFeedback.rating)).scalar() or 0

    return jsonify({
        'total_feedbacks': total_feedbacks,
        'unread_feedbacks': unread_feedbacks,
        'average_rating': round(float(avg_rating), 2),
        'category_breakdown': category_breakdown
    }), 200


@feedback_bp.route('/feedback/categories', methods=['GET'])
@auth_required()
def get_feedback_categories():
    """Get list of available feedback categories"""
    categories = [
        'Work Environment',
        'Management',
        'Benefits',
        'Culture',
        'Career Development',
        'Compensation',
        'Work-Life Balance',
        'Communication',
        'Tools & Resources',
        'Other'
    ]
    return jsonify({'categories': categories}), 200
