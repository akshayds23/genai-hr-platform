import json
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_security import auth_required, current_user

from app.api.genai.chatbot import hr_chatbot_service
from app.models.models import AuditLog, Message, db
from app.services.employee_dashboard import (
    build_employee_dashboard_data,
    get_chat_conversation,
    get_or_create_chat_conversation,
    load_manager_project_announcement_for_employee,
)

employee_dashboard_bp = Blueprint('employee_dashboard', __name__)


@employee_dashboard_bp.route('/employee/dashboard', methods=['GET'])
@auth_required()
def get_employee_dashboard():
    """Return aggregated dashboard data for the authenticated employee."""
    data = build_employee_dashboard_data(current_user)
    return jsonify(data)


@employee_dashboard_bp.route('/employee/project-announcement', methods=['GET'])
@auth_required()
def get_employee_project_announcement():
    """Return the manager project announcement for the current employee."""
    announcement = load_manager_project_announcement_for_employee(current_user)
    return jsonify({'project_announcement': announcement})


@employee_dashboard_bp.route('/employee/feedback', methods=['POST'])
@auth_required()
def submit_dashboard_feedback():
    data = request.get_json() or {}

    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Feedback message is required'}), 400

    subject = (data.get('subject') or 'General').strip()
    rating = data.get('rating')

    payload = {
        'subject': subject,
        'rating': rating,
        'message': message,
    }

    audit_entry = AuditLog(
        actor_id=current_user.id,
        action='feedback-submitted',
        object_type='feedback',
        object_id=str(current_user.id),
        details=json.dumps(payload),
    )
    db.session.add(audit_entry)
    db.session.commit()

    return jsonify({'message': 'Thank you for sharing your feedback!'}), 200


@employee_dashboard_bp.route('/employee/chatbot', methods=['POST'])
@auth_required()
def interact_with_chatbot():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    conversation = get_or_create_chat_conversation(current_user.id)

    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        sender='user',
        content=message,
        created_at=datetime.utcnow()
    )
    db.session.add(user_message)

    try:
        rag_result = hr_chatbot_service.answer_question(
            current_user,
            message,
            conversation,
            auto_escalate=False,
        )
        response_text = rag_result.get('answer') or "I'm still looking into that and will follow up soon."
        chatbot_status = rag_result.get('status')
        knowledge_reference = rag_result.get('reference')
        knowledge_source = rag_result.get('reference_source')
        question_log_id = rag_result.get('question_log_id')
    except Exception as error:  # pragma: no cover - defensive
        current_app.logger.exception('HR chatbot failed to process query: %s', error)
        response_text = (
            "I ran into a technical issue while fetching the answer. "
            "Please try again shortly or reach out to HR directly."
        )
        chatbot_status = 'error'
        knowledge_reference = None
        knowledge_source = None
        question_log_id = None

    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=None,
        sender='assistant',
        content=response_text,
        created_at=datetime.utcnow()
    )
    db.session.add(assistant_message)

    conversation.ended_at = datetime.utcnow()
    db.session.add(conversation)

    db.session.commit()

    return jsonify({
        'conversation_id': conversation.id,
        'response': response_text,
        'status': chatbot_status,
        'reference': knowledge_reference,
        'reference_source': knowledge_source,
        'question_log_id': question_log_id,
        'messages': [
            {
                'sender': 'user',
                'content': message,
                'timestamp': user_message.created_at.isoformat(),
            },
            {
                'sender': 'assistant',
                'content': response_text,
                'timestamp': assistant_message.created_at.isoformat(),
            }
        ]
    }), 200


@employee_dashboard_bp.route('/employee/chatbot/escalate', methods=['POST'])
@auth_required()
def escalate_chatbot_question():
    payload = request.get_json() or {}
    question = (payload.get('message') or '').strip()
    conversation_id = payload.get('conversation_id')

    if not question:
        return jsonify({'error': 'Question is required'}), 400

    conversation = get_chat_conversation(conversation_id, current_user.id)

    try:
        log_entry = hr_chatbot_service.escalate_question(current_user, question, conversation)
    except Exception as error:  # pragma: no cover - defensive
        current_app.logger.exception('Unable to escalate chatbot question: %s', error)
        return jsonify({'error': 'Failed to forward the question to HR.'}), 500

    acknowledgement = (
        "Thanks! I've sent this to HR for review. You'll receive a notification once someone responds."
    )

    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=None,
        sender='assistant',
        content=acknowledgement,
        created_at=datetime.utcnow(),
    )
    db.session.add(assistant_message)
    conversation.ended_at = datetime.utcnow()
    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        'conversation_id': conversation.id,
        'response': acknowledgement,
        'status': 'pending',
        'question_log_id': log_entry.id,
        'reference': None,
        'reference_source': log_entry.source,
        'messages': [
            {
                'sender': 'assistant',
                'content': acknowledgement,
                'timestamp': assistant_message.created_at.isoformat(),
            }
        ]
    }), 200
