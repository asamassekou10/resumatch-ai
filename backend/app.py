from flask import Flask, request, jsonify, redirect, url_for, session, Response, stream_with_context
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
import stripe
from email_service import email_service
from security_config import (
    validate_email,
    validate_password,
    validate_file_upload,
    sanitize_text_input,
    RequestLogger
)
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from config_manager import init_config_manager
from keyword_manager import init_keyword_manager
from routes_config import config_bp
from routes_keywords import keyword_bp
from routes_skills import skill_bp
from routes_market_intelligence import market_bp
from routes_job_postings import job_bp
from routes_scheduler import scheduler_bp
from routes_linkedin import linkedin_bp
from routes_preferences import preferences_bp, detect_industry_from_text, update_user_detected_industries
from routes_job_seeker_insights import job_seeker_bp
from routes_guest import guest_bp
from routes_job_matches import job_matches_bp
from routes_interview_prep import interview_prep_bp
from routes_company_intel import company_intel_bp
from routes_career_path import career_path_bp
from routes_analytics import analytics_bp
from routes.health import health_bp
from routes.auth import auth_bp
from routes.analysis import analysis_bp
from routes.dashboard import dashboard_bp
from routes.jobs import jobs_bp
from routes.payments import payments_bp
from routes.job_applications import job_applications_bp
from routes_admin_diagnostics import admin_diag_bp
from scheduled_ingestion_tasks import init_scheduler
from email_automation import init_email_scheduler
import logging

# Default email preferences
DEFAULT_EMAIL_PREFS = {
    'marketing': True,
    'weekly': True,
    'trial_updates': True
}

# Load environment variables
load_dotenv()

# Create app instance
app = Flask(__name__)

def create_app(config_name=None):
    """Application factory pattern for testing - returns the configured app"""
    # Return the already configured app instance
    return app

# Fix for HTTPS behind proxy (Render, Heroku, etc.)
# This tells Flask to trust the X-Forwarded-* headers from the proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# Security: Require secrets in production
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
SESSION_SECRET = os.getenv('SECRET_KEY')

if not JWT_SECRET or not SESSION_SECRET:
    if not app.debug:
        raise ValueError("JWT_SECRET_KEY and SECRET_KEY environment variables must be set!")
    # Only use defaults in development
    JWT_SECRET = 'dev-jwt-secret-change-in-production'
    SESSION_SECRET = 'dev-session-secret-change-in-production'
    logging.warning("⚠️ Using default secrets - DO NOT use in production!")

# CORS - Allow frontend origins
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
vercel_url = os.getenv('VERCEL_URL', '')  # Add your Vercel URL here
allowed_origins = [
    "http://localhost:3000",
    frontend_url,
    vercel_url,
    "https://resumatch-frontend.onrender.com",  # Old Render frontend (can remove after migration)
    "https://resumeanalyzerai.com",
    "https://www.resumeanalyzerai.com"
]
# Remove duplicates and empty strings
allowed_origins = list(set(filter(None, allowed_origins)))

CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Configuration
database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database connection pooling for production scalability (PostgreSQL only)
# SQLite doesn't support these pooling options
if not database_url.startswith('sqlite'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,              # Base pool size
        'max_overflow': 40,           # Additional connections when needed
        'pool_timeout': 30,           # Wait 30s for connection
        'pool_recycle': 1800,         # Recycle connections after 30min
        'pool_pre_ping': True,        # Test connections before use
    }

app.config['JWT_SECRET_KEY'] = JWT_SECRET
# Shorter access token expiration for security (1 hour)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
# Refresh token lasts longer (7 days)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['SECRET_KEY'] = SESSION_SECRET
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max request size
app.config['PREFERRED_URL_SCHEME'] = 'https'  # Force HTTPS URL generation

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Stripe Configuration
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Price IDs for subscriptions
STRIPE_BASIC_PRICE_ID = os.getenv('STRIPE_BASIC_PRICE_ID')
STRIPE_STUDENT_PRICE_ID = os.getenv('STRIPE_STUDENT_PRICE_ID')
STRIPE_PRO_PRICE_ID = os.getenv('STRIPE_PRO_PRICE_ID')
STRIPE_PRO_FOUNDING_PRICE_ID = os.getenv('STRIPE_PRO_FOUNDING_PRICE_ID')
STRIPE_ELITE_PRICE_ID = os.getenv('STRIPE_ELITE_PRICE_ID')

# Product IDs for tier identification
STRIPE_BASIC_PRODUCT_ID = os.getenv('STRIPE_BASIC_PRODUCT_ID', 'prod_TisCdJIRaSgZTT')
STRIPE_STUDENT_PRODUCT_ID = os.getenv('STRIPE_STUDENT_PRODUCT_ID', 'prod_TirrjGd5KK5QTx')

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY
    if not STRIPE_WEBHOOK_SECRET:
        app.logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook validation will not work")
    if not STRIPE_PRO_PRICE_ID or not STRIPE_ELITE_PRICE_ID:
        app.logger.warning("Stripe Price IDs not configured - subscriptions won't work")
    if not STRIPE_BASIC_PRICE_ID or not STRIPE_STUDENT_PRICE_ID:
        app.logger.warning("Stripe Basic/Student Price IDs not configured - new tiers won't work")
else:
    app.logger.warning("STRIPE_SECRET_KEY not configured - payment features disabled")

# Import db from models to use the same instance for all models
from models import db
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
oauth = OAuth(app)

# Register custom error handlers
from errors import register_error_handlers
register_error_handlers(app)

# Initialize request logging for monitoring
request_logger = RequestLogger(app)

# JWT Token Blacklist for secure logout
# Uses Redis if available, falls back to in-memory set (not suitable for multi-worker production)
jwt_blacklist = set()

# Try to use Redis for blacklist if available
try:
    import redis
    REDIS_URL = os.getenv('REDIS_URL')
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()  # Test connection
        USE_REDIS_BLACKLIST = True
        logging.info("JWT blacklist using Redis storage")
    else:
        USE_REDIS_BLACKLIST = False
        redis_client = None
        logging.warning("JWT blacklist using in-memory storage - not suitable for production with multiple workers")
except Exception as e:
    USE_REDIS_BLACKLIST = False
    redis_client = None
    logging.warning(f"Redis not available for JWT blacklist, using in-memory: {e}")


def add_token_to_blacklist(jti, expires_in_seconds=3600):
    """Add a token JTI to the blacklist"""
    if USE_REDIS_BLACKLIST and redis_client:
        redis_client.setex(f"jwt_blacklist:{jti}", expires_in_seconds, "1")
    else:
        jwt_blacklist.add(jti)


def is_token_blacklisted(jti):
    """Check if a token JTI is blacklisted"""
    if USE_REDIS_BLACKLIST and redis_client:
        return redis_client.get(f"jwt_blacklist:{jti}") is not None
    return jti in jwt_blacklist


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if the token has been revoked"""
    jti = jwt_payload.get("jti")
    return is_token_blacklisted(jti)


# Handle OPTIONS requests for CORS preflight - bypass authentication
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        # Explicitly add CORS headers to OPTIONS response
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        return response

# Initialize Configuration Manager
config_manager = init_config_manager(db)

# Initialize Keyword Manager
keyword_manager = init_keyword_manager()

# Rate Limiting - Use Redis in production for multi-worker support
REDIS_URL = os.getenv('REDIS_URL')
rate_limit_storage = REDIS_URL if REDIS_URL else "memory://"

if rate_limit_storage == "memory://" and not app.debug:
    logging.warning("Rate limiting using in-memory storage - not suitable for production with multiple workers!")

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=rate_limit_storage
)

# Configure Google OAuth
google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
if not google_redirect_uri:
    # Auto-generate based on backend URL
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
    google_redirect_uri = f"{backend_url}/api/auth/callback"
    logging.warning(f"GOOGLE_REDIRECT_URI not set, using: {google_redirect_uri}")

# Only register Google OAuth if credentials are available
google_client_id = app.config.get('GOOGLE_CLIENT_ID')
google_client_secret = app.config.get('GOOGLE_CLIENT_SECRET')

if google_client_id and google_client_secret:
    google = oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        },
        authorize_params={'access_type': 'offline'},
    )
    logging.info("Google OAuth configured successfully")
else:
    google = None
    logging.warning("Google OAuth not configured - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET required")

# Security: Enforce HTTPS in production
@app.before_request
def enforce_https():
    if request.headers.get('X-Forwarded-Proto') == 'http' and not app.debug:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Security: Add security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# Import models from models.py (single source of truth)
from models import User, Analysis, GuestSession, GuestAnalysis, Purchase, Feedback


# Initialize database tables
def init_db():
    """Initialize the database tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

        except Exception as e:
            logging.error(f"Database initialization error: {str(e)}")

# Call init_db when module is loaded (works with gunicorn)
# Skip in test environment to speed up test execution
if os.getenv('FLASK_ENV') != 'testing':
    init_db()

def auto_migrate():
    """Automatically add missing columns if they don't exist"""
    with app.app_context():
        try:
            from sqlalchemy import text
            commands = [
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(100);',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(100);',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT \'email\';',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;',
                'ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);',
                # Subscription and credit fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT \'free\';',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 0;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_id VARCHAR(255);',
                # Admin fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;',
                # Trial tracking fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_start_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_end_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS is_trial_active BOOLEAN DEFAULT FALSE;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_credits_granted INTEGER DEFAULT 0;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_expired_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS last_email_sent_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS email_sequence_step INTEGER DEFAULT 0;',
                # Email automation improvements
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS weekly_email_start_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS email_preferences JSONB DEFAULT \'{}\';',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS last_email_opened_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS last_email_clicked_date TIMESTAMP;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS email_bounce_count INTEGER DEFAULT 0;',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS email_variant VARCHAR(50);',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT \'UTC\';',
                # Set Google OAuth users as verified
                'UPDATE users SET email_verified = TRUE WHERE auth_provider = \'google\';'
            ]
            for command in commands:
                db.session.execute(text(command))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

auto_migrate()


def init_default_configurations():
    """Initialize default configurations if not already done"""
    with app.app_context():
        try:
            from models import SystemConfiguration, SubscriptionTier, RateLimitConfig, ScoringThreshold, ValidationRule

            # Check if configurations already exist
            config_count = SystemConfiguration.query.count()
            tier_count = SubscriptionTier.query.count()

            if config_count == 0 or tier_count == 0:
                logging.info("Initializing default system configurations...")

                # Initialize subscription tiers
                if tier_count == 0:
                    tiers_data = [
                        {
                            'name': 'free',
                            'display_name': 'Free Plan',
                            'monthly_credits': 0,
                            'max_file_size_mb': 5,
                            'max_analyses_per_month': 5,
                            'position': 1,
                            'is_active': True
                        },
                        {
                            'name': 'pro',
                            'display_name': 'Pro Plan',
                            'monthly_credits': 20,
                            'price_cents': 1999,
                            'max_file_size_mb': 16,
                            'max_analyses_per_month': 100,
                            'position': 2,
                            'is_active': True
                        }
                    ]
                    for tier_data in tiers_data:
                        tier = SubscriptionTier(**tier_data)
                        db.session.add(tier)
                    logging.info("✓ Subscription tiers initialized")

                # Initialize system configurations
                if config_count == 0:
                    configs_data = [
                        {'config_key': 'max_file_size_mb', 'config_value': 16, 'data_type': 'int', 'category': 'file'},
                        {'config_key': 'password_min_length', 'config_value': 8, 'data_type': 'int', 'category': 'validation'},
                        {'config_key': 'gemini_model', 'config_value': 'models/gemini-2.5-flash', 'data_type': 'string', 'category': 'ai'},
                        {'config_key': 'jwt_token_expires_days', 'config_value': 7, 'data_type': 'int', 'category': 'security'},
                    ]
                    for config_data in configs_data:
                        config = SystemConfiguration(**config_data)
                        db.session.add(config)
                    logging.info("✓ System configurations initialized")

                db.session.commit()
                logging.info("✓ Default configurations initialized successfully")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error initializing configurations: {str(e)}")


init_default_configurations()


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def create_verification_link(user_id, token):
    """Create verification link that users can click from email"""
    # Point to backend verification endpoint which will redirect to frontend
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
    return f"{backend_url}/api/auth/verify-email?user={user_id}&token={token}"

def transfer_guest_analyses_to_user(guest_token, user_id):
    """Transfer all guest analyses to a newly registered/logged-in user"""
    try:
        if not guest_token:
            return 0

        # Find the guest session
        guest_session = GuestSession.query.filter_by(session_token=guest_token).first()

        if not guest_session:
            return 0

        # Get all analyses for this guest session
        guest_analyses = GuestAnalysis.query.filter_by(guest_session_id=guest_session.id).all()

        transferred_count = 0
        for guest_analysis in guest_analyses:
            # Parse ai_feedback as JSON if it's a string
            ai_feedback_str = guest_analysis.ai_feedback

            # Create a new Analysis record for the user
            new_analysis = Analysis(
                user_id=user_id,
                job_title=guest_analysis.job_title,
                company_name=guest_analysis.company_name,
                match_score=guest_analysis.match_score,
                keywords_found=guest_analysis.keywords_found,
                keywords_missing=guest_analysis.keywords_missing,
                suggestions=guest_analysis.suggestions,
                resume_text=guest_analysis.resume_text,
                job_description=guest_analysis.job_description,
                resume_filename=guest_analysis.resume_filename,
                detected_industry=guest_analysis.detected_industry,
                ai_feedback=ai_feedback_str,
                created_at=guest_analysis.created_at
            )
            db.session.add(new_analysis)
            transferred_count += 1

        # Mark guest session as converted
        guest_session.status = 'converted'
        guest_session.converted_user_id = user_id

        db.session.commit()
        logging.info(f"Transferred {transferred_count} analyses from guest session {guest_session.id} to user {user_id}")
        return transferred_count

    except Exception as e:
        logging.error(f"Error transferring guest analyses: {str(e)}")
        db.session.rollback()
        return 0

# Routes
@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    return jsonify({'status': 'healthy', 'message': 'AI Resume Optimizer API is running'}), 200

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    data = request.json

    # Validate required fields
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    guest_token = data.get('guest_token')  # Accept guest token for analysis transfer

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Validate password strength
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Generate verification token
    verification_token = generate_verification_token()

    # Create user (NOT verified yet)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    now = datetime.utcnow()
    
    # Check if skip_trial flag is set (for micro-purchases)
    skip_trial = data.get('skip_trial', False)
    
    # New system: No automatic trial activation
    # Trial only activates when user subscribes via Stripe with credit card
    # Honor existing trials: If user already has trial_start_date, keep it (for existing users)
    # For new signups: Create with free tier only
    user = User(
        email=email,
        password_hash=hashed_password,
        auth_provider='email',
        email_verified=False,  # Not verified yet
        verification_token=verification_token,
        # Free tier by default - no automatic trial
        subscription_tier='free',
        subscription_status='inactive',
        credits=10,  # Free tier credits
        is_trial_active=False,
        trial_start_date=None,  # No trial until Stripe subscription
        trial_end_date=None,
        trial_credits_granted=0,
        email_sequence_step=0
    )

    try:
        db.session.add(user)
        db.session.commit()

        # Transfer guest analyses if guest_token provided
        transferred_count = 0
        if guest_token:
            transferred_count = transfer_guest_analyses_to_user(guest_token, user.id)

        # Generate verification link
        verification_link = create_verification_link(user.id, verification_token)
        unsubscribe_link = None
        unsubscribe_token = email_service.generate_unsubscribe_token(user.id)
        if unsubscribe_token:
            unsubscribe_link = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"

        # Send emails: verification and welcome (no trial activation email)
        recipient_name = email.split('@')[0]
        email_sent = False
        welcome_sent = False
        
        try:
            # Send verification email
            email_sent = email_service.send_verification_email(
                recipient_email=email,
                recipient_name=recipient_name,
                verification_link=verification_link
            )
            
            # Send welcome email
            welcome_sent = email_service.send_welcome_email(
                recipient_email=email,
                recipient_name=recipient_name,
                verification_required=True,
                unsubscribe_link=unsubscribe_link
            )
            
            # Update email tracking
            user.last_email_sent_date = now
            user.email_sequence_step = 1  # Welcome email sent
            db.session.commit()

            if email_sent:
                logging.info(f"New user registered: {email}, verification email sent")
                response = {
                    'message': 'Registration successful! Please check your email to verify your account.',
                    'email': email,
                    'verification_required': True
                }
            else:
                logging.error(f"User registered but verification email failed: {email}. User ID: {user.id}")
                # Log email service status for debugging
                email_status = {
                    'resend_available': email_service.resend is not None,
                    'api_key_set': bool(email_service.resend_api_key),
                    'api_key_length': len(email_service.resend_api_key) if email_service.resend_api_key else 0,
                    'from_email': email_service.from_email
                }
                logging.error(f"Email service status: {email_status}")
                
                # Still allow registration, but inform user email failed
                response = {
                    'message': 'Registration successful! However, we could not send the verification email. Please use the resend verification feature or contact support@resumeanalyzerai.com.',
                    'email': email,
                    'verification_required': True,
                    'email_sent': False,
                    'verification_link': verification_link  # Provide link as fallback
                }
        except Exception as e:
            logging.error(f"Exception during email sending for {email}: {str(e)}", exc_info=True)
            response = {
                'message': 'Registration successful! However, we encountered an error sending the verification email. Please use the resend verification feature or contact support@resumeanalyzerai.com.',
                'email': email,
                'verification_required': True,
                'email_sent': False,
                'verification_link': verification_link
            }

        if transferred_count > 0:
            response['analyses_transferred'] = transferred_count

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/trial/activate', methods=['POST'])
@jwt_required()
def activate_trial():
    """Activate free trial for existing users who haven't had one yet"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user already had a trial
        if user.trial_start_date is not None:
            return jsonify({
                'error': 'You have already used your free trial',
                'trial_start_date': user.trial_start_date.isoformat() if user.trial_start_date else None
            }), 400
        
        # Check if user is already on a paid plan
        if user.subscription_status == 'active' and user.subscription_tier in ['pro', 'elite']:
            return jsonify({
                'error': 'You already have an active subscription',
                'subscription_tier': user.subscription_tier
            }), 400
        
        # Activate trial
        now = datetime.utcnow()
        trial_end = now + timedelta(days=7)
        
        user.subscription_tier = 'pro'
        user.subscription_status = 'trial'
        user.credits = 100
        user.is_trial_active = True
        user.trial_start_date = now
        user.trial_end_date = trial_end
        user.trial_credits_granted = 100
        user.email_sequence_step = 0
        
        db.session.commit()
        
        # Send welcome emails
        recipient_name = user.name or user.email.split('@')[0]
        unsubscribe_link = None
        unsubscribe_token = email_service.generate_unsubscribe_token(user.id)
        if unsubscribe_token:
            unsubscribe_link = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"
        email_service.send_welcome_email(user.email, recipient_name, verification_required=not user.email_verified, unsubscribe_link=unsubscribe_link)
        email_service.send_trial_activation_email(user.email, recipient_name, trial_end, unsubscribe_link=unsubscribe_link)
        
        # Update email tracking
        user.last_email_sent_date = now
        user.email_sequence_step = 1
        db.session.commit()
        
        logging.info(f"Trial activated for existing user: {user.email}")
        
        return jsonify({
            'message': 'Free trial activated successfully!',
            'trial_active': True,
            'trial_end_date': trial_end.isoformat(),
            'credits': 100
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error activating trial: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to activate trial'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.json

        # Validate input
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.password_hash or not bcrypt.check_password_hash(user.password_hash, password):
            logging.warning(f"Failed login attempt for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if email is verified (only for email auth, not Google OAuth)
        if user.auth_provider == 'email' and not user.email_verified:
            logging.warning(f"Login attempt with unverified email: {email}")
            return jsonify({
                'error': 'Please verify your email before logging in',
                'email_verified': False
            }), 403

        # Check if user is OAuth user trying to login with password
        if user.auth_provider == 'google' and not user.password_hash:
            return jsonify({'error': 'Please login with Google'}), 401

        # Update last login
        now = datetime.utcnow()
        user.last_login = now
        # Initialize weekly email reference date if not set to avoid resetting on subsequent logins
        try:
            if hasattr(user, 'weekly_email_start_date') and not user.weekly_email_start_date:
                user.weekly_email_start_date = user.created_at or now
        except Exception as e:
            # Column might not exist yet, ignore and continue
            logging.warning(f"Could not set weekly_email_start_date: {e}")
        db.session.commit()

        logging.info(f"Successful login: {email}")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_picture': user.profile_picture,
                'auth_provider': user.auth_provider,
                'email_verified': user.email_verified,
                'subscription_tier': user.subscription_tier,
                'subscription_status': user.subscription_status,
                'credits': user.credits,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'is_trial_active': user.is_trial_active,
                'trial_start_date': user.trial_start_date.isoformat() if user.trial_start_date else None,
                'trial_end_date': user.trial_end_date.isoformat() if user.trial_end_date else None
            }
        }), 200

    except Exception as e:
        logging.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed. Please try again.'}), 500


@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Get a new access token using refresh token"""
    try:
        identity = get_jwt_identity()
        user = User.query.get(int(identity))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Create new access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_picture': user.profile_picture,
                'subscription_tier': user.subscription_tier,
                'subscription_status': user.subscription_status,
                'credits': user.credits,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        }), 200

    except Exception as e:
        logging.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token refresh failed'}), 500


# Google OAuth Routes
@app.route('/api/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        # Check if Google OAuth is configured
        if google is None:
            logging.error("Google OAuth not configured")
            return jsonify({'error': 'Google OAuth is not configured on the server'}), 503

        # Use the full URL including protocol
        redirect_uri = url_for('google_callback', _external=True)

        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Google login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'OAuth initialization failed'}), 500

@app.route('/api/auth/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Verify user email with token (GET for email link, POST for API)"""
    # Handle both GET (from email link) and POST (from API)
    if request.method == 'GET':
        user_id = request.args.get('user')
        token = request.args.get('token')
    else:
        data = request.json
        user_id = data.get('user_id')
        token = data.get('token')
    
    if not user_id or not token:
        error_msg = 'Invalid verification link'
        if request.method == 'GET':
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/verify-error?error={error_msg}")
        return jsonify({'error': error_msg}), 400

    try:
        user = User.query.get(int(user_id))

        if not user:
            error_msg = 'User not found'
            if request.method == 'GET':
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                return redirect(f"{frontend_url}/verify-error?error={error_msg}")
            return jsonify({'error': error_msg}), 404

        if user.email_verified:
            if request.method == 'GET':
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                return redirect(f"{frontend_url}/verify-success?already_verified=true")
            return jsonify({'message': 'Email already verified'}), 200

        # Verify token matches
        if user.verification_token != token:
            logging.warning(f"Invalid verification token for user {user.email}")
            error_msg = 'Invalid or expired verification link'
            if request.method == 'GET':
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                return redirect(f"{frontend_url}/verify-error?error={error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Mark as verified
        user.email_verified = True
        user.verification_token = None  # Clear token
        db.session.commit()

        logging.info(f"Email verified successfully for user: {user.email}")

        # Create access token so they can login immediately
        access_token = create_access_token(identity=str(user.id))

        # Handle GET request from email link - redirect to frontend
        if request.method == 'GET':
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            redirect_url = f"{frontend_url}/verify-success?token={access_token}&user_id={user.id}&email={user.email}"
            return redirect(redirect_url)

        # Handle POST request from API
        return jsonify({
            'message': 'Email verified successfully!',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'email_verified': True
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Email verification error: {str(e)}")
        if request.method == 'GET':
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/verify-error?error=Verification failed")
        return jsonify({'error': 'Verification failed'}), 500

@app.route('/api/auth/resend-verification', methods=['POST'])
@limiter.limit("3 per hour")
def resend_verification():
    """Resend verification email"""
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email or not validate_email(email):
        return jsonify({'error': 'Valid email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Don't reveal if user exists
        return jsonify({'message': 'If this email is registered, a verification email has been sent'}), 200
    
    if user.email_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    # Generate new token
    user.verification_token = generate_verification_token()
    db.session.commit()
    
    # Send email
    verification_link = create_verification_link(user.id, user.verification_token)
    email_sent = email_service.send_verification_email(
        recipient_email=email,
        recipient_name=user.name or email.split('@')[0],
        verification_link=verification_link
    )
    
    if email_sent:
        logging.info(f"Verification email resent to: {email}")
    
    return jsonify({'message': 'Verification email sent'}), 200

def get_frontend_url():
    """Determine the correct frontend URL based on the request context"""
    # Check if we're in development mode (localhost backend)
    if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
        return 'http://localhost:3000'
    else:
        return os.getenv('FRONTEND_URL', 'http://localhost:3000')

@app.route('/api/auth/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        logging.info(f"Google OAuth callback received from: {request.url}")
        logging.info(f"Request args: {dict(request.args)}")

        # Check for OAuth errors first
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Authentication failed')
            logging.error(f"Google OAuth error: {error} - {error_description}")
            frontend_url = get_frontend_url()
            from urllib.parse import quote
            return redirect(f"{frontend_url}/auth/error?message={quote(error_description)}")

        # Check if authorization code is present
        if 'code' not in request.args:
            logging.error("No authorization code in OAuth callback")
            frontend_url = get_frontend_url()
            return redirect(f"{frontend_url}/auth/error?message=No authorization code received")

        # Get the token
        logging.info("Attempting to exchange authorization code for token")
        token = google.authorize_access_token()
        logging.info("Token received successfully")
        
        # Get user info
        user_info = token.get('userinfo')
        
        if not user_info:
            # Try alternative method to get user info
            try:
                resp = google.get('userinfo')
                user_info = resp.json()
            except Exception as e:
                frontend_url = get_frontend_url()
                return redirect(f"{frontend_url}/auth/error?message=Failed to get user information")
        
        # Extract user information
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        
        if not email:
            frontend_url = get_frontend_url()
            return redirect(f"{frontend_url}/auth/error?message=Email not provided by Google")
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user with Google info if not already set
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = 'google'
            if not user.name and name:
                user.name = name
            if not user.profile_picture and picture:
                user.profile_picture = picture
            user.last_login = datetime.utcnow()
        else:
            # Create new user - free tier by default, no automatic trial
            now = datetime.utcnow()
            
            user = User(
                email=email,
                google_id=google_id,
                name=name,
                profile_picture=picture,
                auth_provider='google',
                last_login=datetime.utcnow(),
                email_verified=True,  # Google OAuth users are pre-verified
                # Free tier by default - no automatic trial
                subscription_tier='free',
                subscription_status='inactive',
                credits=10,  # Free tier credits
                is_trial_active=False,
                trial_start_date=None,  # No trial until Stripe subscription
                trial_end_date=None,
                trial_credits_granted=0,
                email_sequence_step=0
            )
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email for new Google OAuth users (no trial activation email)
            recipient_name = name or email.split('@')[0]
            unsubscribe_link = None
            unsubscribe_token = email_service.generate_unsubscribe_token(user.id)
            if unsubscribe_token:
                unsubscribe_link = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"
            email_service.send_welcome_email(recipient_email=email, recipient_name=recipient_name, verification_required=False, unsubscribe_link=unsubscribe_link)
            
            # Update email tracking
            user.last_email_sent_date = now
            user.email_sequence_step = 1
            db.session.commit()
        
        db.session.commit()
        
        # Create JWT token
        access_token = create_access_token(identity=str(user.id))
        
        # Return success response with redirect URL for frontend
        frontend_url = get_frontend_url()
        redirect_url = f"{frontend_url}?token={access_token}&user={user.id}"
        return redirect(redirect_url)

    except Exception as e:
        logging.error(f"Google OAuth error: {str(e)}", exc_info=True)

        frontend_url = get_frontend_url()
        return redirect(f"{frontend_url}/auth/error?message=oauth_failed")


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and blacklist the token"""
    try:
        # Get the JWT token identifier and blacklist it
        jwt_data = get_jwt()
        jti = jwt_data.get("jti")

        if jti:
            # Blacklist for 1 hour (same as access token expiry)
            add_token_to_blacklist(jti, expires_in_seconds=3600)

        user_id = get_jwt_identity()
        logging.info(f"User {user_id} logged out, token blacklisted")

        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logging.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logged out'}), 200  # Still return success to client

@app.route('/api/analyze', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")  # Limit resume analyses
def analyze_resume():
    try:
        user_id = int(get_jwt_identity())
        logging.info(f"Analysis request from user: {user_id}")
    except Exception as e:
        logging.error(f"JWT Error: {str(e)}")
        return jsonify({'error': 'Authentication error'}), 401

    # Check abuse patterns
    from abuse_prevention import check_abuse_pattern, check_daily_credit_limit, has_sufficient_credits, deduct_credits

    allowed, msg = check_abuse_pattern(user_id, 'analyze')
    if not allowed:
        return jsonify({'error': msg}), 429

    allowed, msg = check_daily_credit_limit(user_id, 'analyze')
    if not allowed:
        return jsonify({'error': msg}), 429

    # Check if user has sufficient credits
    has_credits, info = has_sufficient_credits(user_id, 'analyze')
    if not has_credits:
        return jsonify(info), 402  # 402 Payment Required

    # Validate file upload
    if 'resume' not in request.files:
        return jsonify({'error': 'Resume file required'}), 400

    resume_file = request.files['resume']

    # Validate file
    is_valid, error_message = validate_file_upload(resume_file)
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    # Sanitize text inputs
    job_description = sanitize_text_input(request.form.get('job_description', ''), max_length=10000)
    job_title = sanitize_text_input(request.form.get('job_title', ''), max_length=200)
    company_name = sanitize_text_input(request.form.get('company_name', ''), max_length=200)
    
    if not job_description:
        return jsonify({'error': 'Job description required'}), 400
    
    if len(job_description) < 50:
        return jsonify({'error': 'Job description too short (minimum 50 characters)'}), 400
    
    # Import AI processing module
    try:
        from ai_processor import extract_text_from_file
        from intelligent_resume_analyzer import get_analyzer
    except ImportError as e:
        logging.error(f"Failed to import AI modules: {str(e)}")
        return jsonify({'error': 'AI processing module not available'}), 500

    try:
        # Extract resume text from file
        resume_text = extract_text_from_file(resume_file)

        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({'error': 'Resume appears empty. Please provide a valid resume.'}), 400

        # Use intelligent analyzer for better results
        analyzer = get_analyzer()
        logging.info(f"Starting intelligent analysis for user {user_id}")
        result = analyzer.comprehensive_resume_analysis(resume_text, job_description)

        # Extract data from intelligent analysis result
        import json
        match_analysis = result.get('match_analysis', {})
        keywords_found = match_analysis.get('keywords_present', [])
        keywords_missing = [k['keyword'] if isinstance(k, dict) else k
                           for k in match_analysis.get('keywords_missing', [])]

        # Save to database with intelligent analysis data
        analysis = Analysis(
            user_id=user_id,
            job_title=job_title,
            company_name=company_name,
            match_score=result.get('overall_score', 0),
            keywords_found=keywords_found[:20],  # Limit to top 20
            keywords_missing=keywords_missing[:20],  # Limit to top 20
            suggestions=result.get('interpretation', ''),
            resume_text=resume_text[:50000],  # Limit stored text
            job_description=job_description,
            resume_filename=resume_file.filename,  # Store original filename
            detected_industry=result.get('job_industry', 'Unknown'),
            ai_feedback=json.dumps(result)  # Store full intelligent analysis as JSON
        )

        db.session.add(analysis)
        db.session.commit()

        # Deduct credits for the analysis
        success, msg = deduct_credits(user_id, 'analyze')
        if success:
            logging.info(f"Analysis completed for user {user_id}, analysis_id: {analysis.id} - {msg}")
        else:
            logging.warning(f"Failed to deduct credits for analysis {analysis.id}: {msg}")

        # Extract skills from resume using Spacy NER and pattern matching
        extracted_skills = []
        try:
            from skill_extractor import get_skill_extractor
            from models import SkillExtraction

            # Get the skill extractor instance
            extractor = get_skill_extractor(db)

            # Extract skills from the full resume text (stored in analysis)
            skills = extractor.extract_skills(analysis.resume_text)

            logging.info(f"Extracted {len(skills)} skills from resume for analysis {analysis.id}")

            # Save extracted skills to database
            for skill in skills:
                skill_extraction = SkillExtraction(
                    analysis_id=analysis.id,
                    extracted_text=skill.skill_name,
                    matched_keyword_id=skill.matched_keyword,
                    confidence=skill.confidence,
                    extraction_method=skill.extraction_method
                )
                db.session.add(skill_extraction)
                extracted_skills.append({
                    'name': skill.skill_name,
                    'matched_keyword_id': skill.matched_keyword,
                    'confidence': round(skill.confidence, 3),
                    'method': skill.extraction_method
                })

            db.session.commit()
            logging.info(f"Saved {len(extracted_skills)} skill extractions for analysis {analysis.id}")

        except Exception as e:
            logging.warning(f"Skill extraction failed for analysis {analysis.id}: {str(e)}")
            # Don't fail the entire analysis if skill extraction fails
            extracted_skills = []
        
        # Note: Email sending is now on-demand via /api/email-analysis endpoint

        # Industry is already detected by intelligent analyzer
        detected_industry = result.get('job_industry', 'Unknown')

        # Update user's detected industries
        try:
            if detected_industry and detected_industry != 'Unknown':
                industry_data = [{'industry': detected_industry, 'confidence': 0.9}]
                update_user_detected_industries(user_id, industry_data)
                logging.info(f"Updated user {user_id} detected industry: {detected_industry}")
        except Exception as e:
            logging.error(f"Error updating user detected industries: {str(e)}")

        # Return new intelligent analysis format
        return jsonify({
            'analysis_id': analysis.id,
            'overall_score': result.get('overall_score'),
            'interpretation': result.get('interpretation'),
            'match_analysis': result.get('match_analysis'),
            'ats_optimization': result.get('ats_optimization'),
            'recommendations': result.get('recommendations'),
            'job_industry': result.get('job_industry'),
            'job_level': result.get('job_level'),
            'resume_level': result.get('resume_level'),
            'expected_ats_pass_rate': result.get('expected_ats_pass_rate'),
            'extracted_skills': extracted_skills,
            'detected_industry': detected_industry,
            'created_at': analysis.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Analysis failed for user {user_id}: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

@app.route('/api/analyze/stream', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def analyze_resume_stream():
    """
    Stream analysis results using Server-Sent Events (SSE).
    Provides progressive updates as analysis progresses.
    """
    try:
        user_id = int(get_jwt_identity())
        logging.info(f"Streaming analysis request from user: {user_id}")
    except Exception as e:
        logging.error(f"JWT Error: {str(e)}")
        return jsonify({'error': 'Authentication error'}), 401

    # Check credits and rate limits
    from abuse_prevention import check_abuse_pattern, check_daily_credit_limit, has_sufficient_credits
    
    allowed, msg = check_abuse_pattern(user_id, 'analyze')
    if not allowed:
        return jsonify({'error': msg}), 429
    
    allowed, msg = check_daily_credit_limit(user_id, 'analyze')
    if not allowed:
        return jsonify({'error': msg}), 429
    
    has_credits, info = has_sufficient_credits(user_id, 'analyze')
    if not has_credits:
        return jsonify(info), 402

    # Accept JSON or form data with resume_text
    if request.is_json:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        job_title = data.get('job_title', '')
        company_name = data.get('company_name', '')
    else:
        # Try form data
        resume_text = request.form.get('resume_text', '')
        job_description = request.form.get('job_description', '')
        job_title = request.form.get('job_title', '')
        company_name = request.form.get('company_name', '')
        
        # If no resume_text, try file upload
        if not resume_text and 'resume' in request.files:
            from ai_processor import extract_text_from_file
            resume_file = request.files['resume']
            resume_text = extract_text_from_file(resume_file)
    
    if not resume_text or len(resume_text.strip()) < 50:
        return jsonify({'error': 'Resume text required (minimum 50 characters)'}), 400
    
    if not job_description or len(job_description.strip()) < 50:
        return jsonify({'error': 'Job description required (minimum 50 characters)'}), 400

    def generate_stream():
        """Generator function for SSE streaming"""
        try:
            from intelligent_resume_analyzer import get_analyzer
            import json
            
            analyzer = get_analyzer()
            
            # Stage 1: Extracting and parsing (10%)
            yield f"data: {json.dumps({'stage': 'extracting', 'progress': 10, 'message': 'Extracting resume content...'})}\n\n"
            
            # Batch 1: Run job + resume extraction in parallel, stream as each completes
            from concurrent.futures import ThreadPoolExecutor, as_completed
            job_analysis = None
            resume_parsed = None
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                job_future = executor.submit(analyzer.extract_job_requirements, job_description)
                resume_future = executor.submit(analyzer.extract_resume_content, resume_text)
                
                # Stream results as they complete (using as_completed)
                futures_map = {job_future: 'job', resume_future: 'resume'}
                for future in as_completed([job_future, resume_future]):
                    try:
                        result = future.result()
                        if futures_map[future] == 'job':
                            job_analysis = result
                            yield f"data: {json.dumps({'stage': 'job_parsed', 'progress': 20, 'message': 'Job requirements extracted', 'data': {'industry': job_analysis.get('industry', 'Unknown')}})}\n\n"
                        else:
                            resume_parsed = result
                            yield f"data: {json.dumps({'stage': 'resume_parsed', 'progress': 25, 'message': 'Resume content extracted'})}\n\n"
                    except Exception as e:
                        logging.error(f"Error in batch 1 task: {e}")
                        yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Error: {str(e)}', 'error': str(e)})}\n\n"
            
            # Ensure we have both results before proceeding
            if not job_analysis or not resume_parsed:
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': 'Failed to extract job or resume data', 'error': 'Extraction failed'})}\n\n"
                return
            
            # Stage 2: Match analysis (must complete before batch 2)
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 30, 'message': 'Matching skills and keywords...'})}\n\n"
            
            try:
                match_analysis = analyzer.intelligent_match_analysis(
                    job_analysis, resume_parsed, job_description, resume_text
                )
                
                # Inject ATS heuristics (instant, Python-based)
                ats_heuristics = analyzer._check_ats_readability_heuristics(resume_text)
                if "match_breakdown" not in match_analysis:
                    match_analysis["match_breakdown"] = {}
                match_analysis["ats_readability_heuristics"] = ats_heuristics
                
                yield f"data: {json.dumps({'stage': 'match_complete', 'progress': 50, 'message': 'Match analysis complete'})}\n\n"
            except Exception as e:
                logging.error(f"Error in match analysis: {e}")
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Match analysis failed: {str(e)}', 'error': str(e)})}\n\n"
                return
            
            # Stage 3: Scoring (instant, Python-based)
            yield f"data: {json.dumps({'stage': 'scoring', 'progress': 60, 'message': 'Calculating match score...'})}\n\n"
            
            try:
                score_data = analyzer._calibrate_match_score(match_analysis, job_analysis)
                score_breakdown = analyzer._generate_score_breakdown(match_analysis, score_data, job_analysis)
                
                # Send score immediately
                yield f"data: {json.dumps({'stage': 'score_ready', 'progress': 70, 'message': 'Score calculated', 'data': {'score': score_data['final_score'], 'score_breakdown': score_breakdown}})}\n\n"
            except Exception as e:
                logging.error(f"Error in scoring: {e}")
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Scoring failed: {str(e)}', 'error': str(e)})}\n\n"
                return
            
            # Stage 4: Final analysis - stream ATS and recommendations as they complete
            yield f"data: {json.dumps({'stage': 'optimizing', 'progress': 75, 'message': 'Generating optimization recommendations...'})}\n\n"
            
            ats_optimization = None
            recommendations = None
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                ats_future = executor.submit(
                    analyzer.generate_ats_optimization_recommendations,
                    job_description, resume_parsed, match_analysis, 'en'
                )
                rec_future = executor.submit(
                    analyzer.generate_intelligent_recommendations,
                    job_description, resume_parsed, match_analysis,
                    job_analysis.get("industry", "unknown"), 'en'
                )
                
                # Stream results as they complete
                futures_map = {ats_future: 'ats', rec_future: 'recommendations'}
                for future in as_completed([ats_future, rec_future]):
                    try:
                        result = future.result()
                        if futures_map[future] == 'ats':
                            ats_optimization = result
                            yield f"data: {json.dumps({'stage': 'ats_ready', 'progress': 85, 'message': 'ATS optimization ready', 'data': {'ats_optimization': ats_optimization}})}\n\n"
                        else:
                            recommendations = result
                            yield f"data: {json.dumps({'stage': 'recommendations_ready', 'progress': 90, 'message': 'Recommendations ready', 'data': {'recommendations': recommendations}})}\n\n"
                    except Exception as e:
                        logging.error(f"Error in batch 2 task: {e}")
                        # Continue with other task even if one fails
                        if futures_map[future] == 'ats':
                            ats_optimization = {"keyword_optimization": [], "natural_integration_tips": []}
                        else:
                            recommendations = {"priority_improvements": [], "quick_wins": []}
                        yield f"data: {json.dumps({'stage': 'warning', 'progress': 0, 'message': f'Partial failure: {futures_map[future]} generation failed, continuing...', 'error': str(e)})}\n\n"
            
            # Use fallback values if generation failed
            if not ats_optimization:
                ats_optimization = {"keyword_optimization": [], "natural_integration_tips": []}
            if not recommendations:
                recommendations = {"priority_improvements": [], "quick_wins": []}
            
            # Complete result
            result = {
                "overall_score": score_data["final_score"],
                "interpretation": score_data["interpretation"],
                "match_analysis": match_analysis,
                "ats_optimization": ats_optimization,
                "recommendations": recommendations,
                "job_industry": job_analysis.get("industry", "Unknown"),
                "job_level": job_analysis.get("experience_level", "Unknown"),
                "resume_level": resume_parsed.get("experience_level", "Unknown"),
                "expected_ats_pass_rate": f"{match_analysis.get('ats_pass_likelihood', 50)}%",
                "detected_language": 'en',
                "score_breakdown": score_breakdown,
            }
            
            # Save to database
            try:
                keywords_found = match_analysis.get('keywords_present', [])
                keywords_missing = [k['keyword'] if isinstance(k, dict) else k
                                  for k in match_analysis.get('keywords_missing', [])]
                
                analysis = Analysis(
                    user_id=user_id,
                    job_title=job_title,
                    company_name=company_name,
                    match_score=result['overall_score'],
                    keywords_found=keywords_found[:20],
                    keywords_missing=keywords_missing[:20],
                    suggestions=result['interpretation'],
                    resume_text=resume_text[:50000],
                    job_description=job_description,
                    ai_feedback=json.dumps(result)
                )
                
                db.session.add(analysis)
                
                # Deduct credits
                from abuse_prevention import deduct_credits
                deduct_credits(user_id, 'analyze')
                
                db.session.commit()
                result['analysis_id'] = analysis.id
            except Exception as e:
                logging.error(f"Error saving analysis: {e}")
                db.session.rollback()
            
            # Final result
            yield f"data: {json.dumps({'stage': 'complete', 'progress': 100, 'message': 'Analysis complete!', 'data': result})}\n\n"
            
        except Exception as e:
            logging.error(f"Streaming analysis error: {e}", exc_info=True)
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Analysis failed: {str(e)}', 'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable buffering in nginx
            'Connection': 'keep-alive'
        }
    )

@app.route('/api/analyze-intelligent', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")  # Limit intelligent analyses
def analyze_resume_intelligent():
    """
    Intelligent resume analysis using Gemini AI
    Provides semantic matching, ATS optimization, and industry-specific recommendations
    """
    try:
        user_id = int(get_jwt_identity())
        logging.info(f"Intelligent analysis request from user: {user_id}")
    except Exception as e:
        logging.error(f"JWT Error: {str(e)}")
        return jsonify({'error': 'Authentication error'}), 401

    try:
        # Validate file upload
        if 'resume' not in request.files:
            return jsonify({'error': 'Resume file required'}), 400

        resume_file = request.files['resume']

        # Validate file
        is_valid, error_message = validate_file_upload(resume_file)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        # Get job description
        job_description = sanitize_text_input(request.form.get('job_description', ''), max_length=10000)

        if not job_description:
            return jsonify({'error': 'Job description required'}), 400

        if len(job_description) < 50:
            return jsonify({'error': 'Job description too short (minimum 50 characters)'}), 400

        # Extract resume text
        from ai_processor import extract_text_from_file
        resume_text = extract_text_from_file(resume_file)

        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({'error': 'Resume appears empty. Please provide a valid resume.'}), 400

        # Use intelligent analyzer
        from intelligent_resume_analyzer import get_analyzer
        analyzer = get_analyzer()

        logging.info(f"Starting intelligent analysis for user {user_id}")
        analysis_result = analyzer.comprehensive_resume_analysis(resume_text, job_description)

        # Deduct credits for analysis (same as regular analyze)
        from abuse_prevention import deduct_credits
        success, msg = deduct_credits(user_id, 'analyze')
        if not success:
            logging.warning(f"Failed to deduct credits for user {user_id}: {msg}")

        return jsonify({
            'analysis_id': None,  # This is a real-time analysis, not stored
            'overall_score': analysis_result['overall_score'],
            'interpretation': analysis_result['interpretation'],
            'match_analysis': analysis_result['match_analysis'],
            'ats_optimization': analysis_result['ats_optimization'],
            'recommendations': analysis_result['recommendations'],
            'job_industry': analysis_result['job_industry'],
            'job_level': analysis_result['job_level'],
            'resume_level': analysis_result['resume_level'],
            'expected_ats_pass_rate': analysis_result['expected_ats_pass_rate'],
            'created_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logging.error(f"Intelligent analysis failed for user {user_id}: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.', 'details': str(e)[:100]}), 500

@app.route('/api/analyses', methods=['GET'])
@jwt_required()
def get_analyses():
    user_id = int(get_jwt_identity())

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page

    # Query with pagination
    pagination = Analysis.query.filter_by(user_id=user_id)\
        .order_by(Analysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    analyses = pagination.items

    return jsonify({
        'analyses': [{
            'id': a.id,
            'job_title': a.job_title,
            'company_name': a.company_name,
            'match_score': a.match_score,
            'resume_filename': a.resume_filename,
            'created_at': a.created_at.isoformat()
        } for a in analyses],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@app.route('/api/analyses/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify({
        'id': analysis.id,
        'job_title': analysis.job_title,
        'company_name': analysis.company_name,
        'match_score': analysis.match_score,
        'keywords_found': analysis.keywords_found,
        'keywords_missing': analysis.keywords_missing,
        'suggestions': analysis.suggestions,
        'resume_filename': analysis.resume_filename,
        'ai_feedback': analysis.ai_feedback,
        'detected_industry': analysis.detected_industry,
        'created_at': analysis.created_at.isoformat()
    }), 200

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user profile including subscription and credit info"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'profile_picture': user.profile_picture,
        'subscription_tier': user.subscription_tier,
        'subscription_status': user.subscription_status,
        'credits': user.credits,
        'email_verified': user.email_verified,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'is_trial_active': user.is_trial_active,
        'trial_start_date': user.trial_start_date.isoformat() if user.trial_start_date else None,
        'trial_end_date': user.trial_end_date.isoformat() if user.trial_end_date else None
    }), 200


@app.route('/api/user/email-preferences', methods=['GET'])
@jwt_required()
def get_email_preferences():
    """Get email preferences for the authenticated user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    prefs = user.email_preferences or {}
    # Ensure defaults are present
    merged = {**DEFAULT_EMAIL_PREFS, **prefs}
    return jsonify({'email_preferences': merged}), 200


@app.route('/api/user/email-preferences', methods=['PUT'])
@jwt_required()
def update_email_preferences():
    """Update email preferences for the authenticated user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json or {}
    current_prefs = user.email_preferences or {}
    updated = {**DEFAULT_EMAIL_PREFS, **current_prefs}

    for key in DEFAULT_EMAIL_PREFS.keys():
        if key in data:
            updated[key] = bool(data.get(key))

    user.email_preferences = updated
    db.session.commit()
    return jsonify({'message': 'Email preferences updated', 'email_preferences': updated}), 200


@app.route('/api/user/unsubscribe', methods=['POST'])
@jwt_required(optional=True)
def unsubscribe():
    """
    Unsubscribe user from all marketing emails using token or auth.
    Priority: token -> authenticated user.
    """
    data = request.json or {}
    token = data.get('token')
    user = None

    if token:
        user_id = email_service.verify_unsubscribe_token(token)
        if user_id:
            user = User.query.get(user_id)

    if not user:
        # Try JWT auth if token not provided/invalid
        try:
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
        except Exception:
            pass

    if not user:
        return jsonify({'error': 'Invalid or expired unsubscribe request'}), 400

    user.email_preferences = {k: False for k in DEFAULT_EMAIL_PREFS.keys()}
    db.session.commit()
    return jsonify({'message': 'You have been unsubscribed from all emails'}), 200

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    user_id = int(get_jwt_identity())

    # Use database aggregation for total count and avg score (more efficient)
    stats = db.session.query(
        func.count(Analysis.id).label('total'),
        func.avg(Analysis.match_score).label('avg_score')
    ).filter_by(user_id=user_id).first()

    total = stats.total or 0
    avg_score = stats.avg_score or 0

    if total == 0:
        return jsonify({
            'total_analyses': 0,
            'average_score': 0,
            'score_trend': [],
            'top_missing_skills': []
        }), 200

    # Score trend (last 10 analyses) - only fetch what we need
    recent_analyses = Analysis.query.filter_by(user_id=user_id)\
        .order_by(Analysis.created_at.desc())\
        .limit(10)\
        .all()

    score_trend = [{
        'date': a.created_at.isoformat(),
        'score': a.match_score,
        'job_title': a.job_title
    } for a in reversed(recent_analyses)]  # Reverse for chronological order

    # Aggregate missing skills - only fetch keywords_missing column
    keyword_results = db.session.query(Analysis.keywords_missing)\
        .filter_by(user_id=user_id)\
        .filter(Analysis.keywords_missing.isnot(None))\
        .all()

    skill_counts = {}
    for (keywords,) in keyword_results:
        if keywords:
            for skill in keywords:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

    top_missing = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'total_analyses': total,
        'average_score': round(float(avg_score), 2),
        'score_trend': score_trend,
        'top_missing_skills': [{'skill': s, 'count': c} for s, c in top_missing]
    }), 200

# Gemini AI Routes

@app.route('/api/analyze/feedback/<int:analysis_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")  # Limit AI feedback generation
def generate_feedback(analysis_id):
    """Generate personalized feedback for an existing analysis"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Check credits for AI feedback (1 credit)
    required_credits = 1
    if user.credits < required_credits:
        return jsonify({
            'error': 'Insufficient credits. Please upgrade your plan.',
            'required_credits': required_credits,
            'current_credits': user.credits
        }), 402
    
    try:
        from gemini_service import generate_personalized_feedback
        
        feedback = generate_personalized_feedback(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            match_score=analysis.match_score,
            keywords_found=analysis.keywords_found,
            keywords_missing=analysis.keywords_missing
        )
        
        # Deduct credits and save feedback
        user.credits -= required_credits
        analysis.ai_feedback = feedback
        db.session.commit()
        
        # Send email with AI feedback
        try:
            user = User.query.get(user_id)
            if user and user.email:
                feedback_data = {
                    'match_score': analysis.match_score,
                    'keywords_found': analysis.keywords_found,
                    'keywords_missing': analysis.keywords_missing,
                    'suggestions': analysis.suggestions,
                    'ai_feedback': feedback,
                    'job_title': analysis.job_title,
                    'company_name': analysis.company_name,
                    'analysis_id': analysis_id
                }
                
                # Generate unsubscribe link for the email
                unsubscribe_token = email_service.generate_unsubscribe_token(user_id)
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                unsubscribe_link = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"
                
                email_sent = email_service.send_analysis_results(
                    recipient_email=user.email,
                    recipient_name=user.name or user.email.split('@')[0],
                    analysis_data=feedback_data,
                    unsubscribe_link=unsubscribe_link
                )
                
                if email_sent:
                    logging.info(f"AI feedback email sent to {user.email}")
                    
        except Exception as e:
            logging.error(f"Error sending AI feedback email: {str(e)}")
        
        return jsonify({
            'feedback': feedback,
            'analysis_id': analysis_id
        }), 200
        
    except Exception as e:
        logging.error(f"Failed to generate feedback: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate feedback'}), 500

@app.route('/api/analyze/optimize/<int:analysis_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")  # Limit Resume Optimization
def optimize_resume(analysis_id):
    """Generate optimized resume version"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Check credits for resume optimization (2 credits)
    required_credits = 2
    if user.credits < required_credits:
        return jsonify({
            'error': 'Insufficient credits. Please upgrade your plan.',
            'required_credits': required_credits,
            'current_credits': user.credits
        }), 402
    
    try:
        from gemini_service import generate_optimized_resume
        
        optimized_resume = generate_optimized_resume(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            keywords_missing=analysis.keywords_missing
        )
        
        if not optimized_resume:
            return jsonify({'error': 'Failed to generate optimized resume'}), 500
        
        # Deduct credits and save optimized version
        user.credits -= required_credits
        analysis.optimized_resume = optimized_resume
        db.session.commit()
        
        # Send email with optimized resume
        try:
            user = User.query.get(user_id)
            if user and user.email:
                email_sent = email_service.send_optimized_resume(
                    recipient_email=user.email,
                    recipient_name=user.name or user.email.split('@')[0],
                    optimized_resume=optimized_resume,
                    job_title=analysis.job_title or "this position"
                )
                
                if email_sent:
                    logging.info(f"Optimized resume email sent to {user.email}")
                    
        except Exception as e:
            logging.error(f"Error sending optimized resume email: {str(e)}")
        
        return jsonify({
            'optimized_resume': optimized_resume,
            'analysis_id': analysis_id
        }), 200
        
    except Exception as e:
        logging.error(f"Failed to optimize resume: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to optimize resume'}), 500

@app.route('/api/analyze/cover-letter/<int:analysis_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")  # Limit cover letter generation
def generate_cover_letter_route(analysis_id):
    """Generate tailored cover letter"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Check credits for cover letter generation (2 credits)
    required_credits = 2
    if user.credits < required_credits:
        return jsonify({
            'error': 'Insufficient credits. Please upgrade your plan.',
            'required_credits': required_credits,
            'current_credits': user.credits
        }), 402
    
    try:
        from gemini_service import generate_cover_letter
        
        cover_letter = generate_cover_letter(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            company_name=analysis.company_name or "the company",
            job_title=analysis.job_title or "this position"
        )
        
        if not cover_letter:
            return jsonify({'error': 'Failed to generate cover letter'}), 500
        
        # Deduct credits
        user.credits -= required_credits
        db.session.commit()
        
        # Send email with cover letter
        try:
            user = User.query.get(user_id)
            if user and user.email:
                email_sent = email_service.send_cover_letter(
                    recipient_email=user.email,
                    recipient_name=user.name or user.email.split('@')[0],
                    cover_letter=cover_letter,
                    job_title=analysis.job_title or "this position",
                    company_name=analysis.company_name or "the company"
                )
                
                if email_sent:
                    logging.info(f"Cover letter email sent to {user.email}")
                    
        except Exception as e:
            logging.error(f"Error sending cover letter email: {str(e)}")
        
        return jsonify({
            'cover_letter': cover_letter,
            'analysis_id': analysis_id
        }), 200
        
    except Exception as e:
        logging.error(f"Failed to generate cover letter: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate cover letter'}), 500

@app.route('/api/analyze/skill-suggestions/<int:analysis_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")  # Limit for skill suggestion
def get_skill_suggestions(analysis_id):
    """Get suggestions for acquiring missing skills"""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    try:
        from gemini_service import suggest_missing_experience
        
        suggestions = suggest_missing_experience(
            keywords_missing=analysis.keywords_missing,
            resume_text=analysis.resume_text
        )
        
        if not suggestions:
            return jsonify({'error': 'Failed to generate suggestions'}), 500
        
        return jsonify({
            'suggestions': suggestions,
            'analysis_id': analysis_id
        }), 200
        
    except Exception as e:
        logging.error(f"Failed to generate suggestions: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate suggestions'}), 500

@app.route('/api/email-analysis', methods=['POST'])
@jwt_required()
def email_analysis():
    """Send analysis results to user's email on-demand"""
    user_id = int(get_jwt_identity())
    
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        
        if not analysis_id:
            return jsonify({'error': 'analysis_id is required'}), 400
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        user = User.query.get(user_id)
        if not user or not user.email:
            return jsonify({'error': 'User email not found'}), 400
        
        # Prepare analysis data with all available information
        recommendations = {}
        if hasattr(analysis, 'recommendations') and analysis.recommendations:
            try:
                import json
                recommendations = json.loads(analysis.recommendations) if isinstance(analysis.recommendations, str) else analysis.recommendations
            except:
                recommendations = {}
        
        priority_improvements = recommendations.get('priority_improvements', []) if recommendations else []
        
        analysis_data = {
            'match_score': analysis.match_score or 0,
            'interpretation': analysis.interpretation or analysis.suggestions or '',
            'keywords_found': analysis.keywords_found[:10] if analysis.keywords_found else [],
            'keywords_missing': analysis.keywords_missing[:10] if analysis.keywords_missing else [],
            'suggestions': analysis.suggestions or analysis.interpretation or '',
            'priority_improvements': priority_improvements[:3] if priority_improvements else [],
            'job_title': analysis.job_title or 'Position',
            'company_name': analysis.company_name or 'Company',
            'analysis_id': analysis_id,
            'industry': getattr(analysis, 'industry', 'Unknown'),
            'ats_pass_rate': getattr(analysis, 'ats_pass_rate', 'N/A')
        }
        
        # Generate unsubscribe link for the email
        unsubscribe_token = email_service.generate_unsubscribe_token(user_id)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        unsubscribe_link = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"
        
        email_sent = email_service.send_analysis_results(
            recipient_email=user.email,
            recipient_name=user.name or user.email.split('@')[0],
            analysis_data=analysis_data,
            unsubscribe_link=unsubscribe_link
        )
        
        if email_sent:
            logging.info(f"Analysis results email sent to {user.email} for analysis {analysis_id}")
            return jsonify({'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logging.error(f"Error sending analysis email: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to send email'}), 500

@app.route('/api/auth/google/test', methods=['GET'])
def test_google_config():
    return jsonify({
        'client_id_set': bool(app.config.get('GOOGLE_CLIENT_ID')),
        'client_secret_set': bool(app.config.get('GOOGLE_CLIENT_SECRET')),
        'redirect_uri': url_for('google_callback', _external=True)
    }), 200

# Stripe Payment Routes

@app.route('/api/payments/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a payment intent for custom checkout page"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name or user.email.split('@')[0]
            )
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Determine which tier to upgrade to
        tier_param = request.args.get('tier', 'pro')  # 'pro' or 'elite'

        if tier_param == 'elite':
            price = 4999  # $49.99
            tier_name = 'Elite'
        else:
            price = 999   # $9.99
            tier_name = 'Pro'

        # Create SetupIntent for subscription (handles payment method)
        setup_intent = stripe.SetupIntent.create(
            customer=user.stripe_customer_id,
            usage='off_session'
        )

        return jsonify({
            'client_secret': setup_intent.client_secret,
            'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
            'tier': tier_param,
            'tier_name': tier_name,
            'price': price / 100,  # Convert to dollars for display
            'currency': 'usd'
        }), 200

    except Exception as e:
        logging.error(f"Error creating payment intent: {str(e)}")
        return jsonify({'error': 'Failed to create payment intent'}), 500

@app.route('/api/payments/confirm-subscription', methods=['POST'])
@jwt_required()
def confirm_subscription():
    """Confirm subscription after payment method is saved"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get tier from request
        data = request.json
        tier = data.get('tier', 'pro')

        # Get the customer's saved payment method
        customer = stripe.Customer.retrieve(user.stripe_customer_id)
        if not customer.invoice_settings.default_payment_method:
            return jsonify({'error': 'No payment method found'}), 400

        # Determine price based on tier
        if tier == 'elite':
            price = 4999  # $49.99
            credits = 1000
            tier_name = 'Elite'
        else:
            price = 999   # $9.99
            credits = 100
            tier_name = 'Pro'

        # Create a subscription
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'ResumeAnalyzer AI {tier_name}',
                    },
                    'unit_amount': price,
                    'recurring': {
                        'interval': 'month',
                    },
                },
            }],
            payment_settings={
                'payment_method_types': ['card'],
                'save_default_payment_method': 'on_subscription',
            },
        )

        # Update user subscription info
        user.subscription_id = subscription.id
        user.subscription_tier = tier
        user.credits = credits
        db.session.commit()

        logging.info(f"Subscription created for user {user_id}: {subscription.id}, tier: {tier}")

        return jsonify({
            'message': 'Subscription confirmed successfully',
            'subscription_id': subscription.id,
            'tier': tier,
            'credits': credits
        }), 200

    except Exception as e:
        error_str = str(e)
        if 'Card' in type(e).__name__ or 'card' in error_str.lower():
            logging.error(f"Card error: {error_str}")
            user_message = getattr(e, 'user_message', 'Payment failed. Please check your card details.')
            return jsonify({'error': f'Payment failed: {user_message}'}), 402
    except Exception as e:
        logging.error(f"Error confirming subscription: {str(e)}")
        return jsonify({'error': 'Failed to confirm subscription'}), 500

@app.route('/api/payments/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    try:
        # Check if Stripe is configured
        if not STRIPE_API_KEY:
            logging.error("Stripe API key not configured")
            return jsonify({'error': 'Payment service is not configured. Please contact support.'}), 500
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            logging.error(f"User not found for checkout: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Determine which tier to upgrade to
        tier_param = request.args.get('tier', 'pro').lower()

        # Get Price ID from environment variables
        if tier_param == 'basic':
            price_id = STRIPE_BASIC_PRICE_ID
        elif tier_param == 'student':
            price_id = STRIPE_STUDENT_PRICE_ID
            # Verify .edu email for student plan
            if not user.email.lower().endswith('.edu'):
                return jsonify({
                    'error': 'Student plan requires a valid .edu email address',
                    'details': 'Please sign up with your educational email to access the Student plan'
                }), 403
        elif tier_param == 'pro_founding' or tier_param == 'monthly_pro':
            # Handle both monthly_pro and pro_founding as the same tier
            price_id = STRIPE_PRO_FOUNDING_PRICE_ID
            # Check founding member limit (first 100 only)
            founding_members_count = User.query.filter_by(subscription_tier='pro_founding').count()
            if founding_members_count >= 100:
                return jsonify({
                    'error': 'Founding Member tier is full',
                    'details': 'All 100 Founding Member spots have been claimed. Please choose Pro tier at $24.99/month.',
                    'alternative_tier': 'pro'
                }), 403
            # Normalize tier to pro_founding for consistency
            tier_param = 'pro_founding'
        elif tier_param == 'elite':
            price_id = STRIPE_ELITE_PRICE_ID
        else:
            price_id = STRIPE_PRO_PRICE_ID

        if not price_id:
            logging.error(f"Missing Stripe Price ID for tier: {tier_param}. BASIC_ID: {bool(STRIPE_BASIC_PRICE_ID)}, STUDENT_ID: {bool(STRIPE_STUDENT_PRICE_ID)}, PRO_ID: {bool(STRIPE_PRO_PRICE_ID)}, ELITE_ID: {bool(STRIPE_ELITE_PRICE_ID)}")
            return jsonify({
                'error': 'Payment configuration error. Please contact support.',
                'details': f'Price ID missing for {tier_param} tier'
            }), 500
        
        # Create or get Stripe customer
        # Handle case where customer ID exists in DB but not in Stripe (test/live mode mismatch)
        customer_id = user.stripe_customer_id
        if customer_id:
            try:
                # Verify customer exists in Stripe
                stripe.Customer.retrieve(customer_id)
                logging.info(f"Using existing Stripe customer for user {user_id}: {customer_id}")
            except Exception as e:
                # Customer doesn't exist in Stripe, clear it and create new one
                logging.warning(f"Stripe customer {customer_id} not found, creating new one. Error: {str(e)}")
                customer_id = None
                user.stripe_customer_id = None
                db.session.commit()
        
        if not customer_id:
            try:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.name or user.email.split('@')[0]
                )
                user.stripe_customer_id = customer.id
                customer_id = customer.id
                db.session.commit()
                logging.info(f"Created Stripe customer for user {user_id}: {customer_id}")
            except Exception as e:
                logging.error(f"Stripe customer creation error: {str(e)}")
                return jsonify({'error': 'Failed to create customer account. Please try again.'}), 500
        
        # Check if user already has a trial (honor existing trials)
        has_existing_trial = user.trial_start_date is not None and user.trial_end_date and user.trial_end_date > datetime.utcnow()
        
        # Create checkout session with actual Price ID
        # Add 7-day trial period for new subscriptions (credit card required)
        checkout_params = {
            'customer': customer_id,
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': 'subscription',
            'success_url': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=success&tier={tier_param}",
            'cancel_url': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/pricing?payment=cancel",
            'metadata': {
                'user_id': str(user_id),
                'tier': tier_param
            }
        }
        
        # Add trial period only if user doesn't have an existing trial
        if not has_existing_trial:
            checkout_params['subscription_data'] = {
                'trial_period_days': 7
            }
        
        try:
            checkout_session = stripe.checkout.Session.create(**checkout_params)
            
            logging.info(f"Checkout session created for user {user_id}, tier {tier_param}: {checkout_session.id}")
            
            return jsonify({
                'checkout_url': checkout_session.url
            }), 200
            
        except Exception as e:
            # Catch all Stripe errors (including _error module)
            error_str = str(e)
            error_type = type(e).__name__
            
            # Check if it's a Stripe error
            if 'stripe' in error_type.lower() or 'InvalidRequestError' in error_type or 'No such customer' in error_str:
                logging.error(f"Stripe error creating checkout: {error_type}: {error_str}")
                if 'No such customer' in error_str:
                    # Customer was deleted, clear it and retry
                    user.stripe_customer_id = None
                    db.session.commit()
                    return jsonify({
                        'error': 'Payment account issue. Please try again.',
                        'retry': True
                    }), 500
                return jsonify({
                    'error': 'Payment service error. Please contact support if this persists.',
                    'details': error_str if app.config.get('DEBUG') else None
                }), 500
            else:
                logging.error(f"Unexpected error creating checkout session: {error_type}: {error_str}", exc_info=True)
                return jsonify({
                    'error': 'Failed to create checkout session',
                    'details': error_str if app.config.get('DEBUG') else None
                }), 500
        
    except Exception as e:
        logging.error(f"Unexpected error creating checkout session: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to create checkout session',
            'details': str(e) if app.config.get('DEBUG') else None
        }), 500

@app.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logging.error("Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except Exception as e:
        if 'SignatureVerificationError' in type(e).__name__ or 'signature' in str(e).lower():
            logging.error("Invalid signature")
            return jsonify({'error': 'Invalid signature'}), 400
        raise
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        tier = session['metadata'].get('tier', 'pro')
        purchase_type = session['metadata'].get('purchase_type')
        guest_token = session['metadata'].get('guest_token') or None
        is_guest = session['metadata'].get('is_guest', 'false') == 'true'

        if user_id:
            user = User.query.get(int(user_id))
            
            # Handle micro-purchases (one-time payments)
            if purchase_type and session.get('mode') == 'payment':
                # This is a micro-purchase checkout session
                payment_intent_id = session.get('payment_intent')
                
                # Check if purchase already exists
                existing_purchase = Purchase.query.filter_by(
                    stripe_payment_intent_id=payment_intent_id
                ).first()
                
                if not existing_purchase and purchase_type in ['single_rescan', 'weekly_pass']:
                    from routes.payments import PRICING
                    pricing_info = PRICING.get(purchase_type, {})
                    
                    # Create purchase record
                    purchase = Purchase(
                        user_id=user.id,
                        purchase_type=purchase_type,
                        amount_usd=pricing_info.get('amount', 0) / 100,
                        credits_granted=pricing_info.get('credits', 0),
                        stripe_payment_intent_id=payment_intent_id,
                        stripe_charge_id=session.get('payment_intent'),
                        payment_status='succeeded',
                        payment_method='card'
                    )
                    
                    # Grant benefits based on purchase type
                    if purchase_type == 'single_rescan':
                        user.credits += 1
                        purchase.credits_granted = 1
                    elif purchase_type == 'weekly_pass':
                        purchase.access_expires_at = datetime.utcnow() + timedelta(days=7)
                        user.subscription_tier = 'weekly_pass'
                        user.subscription_status = 'active'
                        user.subscription_start_date = datetime.utcnow()
                    
                    db.session.add(purchase)
                    db.session.commit()
                    logging.info(f"Processed {purchase_type} purchase for user {user.id} via checkout session")

                    # Update guest session credits when present
                    if guest_token:
                        guest_session = GuestSession.query.filter_by(session_token=guest_token).first()
                        if guest_session and not guest_session.is_expired():
                            if purchase_type == 'single_rescan':
                                guest_session.credits_remaining += 1
                            elif purchase_type == 'weekly_pass':
                                guest_session.credits_remaining = max(guest_session.credits_remaining, 1000)
                                guest_session.expires_at = datetime.utcnow() + timedelta(days=7)
                            guest_session.status = 'active'
                            guest_session.last_activity = datetime.utcnow()
                            db.session.commit()
                            logging.info(f"Added guest credits for session {guest_session.id}")
                
                # Return early - don't process as subscription
                return jsonify({'status': 'success'}), 200
            if user:
                from config_manager import ConfigManager
                config_manager = ConfigManager()

                subscription_id = session.get('subscription')
                user.subscription_id = subscription_id
                # Normalize monthly_pro to pro_founding for consistency
                if tier == 'monthly_pro':
                    tier = 'pro_founding'
                user.subscription_tier = tier
                
                # Check if subscription is in trial period
                if subscription_id:
                    try:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        is_trialing = subscription.status == 'trialing'
                        
                        if is_trialing:
                            # Trial period: grant 10 credits and set trial dates
                            user.subscription_status = 'trialing'
                            user.is_trial_active = True
                            now = datetime.utcnow()
                            user.trial_start_date = now
                            user.trial_end_date = datetime.fromtimestamp(subscription.trial_end, tz=None) if subscription.trial_end else (now + timedelta(days=7))
                            user.trial_credits_granted = 10
                            user.credits = 10  # Grant 10 credits during trial
                            logging.info(f"User {user_id} started 7-day trial for {tier} tier (10 credits)")
                        else:
                            # Active subscription (trial ended or no trial)
                            user.subscription_status = 'active'
                            # Allocate credits based on tier from database
                            tier_config = config_manager.get_subscription_tier(tier)
                            if tier_config:
                                user.credits = tier_config.monthly_credits
                                logging.info(f"User {user_id} upgraded to {tier} tier ({tier_config.monthly_credits} credits)")
                            else:
                                # Fallback for backward compatibility
                                if tier == 'elite':
                                    user.credits = 1000
                                elif tier == 'pro' or tier == 'pro_founding' or tier == 'monthly_pro':
                                    # Normalize monthly_pro to pro_founding
                                    if tier == 'monthly_pro':
                                        tier = 'pro_founding'
                                        user.subscription_tier = 'pro_founding'
                                    user.credits = 100
                                else:
                                    user.credits = 20
                                logging.warning(f"Tier config not found for {tier}, using fallback credits")
                    except Exception as e:
                        logging.error(f"Error checking subscription status: {str(e)}")
                        # Fallback: assume active subscription
                        user.subscription_status = 'active'
                        tier_config = config_manager.get_subscription_tier(tier)
                        if tier_config:
                            user.credits = tier_config.monthly_credits
                        elif tier == 'elite':
                            user.credits = 1000
                        elif tier == 'pro' or tier == 'pro_founding' or tier == 'monthly_pro':
                            # Normalize monthly_pro to pro_founding
                            if tier == 'monthly_pro':
                                tier = 'pro_founding'
                                user.subscription_tier = 'pro_founding'
                            user.credits = 100
                        else:
                            user.credits = 20

                # Set subscription start date for billing anniversary
                if not user.subscription_start_date:
                    user.subscription_start_date = datetime.utcnow()

                db.session.commit()

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        subscription_id = subscription['id']
        
        # Find user by subscription ID
        user = User.query.filter_by(subscription_id=subscription_id).first()
        if user:
            # Check if trial ended and subscription is now active
            if subscription.status == 'active' and user.subscription_status == 'trialing':
                # Trial ended, subscription is now active - grant full credits
                from config_manager import ConfigManager
                config_manager = ConfigManager()
                tier = user.subscription_tier
                
                tier_config = config_manager.get_subscription_tier(tier)
                if tier_config:
                    user.credits = tier_config.monthly_credits
                else:
                    # Fallback
                    if tier == 'elite':
                        user.credits = 1000
                    elif tier == 'pro' or tier == 'pro_founding' or tier == 'monthly_pro':
                        # Normalize monthly_pro to pro_founding
                        if tier == 'monthly_pro':
                            tier = 'pro_founding'
                            user.subscription_tier = 'pro_founding'
                        user.credits = 100
                    else:
                        user.credits = 20
                
                user.subscription_status = 'active'
                user.is_trial_active = False
                db.session.commit()
                logging.info(f"User {user.id} trial ended, subscription now active ({user.credits} credits)")
            elif subscription.status == 'trialing':
                # Still in trial
                user.subscription_status = 'trialing'
                user.is_trial_active = True
                db.session.commit()
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']

        # Find user by subscription ID
        user = User.query.filter_by(subscription_id=subscription_id).first()
        if user:
            # Downgrade to free tier
            user.subscription_tier = 'free'
            user.subscription_status = 'cancelled'
            user.credits = 10  # Free tier gets 10 credits (updated from 3)
            user.subscription_id = None
            user.is_trial_active = False
            db.session.commit()

            logging.info(f"User {user.id} downgraded to free tier (10 credits)")
    
    return jsonify({'status': 'success'}), 200

@app.route('/api/billing/payment-method', methods=['GET'])
@jwt_required()
def get_payment_method():
    """Get user's payment method from Stripe"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # If user doesn't have a Stripe customer ID, return no payment method
        if not user.stripe_customer_id:
            return jsonify({'payment_method': None}), 200

        # Retrieve customer from Stripe
        customer = stripe.Customer.retrieve(user.stripe_customer_id)

        # Get default payment method
        if customer.invoice_settings.default_payment_method:
            payment_method = stripe.PaymentMethod.retrieve(
                customer.invoice_settings.default_payment_method
            )

            return jsonify({
                'payment_method': {
                    'id': payment_method.id,
                    'type': payment_method.type,
                    'card': {
                        'brand': payment_method.card.brand,
                        'last4': payment_method.card.last4,
                        'exp_month': payment_method.card.exp_month,
                        'exp_year': payment_method.card.exp_year
                    }
                }
            }), 200
        else:
            return jsonify({'payment_method': None}), 200

    except Exception as e:
        error_str = str(e)
        if 'Stripe' in type(e).__name__ or 'stripe' in str(type(e)).lower():
            logging.error(f"Stripe error retrieving payment method: {error_str}")
        else:
            logging.error(f"Error retrieving payment method: {error_str}")
        return jsonify({'error': 'Failed to retrieve payment method'}), 500

@app.route('/api/billing/history', methods=['GET'])
@jwt_required()
def get_billing_history():
    """Get user's billing history from Stripe"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # If user doesn't have a Stripe customer ID, return empty history
        if not user.stripe_customer_id:
            return jsonify({'invoices': []}), 200

        # Retrieve invoices from Stripe (last 12 months)
        invoices = stripe.Invoice.list(
            customer=user.stripe_customer_id,
            limit=12
        )

        invoice_list = []
        for invoice in invoices.data:
            invoice_list.append({
                'id': invoice.id,
                'date': invoice.created,
                'amount': invoice.amount_paid / 100,  # Convert cents to dollars
                'currency': invoice.currency.upper(),
                'status': invoice.status,
                'description': invoice.lines.data[0].description if invoice.lines.data else 'Subscription',
                'invoice_pdf': invoice.invoice_pdf,
                'hosted_invoice_url': invoice.hosted_invoice_url
            })

        return jsonify({'invoices': invoice_list}), 200

    except Exception as e:
        error_str = str(e)
        if 'Stripe' in type(e).__name__ or 'stripe' in str(type(e)).lower():
            logging.error(f"Stripe error retrieving billing history: {error_str}")
        else:
            logging.error(f"Error retrieving billing history: {error_str}")
        return jsonify({'error': 'Failed to retrieve billing history'}), 500

@app.route('/api/billing/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's subscription"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.subscription_id:
            return jsonify({'error': 'No active subscription'}), 400

        # Cancel subscription at period end
        subscription = stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=True
        )

        logging.info(f"User {user_id} scheduled subscription cancellation")

        return jsonify({
            'message': 'Subscription will be canceled at the end of the billing period',
            'cancel_at': subscription.cancel_at
        }), 200

    except Exception as e:
        error_str = str(e)
        if 'Stripe' in type(e).__name__ or 'stripe' in str(type(e)).lower():
            logging.error(f"Stripe error canceling subscription: {error_str}")
        else:
            logging.error(f"Error canceling subscription: {error_str}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500


# ============== FEEDBACK ROUTES ==============

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback (no authentication required)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'rating', 'message', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}',
                    'error_type': 'VALIDATION_ERROR'
                }), 400

        # Validate rating
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({
                'status': 'error',
                'message': 'Rating must be between 1 and 5',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Validate category
        valid_categories = ['general', 'bug', 'feature', 'support', 'praise']
        if data['category'] not in valid_categories:
            return jsonify({
                'status': 'error',
                'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Check if user is logged in (optional)
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                user_id = int(identity)
        except:
            pass

        # Create feedback entry
        feedback = Feedback(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            rating=rating,
            category=data['category'],
            message=data['message'].strip(),
            user_id=user_id
        )

        db.session.add(feedback)
        db.session.commit()

        logging.info(f"Feedback submitted: {feedback.id} from {feedback.email} ({feedback.category}, {feedback.rating}/5)")

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your feedback!',
            'feedback_id': feedback.id
        }), 201

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Invalid rating format',
            'error_type': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit feedback',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== ADMIN ROUTES ==============

@app.route('/api/admin/dashboard/stats', methods=['GET'])
@jwt_required()
def admin_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'error_type': 'UNAUTHORIZED'
            }), 403

        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        # User growth (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()

        # Total analyses
        total_analyses = Analysis.query.count()
        analyses_30d = Analysis.query.filter(Analysis.created_at >= thirty_days_ago).count()

        # Average match score
        avg_match_score = db.session.query(func.avg(Analysis.match_score)).scalar() or 0

        # Users by signup date (daily for last 30 days)
        daily_signups = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= thirty_days_ago).group_by(func.date(User.created_at)).all()

        signup_trend = [{'date': str(d[0]), 'count': d[1]} for d in daily_signups]

        # Analyses by day (last 30 days)
        daily_analyses = db.session.query(
            func.date(Analysis.created_at).label('date'),
            func.count(Analysis.id).label('count')
        ).filter(Analysis.created_at >= thirty_days_ago).group_by(
            func.date(Analysis.created_at)
        ).all()

        analyses_trend = [{'date': str(d[0]), 'count': d[1]} for d in daily_analyses]

        return jsonify({
            'status': 'success',
            'data': {
                'metrics': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'admin_users': admin_users,
                    'new_users_30d': new_users_30d,
                    'total_analyses': total_analyses,
                    'analyses_30d': analyses_30d,
                    'avg_match_score': round(avg_match_score, 2)
                },
                'trends': {
                    'signup_trend': signup_trend,
                    'analyses_trend': analyses_trend
                }
            }
        }), 200
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch dashboard stats',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """Get all users with optional filtering"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'error_type': 'UNAUTHORIZED'
            }), 403

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '', type=str)

        query = User.query

        if search:
            query = query.filter(User.email.ilike(f'%{search}%'))

        total = query.count()
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )

        return jsonify({
            'status': 'success',
            'data': {
                'users': [{
                    'id': u.id,
                    'email': u.email,
                    'is_active': u.is_active,
                    'is_admin': u.is_admin,
                    'created_at': u.created_at.isoformat(),
                    'last_login': u.last_login.isoformat() if u.last_login else None
                } for u in users.items],
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit
                }
            }
        }), 200
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch users',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== REGISTER BLUEPRINTS ==============

app.register_blueprint(health_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(config_bp)
app.register_blueprint(keyword_bp)
app.register_blueprint(skill_bp)
app.register_blueprint(market_bp)
app.register_blueprint(job_bp)
app.register_blueprint(scheduler_bp)
app.register_blueprint(linkedin_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(job_seeker_bp)
app.register_blueprint(guest_bp)
app.register_blueprint(job_matches_bp)
app.register_blueprint(interview_prep_bp)
app.register_blueprint(company_intel_bp)
app.register_blueprint(career_path_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(admin_diag_bp)
app.register_blueprint(job_applications_bp)

# Exempt health check endpoints from rate limiting
limiter.exempt(health_bp)


# ============== VERIFY CRITICAL PACKAGES ==============

def verify_critical_packages():
    """Verify that critical packages are installed"""
    missing_packages = []
    
    # Check Resend package
    try:
        import resend
        logging.info("✓ Resend package is installed")
    except ImportError:
        missing_packages.append("resend")
        logging.error("❌ CRITICAL: Resend package is NOT installed!")
        logging.error("   This will prevent email functionality from working.")
        logging.error("   Run: pip install resend")
        logging.error("   Or trigger a rebuild on Render to install from requirements.txt")
    
    if missing_packages:
        logging.error(f"Missing critical packages: {', '.join(missing_packages)}")
        logging.error("Please install missing packages or trigger a rebuild.")
    else:
        logging.info("✓ All critical packages are installed")

# ============== INITIALIZE SCHEDULER ==============

def initialize_app():
    """Initialize the application with all required services"""
    with app.app_context():
        try:
            # Initialize database
            db.create_all()
            logging.info("Database initialized successfully")

            # Initialize scheduler for background jobs (non-critical)
            try:
                init_scheduler(app)
                logging.info("Job ingestion scheduler initialized")
            except Exception as scheduler_error:
                logging.warning(f"Scheduler initialization failed (non-critical): {str(scheduler_error)}")
                logging.info("Application initialized without scheduler - API will work normally")
            
            # Initialize email automation scheduler
            try:
                init_email_scheduler(app, db, User, email_service)
                logging.info("Email automation scheduler initialized")
            except Exception as email_scheduler_error:
                logging.warning(f"Email scheduler initialization failed (non-critical): {str(email_scheduler_error)}")
                logging.info("Application initialized without email scheduler - emails will not be automated")

            # Initialize subscription management scheduler
            try:
                from scheduler import setup_scheduler
                setup_scheduler()
                logging.info("Subscription scheduler initialized (credit reset & trial expiration)")
            except Exception as subscription_scheduler_error:
                logging.warning(f"Subscription scheduler initialization failed (non-critical): {str(subscription_scheduler_error)}")
                logging.info("Application initialized without subscription scheduler - credits will not auto-reset")
        except Exception as e:
            logging.error(f"Critical error initializing application: {str(e)}")
            raise


# ============== VERIFY CRITICAL PACKAGES ==============

def verify_critical_packages():
    """Verify that critical packages are installed"""
    missing_packages = []
    
    # Check Resend package
    try:
        import resend
        logging.info("✓ Resend package is installed")
    except ImportError:
        missing_packages.append("resend")
        logging.error("❌ CRITICAL: Resend package is NOT installed!")
        logging.error("   This will prevent email functionality from working.")
        logging.error("   Run: pip install resend")
        logging.error("   Or trigger a rebuild on Render to install from requirements.txt")
    
    if missing_packages:
        logging.error(f"Missing critical packages: {', '.join(missing_packages)}")
        logging.error("Please install missing packages or trigger a rebuild.")
    else:
        logging.info("✓ All critical packages are installed")

# Verify packages before initialization
verify_critical_packages()

# Initialize on app startup
try:
    initialize_app()
except Exception as e:
    logging.error(f"Fatal initialization error: {str(e)}")
    # Continue anyway - let gunicorn handle the error


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use FLASK_ENV to control debug mode. Default to False for safety
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)