# app/__init__.py
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore

from app.auth import create_default_roles_and_admin
from app.config.config import Configuration
from app.extensions import init_extensions
from app.models.models import Role, User, db
from app.services.ai import AIRateLimitError, AIUnavailableError
from sqlalchemy import text

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
    origins = app.config.get('CORS_ORIGINS') or [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
    ]
    CORS(
        app,
        resources={r"/api/*": {"origins": origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Authentication-Token"],
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    )

    # Register blueprints
    register_blueprints(app)

    @app.errorhandler(AIUnavailableError)
    def handle_ai_unavailable(e):
        return jsonify({"error": "AI service is not available right now"}), 503

    @app.errorhandler(AIRateLimitError)
    def handle_ai_rate_limit(e):
        return jsonify({"error": str(e) or "Daily AI limit reached for this demo account. Try again tomorrow."}), 429

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"error": getattr(e, "description", "Bad Request")}), 400

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({"error": getattr(e, "description", "Unauthorized")}), 401

    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({"error": getattr(e, "description", "Forbidden")}), 403

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"error": getattr(e, "description", "Resource not found")}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"error": getattr(e, "description", "Method Not Allowed")}), 405

    @app.errorhandler(500)
    def handle_server_error(e):
        app.logger.exception("Internal server error: %s", e)
        return jsonify({"error": "Internal server error"}), 500

    # Setup scheduler to run offboarding reminders daily at 09:00
    enable_scheduler = str(os.getenv('ENABLE_SCHEDULER', 'true')).lower() in ('1', 'true', 'yes')
    is_reloader_main = os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug
    if enable_scheduler and is_reloader_main:
        try:
            scheduler = BackgroundScheduler()
            from app.services.offboarding import run_reminders

            # Cron: run every day at 9:00
            scheduler.add_job(run_reminders, CronTrigger(hour=9, minute=0))

            demo_mode = str(os.getenv('DEMO_MODE', 'false')).lower() in ('1', 'true', 'yes')
            if demo_mode:
                from app.seed import reset_demo_data

                def _scheduled_demo_reset():
                    with app.app_context():
                        reset_demo_data()

                scheduler.add_job(_scheduled_demo_reset, CronTrigger(hour=3, minute=0))

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
        except Exception as exc:
            app.logger.warning('APScheduler failed to start: %s', exc)

    @app.cli.command('seed-demo')
    def seed_demo_cmd():
        """Seed demo data into the database."""
        import click
        from app.seed import seed_demo_data
        res = seed_demo_data(force=True)
        click.echo(f"Demo data seeded: {res}")

    @app.cli.command('reset-demo')
    def reset_demo_cmd():
        """Reset and re-seed demo data."""
        import click
        from app.seed import reset_demo_data
        res = reset_demo_data()
        click.echo(f"Demo data reset: {res}")

    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok"}), 200
        except Exception as exc:
            app.logger.error("Health check failed: %s", exc)
            return jsonify({"status": "error", "message": "Database unavailable"}), 503

    @app.route('/api/cron/daily', methods=['POST'])
    def cron_daily():
        secret = os.getenv('CRON_SECRET')
        if not secret:
            return jsonify({"error": "CRON_SECRET not configured"}), 503
        incoming_secret = request.headers.get('X-Cron-Secret')
        if not incoming_secret or incoming_secret != secret:
            return jsonify({"error": "Unauthorized"}), 401

        results = {}
        try:
            from app.services.offboarding import run_reminders
            run_reminders()
            results['reminders'] = 'ok'
        except Exception as exc:
            app.logger.error("Cron offboarding reminders failed: %s", exc)
            results['reminders'] = str(exc)

        demo_mode = str(os.getenv('DEMO_MODE', 'false')).lower() in ('1', 'true', 'yes')
        if demo_mode:
            try:
                from app.seed import reset_demo_data
                reset_demo_data()
                results['demo_reset'] = 'ok'
            except Exception as exc:
                app.logger.error("Cron demo reset failed: %s", exc)
                results['demo_reset'] = str(exc)

        return jsonify({"status": "completed", "results": results}), 200

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
    app.config['CORS_ORIGINS'] = cfg.get('cors.origins')
    app.config['DEBUG'] = cfg.get('env.debug', False)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
        demo_mode = str(os.getenv('DEMO_MODE', 'false')).lower() in ('1', 'true', 'yes')
        if demo_mode:
            try:
                from app.seed import seed_demo_data
                seed_demo_data(force=False)
            except Exception as exc:
                app.logger.warning('Auto-seeding demo data failed: %s', exc)


def register_blueprints(app):
    """Register all application blueprints"""
    from app.api.admin import admin_bp
    from app.api.admin_portal import admin_portal_bp
    from app.api.authentication import auth_bp
    from app.api.birthdays import birthday_tracker_bp
    from app.api.employee_dashboard import employee_dashboard_bp
    from app.api.faq_management import faq_management_bp
    from app.api.feedback import feedback_bp
    from app.api.genai.career_path import career_bp
    from app.api.genai.chatbot import hr_chatbot_bp
    from app.api.genai.jd_maker import jd_bp
    from app.api.hr import hr_bp
    from app.api.hr_signup import hr_signup_bp
    from app.api.leave import leave_bp
    from app.api.letters import letters_bp
    from app.api.manager_dashboard import manager_dashboard_bp
    from app.api.notifications import notification_bp

    # Additional custom blueprints
    from app.api.offboarding import offboarding_bp
    from app.api.super_admin_users import super_admin_users_bp
    from app.api.teams import teams_bp

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

