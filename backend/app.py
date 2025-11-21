from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from email_service import email_service
from security_config import (
    validate_email,
    validate_password,
    validate_file_upload,
    sanitize_text_input
)
import logging
import stripe

# Load environment variables
load_dotenv()

app = Flask(__name__)


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

# CORS - Strict origins only
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://resumatch-frontend.onrender.com",
            "https://resumeanalyzerai.com",
            "https://www.resumeanalyzerai.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['SECRET_KEY'] = SESSION_SECRET
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max request size

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
oauth = OAuth(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    }
)

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


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    name = db.Column(db.String(100), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    auth_provider = db.Column(db.String(20), default='email')  # 'email' or 'google'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    # Subscription and credit fields
    subscription_tier = db.Column(db.String(50), default='free', nullable=False)
    credits = db.Column(db.Integer, default=0, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True, unique=True)
    subscription_id = db.Column(db.String(255), nullable=True, unique=True)
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    match_score = db.Column(db.Float)
    keywords_found = db.Column(db.JSON)
    keywords_missing = db.Column(db.JSON)
    suggestions = db.Column(db.Text)
    resume_text = db.Column(db.Text)
    job_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_feedback = db.Column(db.Text)
    optimized_resume = db.Column(db.Text)


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
                # Set Google OAuth users as verified
                'UPDATE "user" SET email_verified = TRUE WHERE auth_provider = \'google\';'
            ]
            for command in commands:
                db.session.execute(text(command))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

auto_migrate()


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def create_verification_link(user_id, token):
    """Create verification link"""
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    return f"{frontend_url}?verify=true&user={user_id}&token={token}"

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'AI Resume Optimizer API is running'}), 200

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    data = request.json
    
    # Validate required fields
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
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
        verification_token=verification_token
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        
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
        
        return jsonify({
            'message': 'Registration successful! Please check your email to verify your account.',
            'email': email,
            'verification_required': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
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

# Google OAuth Routes
@app.route('/api/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        # Use the full URL including protocol
        redirect_uri = url_for('google_callback', _external=True)

        
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Google login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'OAuth initialization failed: {str(e)}'}), 500

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    data = request.json
    
    user_id = data.get('user_id')
    token = data.get('token')
    
    if not user_id or not token:
        return jsonify({'error': 'Invalid verification link'}), 400
    
    try:
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.email_verified:
            return jsonify({'message': 'Email already verified'}), 200
        
        # Verify token matches
        if user.verification_token != token:
            logging.warning(f"Invalid verification token for user {user.email}")
            return jsonify({'error': 'Invalid or expired verification link'}), 400
        
        # Mark as verified
        user.email_verified = True
        user.verification_token = None  # Clear token
        db.session.commit()
        
        logging.info(f"Email verified successfully for user: {user.email}")
        
        # Create access token so they can login immediately
        access_token = create_access_token(identity=str(user.id))
        
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
        
        # Check for OAuth errors first
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Authentication failed')
            frontend_url = get_frontend_url()
            from urllib.parse import quote
            return redirect(f"{frontend_url}/auth/error?message={quote(error_description)}")
        
        # Check if authorization code is present
        if 'code' not in request.args:
            frontend_url = get_frontend_url()
            return redirect(f"{frontend_url}/auth/error?message=No authorization code received")
        
        # Get the token
        token = google.authorize_access_token()
        
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
                email_verified=True
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
        logging.error(f"Google OAuth error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        frontend_url = get_frontend_url()
        from urllib.parse import quote
        error_message = str(e).replace('\n', ' ')[:200]
        return redirect(f"{frontend_url}/auth/error?message={quote(error_message)}")


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
        from ai_processor import process_resume_analysis
    except ImportError as e:
        logging.error(f"Failed to import ai_processor: {str(e)}")
        return jsonify({'error': 'AI processing module not available'}), 500
    
    try:
        # Process the analysis
        result = process_resume_analysis(resume_file, job_description)
        
        # Save to database
        analysis = Analysis(
            user_id=user_id,
            job_title=job_title,
            company_name=company_name,
            match_score=result['match_score'],
            keywords_found=result['keywords_found'],
            keywords_missing=result['keywords_missing'],
            suggestions=result['suggestions'],
            resume_text=result['resume_text'][:50000],  # Limit stored text
            job_description=job_description
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        logging.info(f"Analysis completed for user {user_id}, analysis_id: {analysis.id}")
        
        # Send email with analysis results
        try:
            user = User.query.get(user_id)
            if user and user.email:
                analysis_data = {
                    'match_score': result['match_score'],
                    'keywords_found': result['keywords_found'],
                    'keywords_missing': result['keywords_missing'],
                    'suggestions': result['suggestions'],
                    'job_title': job_title,
                    'company_name': company_name,
                    'analysis_id': analysis.id
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
        
        return jsonify({
            'analysis_id': analysis.id,
            'match_score': result['match_score'],
            'keywords_found': result['keywords_found'],
            'keywords_missing': result['keywords_missing'],
            'suggestions': result['suggestions'],
            'created_at': analysis.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Analysis failed for user {user_id}: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

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
        'subscription_tier': user.subscription_tier,
        'credits': user.credits,
        'email_verified': user.email_verified
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate feedback: {str(e)}'}), 500

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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to optimize resume: {str(e)}'}), 500

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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate cover letter: {str(e)}'}), 500

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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate suggestions: {str(e)}'}), 500

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
        logging.error(f"Error resending analysis email: {str(e)}")
        return jsonify({'error': f'Failed to resend email: {str(e)}'}), 500

@app.route('/api/auth/google/test', methods=['GET'])
def test_google_config():
    return jsonify({
        'client_id_set': bool(app.config.get('GOOGLE_CLIENT_ID')),
        'client_secret_set': bool(app.config.get('GOOGLE_CLIENT_SECRET')),
        'redirect_uri': url_for('google_callback', _external=True)
    }), 200

# Stripe Payment Routes

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
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'ResuMatch AI Pro',
                        'description': 'Monthly subscription with 20 AI credits',
                    },
                    'unit_amount': 1999,  # $19.99
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://resumeanalyzerai.com/dashboard?payment=success',
            cancel_url='https://resumeanalyzerai.com/dashboard?payment=cancel',
            metadata={
                'user_id': str(user_id)
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
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                # Update user to Pro tier
                user.subscription_tier = 'pro'
                user.credits = 20  # Grant monthly credits
                user.subscription_id = session.get('subscription')
                db.session.commit()
                
                logging.info(f"User {user.email} upgraded to Pro tier")
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']
        
        # Find user by subscription ID
        user = User.query.filter_by(subscription_id=subscription_id).first()
        if user:
            # Downgrade to free tier
            user.subscription_tier = 'free'
            user.credits = 0
            user.subscription_id = None
            db.session.commit()
            
            logging.info(f"User {user.email} downgraded to free tier")
    
    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)