from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from models import db, User, Analysis, analysis_schema, analysis_create_schema
from validators import FileValidator, TextValidator, RequestValidator, RateLimitValidator
from errors import ValidationError, NotFoundError, AIProcessingError, FileProcessingError
from ai_processor import ai_processor
from gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/v1/analysis')

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_success_response(message: str, data: dict = None, status_code: int = 200):
    """Create standardized success response"""
    response = {
        'status': 'success',
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data:
        response['data'] = data
    return jsonify(response), status_code

def get_current_user():
    """Get current user from JWT token"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        raise NotFoundError("User not found")
    if not user.is_active:
        raise ValidationError("Account is disabled")
    return user

@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def analyze_resume():
    """Analyze resume against job description"""
    try:
        user = get_current_user()
        
        # Check rate limits
        today = datetime.utcnow().date()
        analyses_today = Analysis.query.filter(
            Analysis.user_id == user.id,
            db.func.date(Analysis.created_at) == today
        ).count()
        
        RateLimitValidator.validate_analysis_rate_limit(user.id, analyses_today)
        
        # Validate file upload
        if 'resume' not in request.files:
            raise ValidationError("Resume file is required")
        
        resume_file = request.files['resume']
        FileValidator.validate_file_upload(resume_file, 'resume')
        
        # Validate form data
        form_data = RequestValidator.validate_form_request(
            ['job_description'],
            ['job_title', 'company_name']
        )
        
        job_description = TextValidator.validate_job_description(form_data['job_description'])
        job_title = TextValidator.validate_job_title(form_data.get('job_title'))
        company_name = TextValidator.validate_company_name(form_data.get('company_name'))
        
        # Process the analysis
        logger.info(f"Starting resume analysis for user {user.id}")
        result = ai_processor.process_resume_analysis(resume_file, job_description)
        
        # Save to database
        analysis = Analysis(
            user_id=user.id,
            job_title=job_title,
            company_name=company_name,
            match_score=result['match_score'],
            keywords_found=result['keywords_found'],
            keywords_missing=result['keywords_missing'],
            suggestions=result['suggestions'],
            resume_text=result['resume_text'],
            job_description=job_description,
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        logger.info(f"Analysis completed for user {user.id}, score: {result['match_score']}%")
        
        return create_success_response(
            "Analysis completed successfully",
            {
                'analysis_id': analysis.id,
                'match_score': result['match_score'],
                'keywords_found': result['keywords_found'],
                'keywords_missing': result['keywords_missing'],
                'suggestions': result['suggestions'],
                'created_at': analysis.created_at.isoformat()
            }
        )
        
    except (ValidationError, FileProcessingError, AIProcessingError) as e:
        logger.warning(f"Analysis error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        db.session.rollback()
        raise

@analysis_bp.route('/analyses', methods=['GET'])
@jwt_required()
def get_analyses():
    """Get user's analysis history"""
    try:
        user = get_current_user()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        # Query analyses with pagination
        analyses_query = Analysis.query.filter_by(user_id=user.id)\
            .order_by(Analysis.created_at.desc())
        
        pagination = analyses_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        analyses_data = []
        for analysis in pagination.items:
            analyses_data.append({
                'id': analysis.id,
                'job_title': analysis.job_title,
                'company_name': analysis.company_name,
                'match_score': analysis.match_score,
                'created_at': analysis.created_at.isoformat()
            })
        
        return create_success_response(
            "Analyses retrieved successfully",
            {
                'analyses': analyses_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Get analyses error: {e}")
        raise

@analysis_bp.route('/analyses/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get specific analysis details"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        return create_success_response(
            "Analysis retrieved successfully",
            {'analysis': analysis.to_dict()}
        )
        
    except NotFoundError as e:
        logger.warning(f"Get analysis not found: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Get analysis error: {e}")
        raise

@analysis_bp.route('/analyses/<int:analysis_id>/feedback', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def generate_feedback(analysis_id):
    """Generate AI-powered feedback for analysis"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        # Generate feedback using Gemini
        feedback = gemini_service.generate_personalized_feedback(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            match_score=analysis.match_score,
            keywords_found=analysis.keywords_found or [],
            keywords_missing=analysis.keywords_missing or []
        )
        
        if not feedback:
            raise AIProcessingError("Failed to generate feedback")
        
        # Save feedback to analysis
        analysis.ai_feedback = feedback
        analysis.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Feedback generated for analysis {analysis_id}")
        
        return create_success_response(
            "Feedback generated successfully",
            {
                'feedback': feedback,
                'analysis_id': analysis_id
            }
        )
        
    except (NotFoundError, AIProcessingError) as e:
        logger.warning(f"Generate feedback error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Generate feedback error: {e}")
        db.session.rollback()
        raise

@analysis_bp.route('/analyses/<int:analysis_id>/optimize', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def optimize_resume(analysis_id):
    """Generate optimized resume version"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        # Generate optimized resume using Gemini
        optimized_resume = gemini_service.generate_optimized_resume(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            keywords_missing=analysis.keywords_missing or []
        )
        
        if not optimized_resume:
            raise AIProcessingError("Failed to generate optimized resume")
        
        # Save optimized version
        analysis.optimized_resume = optimized_resume
        analysis.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Optimized resume generated for analysis {analysis_id}")
        
        return create_success_response(
            "Optimized resume generated successfully",
            {
                'optimized_resume': optimized_resume,
                'analysis_id': analysis_id
            }
        )
        
    except (NotFoundError, AIProcessingError) as e:
        logger.warning(f"Optimize resume error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Optimize resume error: {e}")
        db.session.rollback()
        raise

@analysis_bp.route('/analyses/<int:analysis_id>/cover-letter', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def generate_cover_letter(analysis_id):
    """Generate tailored cover letter"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        # Generate cover letter using Gemini
        cover_letter = gemini_service.generate_cover_letter(
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            company_name=analysis.company_name or "the company",
            job_title=analysis.job_title or "this position"
        )
        
        if not cover_letter:
            raise AIProcessingError("Failed to generate cover letter")
        
        logger.info(f"Cover letter generated for analysis {analysis_id}")
        
        return create_success_response(
            "Cover letter generated successfully",
            {
                'cover_letter': cover_letter,
                'analysis_id': analysis_id
            }
        )
        
    except (NotFoundError, AIProcessingError) as e:
        logger.warning(f"Generate cover letter error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Generate cover letter error: {e}")
        raise

@analysis_bp.route('/analyses/<int:analysis_id>/skill-suggestions', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def get_skill_suggestions(analysis_id):
    """Get suggestions for acquiring missing skills"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        # Generate skill suggestions using Gemini
        suggestions = gemini_service.suggest_missing_experience(
            keywords_missing=analysis.keywords_missing or [],
            resume_text=analysis.resume_text
        )
        
        if not suggestions:
            raise AIProcessingError("Failed to generate skill suggestions")
        
        logger.info(f"Skill suggestions generated for analysis {analysis_id}")
        
        return create_success_response(
            "Skill suggestions generated successfully",
            {
                'suggestions': suggestions,
                'analysis_id': analysis_id
            }
        )
        
    except (NotFoundError, AIProcessingError) as e:
        logger.warning(f"Get skill suggestions error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Get skill suggestions error: {e}")
        raise

@analysis_bp.route('/analyses/<int:analysis_id>', methods=['DELETE'])
@jwt_required()
def delete_analysis(analysis_id):
    """Delete an analysis"""
    try:
        user = get_current_user()
        
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
        if not analysis:
            raise NotFoundError("Analysis not found")
        
        db.session.delete(analysis)
        db.session.commit()
        
        logger.info(f"Analysis {analysis_id} deleted by user {user.id}")
        
        return create_success_response("Analysis deleted successfully")
        
    except NotFoundError as e:
        logger.warning(f"Delete analysis not found: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Delete analysis error: {e}")
        db.session.rollback()
        raise
