import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
mail = Mail()
csrf = CSRFProtect()
app = Flask(__name__)

# Configure secret key for session management
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key"

# Configure security settings
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for HTTP in development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Stylish Cuts', os.environ.get('MAIL_USERNAME'))

# Initialize extensions
db.init_app(app)
mail.init_app(app)
csrf.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models and create tables
with app.app_context():
    import models  # noqa: F401
    import routes  # noqa: F401
    
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
        
        # Create admin user if it doesn't exist
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(email='admin@stylishcuts.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@stylishcuts.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Admin user created successfully")

        # Create default services if none exist
        from models import Service
        if Service.query.count() == 0:
            default_services = [
                Service(name='Classic Haircut', description='Traditional barbershop haircut', price=30.00, duration=30),
                Service(name='Beard Trim', description='Professional beard grooming', price=20.00, duration=30),
                Service(name='Hair & Beard Combo', description='Complete grooming package', price=45.00, duration=60),
                Service(name='Hot Towel Shave', description='Traditional straight razor shave', price=35.00, duration=45)
            ]
            for service in default_services:
                db.session.add(service)
            db.session.commit()
            app.logger.info("Default services created successfully")
    except Exception as e:
        app.logger.error(f"Error during database initialization: {str(e)}")
        raise
