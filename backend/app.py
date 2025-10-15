from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from email_service import email_service
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  # Local development
            "https://resumatch-frontend.onrender.com",  # Production
            "https://resumatch-frontend-*.onrender.com", # Any Render preview
            "https://resumeanalyzerai.com",  #Production domain
            "https://www.resumeanalyzerai.com"  
        ]
        "methods": ["GET", "POST", "PUT", "DELETE","OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        
    }
})
# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'my-super-secret-key-12345')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-for-sessions')

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
oauth = OAuth(app)

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
            print("✅ Database tables created successfully")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Available tables: {tables}")
            
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")

# Call init_db when module is loaded (works with gunicorn)
init_db()


# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'AI Resume Optimizer API is running'}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(email=data['email'], password_hash=hashed_password)
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': {'id': user.id, 'email': user.email}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id, 
            'email': user.email,
            'name': user.name,
            'auth_provider': user.auth_provider
        }
    }), 200

# Google OAuth Routes
@app.route('/api/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        # Use the full URL including protocol
        redirect_uri = url_for('google_callback', _external=True, _scheme='http')
        print(f"Redirect URI: {redirect_uri}")
        print(f"Google Client ID: {app.config.get('GOOGLE_CLIENT_ID', 'NOT SET')}")
        
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Google login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'OAuth initialization failed: {str(e)}'}), 500


@app.route('/api/auth/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        print("=== Google Callback Started ===")
        
        # Check for OAuth errors first
        error = request.args.get('error')
        if error:
            print(f"OAuth Error: {error}")
            error_description = request.args.get('error_description', 'Authentication failed')
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            from urllib.parse import quote
            return redirect(f"{frontend_url}/auth/error?message={quote(error_description)}")
        
        # Check if authorization code is present
        if 'code' not in request.args:
            print("ERROR: No authorization code in callback")
            print(f"Request args: {request.args}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/auth/error?message=No authorization code received")
        
        # Get the token
        token = google.authorize_access_token()
        print(f"Token received: {token is not None}")
        
        # Get user info
        user_info = token.get('userinfo')
        print(f"User info: {user_info}")
        
        if not user_info:
            print("ERROR: No user_info in token")
            print(f"Token keys: {token.keys() if token else 'No token'}")
            # Try alternative method to get user info
            try:
                resp = google.get('userinfo')
                user_info = resp.json()
                print(f"User info from API: {user_info}")
            except Exception as e:
                print(f"Failed to get user info from API: {str(e)}")
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                return redirect(f"{frontend_url}/auth/error?message=Failed to get user information")
        
        # Extract user information
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        print(f"Google ID: {google_id}")
        print(f"Email: {email}")
        print(f"Name: {name}")
        
        if not email:
            print("ERROR: No email provided by Google")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/auth/error?message=Email not provided by Google")
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        print(f"Existing user found: {user is not None}")
        
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
            print("Creating new user")
            user = User(
                email=email,
                google_id=google_id,
                name=name,
                profile_picture=picture,
                auth_provider='google',
                last_login=datetime.utcnow()
            )
            db.session.add(user)
        
        db.session.commit()
        print(f"User saved with ID: {user.id}")
        
        # Create JWT token
        access_token = create_access_token(identity=str(user.id))
        print(f"JWT token created: {access_token[:20]}...")
        
        # Return success response with redirect URL for frontend
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        redirect_url = f"{frontend_url}/auth/success?token={access_token}&user={user.id}"
        print(f"Redirecting to: {redirect_url}")
        return redirect(redirect_url)
        
    except Exception as e:
        logging.error(f"Google OAuth error: {str(e)}")
        print(f"=== EXCEPTION in google_callback ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

        error_message = str(e).replace(' ', '%20')
        return redirect(f"{frontend_url}/auth/error?message={error_message}")
Stashed changes
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
def analyze_resume():
    try:
        user_id = int(get_jwt_identity())
        print(f"User ID from token: {user_id}")
    except Exception as e:
        print(f"JWT Error: {str(e)}")
        return jsonify({'error': f'Authentication error: {str(e)}'}), 401
    
    if 'resume' not in request.files:
        return jsonify({'error': 'Resume file required'}), 400
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    job_title = request.form.get('job_title', '')
    company_name = request.form.get('company_name', '')
    
    if not job_description:
        return jsonify({'error': 'Job description required'}), 400
    
    # Import AI processing module
    try:
        from ai_processor import process_resume_analysis
        print("AI processor imported successfully")
    except ImportError as e:
        print(f"Failed to import ai_processor: {str(e)}")
        return jsonify({'error': f'AI processing module not available: {str(e)}'}), 500
    
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
            resume_text=result['resume_text'],
            job_description=job_description
        )
        
        db.session.add(analysis)
        db.session.commit()
        
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
                else:
                    logging.warning(f"Failed to send analysis results email to {user.email}")
                    
        except Exception as e:
            logging.error(f"Error sending analysis results email: {str(e)}")
            # Don't fail the request if email fails
        
        return jsonify({
            'analysis_id': analysis.id,
            'match_score': result['match_score'],
            'keywords_found': result['keywords_found'],
            'keywords_missing': result['keywords_missing'],
            'suggestions': result['suggestions'],
            'created_at': analysis.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

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
def generate_feedback(analysis_id):
    """Generate personalized feedback for an existing analysis"""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    try:
        from gemini_service import generate_personalized_feedback
        
        feedback = generate_personalized_feedback(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            match_score=analysis.match_score,
            keywords_found=analysis.keywords_found,
            keywords_missing=analysis.keywords_missing
        )
        
        # Save feedback to analysis
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
        print(f"❌ Error generating feedback: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate feedback: {str(e)}'}), 500

@app.route('/api/analyze/optimize/<int:analysis_id>', methods=['POST'])
@jwt_required()
def optimize_resume(analysis_id):
    """Generate optimized resume version"""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    try:
        from gemini_service import generate_optimized_resume
        
        optimized_resume = generate_optimized_resume(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            keywords_missing=analysis.keywords_missing
        )
        
        if not optimized_resume:
            return jsonify({'error': 'Failed to generate optimized resume'}), 500
        
        # Save optimized version
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
        print(f"❌ Error optimizing resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to optimize resume: {str(e)}'}), 500

@app.route('/api/analyze/cover-letter/<int:analysis_id>', methods=['POST'])
@jwt_required()
def generate_cover_letter_route(analysis_id):
    """Generate tailored cover letter"""
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
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
        print(f"❌ Error generating cover letter: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate cover letter: {str(e)}'}), 500

@app.route('/api/analyze/skill-suggestions/<int:analysis_id>', methods=['POST'])
@jwt_required()
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
        print(f"❌ Error generating suggestions: {str(e)}")
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
