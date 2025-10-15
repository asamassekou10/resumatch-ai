import os
import logging
from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
import structlog

# Import configuration
from config import get_config

# Import models and extensions
from models import db
from errors import register_error_handlers, log_request_info, log_response_info

# Import routes
from routes.auth import auth_bp
from routes.analysis import analysis_bp
from routes.dashboard import dashboard_bp
from routes.health import health_bp

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Add request/response logging
    add_request_logging(app)
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    return app

def initialize_extensions(app):
    """Initialize Flask extensions"""
    # Database
    db.init_app(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # JWT
    jwt_manager = JWTManager()
    jwt_manager.init_app(app)
    
    # Set up JWT error handlers
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'status': 'error', 'message': 'Token has expired'}, 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        return {'status': 'error', 'message': 'Invalid token'}, 401

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error):
        return {'status': 'error', 'message': 'Authorization token required'}, 401
    
    # Bcrypt
    Bcrypt(app)
    
    # Migrate
    Migrate(app, db)
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["1000 per day", "100 per hour"]
        )
        limiter.init_app(app)
    
    # Marshmallow
    Marshmallow(app)

def configure_logging(app):
    """Configure application logging"""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure Flask logging
    if not app.debug:
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
        app.logger.setLevel(log_level)
        
        # Add file handler for production
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        
        app.logger.info('Application startup')

def register_blueprints(app):
    """Register application blueprints"""
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(dashboard_bp)

def add_request_logging(app):
    """Add request/response logging middleware"""
    @app.before_request
    def log_request():
        if not app.debug:  # Only log in production
            log_request_info()
    
    @app.after_request
    def log_response(response):
        if not app.debug:  # Only log in production
            return log_response_info(response)
        return response

# Create the application
app = create_app()


# Development server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
