from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Analysis
from datetime import datetime, timedelta
from sqlalchemy import text, func
import logging
import os
import time

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


def check_redis_status():
    """Check Redis connection status"""
    try:
        import redis
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return 'not_configured'
        client = redis.from_url(redis_url)
        client.ping()
        return 'healthy'
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return 'unhealthy'


def check_database_latency():
    """Check database connection latency"""
    try:
        start = time.time()
        db.session.execute(text('SELECT 1'))
        latency_ms = round((time.time() - start) * 1000, 2)
        return 'healthy', latency_ms
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return 'unhealthy', -1


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint with environment diagnostics"""
    db_status, db_latency = check_database_latency()
    redis_status = check_redis_status()

    # Determine overall status
    overall_status = 'healthy'
    if db_status == 'unhealthy':
        overall_status = 'unhealthy'
    elif redis_status == 'unhealthy':
        overall_status = 'degraded'

    # Environment variable diagnostics (only essential info)
    env_diagnostics = {
        'flask_env': os.getenv('FLASK_ENV', 'production'),
        'has_jwt_secret': 'yes' if os.getenv('JWT_SECRET_KEY') else 'no',
        'has_google_oauth': 'yes' if os.getenv('GOOGLE_CLIENT_ID') else 'no',
        'has_gemini_key': 'yes' if os.getenv('GEMINI_API_KEY') else 'no',
        'has_database_url': 'yes' if os.getenv('DATABASE_URL') else 'no',
        'has_redis_url': 'yes' if os.getenv('REDIS_URL') else 'no',
        'has_stripe_key': 'yes' if os.getenv('STRIPE_SECRET_KEY') else 'no',
    }

    services = {
        'database': {'status': db_status, 'latency_ms': db_latency},
        'redis': {'status': redis_status},
    }

    return create_success_response(
        "AI Resume Optimizer API is running",
        {
            'status': overall_status,
            'services': services,
            'environment': env_diagnostics,
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
        db.session.execute(text('SELECT 1'))
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
