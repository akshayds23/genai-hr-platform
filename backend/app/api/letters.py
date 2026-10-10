"""
Endpoints for managing letter templates and generating letters for employees.

Only super admin (HR) users may create, update or delete templates. All
authenticated users can request a letter be generated for themselves using
a predefined template.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request
from flask_security import auth_required, current_user, roles_required

from app.models.models import GeneratedLetter, LetterTemplate, OffboardingTask, User, db

letters_bp = Blueprint('letters', __name__)


def _render_template(template: LetterTemplate, user: User, extra_context: dict[str, Any] | None = None) -> str:

    exit_date = ''
    try:
        exit_task = (
            user.offboarding_tasks
            .order_by(OffboardingTask.due_date.desc())
            .first()
        )
    except Exception:
        exit_task = None
    if exit_task and exit_task.due_date:
        exit_date = exit_task.due_date.isoformat()

    context = {
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'full_name': ' '.join(part for part in (user.first_name, user.last_name) if part) or user.username or user.email,
        'job_title': user.job_title or '',
        'department': user.department or '',
        'employee_id': user.employee_id or '',
        'team_number': user.team_number or '',
        'hire_date': user.hire_date.isoformat() if user.hire_date else '',
        'exit_date': exit_date,
        'today': datetime.utcnow().date().isoformat(),
    }
    if extra_context:
        context.update(extra_context)

    if 'company_name' not in context or not context.get('company_name'):
        cfg_name = None
        try:
            # current_app may have an app-level name configured
            cfg_name = current_app.config.get('APP_NAME')
        except Exception:
            cfg_name = None
        context.setdefault('company_name', cfg_name or '')

    # Ensure other HR fields exist so format doesn't fail
    context.setdefault('hr_representative_name', '')
    context.setdefault('hr_title', '')
    context.setdefault('last_day', '')

    # Use format_map with a defaultdict to return empty string for any missing keys
    safe_map = defaultdict(str, context)
    try:
        return template.content.format_map(safe_map)
    except Exception as exc:
        # Any other formatting error -> surface as a ValueError for the API
        raise ValueError(f'Failed to render template: {exc!s}')


@letters_bp.route('/letters/templates', methods=['GET'])
@auth_required()
def list_templates():
    """Return a list of all letter templates."""
    templates = [tpl.to_dict() for tpl in LetterTemplate.query.order_by(LetterTemplate.name.asc()).all()]
    return jsonify({'templates': templates})


@letters_bp.route('/letters/templates', methods=['POST'])
@auth_required()
@roles_required('hr')
def create_template():
    """
    Create a new letter template. Only hr users may create templates.
    Request body must include 'name' and 'content'. 'description' is optional.
    """
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    content = (data.get('content') or '').strip()
    if not name or not content:
        return jsonify({'error': 'Both name and content are required'}), 400
    if LetterTemplate.query.filter(LetterTemplate.name.ilike(name)).first():
        return jsonify({'error': 'A template with that name already exists'}), 400
    template = LetterTemplate(
        name=name,
        description=(data.get('description') or '').strip() or None,
        content=content,
    )
    db.session.add(template)
    db.session.commit()
    return jsonify({'message': 'Template created successfully', 'template': template.to_dict()}), 200


@letters_bp.route('/letters/templates/<int:template_id>', methods=['PUT', 'PATCH'])
@auth_required()
@roles_required('hr')
def update_template(template_id: int):
    """Update an existing letter template. Only hr users may update."""
    template = LetterTemplate.query.get_or_404(template_id)
    data = request.get_json() or {}
    name = data.get('name')
    content = data.get('content')
    description = data.get('description')
    if name:
        cleaned = name.strip()
        if cleaned and cleaned.lower() != template.name.lower():
            if LetterTemplate.query.filter(LetterTemplate.name.ilike(cleaned)).first():
                return jsonify({'error': 'A template with that name already exists'}), 400
            template.name = cleaned
    if content is not None:
        cleaned_content = content.strip()
        if cleaned_content:
            template.content = cleaned_content
    if description is not None:
        template.description = description.strip() or None
    db.session.add(template)
    db.session.commit()
    return jsonify({'message': 'Template updated', 'template': template.to_dict()})


@letters_bp.route('/letters/templates/<int:template_id>', methods=['DELETE'])
@auth_required()
@roles_required('hr')
def delete_template(template_id: int):
    """Delete an existing letter template."""
    template = LetterTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return jsonify({'message': 'Template deleted'})


@letters_bp.route('/letters/generate', methods=['POST'])
@auth_required()
def generate_letter():
    """
    Generate a letter for a user from a template and save it to the database.

    Request body parameters:
      - template_id (required): ID of the template to use
      - user_id (optional): target employee. Defaults to current user
      - variables (optional): JSON object of additional placeholder values

    Returns the generated letter content and metadata.
    """
    data = request.get_json() or {}
    template_id = data.get('template_id')
    if not template_id:
        return jsonify({'error': 'template_id is required'}), 400
    try:
        tpl_id = int(template_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'template_id must be an integer'}), 400
    target_user_id = data.get('user_id')
    if target_user_id:
        try:
            uid = int(target_user_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'user_id must be an integer'}), 400
        # Only admins and super admins can generate letters for other users
        if not current_user.is_admin() and current_user.id != uid:
            return jsonify({'error': 'Unauthorized to generate letters for other users'}), 403
        user = User.query.get_or_404(uid)
    else:
        user = current_user

    template = LetterTemplate.query.get_or_404(tpl_id)

    variables = data.get('variables') or {}
    if not isinstance(variables, dict):
        return jsonify({'error': 'variables must be a JSON object'}), 400
    try:
        content = _render_template(template, user, variables)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    letter = GeneratedLetter(
        user_id=user.id,
        template_id=template.id,
        content=content,
    )
    db.session.add(letter)
    db.session.commit()
    return jsonify({'message': 'Letter generated', 'letter': letter.to_dict()}), 200


@letters_bp.route('/letters/<int:letter_id>/download', methods=['GET'])
@auth_required()
def download_letter(letter_id: int):
    """
    Download a generated letter as plain text. Only the subject user or
    administrators may download a letter.
    """
    letter = GeneratedLetter.query.get_or_404(letter_id)
    if not current_user.is_admin() and current_user.id != letter.user_id:
        return jsonify({'error': 'Unauthorized to download this letter'}), 403
    # Create a simple text response
    filename = f"letter_{letter.id}.txt"
    return Response(
        letter.content,
        mimetype='text/plain',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )
