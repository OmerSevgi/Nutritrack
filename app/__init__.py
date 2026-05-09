from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from app import models  # Modelleri import et

    from app.routes.auth import auth_bp
    from app.routes.nutrition import nutrition_bp
    from app.routes.ai import ai_bp
    from app.routes.fitness import fitness_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(nutrition_bp, url_prefix='/api/nutrition')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(fitness_bp, url_prefix='/api/fitness')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from flask import render_template

    @app.route('/')
    def index():
        return render_template('landing.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('index.html')

    @app.route('/auth')
    def auth():
        return render_template('auth.html')

    @app.route('/settings')
    def settings():
        return render_template('settings.html')

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        print(traceback.format_exc())
        return {"error": "Internal server error"}, 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}, 500

    return app
