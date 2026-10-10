from datetime import date
from flask_security.models import fsqla_v3 as fsqla
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Set up Flask-Security models
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    """Role model for user permissions"""
    __tablename__ = 'role'

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, fsqla.FsUserMixin):
    """User model with authentication support"""
    __tablename__ = 'user'
    # Additional profile fields
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    organization = db.Column(db.String(150), nullable=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    department = db.Column(db.String(120), nullable=True)
    manager_id = db.Column(db.Integer, nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team_number = db.Column(db.String(50), nullable=True)
    employment_role = db.Column(db.String(20), nullable=False, default='employee')
    hire_date = db.Column(db.Date, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    resume_file = db.Column(db.LargeBinary, nullable=True)
    resume_blob = db.Column(db.LargeBinary, nullable=True)
    skills_json = db.Column(db.Text, nullable=True)
    education_json = db.Column(db.Text, nullable=True)
    experience_json = db.Column(db.Text, nullable=True)
    chat_history = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    # association objects for skills (stores proficiency and years_experience)
    user_skills = db.relationship(
        'UserSkill',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    leave_requests = db.relationship(
        'LeaveRequest',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='LeaveRequest.user_id',
        overlaps='approved_leaves'
    )
    approved_leaves = db.relationship(
        'LeaveRequest',
        back_populates='approver',
        lazy='dynamic',
        foreign_keys='LeaveRequest.approver_id',
        overlaps='leave_requests'
    )
    team_events_created = db.relationship(
        'TeamEvent',
        back_populates='created_by',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamEvent.created_by_id'
    )
    hr_questions_asked = db.relationship(
        'HRQuestionLog',
        back_populates='requester',
        lazy='dynamic',
        foreign_keys='HRQuestionLog.user_id'
    )
    hr_questions_assigned = db.relationship(
        'HRQuestionLog',
        back_populates='assignee',
        lazy='dynamic',
        foreign_keys='HRQuestionLog.manager_id'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'roles': [role.name for role in self.roles],
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'address': self.address,
            'organization': self.organization,
            'employee_id': self.employee_id,
            'job_title': self.job_title,
            'department': self.department,
            'manager_id': self.manager_id,
            'team_number': self.team_number,
            'employment_role': self.employment_role,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'has_resume': bool(self.resume_file),
            'has_resume_blob': bool(self.resume_blob),
            'skills_json': self.skills_json,
            'education_json': self.education_json,
            'experience_json': self.experience_json,
            'chat_history': self.chat_history,
            'skills_list': [us.skill.name for us in self.user_skills],
            'is_verified': self.is_verified,
            'created_at': self.create_datetime.isoformat() if self.create_datetime else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def has_role(self, role_name):
        """Check if user has specific role"""
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        """Check if user is manager or hr"""
        return any(role.name in ['manager', 'hr'] for role in self.roles)

    def is_super_admin(self):
        """Check if user is hr"""
        return self.has_role('hr')


class Admin(db.Model):
    """User model with authentication support"""
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    organization = db.Column(db.String(150), nullable=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    department = db.Column(db.String(120), nullable=True)
    manager_id = db.Column(db.Integer, nullable=True)
    team_number = db.Column(db.String(50), nullable=True)
    employment_role = db.Column(db.String(20), nullable=False, default='employee')
    hire_date = db.Column(db.Date, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    resume_file = db.Column(db.LargeBinary, nullable=True)
    resume_blob = db.Column(db.LargeBinary, nullable=True)
    skills_json = db.Column(db.Text, nullable=True)
    education_json = db.Column(db.Text, nullable=True)
    experience_json = db.Column(db.Text, nullable=True)
    chat_history = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    def __repr__(self):
        return f'<Admin {getattr(self, "username", None)}>'

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': getattr(self, 'username', None),
            'email': getattr(self, 'email', None),
            'active': getattr(self, 'active', None),
            'roles': [role.name for role in getattr(self, 'roles', [])],
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'address': self.address,
            'organization': self.organization,
            'employee_id': self.employee_id,
            'job_title': self.job_title,
            'department': self.department,
            'manager_id': self.manager_id,
            'team_number': self.team_number,
            'employment_role': self.employment_role,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'has_resume': bool(self.resume_file),
            'has_resume_blob': bool(self.resume_blob),
            'skills_json': self.skills_json,
            'education_json': self.education_json,
            'experience_json': self.experience_json,
            'chat_history': self.chat_history,
            'is_verified': self.is_verified,
            'created_at': getattr(self, 'create_datetime', None).isoformat() if getattr(self, 'create_datetime', None) else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def has_role(self, role_name):
        """Check if user has specific role"""
        return any(role.name == role_name for role in getattr(self, 'roles', []))

    def is_admin(self):
        """Check if user is manager or hr"""
        return any(role.name in ['manager', 'hr'] for role in getattr(self, 'roles', []))

    def is_super_admin(self):
        """Check if user is hr"""
        return self.has_role('hr')

class SuperAdmin(db.Model):
    """User model with authentication support"""
    # keep a conventional lowercase table name
    __tablename__ = 'super_admin'
    id = db.Column(db.Integer, primary_key=True)
    # Additional profile fields
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    organization = db.Column(db.String(150), nullable=True)
    resume_file = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<SuperAdmin {getattr(self, "username", None)}>'

    def to_dict(self):
        """Convert SuperAdmin object to dictionary"""
        return {
            'id': self.id,
            'username': getattr(self, 'username', None),
            'email': getattr(self, 'email', None),
            'roles': [role.name for role in getattr(self, 'roles', [])],
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'organization': self.organization,
            'has_resume': bool(self.resume_file),
        }

    def has_role(self, role_name):
        """Check if user has specific role"""
        return any(role.name == role_name for role in getattr(self, 'roles', []))

    def is_admin(self):
        """Check if user is manager or hr"""
        return any(role.name in ['manager', 'hr'] for role in getattr(self, 'roles', []))

    def is_super_admin(self):
        """Check if user is hr"""
        return self.has_role('hr')


class UserSkill(db.Model):
    __tablename__ = 'user_skill'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)
    proficiency = db.Column(db.Integer, nullable=True)
    years_experience = db.Column(db.Float, nullable=True)

    # relationships
    user = db.relationship('User', back_populates='user_skills')
    skill = db.relationship('Skill', back_populates='skill_users')


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    skill_users = db.relationship(
        'UserSkill',
        back_populates='skill',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Skill {self.name}>"


class Document(db.Model):
    """Store metadata for uploaded documents (resumes, contracts, etc.).
    Store files externally (S3/local) and keep metadata here.
    """
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    doc_type = db.Column(db.String(50), nullable=False)  # resume, offer, contract
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(1024), nullable=True)
    mime_type = db.Column(db.String(120), nullable=True)
    size = db.Column(db.Integer, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref=db.backref('documents', lazy='dynamic'))

    def __repr__(self):
        return f"<Document {self.filename} for user={self.user_id}>"


class Conversation(db.Model):
    """HR chatbot conversation session"""
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    started_at = db.Column(db.DateTime, default=db.func.now())
    ended_at = db.Column(db.DateTime, nullable=True)
    # 'metadata' is a reserved attribute name in SQLAlchemy's Declarative API.
    # Use a different Python attribute name but keep the DB column name as 'metadata'
    metadata_json = db.Column('metadata', db.Text, nullable=True)  # store JSON as text

    user = db.relationship('User', backref=db.backref('conversations', lazy='dynamic'))
    hr_questions = db.relationship(
        'HRQuestionLog',
        back_populates='conversation',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<Conversation {self.id} user={self.user_id}>"


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sender = db.Column(db.String(30), nullable=False)  # 'user' | 'assistant' | 'system' | 'admin'
    content = db.Column(db.Text, nullable=False)
    # Avoid using the reserved attribute name 'metadata' on the mapped class.
    metadata_json = db.Column('metadata', db.Text, nullable=True)  # model, score, etc.
    created_at = db.Column(db.DateTime, default=db.func.now())
    index = db.Column(db.Integer, nullable=True)

    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy='dynamic', order_by='Message.created_at'))
    user = db.relationship('User', backref=db.backref('messages', lazy='dynamic'))

    def __repr__(self):
        return f"<Message {self.id} conv={self.conversation_id} sender={self.sender}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    object_type = db.Column(db.String(120), nullable=True)
    object_id = db.Column(db.String(120), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON/text
    created_at = db.Column(db.DateTime, default=db.func.now())

    actor = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f"<AuditLog {self.id} actor={self.actor_id} action={self.action}>"


class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    category = db.Column(db.String(80), nullable=False, default='general')
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=True)
    metadata_json = db.Column('metadata', db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    read_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return f"<Notification {self.id} category={self.category} user={self.user_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'title': self.title,
            'message': self.message,
            'metadata': self.metadata_json,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }


class ProjectAnnouncement(db.Model):
    __tablename__ = 'project_announcement'
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    manager = db.relationship(
        'User',
        backref=db.backref('project_announcement_entry', uselist=False, cascade='all, delete-orphan'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'manager_id': self.manager_id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class HRKnowledge(db.Model):
    __tablename__ = 'hr_knowledge'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(255), nullable=True)
    embedding = db.Column(db.Text, nullable=True)  # store JSON encoded vector
    metadata_json = db.Column('metadata', db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'source': self.source,
            'metadata': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class HRQuestionLog(db.Model):
    __tablename__ = 'hr_question_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=True)
    question = db.Column(db.Text, nullable=False)
    normalized_question = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, auto_answered, resolved
    source = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    details = db.Column(db.Text, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    requester = db.relationship('User', foreign_keys=[user_id], back_populates='hr_questions_asked')
    assignee = db.relationship('User', foreign_keys=[manager_id], back_populates='hr_questions_assigned')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    conversation = db.relationship('Conversation', back_populates='hr_questions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manager_id': self.manager_id,
            'conversation_id': self.conversation_id,
            'question': self.question,
            'answer': self.answer,
            'status': self.status,
            'source': self.source,
            'confidence': self.confidence,
            'details': self.details,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # reset, confirm, 2fa
    expires_at = db.Column(db.DateTime, nullable=True)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref=db.backref('tokens', lazy='dynamic'))

    def __repr__(self):
        return f"<Token {self.purpose} user={self.user_id} used={self.used}>"


class Education(db.Model):
    __tablename__ = 'education'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution = db.Column(db.String(255), nullable=False)
    degree = db.Column(db.String(255), nullable=True)
    field_of_study = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('educations', lazy='dynamic'))

    def __repr__(self):
        return f"<Education {self.institution} user={self.user_id}>"


class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('experiences', lazy='dynamic'))

    def __repr__(self):
        return f"<Experience {self.company} user={self.user_id}>"


class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    leave_type = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    decision_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='leave_requests',
        overlaps='approved_leaves'
    )
    approver = db.relationship(
        'User',
        foreign_keys=[approver_id],
        back_populates='approved_leaves',
        overlaps='leave_requests'
    )

    def __repr__(self):
        return f"<LeaveRequest {self.id} user={self.user_id} status={self.status}>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'approver_id': self.approver_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'reason': self.reason,
            'status': self.status,
            'decision_reason': self.decision_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TeamEvent(db.Model):
    __tablename__ = 'team_event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=True)
    team_number = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    created_by = db.relationship(
        'User',
        back_populates='team_events_created',
        foreign_keys=[created_by_id]
    )

    def __repr__(self):
        return f"<TeamEvent {self.title} start={self.start_datetime}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'team_number': self.team_number,
            'location': self.location,
            'created_by_id': self.created_by_id
        }


class CandidateResume(db.Model):
    """Model to store extracted resume data from candidates"""
    __tablename__ = 'candidate_resume'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON array
    experience = db.Column(db.Text, nullable=True)  # JSON array
    education = db.Column(db.Text, nullable=True)  # JSON array
    summary = db.Column(db.Text, nullable=True)
    total_experience = db.Column(db.Float, nullable=True)
    current_role = db.Column(db.String(200), nullable=True)
    current_company = db.Column(db.String(200), nullable=True)
    source = db.Column(db.String(100), nullable=True)  # LinkedIn, Indeed, Referral, etc.
    status = db.Column(db.String(50), nullable=True)  # Shortlisted, Interviewed, Rejected, etc.
    uploaded_at = db.Column(db.DateTime, default=db.func.now())
    gender = db.Column(db.String(20), nullable=True)  # For analytics
    resume_text = db.Column(db.Text, nullable=True)  # Full text content

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'filename': self.filename,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'skills': json.loads(self.skills) if self.skills else [],
            'experience': json.loads(self.experience) if self.experience else [],
            'education': json.loads(self.education) if self.education else [],
            'summary': self.summary,
            'total_experience': self.total_experience,
            'current_role': self.current_role,
            'current_company': self.current_company,
            'source': self.source,
            'status': self.status,
            'gender': self.gender,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __repr__(self):
        return f'<CandidateResume {self.name} - {self.email}>'


class JobDescription(db.Model):
    """Model to store job descriptions for matching"""
    __tablename__ = 'job_description'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), nullable=True)
    requirements = db.Column(db.Text, nullable=True)  # JSON array
    skills_required = db.Column(db.Text, nullable=True)  # JSON array
    experience_required = db.Column(db.Float, nullable=True)
    salary_range = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'title': self.title,
            'department': self.department,
            'requirements': json.loads(self.requirements) if self.requirements else [],
            'skills_required': json.loads(self.skills_required) if self.skills_required else [],
            'experience_required': self.experience_required,
            'salary_range': self.salary_range,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __repr__(self):
        return f'<JobDescription {self.title}>'


class ResumeMatch(db.Model):
    """Model to store resume matching results"""
    __tablename__ = 'resume_match'
    id = db.Column(db.Integer, primary_key=True)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    candidate_resume_id = db.Column(db.Integer, db.ForeignKey('candidate_resume.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    reasoning = db.Column(db.Text, nullable=True)
    matched_at = db.Column(db.DateTime, default=db.func.now())

    job_description = db.relationship('JobDescription', backref='matches')
    candidate_resume = db.relationship('CandidateResume', backref='matches')

    def to_dict(self):
        return {
            'id': self.id,
            'job_description_id': self.job_description_id,
            'candidate_resume_id': self.candidate_resume_id,
            'candidate': self.candidate_resume.to_dict() if self.candidate_resume else None,
            'match_score': self.match_score,
            'reasoning': self.reasoning,
            'matched_at': self.matched_at.isoformat() if self.matched_at else None
        }

    def __repr__(self):
        return f'<ResumeMatch {self.candidate_resume_id} -> {self.job_description_id}: {self.match_score}%>'


class Team(db.Model):
    """Team model for grouping users"""
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_teams_list')
    members = db.relationship('User', backref='team_membership', foreign_keys='User.team_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'manager_name': f"{self.manager.first_name} {self.manager.last_name}" if self.manager else None,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# -----------------------------------------------------------------------------
# Offboarding and Letters
# -----------------------------------------------------------------------------

class OffboardingTask(db.Model):
    """
    Tasks that need to be completed when an employee exits the organisation.

    Each task is associated with a departing user and is assigned to a role or
    department (e.g. admin, IT, HR). Offboarding tasks track their status so
    managers and administrators can monitor progress and mark them complete.
    """

    __tablename__ = 'offboarding_task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_role = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), nullable=False, default='pending')
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('offboarding_tasks', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assignee_role': self.assignee_role,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class LetterTemplate(db.Model):
    """
    Reusable templates for generating official letters such as offer letters,
    experience certificates and relieving letters. Templates contain placeholders
    that will be interpolated with user data when generating a letter.
    """

    __tablename__ = 'letter_template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class GeneratedLetter(db.Model):
    """
    Letters that have been generated for employees from templates. The
    generated content is stored immutably so that it can be downloaded or
    audited later.
    """

    __tablename__ = 'generated_letter'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('letter_template.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship('User', backref=db.backref('generated_letters', lazy='dynamic'))
    template = db.relationship('LetterTemplate', backref=db.backref('generated_letters', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'template': self.template.to_dict() if self.template else None,
        }


class AnonymousFeedback(db.Model):
    """Model to store anonymous employee feedback"""
    __tablename__ = 'anonymous_feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional, for tracking but anonymous display
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., 'Work Environment', 'Management', 'Benefits', 'Culture', 'Other'
    feedback_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 rating
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('feedbacks', lazy='dynamic'))

    def to_dict(self, anonymous=True):
        return {
            'id': self.id,
            'user_id': self.user_id if not anonymous else None,
            'title': self.title,
            'category': self.category,
            'feedback_text': self.feedback_text,
            'rating': self.rating,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<AnonymousFeedback {self.id}>'


class AIUsage(db.Model):
    __tablename__ = 'ai_usage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    day = db.Column(db.Date, nullable=False, default=date.today)
    count = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship('User', backref=db.backref('ai_usages', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'day': self.day.isoformat() if self.day else None,
            'count': self.count,
        }

