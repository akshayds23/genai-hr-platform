# app/__init__.py
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from flask import Flask, render_template_string, url_for

from app.config.config import Configuration
from app.models.models import db, User, Role
from app.extensions import init_extensions
from app.auth import create_default_roles_and_admin
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Initialize extensions
security = Security()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    configure_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup security
    setup_security(app)
    # Initialize cors for apis
    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
            "http://localhost",
            "http://127.0.0.1"
        ]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Authentication-Token"],
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"]
    )

    # Register blueprints
    register_blueprints(app)

    # Setup scheduler to run offboarding reminders daily at 09:00
    try:
        scheduler = BackgroundScheduler()
        from app.services.offboarding import run_reminders

        # Cron: run every day at 9:00
        scheduler.add_job(run_reminders, CronTrigger(hour=9, minute=0))
        scheduler.start()
        # store on app for later inspection/shutdown
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['apscheduler'] = scheduler
        # ensure clean shutdown on process exit
        try:
            import atexit
            atexit.register(lambda: scheduler.shutdown(wait=False))
        except Exception:
            pass
    except Exception:
        # If scheduler fails to initialize, log to stdout and continue
        print('Warning: APScheduler failed to start. Reminders endpoint still available.')

    @app.route('/apidocs')
    def apidocs():
        return render_template_string("""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>HRM API Docs</title>
          <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
        </head>
        <body>
          <div id="swagger-ui"></div>
          <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
          <script>
          window.onload = function() {
            SwaggerUIBundle({
              url: "{{ url_for('static', filename='openapi.yaml') }}",
              dom_id: '#swagger-ui'
            });
          };
          </script>
        </body>
        </html>
        """)
    return app


def configure_app(app):
    """Configure Flask app with settings"""
    cfg = Configuration()
    
    # Core Flask settings
    app.config['SECRET_KEY'] = cfg.ENV.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = cfg.DATABASE.URL or 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Security settings
    app.config['SECURITY_PASSWORD_SALT'] = cfg.get('security.password_salt')
    app.config['SECURITY_REGISTERABLE'] = cfg.get('security.registerable')
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = cfg.get('security.send_register_email')
    app.config['SECURITY_USERNAME_ENABLE'] = cfg.get('security.username_enable')
    app.config['SECURITY_USERNAME_REQUIRED'] = cfg.get('security.username_required')
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
    app.config['SECURITY_CSRF_PROTECT'] = False
    
    # Cookie security settings
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def setup_security(app):
    """Setup Flask-Security with user datastore"""
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    
    # Create tables and default data
    with app.app_context():
        db.create_all()
        cfg = Configuration()
        create_default_roles_and_admin(user_datastore, cfg)


def register_blueprints(app):
    """Register all application blueprints"""
    from app.api.authentication import auth_bp
    from app.api.admin import admin_bp
    from app.api.admin_portal import admin_portal_bp
    from app.api.B_leave import leave_bp
    from app.api.B_employee_dashboard import employee_dashboard_bp
    from app.api.B_manager_dashboard import manager_dashboard_bp
    from app.api.B_Hr import hr_bp
    from app.api.B_birthday_tracker import birthday_tracker_bp
    from app.api.B_notification import notification_bp
    from app.api.genai.B_HRchatbot import hr_chatbot_bp
    from app.api.genai.B_jdmaker import jd_bp
    from app.api.genai.B_careerpath import career_bp
    from app.api.B_feedback import feedback_bp

    # Additional custom blueprints
    from app.api.offboarding import offboarding_bp
    from app.api.letters import letters_bp
    from app.api.hr_signup import hr_signup_bp
    from app.api.super_admin_users import super_admin_users_bp
    from app.api.teams import teams_bp
    from app.api.faq_management import faq_management_bp

    app.register_blueprint(auth_bp,url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(admin_portal_bp, url_prefix='/api')
    app.register_blueprint(leave_bp, url_prefix='/api')
    app.register_blueprint(employee_dashboard_bp, url_prefix='/api')
    app.register_blueprint(manager_dashboard_bp, url_prefix='/api')
    app.register_blueprint(hr_bp, url_prefix='/api')
    app.register_blueprint(birthday_tracker_bp, url_prefix='/api')
    app.register_blueprint(notification_bp, url_prefix='/api')
    app.register_blueprint(hr_chatbot_bp, url_prefix='/api')
    app.register_blueprint(jd_bp, url_prefix='/api')
    app.register_blueprint(career_bp, url_prefix='/api')
    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(offboarding_bp, url_prefix='/api')
    app.register_blueprint(letters_bp, url_prefix='/api')
    app.register_blueprint(hr_signup_bp, url_prefix='/')
    app.register_blueprint(super_admin_users_bp, url_prefix='/api')
    app.register_blueprint(teams_bp, url_prefix='/api')
    app.register_blueprint(faq_management_bp, url_prefix='/api')

