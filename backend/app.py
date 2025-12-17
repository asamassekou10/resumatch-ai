from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
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
    sanitize_text_input
)
from sqlalchemy import func
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
from routes.health import health_bp
from routes_admin_diagnostics import admin_diag_bp
from scheduled_ingestion_tasks import init_scheduler
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
allowed_origins = [
    "http://localhost:3000",
    frontend_url,
    "https://resumatch-frontend.onrender.com",
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['SECRET_KEY'] = SESSION_SECRET
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max request size
app.config['PREFERRED_URL_SCHEME'] = 'https'  # Force HTTPS URL generation

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Stripe Configuration
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY
    if not STRIPE_WEBHOOK_SECRET:
        app.logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook validation will not work")
else:
    app.logger.warning("STRIPE_SECRET_KEY not configured - payment features will not work")

# Import db from models to use the same instance for all models
from models import db
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
oauth = OAuth(app)

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

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
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
from models import User, Analysis, GuestSession, GuestAnalysis


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
init_db()

def auto_migrate():
    """Automatically add missing columns if they don't exist"""
    with app.app_context():
        try:
            from sqlalchemy import text
            commands = [
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS name VARCHAR(100);',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS google_id VARCHAR(100);',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT \'email\';',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;',
                'ALTER TABLE "user" ALTER COLUMN password_hash DROP NOT NULL;',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);',
                # Subscription and credit fields
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT \'free\';',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 0;',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_id VARCHAR(255);',
                # Admin fields
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;',
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;',
                # Set Google OAuth users as verified
                'UPDATE "user" SET email_verified = TRUE WHERE auth_provider = \'google\';'
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
    user = User(
        email=email,
        password_hash=hashed_password,
        auth_provider='email',
        email_verified=False,  # Not verified yet
        verification_token=verification_token,
        credits=5  # Free users get 5 initial credits
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

        # Send verification email
        email_sent = email_service.send_verification_email(
            recipient_email=email,
            recipient_name=email.split('@')[0],
            verification_link=verification_link
        )

        if email_sent:
            logging.info(f"New user registered: {email}, verification email sent")
        else:
            logging.warning(f"User registered but verification email failed: {email}")

        response = {
            'message': 'Registration successful! Please check your email to verify your account.',
            'email': email,
            'verification_required': True
        }

        if transferred_count > 0:
            response['analyses_transferred'] = transferred_count

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

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
        user.last_login = datetime.utcnow()
        db.session.commit()

        logging.info(f"Successful login: {email}")

        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'auth_provider': user.auth_provider,
                'email_verified': user.email_verified,
                'subscription_tier': user.subscription_tier,
                'credits': user.credits
            }
        }), 200

    except Exception as e:
        logging.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed. Please try again.'}), 500

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
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                name=name,
                profile_picture=picture,
                auth_provider='google',
                last_login=datetime.utcnow(),
                email_verified=True,
                credits=5  # Free users get 5 initial credits
            )
            db.session.add(user)
        
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
    """Logout user (client-side token removal)"""
    # In JWT, logout is typically handled client-side by removing the token
    # But we can log the logout event
    user_id = get_jwt_identity()
    logging.info(f"User {user_id} logged out")
    
    return jsonify({'message': 'Logged out successfully'}), 200

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
        
        # Send email with analysis results
        try:
            user = User.query.get(user_id)
            if user and user.email:
                # Prepare new analysis data format
                recommendations = result.get('recommendations', {})
                priority_improvements = recommendations.get('priority_improvements', [])

                analysis_data = {
                    'match_score': result.get('overall_score', 0),
                    'interpretation': result.get('interpretation', ''),
                    'keywords_found': keywords_found[:10],
                    'keywords_missing': keywords_missing[:10],
                    'suggestions': result.get('interpretation', ''),
                    'priority_improvements': priority_improvements[:3] if priority_improvements else [],
                    'job_title': job_title,
                    'company_name': company_name,
                    'analysis_id': analysis.id,
                    'industry': result.get('job_industry', 'Unknown'),
                    'ats_pass_rate': result.get('expected_ats_pass_rate', 'N/A')
                }

                email_sent = email_service.send_analysis_results(
                    recipient_email=user.email,
                    recipient_name=user.name or user.email.split('@')[0],
                    analysis_data=analysis_data
                )

                if email_sent:
                    logging.info(f"Analysis results email sent to {user.email}")

        except Exception as e:
            logging.error(f"Error sending analysis results email: {str(e)}")

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
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'job_title': a.job_title,
        'company_name': a.company_name,
        'match_score': a.match_score,
        'resume_filename': a.resume_filename,
        'created_at': a.created_at.isoformat()
    } for a in analyses]), 200

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
        'is_active': user.is_active
    }), 200

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    user_id = int(get_jwt_identity())
    analyses = Analysis.query.filter_by(user_id=user_id).all()
    
    if not analyses:
        return jsonify({
            'total_analyses': 0,
            'average_score': 0,
            'score_trend': [],
            'top_missing_skills': []
        }), 200
    
    # Calculate statistics
    total = len(analyses)
    avg_score = sum(a.match_score for a in analyses) / total
    
    # Score trend (last 10 analyses)
    score_trend = [{
        'date': a.created_at.isoformat(),
        'score': a.match_score,
        'job_title': a.job_title
    } for a in sorted(analyses, key=lambda x: x.created_at)[-10:]]
    
    # Aggregate missing skills
    skill_counts = {}
    for a in analyses:
        for skill in a.keywords_missing:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_missing = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'total_analyses': total,
        'average_score': round(avg_score, 2),
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
                
                email_sent = email_service.send_analysis_results(
                    recipient_email=user.email,
                    recipient_name=user.name or user.email.split('@')[0],
                    analysis_data=feedback_data
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

@app.route('/api/analyses/<int:analysis_id>/resend-email', methods=['POST'])
@jwt_required()
def resend_analysis_email(analysis_id):
    """Manually resend analysis results via email"""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    try:
        user = User.query.get(user_id)
        if not user or not user.email:
            return jsonify({'error': 'User email not found'}), 400
        
        # Prepare analysis data
        analysis_data = {
            'match_score': analysis.match_score,
            'keywords_found': analysis.keywords_found,
            'keywords_missing': analysis.keywords_missing,
            'suggestions': analysis.suggestions,
            'ai_feedback': analysis.ai_feedback,
            'job_title': analysis.job_title,
            'company_name': analysis.company_name,
            'analysis_id': analysis_id
        }
        
        email_sent = email_service.send_analysis_results(
            recipient_email=user.email,
            recipient_name=user.name or user.email.split('@')[0],
            analysis_data=analysis_data
        )
        
        if email_sent:
            return jsonify({'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logging.error(f"Error resending analysis email: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to resend email'}), 500

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
                        'name': f'ResuMatch AI {tier_name}',
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

    except stripe.error.CardError as e:
        logging.error(f"Card error: {str(e)}")
        return jsonify({'error': f'Payment failed: {e.user_message}'}), 402
    except Exception as e:
        logging.error(f"Error confirming subscription: {str(e)}")
        return jsonify({'error': 'Failed to confirm subscription'}), 500

@app.route('/api/payments/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create Stripe checkout session for Pro subscription"""
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
            # Elite tier: 1000 credits/month at $49.99
            price = 4999
            description = 'Monthly subscription - 1000 AI credits'
            tier_name = 'Elite'
        else:
            # Pro tier: 100 credits/month at $9.99
            price = 999
            description = 'Monthly subscription - 100 AI credits'
            tier_name = 'Pro'

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'ResumeAnalyzer AI {tier_name}',
                        'description': description,
                    },
                    'unit_amount': price,
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=success",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=cancel",
            metadata={
                'user_id': str(user_id),
                'tier': tier_param
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

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
    except stripe.error.SignatureVerificationError:
        logging.error("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        tier = session['metadata'].get('tier', 'pro')

        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_id = session.get('subscription')

                # Allocate credits based on tier
                if tier == 'elite':
                    user.subscription_tier = 'elite'
                    user.credits = 1000  # 1000 credits/month for Elite
                    logging.info(f"User {user_id} upgraded to Elite tier (1000 credits)")
                else:
                    user.subscription_tier = 'pro'
                    user.credits = 100  # 100 credits/month for Pro
                    logging.info(f"User {user_id} upgraded to Pro tier (100 credits)")

                db.session.commit()

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']

        # Find user by subscription ID
        user = User.query.filter_by(subscription_id=subscription_id).first()
        if user:
            # Downgrade to free tier
            user.subscription_tier = 'free'
            user.credits = 5  # Free tier gets 5 credits
            user.subscription_id = None
            db.session.commit()

            logging.info(f"User {user.id} downgraded to free tier (5 credits)")
    
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

    except stripe.error.StripeError as e:
        logging.error(f"Stripe error retrieving payment method: {str(e)}")
        return jsonify({'error': 'Failed to retrieve payment method'}), 500
    except Exception as e:
        logging.error(f"Error retrieving payment method: {str(e)}")
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

    except stripe.error.StripeError as e:
        logging.error(f"Stripe error retrieving billing history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve billing history'}), 500
    except Exception as e:
        logging.error(f"Error retrieving billing history: {str(e)}")
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

    except stripe.error.StripeError as e:
        logging.error(f"Stripe error canceling subscription: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500
    except Exception as e:
        logging.error(f"Error canceling subscription: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500


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
app.register_blueprint(admin_diag_bp)

# Exempt health check endpoints from rate limiting
limiter.exempt(health_bp)


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
                logging.info("Application initialized successfully")
            except Exception as scheduler_error:
                logging.warning(f"Scheduler initialization failed (non-critical): {str(scheduler_error)}")
                logging.info("Application initialized without scheduler - API will work normally")
        except Exception as e:
            logging.error(f"Critical error initializing application: {str(e)}")
            raise


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