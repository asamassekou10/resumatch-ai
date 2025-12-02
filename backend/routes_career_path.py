"""
Career Path API Routes - AI-powered career roadmap endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import subscription_required
from models import User, CareerPath, db
from services.career_path_service import get_career_path_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
career_path_bp = Blueprint('career_path', __name__, url_prefix='/api/career-path')


@career_path_bp.route('/generate', methods=['POST'])
@jwt_required()
@subscription_required
def generate_career_path():
    """
    Generate AI-powered career roadmap

    Request body:
        {
            "current_role": "Software Engineer",
            "target_role": "Engineering Manager",
            "industry": "Technology",
            "years_of_experience": 5,
            "current_skills": ["Python", "Leadership"],
            "refresh": false
        }

    Returns:
        Comprehensive career path roadmap
    """
    try:
        user = g.current_user
        data = request.get_json()

        # Validate input
        if not data or 'current_role' not in data or 'target_role' not in data:
            return jsonify({
                'error': 'Current role and target role are required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        current_role = data['current_role'].strip()
        target_role = data['target_role'].strip()
        industry = data.get('industry')
        years_of_experience = data.get('years_of_experience')
        current_skills = data.get('current_skills', [])
        force_refresh = data.get('refresh', False)

        if not current_role or len(current_role) < 2:
            return jsonify({
                'error': 'Invalid current role',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        if not target_role or len(target_role) < 2:
            return jsonify({
                'error': 'Invalid target role',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Get career path service
        service = get_career_path_service()

        # Generate career path
        path_data = service.generate_career_path(
            user_id=user.id,
            current_role=current_role,
            target_role=target_role,
            industry=industry,
            years_of_experience=years_of_experience,
            current_skills=current_skills,
            force_refresh=force_refresh
        )

        return jsonify(path_data), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }), 400

    except Exception as e:
        logger.error(f"Error generating career path: {str(e)}")
        return jsonify({
            'error': 'Failed to generate career path',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/', methods=['GET'])
@jwt_required()
@subscription_required
def get_user_career_paths():
    """
    Get all career paths for current user

    Query parameters:
        - saved_only: Return only saved paths (default: false)

    Returns:
        List of career paths
    """
    try:
        user = g.current_user
        saved_only = request.args.get('saved_only', 'false').lower() == 'true'

        query = CareerPath.query.filter_by(user_id=user.id)

        if saved_only:
            query = query.filter_by(is_saved=True)

        paths = query.order_by(CareerPath.created_at.desc()).all()

        return jsonify({
            'paths': [path.to_dict() for path in paths],
            'total': len(paths)
        }), 200

    except Exception as e:
        logger.error(f"Error getting career paths: {str(e)}")
        return jsonify({
            'error': 'Failed to get career paths',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>', methods=['GET'])
@jwt_required()
@subscription_required
def get_career_path(path_id):
    """
    Get specific career path by ID

    Returns:
        Career path details
    """
    try:
        user = g.current_user

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        return jsonify(path.to_dict()), 200

    except Exception as e:
        logger.error(f"Error getting career path: {str(e)}")
        return jsonify({
            'error': 'Failed to get career path',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>/save', methods=['POST'])
@jwt_required()
@subscription_required
def save_career_path(path_id):
    """
    Save career path for later review

    Returns:
        Updated path
    """
    try:
        user = g.current_user

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        path.is_saved = True
        db.session.commit()

        logger.info(f"User {user.id} saved career path: {path.current_role} → {path.target_role}")

        return jsonify({
            'message': 'Career path saved successfully',
            'path': path.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error saving career path: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save career path',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>/unsave', methods=['POST'])
@jwt_required()
@subscription_required
def unsave_career_path(path_id):
    """
    Remove career path from saved

    Returns:
        Updated path
    """
    try:
        user = g.current_user

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        path.is_saved = False
        db.session.commit()

        logger.info(f"User {user.id} unsaved career path: {path.current_role} → {path.target_role}")

        return jsonify({
            'message': 'Career path removed from saved',
            'path': path.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error unsaving career path: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to unsave career path',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>/notes', methods=['PUT'])
@jwt_required()
@subscription_required
def update_notes(path_id):
    """
    Add or update personal notes for career path

    Request body:
        {
            "notes": "My career planning notes"
        }

    Returns:
        Updated path
    """
    try:
        user = g.current_user
        data = request.get_json()

        if not data or 'notes' not in data:
            return jsonify({
                'error': 'Notes content is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        path.notes = data['notes']
        db.session.commit()

        logger.info(f"User {user.id} updated notes for career path {path_id}")

        return jsonify({
            'message': 'Notes updated successfully',
            'path': path.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error updating notes: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update notes',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>/progress', methods=['PUT'])
@jwt_required()
@subscription_required
def update_progress(path_id):
    """
    Update progress tracking for career path steps

    Request body:
        {
            "step_key": "step_1",
            "completed": true,
            "date": "2024-01-15",
            "notes": "Completed online course"
        }

    Returns:
        Updated path with completion percentage
    """
    try:
        user = g.current_user
        data = request.get_json()

        if not data or 'step_key' not in data:
            return jsonify({
                'error': 'Step key is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update progress tracking
        if not path.progress_tracking:
            path.progress_tracking = {}

        step_key = data['step_key']
        path.progress_tracking[step_key] = {
            'completed': data.get('completed', False),
            'date': data.get('date'),
            'notes': data.get('notes', '')
        }

        # Mark as modified (for JSON column)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(path, 'progress_tracking')

        db.session.commit()

        logger.info(f"User {user.id} updated progress for step {step_key} in path {path_id}")

        return jsonify({
            'message': 'Progress updated successfully',
            'path': path.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update progress',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/<int:path_id>', methods=['DELETE'])
@jwt_required()
@subscription_required
def delete_career_path(path_id):
    """
    Delete career path

    Returns:
        Success message
    """
    try:
        user = g.current_user

        path = CareerPath.query.filter_by(
            id=path_id,
            user_id=user.id
        ).first()

        if not path:
            return jsonify({
                'error': 'Career path not found',
                'error_type': 'NOT_FOUND'
            }), 404

        transition = f"{path.current_role} → {path.target_role}"
        db.session.delete(path)
        db.session.commit()

        logger.info(f"User {user.id} deleted career path: {transition}")

        return jsonify({
            'message': 'Career path deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting career path: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete career path',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@career_path_bp.route('/transitions', methods=['GET'])
@jwt_required()
@subscription_required
def get_transitions():
    """
    Get common career transitions for current user

    Returns:
        List of transitions with metadata
    """
    try:
        user = g.current_user

        paths = CareerPath.query.filter_by(user_id=user.id).all()

        transitions = {}
        for path in paths:
            transition_key = f"{path.current_role}|{path.target_role}"
            if transition_key not in transitions:
                transitions[transition_key] = {
                    'current_role': path.current_role,
                    'target_role': path.target_role,
                    'industry': path.industry,
                    'last_viewed': path.created_at.isoformat(),
                    'is_saved': path.is_saved,
                    'has_notes': bool(path.notes),
                    'completion_percentage': path.get_completion_percentage(),
                    'estimated_duration': path.estimated_duration,
                    'difficulty_level': path.difficulty_level
                }

        return jsonify({
            'transitions': list(transitions.values()),
            'total': len(transitions)
        }), 200

    except Exception as e:
        logger.error(f"Error getting transitions: {str(e)}")
        return jsonify({
            'error': 'Failed to get transitions',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
