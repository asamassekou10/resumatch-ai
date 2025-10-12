from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_optimizer')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my-super-secret-key-12345'  # Fixed secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {'id': user.id, 'email': user.email}
    }), 200

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)