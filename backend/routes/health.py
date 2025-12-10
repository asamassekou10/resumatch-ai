from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from datetime import datetime
from sqlalchemy import text
import logging
import os

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')

# Import limiter to exempt health endpoints
from app import limiter

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

@health_bp.route('/health', methods=['GET'])
@limiter.exempt
def health_check():
    """Basic health check endpoint with environment diagnostics"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f'unhealthy: {str(e)}'

    # Environment variable diagnostics
    env_diagnostics = {
        'flask_env': os.getenv('FLASK_ENV', 'not set'),
        'frontend_url': os.getenv('FRONTEND_URL', 'not set'),
        'backend_url': os.getenv('BACKEND_URL', 'not set'),
        'has_jwt_secret': 'yes' if os.getenv('JWT_SECRET_KEY') else 'no',
        'has_google_oauth': 'yes' if os.getenv('GOOGLE_CLIENT_ID') else 'no',
        'has_gemini_key': 'yes' if os.getenv('GEMINI_API_KEY') else 'no',
        'has_database_url': 'yes' if os.getenv('DATABASE_URL') else 'no',
        'has_adzuna_keys': 'yes' if (os.getenv('ADZUNA_APP_ID') and os.getenv('ADZUNA_APP_KEY')) else 'no',
    }

    return create_success_response(
        "AI Resume Optimizer API is running",
        {
            'status': 'healthy',
            'database': db_status,
            'environment': env_diagnostics,
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
    )

@health_bp.route('/health/detailed', methods=['GET'])
@jwt_required()
@limiter.exempt
def detailed_health_check():
    """Detailed health check for authenticated users"""
    try:
        user = User.query.get(int(get_jwt_identity()))
        
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
        
        # Test user access
        user_status = 'healthy' if user else 'unhealthy'
        
        return create_success_response(
            "Detailed health check completed",
            {
                'status': 'healthy',
                'database': db_status,
                'user_access': user_status,
                'version': '2.0.0',
                'features': {
                    'ai_processing': 'enabled',
                    'file_upload': 'enabled',
                    'analysis_caching': 'enabled'
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return create_success_response(
            "Health check completed with issues",
            {
                'status': 'degraded',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            },
            503
        )
