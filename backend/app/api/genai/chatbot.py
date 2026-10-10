import json
import logging

from flask import Blueprint, current_app, jsonify, request
from flask_security import auth_required, current_user

from app.models.models import AuditLog, Conversation, HRKnowledge, HRQuestionLog, Message, User, db
from app.services.ai import AIRateLimitError, AIUnavailableError
from app.services.chatbot import hr_chatbot_service
from app.services.notifications import notify_users

logger = logging.getLogger(__name__)

hr_chatbot_bp = Blueprint('hr_chatbot', __name__)

# API routes
# ------------------------------------------------------------------------- #


@hr_chatbot_bp.route('/hr/questions', methods=['GET'])
@auth_required()
def list_hr_questions():
    status_filter = request.args.get('status', 'pending').lower()
    statuses = {status.strip() for status in status_filter.split(',') if status.strip()}
    if not statuses:
        statuses = {'pending'}

    query = HRQuestionLog.query
    if 'all' not in statuses:
        query = query.filter(HRQuestionLog.status.in_(list(statuses)))

    if current_user.is_admin():
        pass
    elif current_user.employment_role == 'manager':
        team_number = getattr(current_user, 'team_number', None)
        team_user_ids = []
        if team_number:
            team_user_ids = [
                member.id
                for member in User.query
                .filter(User.team_number == team_number)
                .filter(User.active.is_(True))
                .all()
            ]
        query = query.filter(
            (HRQuestionLog.manager_id == current_user.id)
            | (HRQuestionLog.user_id.in_(team_user_ids) if team_user_ids else False)
        )
    else:
        query = query.filter(HRQuestionLog.user_id == current_user.id)

    questions = [
        {
            'id': item.id,
            'question': item.question,
            'answer': item.answer,
            'status': item.status,
            'source': item.source,
            'confidence': item.confidence,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            'resolved_at': item.resolved_at.isoformat() if item.resolved_at else None,
            'user_id': item.user_id,
            'manager_id': item.manager_id,
        }
        for item in query.order_by(HRQuestionLog.created_at.desc()).limit(100).all()
    ]
    return jsonify({'questions': questions})


@hr_chatbot_bp.route('/hr/questions/<int:question_id>/answer', methods=['POST'])
@auth_required()
def resolve_hr_question(question_id: int):
    if not (current_user.is_admin() or current_user.employment_role == 'manager'):
        return jsonify({'error': 'Only managers or HR can resolve questions.'}), 403

    payload = request.get_json() or {}
    answer = (payload.get('answer') or '').strip()
    if not answer:
        return jsonify({'error': 'Answer is required.'}), 400

    question = HRQuestionLog.query.get_or_404(question_id)
    question.answer = answer
    question.status = 'resolved'
    question.resolved_by = current_user.id
    question.resolved_at = db.func.now()
    question.source = question.source or 'manual_review'
    question.updated_at = db.func.now()

    if not question.manager_id:
        question.manager_id = current_user.id

    hr_chatbot_service.add_manual_knowledge(
        question.question,
        answer,
        source='manual_review',
    )

    details_payload = {
        'question_id': question.id,
        'question': question.question,
        'answer': answer,
        'resolved_by': current_user.id,
    }
    if question.user_id:
        audit_entry = AuditLog(
            actor_id=current_user.id,
            action='hr-question-resolved',
            object_type='hr_question',
            object_id=str(question.user_id),
            details=json.dumps(details_payload),
        )
        db.session.add(audit_entry)

        notify_users(
            [question.user_id],
            category='hr_question',
            title='HR question answered',
            message='HR has responded to your question. Tap to read the reply.',
            metadata={
                'question_id': question.id,
                'status': question.status,
            },
        )
        if question.manager_id and question.manager_id != question.user_id:
            notify_users(
                [question.manager_id],
                category='hr_question',
                title='HR question answered',
                message='HR has responded to the escalated question from your team.',
                metadata={
                    'question_id': question.id,
                    'status': question.status,
                    'resolved_for': 'manager',
                },
            )

    db.session.commit()

    return jsonify({'message': 'Question resolved and knowledge base updated.'})


@hr_chatbot_bp.route('/genai/chat/knowledge', methods=['GET'])
@auth_required()
def get_knowledge_base():
    """Get all questions in the HR knowledge base (for debugging/reference)."""
    try:
        records = HRKnowledge.query.order_by(HRKnowledge.id.asc()).all()
        questions = [
            {
                'id': record.id,
                'question': record.question,
                'source': record.source,
            }
            for record in records[:20]  # Limit to first 20
        ]
        return jsonify({
            'total': len(records),
            'questions': questions,
        }), 200
    except Exception as error:
        current_app.logger.exception('Error fetching knowledge base: %s', error)
        return jsonify({'error': str(error)}), 500


@hr_chatbot_bp.route('/genai/chat', methods=['POST'])
@auth_required()
def chat():
    """Send a message to the HR chatbot and get a response."""
    payload = request.get_json() or {}
    user_message = (payload.get('message') or '').strip()
    raw_auto_escalate = payload.get('auto_escalate')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    if isinstance(raw_auto_escalate, str):
        normalized = raw_auto_escalate.strip().lower()
        auto_escalate = normalized not in {'false', '0', 'no'}
    elif raw_auto_escalate is None:
        auto_escalate = True
    else:
        auto_escalate = bool(raw_auto_escalate)

    try:
        conversation = Conversation.query.filter_by(
            user_id=current_user.id,
        ).first()
        if not conversation:
            conversation = Conversation(user_id=current_user.id)
            db.session.add(conversation)
            db.session.commit()

        user_msg = Message(
            conversation_id=conversation.id,
            sender='user',
            content=user_message,
        )
        db.session.add(user_msg)
        db.session.commit()

        result = hr_chatbot_service.answer_question(
            current_user,
            user_message,
            conversation,
            auto_escalate=auto_escalate,
        )

        ai_msg = Message(
            conversation_id=conversation.id,
            sender='assistant',
            content=result['answer'],
        )
        db.session.add(ai_msg)
        db.session.commit()

        return jsonify({
            'response': result['answer'],
            'status': result.get('status', 'answered'),
            'question_id': result.get('question_log_id'),
            'reference': result.get('reference'),
            'reference_source': result.get('reference_source'),
            'conversation_id': conversation.id,
        }), 200
    except AIRateLimitError as error:
        return jsonify({'error': str(error)}), 429
    except AIUnavailableError:
        return jsonify({'error': 'AI service is not available right now'}), 503
    except Exception as error:
        current_app.logger.exception('Chat error: %s', error)
        return jsonify({'error': str(error)}), 500
