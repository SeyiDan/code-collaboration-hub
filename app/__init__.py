from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
# Initialize SocketIO with specific parameters for compatibility
socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent', logger=True, engineio_logger=True)
login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_replace_in_production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///codecollab.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Import socket event handlers after app creation
        from app.sockets import events
    
    return app

app = create_app() 