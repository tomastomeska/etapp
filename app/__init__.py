"""
European Transport CZ s.r.o. - Firemní Aplikační Server
Hlavní inicializační modul Flask aplikace
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from config import config

# Inicializace rozšíření
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO()

def create_app(config_name='default'):
    """Factory funkce pro vytvoření Flask aplikace."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializace rozšíření s aplikací
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Konfigurace login manageru
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Pro přístup k této stránce se prosím přihlaste.'
    login_manager.login_message_category = 'info'
    
    # Registrace blueprintů
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Vytvoření upload složky
    import os
    upload_folder = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    """Načtení uživatele pro Flask-Login."""
    from app.models import User
    return User.query.get(int(user_id))