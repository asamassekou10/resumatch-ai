"""
Company Intel API Routes - AI-powered company research endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import subscription_required
from models import User, CompanyIntel, db
from services.company_intel_service import get_company_intel_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
company_intel_bp = Blueprint('company_intel', __name__, url_prefix='/api/company-intel')


@company_intel_bp.route('/generate', methods=['POST'])
@jwt_required()
@subscription_required
def generate_company_intel():
    """
    Generate AI-powered company intelligence

    Request body:
        {
            "company": "Google",
            "industry": "Technology",
            "refresh": false
        }

    Returns:
        Comprehensive company intelligence
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
        industry = data.get('industry')
        force_refresh = data.get('refresh', False)

        if not company or len(company) < 2:
            return jsonify({
                'error': 'Invalid company name',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Get company intel service
        service = get_company_intel_service()

        # Generate intel
        intel_data = service.generate_company_intel(
            user_id=user.id,
            company=company,
            industry=industry,
            force_refresh=force_refresh
        )

        return jsonify(intel_data), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'VALIDATION_ERROR'
        }), 400

    except Exception as e:
        logger.error(f"Error generating company intel: {str(e)}")
        return jsonify({
            'error': 'Failed to generate company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/', methods=['GET'])
@jwt_required()
@subscription_required
def get_user_company_intels():
    """
    Get all company intelligence reports for current user

    Query parameters:
        - saved_only: Return only saved reports (default: false)

    Returns:
        List of company intelligence reports
    """
    try:
        user = g.current_user
        saved_only = request.args.get('saved_only', 'false').lower() == 'true'

        query = CompanyIntel.query.filter_by(user_id=user.id)

        if saved_only:
            query = query.filter_by(is_saved=True)

        intels = query.order_by(CompanyIntel.created_at.desc()).all()

        return jsonify({
            'intels': [intel.to_dict() for intel in intels],
            'total': len(intels)
        }), 200

    except Exception as e:
        logger.error(f"Error getting company intels: {str(e)}")
        return jsonify({
            'error': 'Failed to get company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/<int:intel_id>', methods=['GET'])
@jwt_required()
@subscription_required
def get_company_intel(intel_id):
    """
    Get specific company intelligence by ID

    Returns:
        Company intelligence details
    """
    try:
        user = g.current_user

        intel = CompanyIntel.query.filter_by(
            id=intel_id,
            user_id=user.id
        ).first()

        if not intel:
            return jsonify({
                'error': 'Company intelligence not found',
                'error_type': 'NOT_FOUND'
            }), 404

        return jsonify(intel.to_dict()), 200

    except Exception as e:
        logger.error(f"Error getting company intel: {str(e)}")
        return jsonify({
            'error': 'Failed to get company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/<int:intel_id>/save', methods=['POST'])
@jwt_required()
@subscription_required
def save_company_intel(intel_id):
    """
    Save company intelligence for later review

    Returns:
        Updated intel
    """
    try:
        user = g.current_user

        intel = CompanyIntel.query.filter_by(
            id=intel_id,
            user_id=user.id
        ).first()

        if not intel:
            return jsonify({
                'error': 'Company intelligence not found',
                'error_type': 'NOT_FOUND'
            }), 404

        intel.is_saved = True
        db.session.commit()

        logger.info(f"User {user.id} saved company intel for {intel.company}")

        return jsonify({
            'message': 'Company intelligence saved successfully',
            'intel': intel.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error saving company intel: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/<int:intel_id>/unsave', methods=['POST'])
@jwt_required()
@subscription_required
def unsave_company_intel(intel_id):
    """
    Remove company intelligence from saved

    Returns:
        Updated intel
    """
    try:
        user = g.current_user

        intel = CompanyIntel.query.filter_by(
            id=intel_id,
            user_id=user.id
        ).first()

        if not intel:
            return jsonify({
                'error': 'Company intelligence not found',
                'error_type': 'NOT_FOUND'
            }), 404

        intel.is_saved = False
        db.session.commit()

        logger.info(f"User {user.id} unsaved company intel for {intel.company}")

        return jsonify({
            'message': 'Company intelligence removed from saved',
            'intel': intel.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error unsaving company intel: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to unsave company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/<int:intel_id>/notes', methods=['PUT'])
@jwt_required()
@subscription_required
def update_notes(intel_id):
    """
    Add or update personal notes for company intelligence

    Request body:
        {
            "notes": "My personal notes about this company"
        }

    Returns:
        Updated intel
    """
    try:
        user = g.current_user
        data = request.get_json()

        if not data or 'notes' not in data:
            return jsonify({
                'error': 'Notes content is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        intel = CompanyIntel.query.filter_by(
            id=intel_id,
            user_id=user.id
        ).first()

        if not intel:
            return jsonify({
                'error': 'Company intelligence not found',
                'error_type': 'NOT_FOUND'
            }), 404

        intel.notes = data['notes']
        db.session.commit()

        logger.info(f"User {user.id} updated notes for {intel.company}")

        return jsonify({
            'message': 'Notes updated successfully',
            'intel': intel.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error updating notes: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update notes',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/<int:intel_id>', methods=['DELETE'])
@jwt_required()
@subscription_required
def delete_company_intel(intel_id):
    """
    Delete company intelligence

    Returns:
        Success message
    """
    try:
        user = g.current_user

        intel = CompanyIntel.query.filter_by(
            id=intel_id,
            user_id=user.id
        ).first()

        if not intel:
            return jsonify({
                'error': 'Company intelligence not found',
                'error_type': 'NOT_FOUND'
            }), 404

        company_name = intel.company
        db.session.delete(intel)
        db.session.commit()

        logger.info(f"User {user.id} deleted company intel for {company_name}")

        return jsonify({
            'message': 'Company intelligence deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting company intel: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete company intelligence',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@company_intel_bp.route('/companies', methods=['GET'])
@jwt_required()
@subscription_required
def get_researched_companies():
    """
    Get list of companies user has researched

    Returns:
        List of company names with research counts
    """
    try:
        user = g.current_user

        intels = CompanyIntel.query.filter_by(user_id=user.id).all()

        companies = {}
        for intel in intels:
            if intel.company not in companies:
                companies[intel.company] = {
                    'company': intel.company,
                    'industry': intel.industry,
                    'last_researched': intel.created_at.isoformat(),
                    'is_saved': intel.is_saved,
                    'has_notes': bool(intel.notes)
                }

        return jsonify({
            'companies': list(companies.values()),
            'total': len(companies)
        }), 200

    except Exception as e:
        logger.error(f"Error getting researched companies: {str(e)}")
        return jsonify({
            'error': 'Failed to get companies',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
