"""
Scheduler Management API Routes

Provides admin endpoints for managing scheduled job posting ingestion tasks:
- View all scheduled jobs
- Get job status
- Start/stop scheduler
- Pause/resume individual jobs
- Trigger manual job execution
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

from job_scheduler import get_scheduler
from models import User

# Create blueprint
scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/admin/scheduler')

logger = logging.getLogger(__name__)


def require_admin(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@scheduler_bp.route('/status', methods=['GET'])
@jwt_required()
@require_admin
def get_scheduler_status():
    """
    Get overall scheduler status

    Returns:
        - is_running: Whether scheduler is active
        - timestamp: Current server time
        - jobs_count: Number of scheduled jobs
    """
    try:
        scheduler = get_scheduler()

        return jsonify({
            'success': True,
            'scheduler': {
                'is_running': scheduler.is_running,
                'timestamp': datetime.utcnow().isoformat(),
                'jobs_count': len(scheduler.tasks)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        return jsonify({'error': 'Failed to get scheduler status'}), 500


@scheduler_bp.route('/start', methods=['POST'])
@jwt_required()
@require_admin
def start_scheduler():
    """
    Start the job scheduler

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if scheduler.is_running:
            return jsonify({
                'success': False,
                'message': 'Scheduler is already running'
            }), 400

        scheduler.start()

        return jsonify({
            'success': True,
            'message': 'Scheduler started successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return jsonify({'error': 'Failed to start scheduler'}), 500


@scheduler_bp.route('/stop', methods=['POST'])
@jwt_required()
@require_admin
def stop_scheduler():
    """
    Stop the job scheduler

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if not scheduler.is_running:
            return jsonify({
                'success': False,
                'message': 'Scheduler is not running'
            }), 400

        scheduler.stop()

        return jsonify({
            'success': True,
            'message': 'Scheduler stopped successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        return jsonify({'error': 'Failed to stop scheduler'}), 500


@scheduler_bp.route('/jobs', methods=['GET'])
@jwt_required()
@require_admin
def list_jobs():
    """
    Get list of all scheduled jobs

    Returns:
        - jobs: List of scheduled jobs with their status
        - count: Total number of jobs
    """
    try:
        scheduler = get_scheduler()
        jobs = scheduler.get_all_jobs()

        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        }), 200

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return jsonify({'error': 'Failed to list jobs'}), 500


@scheduler_bp.route('/jobs/<job_id>', methods=['GET'])
@jwt_required()
@require_admin
def get_job_status(job_id):
    """
    Get status of a specific job

    Args:
        job_id: Job identifier

    Returns:
        - job: Job status details
    """
    try:
        scheduler = get_scheduler()
        job = scheduler.get_job_status(job_id)

        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({
            'success': True,
            'job': job
        }), 200

    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({'error': 'Failed to get job status'}), 500


@scheduler_bp.route('/jobs/<job_id>/pause', methods=['POST'])
@jwt_required()
@require_admin
def pause_job(job_id):
    """
    Pause a scheduled job

    Args:
        job_id: Job identifier

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if job_id not in scheduler.tasks:
            return jsonify({'error': 'Job not found'}), 404

        scheduler.pause_job(job_id)

        return jsonify({
            'success': True,
            'message': f'Job {job_id} paused successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error pausing job: {str(e)}")
        return jsonify({'error': 'Failed to pause job'}), 500


@scheduler_bp.route('/jobs/<job_id>/resume', methods=['POST'])
@jwt_required()
@require_admin
def resume_job(job_id):
    """
    Resume a paused job

    Args:
        job_id: Job identifier

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if job_id not in scheduler.tasks:
            return jsonify({'error': 'Job not found'}), 404

        scheduler.resume_job(job_id)

        return jsonify({
            'success': True,
            'message': f'Job {job_id} resumed successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error resuming job: {str(e)}")
        return jsonify({'error': 'Failed to resume job'}), 500


@scheduler_bp.route('/jobs/<job_id>/trigger', methods=['POST'])
@jwt_required()
@require_admin
def trigger_job(job_id):
    """
    Manually trigger a job execution

    Args:
        job_id: Job identifier

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if job_id not in scheduler.tasks:
            return jsonify({'error': 'Job not found'}), 404

        job = scheduler.tasks[job_id]['job']

        if not job:
            return jsonify({'error': 'Job not properly initialized'}), 400

        # Get the job function and execute it
        try:
            result = job.func()
            return jsonify({
                'success': True,
                'message': f'Job {job_id} executed successfully',
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as job_error:
            logger.error(f"Job execution failed: {str(job_error)}")
            return jsonify({
                'success': False,
                'error': f'Job execution failed: {str(job_error)}'
            }), 500

    except Exception as e:
        logger.error(f"Error triggering job: {str(e)}")
        return jsonify({'error': 'Failed to trigger job'}), 500


@scheduler_bp.route('/jobs/<job_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def remove_job(job_id):
    """
    Remove a scheduled job

    Args:
        job_id: Job identifier

    Returns:
        - success: Operation result
        - message: Status message
    """
    try:
        scheduler = get_scheduler()

        if job_id not in scheduler.tasks:
            return jsonify({'error': 'Job not found'}), 404

        scheduler.remove_job(job_id)

        return jsonify({
            'success': True,
            'message': f'Job {job_id} removed successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error removing job: {str(e)}")
        return jsonify({'error': 'Failed to remove job'}), 500


@scheduler_bp.route('/config', methods=['GET'])
@jwt_required()
@require_admin
def get_scheduler_config():
    """
    Get scheduler configuration and task definitions

    Returns:
        - config: Scheduler configuration
        - default_tasks: Information about default scheduled tasks
    """
    try:
        return jsonify({
            'success': True,
            'config': {
                'scheduler_type': 'BackgroundScheduler',
                'timezone': 'UTC',
                'max_instances': 1
            },
            'default_tasks': {
                'daily_sample_ingestion': {
                    'description': 'Ingest sample job postings daily',
                    'schedule': 'Daily at 02:00 UTC',
                    'frequency': 'Once per day',
                    'retention_days': None
                },
                'refresh_market_stats': {
                    'description': 'Refresh market intelligence statistics',
                    'schedule': 'Every 24 hours',
                    'frequency': 'Once per day',
                    'retention_days': None
                },
                'cleanup_old_data': {
                    'description': 'Cleanup and archive old data',
                    'schedule': 'Weekly on Sundays at 03:00 UTC',
                    'frequency': 'Once per week',
                    'retention_days': 90
                },
                'rebuild_skill_relationships': {
                    'description': 'Rebuild skill relationship cache',
                    'schedule': 'Every 7 days',
                    'frequency': 'Once per week',
                    'retention_days': None
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting scheduler config: {str(e)}")
        return jsonify({'error': 'Failed to get scheduler config'}), 500


@scheduler_bp.route('/refresh-market-data', methods=['POST'])
@jwt_required()
@require_admin
def refresh_market_data():
    """
    Manually trigger market data refresh
    
    This endpoint runs both:
    - Real job postings ingestion from external APIs
    - Market statistics refresh
    
    Returns:
        - success: Operation result
        - jobs_result: Result from job ingestion
        - stats_result: Result from stats refresh
    """
    try:
        from scheduled_ingestion_tasks import (
            ingest_real_job_postings,
            refresh_market_statistics
        )
        
        logger.info("Manual market data refresh triggered by admin")
        
        # Run job ingestion
        jobs_result = ingest_real_job_postings()
        
        # Run stats refresh
        stats_result = refresh_market_statistics()
        
        return jsonify({
            'success': True,
            'message': 'Market data refresh completed',
            'jobs_result': jobs_result,
            'stats_result': stats_result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error refreshing market data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to refresh market data: {str(e)}'
        }), 500
