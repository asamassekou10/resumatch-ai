"""
Interview Prep API Routes - AI-powered interview preparation endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import subscription_required
from models import User, InterviewPrep, db
from services.interview_prep_service import get_interview_prep_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
interview_prep_bp = Blueprint('interview_prep', __name__, url_prefix='/api/interview-prep')


@interview_prep_bp.route('/generate', methods=['POST'])
@jwt_required()
@subscription_required
def generate_interview_prep():
    """
    Generate AI-powered interview preparation for a company/role

    Request body:
        {
            "company": "Google",
            "job_title": "Software Engineer",
            "industry": "Technology",
            "refresh": false
        }

    Returns:
        Interview prep with questions, culture, tips, process
    """
    try:
        user = g.current_user
        data = request.get_json()

        # Validate input
        if not data or 'company' not in data:
            return jsonify({
                'error': 'Company name is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        company = data['company'].strip()
        job_title = data.get('job_title')
        industry = data.get('industry')
        force_refresh = data.get('refresh', False)

        if not company or len(company) < 2:
            return jsonify({
                'error': 'Invalid company name',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Get interview prep service
        service = get_interview_prep_service()

        # Generate prep
        prep_data = service.generate_interview_prep(
            user_id=user.id,
            company=company,
            job_title=job_title,
            industry=industry,
            force_refresh=force_refresh
        )

        return jsonify(prep_data), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }), 400

    except Exception as e:
        logger.error(f"Error generating interview prep: {str(e)}")
        return jsonify({
            'error': 'Failed to generate interview preparation',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/', methods=['GET'])
@jwt_required()
@subscription_required
def get_user_interview_preps():
    """
    Get all interview preps for current user

    Query parameters:
        - saved_only: Return only saved preps (default: false)

    Returns:
        List of interview preps
    """
    try:
        user = g.current_user
        saved_only = request.args.get('saved_only', 'false').lower() == 'true'

        query = InterviewPrep.query.filter_by(user_id=user.id)

        if saved_only:
            query = query.filter_by(is_saved=True)

        preps = query.order_by(InterviewPrep.created_at.desc()).all()

        return jsonify({
            'preps': [prep.to_dict() for prep in preps],
            'total': len(preps)
        }), 200

    except Exception as e:
        logger.error(f"Error getting interview preps: {str(e)}")
        return jsonify({
            'error': 'Failed to get interview preps',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/<int:prep_id>', methods=['GET'])
@jwt_required()
@subscription_required
def get_interview_prep(prep_id):
    """
    Get specific interview prep by ID

    Returns:
        Interview prep details
    """
    try:
        user = g.current_user

        prep = InterviewPrep.query.filter_by(
            id=prep_id,
            user_id=user.id
        ).first()

        if not prep:
            return jsonify({
                'error': 'Interview prep not found',
                'error_type': 'NOT_FOUND'
            }), 404

        return jsonify(prep.to_dict()), 200

    except Exception as e:
        logger.error(f"Error getting interview prep: {str(e)}")
        return jsonify({
            'error': 'Failed to get interview prep',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/<int:prep_id>/save', methods=['POST'])
@jwt_required()
@subscription_required
def save_interview_prep(prep_id):
    """
    Save interview prep for later review

    Returns:
        Updated prep
    """
    try:
        user = g.current_user

        prep = InterviewPrep.query.filter_by(
            id=prep_id,
            user_id=user.id
        ).first()

        if not prep:
            return jsonify({
                'error': 'Interview prep not found',
                'error_type': 'NOT_FOUND'
            }), 404

        prep.is_saved = True
        db.session.commit()

        logger.info(f"User {user.id} saved interview prep for {prep.company}")

        return jsonify({
            'message': 'Interview prep saved successfully',
            'prep': prep.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error saving interview prep: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save interview prep',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/<int:prep_id>/unsave', methods=['POST'])
@jwt_required()
@subscription_required
def unsave_interview_prep(prep_id):
    """
    Remove interview prep from saved

    Returns:
        Updated prep
    """
    try:
        user = g.current_user

        prep = InterviewPrep.query.filter_by(
            id=prep_id,
            user_id=user.id
        ).first()

        if not prep:
            return jsonify({
                'error': 'Interview prep not found',
                'error_type': 'NOT_FOUND'
            }), 404

        prep.is_saved = False
        db.session.commit()

        logger.info(f"User {user.id} unsaved interview prep for {prep.company}")

        return jsonify({
            'message': 'Interview prep removed from saved',
            'prep': prep.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error unsaving interview prep: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to unsave interview prep',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/<int:prep_id>/practice', methods=['POST'])
@jwt_required()
@subscription_required
def mark_question_practiced(prep_id):
    """
    Mark a question as practiced

    Request body:
        {
            "question_index": 0
        }

    Returns:
        Updated prep
    """
    try:
        user = g.current_user
        data = request.get_json()

        if not data or 'question_index' not in data:
            return jsonify({
                'error': 'Question index is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        question_index = data['question_index']

        prep = InterviewPrep.query.filter_by(
            id=prep_id,
            user_id=user.id
        ).first()

        if not prep:
            return jsonify({
                'error': 'Interview prep not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Validate question index
        if not prep.questions or question_index >= len(prep.questions):
            return jsonify({
                'error': 'Invalid question index',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Mark as practiced
        prep.mark_question_practiced(question_index)
        db.session.commit()

        logger.info(f"User {user.id} practiced question {question_index} for {prep.company}")

        return jsonify({
            'message': 'Question marked as practiced',
            'prep': prep.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error marking question practiced: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to mark question as practiced',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/<int:prep_id>', methods=['DELETE'])
@jwt_required()
@subscription_required
def delete_interview_prep(prep_id):
    """
    Delete interview prep

    Returns:
        Success message
    """
    try:
        user = g.current_user

        prep = InterviewPrep.query.filter_by(
            id=prep_id,
            user_id=user.id
        ).first()

        if not prep:
            return jsonify({
                'error': 'Interview prep not found',
                'error_type': 'NOT_FOUND'
            }), 404

        company_name = prep.company
        db.session.delete(prep)
        db.session.commit()

        logger.info(f"User {user.id} deleted interview prep for {company_name}")

        return jsonify({
            'message': 'Interview prep deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting interview prep: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete interview prep',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@interview_prep_bp.route('/companies', methods=['GET'])
@jwt_required()
@subscription_required
def get_prepared_companies():
    """
    Get list of companies user has prepared for

    Returns:
        List of company names with prep counts
    """
    try:
        user = g.current_user

        preps = InterviewPrep.query.filter_by(user_id=user.id).all()

        companies = {}
        for prep in preps:
            if prep.company not in companies:
                companies[prep.company] = {
                    'company': prep.company,
                    'prep_count': 0,
                    'last_prepared': prep.created_at.isoformat(),
                    'is_saved': prep.is_saved
                }
            companies[prep.company]['prep_count'] += 1

        return jsonify({
            'companies': list(companies.values()),
            'total': len(companies)
        }), 200

    except Exception as e:
        logger.error(f"Error getting prepared companies: {str(e)}")
        return jsonify({
            'error': 'Failed to get companies',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
