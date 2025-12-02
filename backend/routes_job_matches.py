"""
Job Matches API Routes - AI-powered job matching endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import subscription_required
from models import User, JobMatch, JobPosting, db
from services.job_matcher import get_job_matcher
from services import industry_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
job_matches_bp = Blueprint('job_matches', __name__, url_prefix='/api/job-matches')


@job_matches_bp.route('/', methods=['GET'])
@jwt_required()
@subscription_required
def get_job_matches():
    """
    Get AI-powered job matches for current user

    Query parameters:
        - industry: Filter by industry (optional, uses user's industry by default)
        - limit: Max matches to return (default: 20, max: 50)
        - min_score: Minimum match score (default: 50, range: 0-100)
        - refresh: Force refresh matches (default: false)
        - use_adzuna: Fetch fresh jobs from Adzuna API (default: true)

    Returns:
        List of job matches with scores, explanations, and job details
    """
    try:
        user = g.current_user
        industry = request.args.get('industry')
        limit = min(int(request.args.get('limit', 20)), 50)
        min_score = float(request.args.get('min_score', 50.0))
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        use_adzuna = request.args.get('use_adzuna', 'true').lower() == 'true'

        # Get user's industry if not specified
        if not industry:
            industry = industry_service.get_user_industry(user)

        # Get job matcher service
        matcher = get_job_matcher()

        # Generate matches (with Adzuna integration)
        matches = matcher.generate_job_matches(
            user_id=user.id,
            industry=industry,
            limit=limit,
            min_score=min_score,
            force_refresh=force_refresh,
            use_adzuna=use_adzuna
        )

        return jsonify({
            'matches': matches,
            'total': len(matches),
            'industry': industry,
            'min_score': min_score,
            'user_profile': {
                'preferred_industry': user.preferred_industry,
                'experience_level': user.experience_level,
                'detected_industries': user.detected_industries or []
            }
        }), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }), 400

    except Exception as e:
        logger.error(f"Error getting job matches: {str(e)}")
        return jsonify({
            'error': 'Failed to get job matches',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/<int:match_id>', methods=['GET'])
@jwt_required()
@subscription_required
def get_job_match_detail(match_id):
    """
    Get detailed information about a specific job match

    Returns:
        Job match with full job details
    """
    try:
        user = g.current_user

        match = JobMatch.query.filter_by(
            id=match_id,
            user_id=user.id
        ).first()

        if not match:
            return jsonify({
                'error': 'Job match not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Mark as viewed
        match.mark_viewed()
        db.session.commit()

        return jsonify(match.to_dict(include_job_details=True)), 200

    except Exception as e:
        logger.error(f"Error getting job match detail: {str(e)}")
        return jsonify({
            'error': 'Failed to get job match details',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/<int:match_id>/save', methods=['POST'])
@jwt_required()
@subscription_required
def save_job_match(match_id):
    """
    Save a job match for later review

    Returns:
        Updated job match
    """
    try:
        user = g.current_user

        match = JobMatch.query.filter_by(
            id=match_id,
            user_id=user.id
        ).first()

        if not match:
            return jsonify({
                'error': 'Job match not found',
                'error_type': 'NOT_FOUND'
            }), 404

        match.mark_saved()
        db.session.commit()

        logger.info(f"User {user.id} saved job match {match_id}")

        return jsonify({
            'message': 'Job saved successfully',
            'match': match.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error saving job match: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save job match',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/<int:match_id>/unsave', methods=['POST'])
@jwt_required()
@subscription_required
def unsave_job_match(match_id):
    """
    Remove a job from saved matches

    Returns:
        Updated job match
    """
    try:
        user = g.current_user

        match = JobMatch.query.filter_by(
            id=match_id,
            user_id=user.id
        ).first()

        if not match:
            return jsonify({
                'error': 'Job match not found',
                'error_type': 'NOT_FOUND'
            }), 404

        match.is_saved = False
        match.saved_at = None
        db.session.commit()

        logger.info(f"User {user.id} unsaved job match {match_id}")

        return jsonify({
            'message': 'Job removed from saved',
            'match': match.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error unsaving job match: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to unsave job match',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/<int:match_id>/apply', methods=['POST'])
@jwt_required()
@subscription_required
def mark_job_applied(match_id):
    """
    Mark a job as applied to

    Returns:
        Updated job match
    """
    try:
        user = g.current_user

        match = JobMatch.query.filter_by(
            id=match_id,
            user_id=user.id
        ).first()

        if not match:
            return jsonify({
                'error': 'Job match not found',
                'error_type': 'NOT_FOUND'
            }), 404

        match.mark_applied()
        db.session.commit()

        logger.info(f"User {user.id} marked job {match_id} as applied")

        return jsonify({
            'message': 'Job marked as applied',
            'match': match.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error marking job as applied: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to mark job as applied',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/saved', methods=['GET'])
@jwt_required()
@subscription_required
def get_saved_jobs():
    """
    Get all saved job matches for current user

    Returns:
        List of saved job matches
    """
    try:
        user = g.current_user

        saved_matches = JobMatch.query.filter_by(
            user_id=user.id,
            is_saved=True
        ).order_by(JobMatch.saved_at.desc()).all()

        return jsonify({
            'matches': [match.to_dict() for match in saved_matches],
            'total': len(saved_matches)
        }), 200

    except Exception as e:
        logger.error(f"Error getting saved jobs: {str(e)}")
        return jsonify({
            'error': 'Failed to get saved jobs',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/applied', methods=['GET'])
@jwt_required()
@subscription_required
def get_applied_jobs():
    """
    Get all jobs user has applied to

    Returns:
        List of applied job matches
    """
    try:
        user = g.current_user

        applied_matches = JobMatch.query.filter_by(
            user_id=user.id,
            is_applied=True
        ).order_by(JobMatch.applied_at.desc()).all()

        return jsonify({
            'matches': [match.to_dict() for match in applied_matches],
            'total': len(applied_matches)
        }), 200

    except Exception as e:
        logger.error(f"Error getting applied jobs: {str(e)}")
        return jsonify({
            'error': 'Failed to get applied jobs',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/<int:match_id>/dismiss', methods=['POST'])
@jwt_required()
@subscription_required
def dismiss_job_match(match_id):
    """
    Dismiss a job match (won't show up in future matches)

    Returns:
        Success message
    """
    try:
        user = g.current_user

        match = JobMatch.query.filter_by(
            id=match_id,
            user_id=user.id
        ).first()

        if not match:
            return jsonify({
                'error': 'Job match not found',
                'error_type': 'NOT_FOUND'
            }), 404

        match.is_dismissed = True
        db.session.commit()

        logger.info(f"User {user.id} dismissed job match {match_id}")

        return jsonify({
            'message': 'Job dismissed successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error dismissing job match: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to dismiss job match',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@job_matches_bp.route('/stats', methods=['GET'])
@jwt_required()
@subscription_required
def get_match_stats():
    """
    Get statistics about user's job matches

    Returns:
        Match statistics (total, saved, applied, avg score, etc.)
    """
    try:
        user = g.current_user

        total_matches = JobMatch.query.filter_by(user_id=user.id).count()
        saved_count = JobMatch.query.filter_by(user_id=user.id, is_saved=True).count()
        applied_count = JobMatch.query.filter_by(user_id=user.id, is_applied=True).count()

        # Average match score
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(JobMatch.match_score)).filter_by(
            user_id=user.id
        ).scalar() or 0

        # Top matches (>= 80 score)
        high_matches = JobMatch.query.filter(
            JobMatch.user_id == user.id,
            JobMatch.match_score >= 80
        ).count()

        return jsonify({
            'total_matches': total_matches,
            'saved_count': saved_count,
            'applied_count': applied_count,
            'avg_match_score': round(avg_score, 1),
            'high_matches': high_matches,
            'conversion_rate': round((applied_count / total_matches * 100), 1) if total_matches > 0 else 0
        }), 200

    except Exception as e:
        logger.error(f"Error getting match stats: {str(e)}")
        return jsonify({
            'error': 'Failed to get match statistics',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
