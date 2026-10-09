"""FAQ Management API for HR Knowledge Base"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename

from flask import Blueprint, current_app, jsonify, request
from flask_security import auth_required, roles_required, current_user
from pypdf import PdfReader

from app.models.models import db, HRKnowledge
from app.api.genai.B_HRchatbot import hr_chatbot_service


faq_management_bp = Blueprint('faq_management', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_qa_pairs_from_text(text: str) -> List[tuple[str, str]]:
    """Parse Q&A pairs from text content"""
    lines = text.splitlines()
    qa_pairs: List[tuple[str, str]] = []
    current_question: Optional[str] = None
    current_answer_lines: List[str] = []

    for raw_line in lines:
        line = (raw_line or '').strip()
        if not line:
            continue

        normalized = line.lower()
        is_question = (
            line.endswith('?')
            or normalized.startswith('q:')
            or normalized.startswith('question')
        )

        if is_question:
            if current_question:
                answer_text = ' '.join(current_answer_lines).strip()
                if answer_text:
                    qa_pairs.append((current_question.strip(), answer_text))
                current_answer_lines = []

            if ':' in line:
                current_question = line.split(':', 1)[1].strip() or line
            else:
                current_question = line
        else:
            cleaned = (
                line.split(':', 1)[1].strip()
                if normalized.startswith(('answer', 'a:'))
                else line
            )
            current_answer_lines.append(cleaned)

    if current_question and current_answer_lines:
        answer_text = ' '.join(current_answer_lines).strip()
        if answer_text:
            qa_pairs.append((current_question.strip(), answer_text))

    return qa_pairs


@faq_management_bp.route('/admin/faqs', methods=['GET'])
@auth_required()
@roles_required('hr')
def list_faqs():
    """Get all FAQs from knowledge base"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '').strip()
        
        query = HRKnowledge.query
        
        if search:
            query = query.filter(
                db.or_(
                    HRKnowledge.question.ilike(f'%{search}%'),
                    HRKnowledge.answer.ilike(f'%{search}%')
                )
            )
        
        paginated = query.order_by(HRKnowledge.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        faqs = [
            {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'source': faq.source,
                'created_at': faq.created_at.isoformat() if faq.created_at else None,
                'updated_at': faq.updated_at.isoformat() if faq.updated_at else None,
            }
            for faq in paginated.items
        ]
        
        return jsonify({
            'faqs': faqs,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
        })
        
    except Exception as error:
        current_app.logger.exception('Error fetching FAQs: %s', error)
        return jsonify({'error': 'Failed to fetch FAQs'}), 500


@faq_management_bp.route('/admin/faqs', methods=['POST'])
@auth_required()
@roles_required('hr')
def create_faq():
    """Create a new FAQ manually"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        question = (data.get('question') or '').strip()
        answer = (data.get('answer') or '').strip()
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        # Check for duplicate question
        existing = HRKnowledge.query.filter(
            db.func.lower(HRKnowledge.question) == question.lower()
        ).first()
        
        if existing:
            return jsonify({'error': 'A FAQ with this question already exists'}), 409
        
        # Create new FAQ
        faq = HRKnowledge(
            question=question,
            answer=answer,
            source='manual_entry'
        )
        
        db.session.add(faq)
        db.session.commit()
        
        # Add to chatbot knowledge using the service
        hr_chatbot_service.add_manual_knowledge(question, answer, source='manual_entry')
        
        return jsonify({
            'message': 'FAQ created successfully',
            'faq': {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'source': faq.source,
                'created_at': faq.created_at.isoformat() if faq.created_at else None,
            }
        }), 200
        
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error creating FAQ: %s', error)
        return jsonify({'error': 'Failed to create FAQ'}), 500


@faq_management_bp.route('/admin/faqs/<int:faq_id>', methods=['PUT'])
@auth_required()
@roles_required('hr')
def update_faq(faq_id: int):
    """Update an existing FAQ"""
    try:
        faq = HRKnowledge.query.get_or_404(faq_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        question = (data.get('question') or '').strip()
        answer = (data.get('answer') or '').strip()
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        # Check for duplicate question (excluding current FAQ)
        existing = HRKnowledge.query.filter(
            db.and_(
                db.func.lower(HRKnowledge.question) == question.lower(),
                HRKnowledge.id != faq_id
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'A FAQ with this question already exists'}), 409
        
        # Update FAQ
        faq.question = question
        faq.answer = answer
        faq.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update chatbot knowledge
        hr_chatbot_service.add_manual_knowledge(question, answer, source=faq.source or 'manual_entry')
        
        return jsonify({
            'message': 'FAQ updated successfully',
            'faq': {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'source': faq.source,
                'updated_at': faq.updated_at.isoformat() if faq.updated_at else None,
            }
        })
        
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error updating FAQ: %s', error)
        return jsonify({'error': 'Failed to update FAQ'}), 500


@faq_management_bp.route('/admin/faqs/<int:faq_id>', methods=['DELETE'])
@auth_required()
@roles_required('hr')
def delete_faq(faq_id: int):
    """Delete an FAQ"""
    try:
        faq = HRKnowledge.query.get_or_404(faq_id)
        
        db.session.delete(faq)
        db.session.commit()
        
        # Clear knowledge cache to refresh without deleted item
        hr_chatbot_service._knowledge_cache = []
        
        return jsonify({'message': 'FAQ deleted successfully'})
        
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error deleting FAQ: %s', error)
        return jsonify({'error': 'Failed to delete FAQ'}), 500


@faq_management_bp.route('/admin/faqs/upload', methods=['POST'])
@auth_required()
@roles_required('hr')
def upload_faq_file():
    """Upload PDF or text file to extract FAQs"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and TXT files are allowed'}), 400
        
        # Read file content
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            # Parse PDF content
            try:
                from io import BytesIO
                pdf_reader = PdfReader(BytesIO(file_content))
                text_content = ''
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + '\n'
            except Exception as pdf_error:
                current_app.logger.error('Error parsing PDF: %s', pdf_error)
                return jsonify({'error': 'Failed to parse PDF file'}), 400
        else:
            # Handle text file
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                return jsonify({'error': 'Invalid text file encoding. Please use UTF-8'}), 400
        
        # Parse Q&A pairs from content
        qa_pairs = parse_qa_pairs_from_text(text_content)
        
        if not qa_pairs:
            return jsonify({'error': 'No Q&A pairs found in the file. Please format as Q: question A: answer'}), 400
        
        # Store FAQs in database
        added_count = 0
        skipped_count = 0
        
        for question, answer in qa_pairs:
            if not question.strip() or not answer.strip():
                continue
                
            # Check for existing question
            existing = HRKnowledge.query.filter(
                db.func.lower(HRKnowledge.question) == question.lower()
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            faq = HRKnowledge(
                question=question.strip(),
                answer=answer.strip(),
                source=f'file_upload:{filename}'
            )
            
            db.session.add(faq)
            added_count += 1
        
        db.session.commit()
        
        # Refresh chatbot knowledge cache
        hr_chatbot_service._knowledge_cache = []
        
        return jsonify({
            'message': f'Upload completed. Added {added_count} new FAQs, skipped {skipped_count} duplicates.',
            'added': added_count,
            'skipped': skipped_count,
            'total_processed': len(qa_pairs)
        }), 200
        
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error uploading FAQ file: %s', error)
        return jsonify({'error': 'Failed to process uploaded file'}), 500


@faq_management_bp.route('/admin/faqs/bulk-delete', methods=['POST'])
@auth_required()
@roles_required('hr')
def bulk_delete_faqs():
    """Delete multiple FAQs"""
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': 'FAQ IDs are required'}), 400
            
        faq_ids = data['ids']
        if not isinstance(faq_ids, list) or not faq_ids:
            return jsonify({'error': 'Invalid FAQ IDs format'}), 400
        
        # Delete FAQs
        deleted_count = HRKnowledge.query.filter(HRKnowledge.id.in_(faq_ids)).delete()
        db.session.commit()
        
        # Clear knowledge cache
        hr_chatbot_service._knowledge_cache = []
        
        return jsonify({
            'message': f'Deleted {deleted_count} FAQs successfully',
            'deleted_count': deleted_count
        })
        
    except Exception as error:
        db.session.rollback()
        current_app.logger.exception('Error bulk deleting FAQs: %s', error)
        return jsonify({'error': 'Failed to delete FAQs'}), 500