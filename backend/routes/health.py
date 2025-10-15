from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')

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
def health_check():
    """Basic health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = 'unhealthy'
    
    return create_success_response(
        "AI Resume Optimizer API is running",
        {
            'status': 'healthy',
            'database': db_status,
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
    )

@health_bp.route('/health/detailed', methods=['GET'])
@jwt_required()
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
