from flask import Flask, app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()   # <-- c'est cette ligne qui manquait

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'   # redirige ici si @login_required échoue

    # Import des modules contenant les modèles et les blueprints
    # (doit être fait après l'initialisation pour éviter les imports circulaires)
    from app import models
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.profile import profile_bp
    app.register_blueprint(profile_bp)

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    return app