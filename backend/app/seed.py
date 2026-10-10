import json
import logging
import uuid
from datetime import date, datetime, timedelta

from flask_security.utils import hash_password

from app.api.utils import set_user_roles
from app.models.models import (
    CandidateResume,
    HRKnowledge,
    JobDescription,
    LeaveRequest,
    Notification,
    ProjectAnnouncement,
    Role,
    Team,
    TeamEvent,
    User,
    db,
)

logger = logging.getLogger(__name__)


def seed_demo_data(force: bool = False) -> dict:
    """
    Seed comprehensive demo data for the HRM platform.
    Idempotent: if data already exists and force=False, returns existing counts.
    """
    existing_employees = User.query.filter(User.email.endswith('@example.com')).count()
    if existing_employees >= 8 and not force:
        logger.info("Demo data already seeded (%s demo users exist).", existing_employees)
        return {"status": "already_seeded", "users": existing_employees}

    logger.info("Seeding demo data...")

    # Ensure roles exist
    roles = {
        'hr': Role.query.filter_by(name='hr').first(),
        'manager': Role.query.filter_by(name='manager').first(),
        'employee': Role.query.filter_by(name='employee').first(),
    }
    for r_name, desc in [('hr', 'Super Administrator'), ('manager', 'Manager'), ('employee', 'Employee')]:
        if not roles[r_name]:
            r = Role(name=r_name, description=desc)
            db.session.add(r)
            roles[r_name] = r
    db.session.commit()

    # Create Teams
    team1 = Team.query.filter_by(name='Engineering').first()
    if not team1:
        team1 = Team(name='Engineering', description='Core product engineering team')
        db.session.add(team1)

    team2 = Team.query.filter_by(name='Product & Design').first()
    if not team2:
        team2 = Team(name='Product & Design', description='Product management and UX design')
        db.session.add(team2)
    db.session.commit()

    # Core demo users
    # HR
    hr_user = User.query.filter_by(email='hr@example.com').first()
    if not hr_user:
        hr_user = User(
            email='hr@example.com',
            username='hr',
            password=hash_password('hr123'),
            first_name='Helen',
            last_name='Roberts',
            job_title='HR Director',
            department='Human Resources',
            employment_role='hr',
            active=True,
            fs_uniquifier=uuid.uuid4().hex,
            hire_date=date(2022, 1, 15),
            birth_date=date(1985, 4, 12),
        )
        db.session.add(hr_user)
        db.session.flush()
        set_user_roles(hr_user, ['hr'])
    else:
        if not hr_user.fs_uniquifier:
            hr_user.fs_uniquifier = uuid.uuid4().hex
        hr_user.first_name = hr_user.first_name or 'Helen'
        hr_user.last_name = hr_user.last_name or 'Roberts'
        hr_user.job_title = hr_user.job_title or 'HR Director'
        hr_user.department = hr_user.department or 'Human Resources'

    # Manager
    mgr_user = User.query.filter_by(email='manager@example.com').first()
    if not mgr_user:
        mgr_user = User(
            email='manager@example.com',
            username='manager',
            password=hash_password('manager123'),
            first_name='Marcus',
            last_name='Vance',
            job_title='Engineering Manager',
            department='Engineering',
            employment_role='manager',
            team_id=team1.id,
            team_number='Engineering',
            active=True,
            fs_uniquifier=uuid.uuid4().hex,
            hire_date=date(2021, 6, 1),
            birth_date=date(1988, 7, 23),
        )
        db.session.add(mgr_user)
        db.session.flush()
        set_user_roles(mgr_user, ['manager'])
    else:
        if not mgr_user.fs_uniquifier:
            mgr_user.fs_uniquifier = uuid.uuid4().hex
        mgr_user.first_name = mgr_user.first_name or 'Marcus'
        mgr_user.last_name = mgr_user.last_name or 'Vance'
        mgr_user.job_title = mgr_user.job_title or 'Engineering Manager'
        mgr_user.department = mgr_user.department or 'Engineering'
        mgr_user.team_id = team1.id
        mgr_user.team_number = 'Engineering'

    team1.manager_id = mgr_user.id
    db.session.commit()

    # Primary Employee
    today = date.today()
    emp_user = User.query.filter_by(email='employee@example.com').first()
    if not emp_user:
        emp_user = User(
            email='employee@example.com',
            username='employee',
            password=hash_password('employee123'),
            first_name='Elena',
            last_name='Rostova',
            job_title='Senior Frontend Engineer',
            department='Engineering',
            employment_role='employee',
            manager_id=mgr_user.id,
            team_id=team1.id,
            team_number='Engineering',
            active=True,
            fs_uniquifier=uuid.uuid4().hex,
            hire_date=date(2023, 3, 10),
            birth_date=date(1994, today.month, max(1, (today.day + 5) % 28)),
        )
        db.session.add(emp_user)
        db.session.flush()
        set_user_roles(emp_user, ['employee'])
    else:
        if not emp_user.fs_uniquifier:
            emp_user.fs_uniquifier = uuid.uuid4().hex
        emp_user.first_name = emp_user.first_name or 'Elena'
        emp_user.last_name = emp_user.last_name or 'Rostova'
        emp_user.job_title = emp_user.job_title or 'Senior Frontend Engineer'
        emp_user.department = emp_user.department or 'Engineering'
        emp_user.manager_id = mgr_user.id
        emp_user.team_id = team1.id
        emp_user.team_number = 'Engineering'

    # Additional fictional employees
    additional_employees = [
        {
            'email': 'sarah.chen@example.com',
            'username': 'sarah_c',
            'first_name': 'Sarah',
            'last_name': 'Chen',
            'job_title': 'Backend Developer',
            'department': 'Engineering',
            'team_id': team1.id,
            'team_number': 'Engineering',
            'manager_id': mgr_user.id,
            'hire_date': date(2023, 5, 1),
            'birth_date': date(1996, today.month, max(1, (today.day + 12) % 28)),
        },
        {
            'email': 'david.miller@example.com',
            'username': 'david_m',
            'first_name': 'David',
            'last_name': 'Miller',
            'job_title': 'DevOps Engineer',
            'department': 'Engineering',
            'team_id': team1.id,
            'team_number': 'Engineering',
            'manager_id': mgr_user.id,
            'hire_date': date(2022, 11, 15),
            'birth_date': date(1991, 10, 8),
        },
        {
            'email': 'priya.sharma@example.com',
            'username': 'priya_s',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'job_title': 'QA Automation Lead',
            'department': 'Engineering',
            'team_id': team1.id,
            'team_number': 'Engineering',
            'manager_id': mgr_user.id,
            'hire_date': date(2023, 8, 20),
            'birth_date': date(1995, 2, 14),
        },
        {
            'email': 'tom.wright@example.com',
            'username': 'tom_w',
            'first_name': 'Tom',
            'last_name': 'Wright',
            'job_title': 'Product Manager',
            'department': 'Product & Design',
            'team_id': team2.id,
            'team_number': 'Product & Design',
            'manager_id': mgr_user.id,
            'hire_date': date(2022, 4, 1),
            'birth_date': date(1990, 8, 19),
        },
        {
            'email': 'maya.lin@example.com',
            'username': 'maya_l',
            'first_name': 'Maya',
            'last_name': 'Lin',
            'job_title': 'Product Designer',
            'department': 'Product & Design',
            'team_id': team2.id,
            'team_number': 'Product & Design',
            'manager_id': mgr_user.id,
            'hire_date': date(2024, 1, 10),
            'birth_date': date(1997, today.month, max(1, (today.day + 2) % 28)),
        },
        {
            'email': 'alex.patel@example.com',
            'username': 'alex_p',
            'first_name': 'Alex',
            'last_name': 'Patel',
            'job_title': 'UX Researcher',
            'department': 'Product & Design',
            'team_id': team2.id,
            'team_number': 'Product & Design',
            'manager_id': mgr_user.id,
            'hire_date': date(2024, 2, 1),
            'birth_date': date(1998, 12, 5),
        },
    ]

    for data in additional_employees:
        if not User.query.filter_by(email=data['email']).first():
            u = User(
                email=data['email'],
                username=data['username'],
                password=hash_password('demo123'),
                first_name=data['first_name'],
                last_name=data['last_name'],
                job_title=data['job_title'],
                department=data['department'],
                employment_role='employee',
                team_id=data['team_id'],
                team_number=data['team_number'],
                manager_id=data['manager_id'],
                hire_date=data['hire_date'],
                birth_date=data['birth_date'],
                active=True,
                fs_uniquifier=uuid.uuid4().hex,
            )
            db.session.add(u)
            db.session.flush()
            set_user_roles(u, ['employee'])

    db.session.commit()

    # Leave requests for employee
    if LeaveRequest.query.filter_by(user_id=emp_user.id).count() == 0:
        leaves = [
            LeaveRequest(
                user_id=emp_user.id,
                leave_type='Vacation',
                start_date=today + timedelta(days=10),
                end_date=today + timedelta(days=14),
                reason='Annual family vacation',
                status='pending',
            ),
            LeaveRequest(
                user_id=emp_user.id,
                leave_type='Sick Leave',
                start_date=today - timedelta(days=20),
                end_date=today - timedelta(days=19),
                reason='Mild flu recovery',
                status='approved',
                approver_id=mgr_user.id,
            ),
            LeaveRequest(
                user_id=emp_user.id,
                leave_type='Personal',
                start_date=today - timedelta(days=45),
                end_date=today - timedelta(days=45),
                reason='Personal errand',
                status='rejected',
                approver_id=mgr_user.id,
            ),
        ]
        for req in leaves:
            db.session.add(req)

    # Project announcements
    if ProjectAnnouncement.query.filter_by(manager_id=mgr_user.id).count() == 0:
        db.session.add(ProjectAnnouncement(
            manager_id=mgr_user.id,
            title='Q4 Platform Modernization & Performance Push',
            description='Targeting sub-100ms API response times and revamped employee experience dashboard.',
        ))

    # 5 HR FAQs in knowledge base
    if HRKnowledge.query.count() < 5:
        faqs = [
            {
                'question': 'How many annual paid leave days do full-time employees receive?',
                'answer': 'Full-time employees receive 20 days of paid annual leave per calendar year. Leave balances renew on January 1st and up to 5 unused days may roll over with manager approval.',
                'source': 'Employee Handbook 2025 - Section 4.1',
            },
            {
                'question': 'What is the company remote work policy?',
                'answer': 'We follow a flexible hybrid policy. Team members may work remotely up to 3 days per week with manager coordination. Core collaboration hours are 10:00 AM to 3:00 PM local time.',
                'source': 'Remote Work Guidelines 2025',
            },
            {
                'question': 'How do I claim health insurance or medical reimbursements?',
                'answer': 'Submit receipts through the employee benefits portal under Healthcare Claims within 30 days of the medical service. Processing typically takes 5 to 7 business days.',
                'source': 'Health & Wellness Benefit Guide',
            },
            {
                'question': 'What is the annual learning and professional development budget?',
                'answer': 'Every permanent employee is eligible for an annual professional development budget of $1,500 for approved conferences, certifications, and courses.',
                'source': 'Learning and Growth Policy',
            },
            {
                'question': 'What is the required notice period for resignation?',
                'answer': 'Standard notice period is 30 days for individual contributors and 60 days for managers, unless otherwise specified in your formal employment agreement.',
                'source': 'Offboarding & Separation Policy',
            },
        ]
        for faq in faqs:
            if not HRKnowledge.query.filter_by(question=faq['question']).first():
                db.session.add(HRKnowledge(**faq))

    # 3 Sample Resumes (fictional people, @example.com)
    if CandidateResume.query.count() < 3:
        sample_resumes = [
            {
                'name': 'Sophia Martinez',
                'email': 'sophia.martinez@example.com',
                'phone': '+1 (555) 234-5678',
                'skills': json.dumps(['Python', 'FastAPI', 'Docker', 'PostgreSQL', 'Redis', 'AWS']),
                'experience': json.dumps([
                    {'company': 'CloudScale Tech', 'role': 'Senior Backend Engineer', 'duration': '3 years', 'responsibilities': 'Designed scalable microservices with FastAPI and PostgreSQL.'},
                    {'company': 'DataStream Inc', 'role': 'Software Developer', 'duration': '2 years', 'responsibilities': 'Built REST APIs and asynchronous task processing pipelines.'},
                ]),
                'education': json.dumps([{'institution': 'State University', 'degree': 'B.S.', 'field': 'Computer Science', 'year': '2019'}]),
                'summary': 'Senior Backend Engineer with 5+ years specializing in distributed Python microservices, cloud deployments, and database optimization.',
                'total_experience': 5.0,
                'current_role': 'Senior Backend Engineer',
                'current_company': 'CloudScale Tech',
                'gender': 'Female',
                'source': 'Direct Referral',
                'status': 'Reviewing',
                'filename': 'sophia_martinez_resume.pdf',
                'resume_text': 'Sophia Martinez. Senior Backend Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL on AWS.',
            },
            {
                'name': 'Liam O Connor',
                'email': 'liam.oconnor@example.com',
                'phone': '+1 (555) 345-6789',
                'skills': json.dumps(['Vue.js', 'React', 'TypeScript', 'TailwindCSS', 'HTML5', 'CSS3']),
                'experience': json.dumps([
                    {'company': 'PixelCraft Studio', 'role': 'Frontend Lead', 'duration': '4 years', 'responsibilities': 'Architected Vue 3 component design system and improved web vitals by 40%.'},
                ]),
                'education': json.dumps([{'institution': 'Design & Arts College', 'degree': 'B.A.', 'field': 'Web & Digital Media', 'year': '2020'}]),
                'summary': 'Product-focused Frontend Engineer with 4 years building accessible, performant design systems and responsive user interfaces with Vue and TypeScript.',
                'total_experience': 4.0,
                'current_role': 'Frontend Lead',
                'current_company': 'PixelCraft Studio',
                'gender': 'Male',
                'source': 'LinkedIn',
                'status': 'Interview',
                'filename': 'liam_oconnor_resume.pdf',
                'resume_text': 'Liam O Connor. Frontend Engineer specialized in Vue.js, TypeScript, and responsive design systems with TailwindCSS.',
            },
            {
                'name': 'Amina Diallo',
                'email': 'amina.diallo@example.com',
                'phone': '+1 (555) 456-7890',
                'skills': json.dumps(['Kubernetes', 'Terraform', 'CI/CD', 'AWS', 'Python', 'Linux', 'Monitoring']),
                'experience': json.dumps([
                    {'company': 'FinCloud Services', 'role': 'DevOps Specialist', 'duration': '3.5 years', 'responsibilities': 'Automated multi-region Kubernetes clusters and CI/CD delivery pipelines.'},
                ]),
                'education': json.dumps([{'institution': 'Global Institute of Technology', 'degree': 'B.Eng.', 'field': 'Software Engineering', 'year': '2021'}]),
                'summary': 'DevOps & Site Reliability Specialist experienced with Terraform infrastructure-as-code, Kubernetes orchestration, and 99.99% uptime operations.',
                'total_experience': 3.5,
                'current_role': 'DevOps Specialist',
                'current_company': 'FinCloud Services',
                'gender': 'Female',
                'source': 'Career Page',
                'status': 'New',
                'filename': 'amina_diallo_resume.pdf',
                'resume_text': 'Amina Diallo. DevOps Engineer with expertise in Kubernetes, Terraform, AWS, and CI/CD pipeline automation.',
            },
        ]
        for r in sample_resumes:
            db.session.add(CandidateResume(**r))

    # 1 Saved Job Description
    if JobDescription.query.count() == 0:
        jd = JobDescription(
            title='Senior Full Stack Python Engineer',
            department='Engineering',
            requirements=json.dumps(['5+ years software development experience', 'Proficiency in Python and modern frontend frameworks', 'Experience with cloud infrastructure (AWS/GCP)']),
            skills_required=json.dumps(['Python', 'Flask', 'Vue.js', 'PostgreSQL', 'Docker']),
            experience_required=5.0,
            description='We are seeking an experienced Senior Full Stack Engineer to lead architecture across our Python Flask backend and modern Vue.js frontend.',
        )
        db.session.add(jd)

    # Notifications
    if Notification.query.filter_by(user_id=emp_user.id).count() == 0:
        notifs = [
            Notification(
                user_id=emp_user.id,
                category='workflow',
                title='Quarterly Performance Reviews Open',
                message='Self-evaluations for Q3 are now open. Please complete yours by the 15th.',
                is_read=False,
            ),
            Notification(
                user_id=emp_user.id,
                category='announcement',
                title='All-Hands Team Meeting',
                message='Monthly team sync is scheduled for this Thursday at 2:00 PM in Main Conf Room & Zoom.',
                is_read=False,
            ),
        ]
        for n in notifs:
            db.session.add(n)

    # Team Events
    if TeamEvent.query.count() == 0:
        db.session.add(TeamEvent(
            title='Sprint 24 Planning & Architecture Review',
            description='Bi-weekly sprint planning and roadmap alignment.',
            location='Engineering Room & Zoom',
            start_datetime=datetime.utcnow() + timedelta(days=2, hours=3),
            end_datetime=datetime.utcnow() + timedelta(days=2, hours=4),
            team_number='Engineering',
            created_by_id=mgr_user.id,
        ))

    db.session.commit()
    logger.info("Demo data seeding completed successfully.")
    return {"status": "seeded", "users": User.query.count()}


def reset_demo_data() -> dict:
    """Reset and re-seed all demo records."""
    logger.info("Resetting demo data...")
    # Clean up non-core data
    LeaveRequest.query.delete()
    Notification.query.delete()
    ProjectAnnouncement.query.delete()
    TeamEvent.query.delete()
    CandidateResume.query.delete()
    JobDescription.query.delete()
    HRKnowledge.query.delete()
    # Delete non-admin demo users
    User.query.filter(~User.email.in_(['hr@example.com', 'manager@example.com', 'employee@example.com'])).delete()
    db.session.commit()
    return seed_demo_data(force=True)
