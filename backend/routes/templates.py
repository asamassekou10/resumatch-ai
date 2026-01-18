"""
Template Routes - API endpoints for resume/cover letter templates and PDF generation.
"""

import io
import logging
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Analysis
from templates.config import get_template_list, RESUME_TEMPLATES, COVER_LETTER_TEMPLATES
from templates.resume_parser import resume_parser
from templates.pdf_generator import pdf_generator

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__, url_prefix='/api')


# ============================================================================
# Template Listing Endpoints
# ============================================================================

@templates_bp.route('/templates/resume', methods=['GET'])
def get_resume_templates():
    """Get list of available resume templates."""
    try:
        templates = get_template_list('resume')
        return jsonify({
            'status': 'success',
            'data': {
                'templates': templates
            }
        })
    except Exception as e:
        logger.error(f"Error fetching resume templates: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch templates'
        }), 500


@templates_bp.route('/templates/cover-letter', methods=['GET'])
def get_cover_letter_templates():
    """Get list of available cover letter templates."""
    try:
        templates = get_template_list('cover-letter')
        return jsonify({
            'status': 'success',
            'data': {
                'templates': templates
            }
        })
    except Exception as e:
        logger.error(f"Error fetching cover letter templates: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch templates'
        }), 500


# ============================================================================
# Resume Parsing Endpoints
# ============================================================================

@templates_bp.route('/analyze/<int:analysis_id>/parse-resume', methods=['POST'])
@jwt_required()
def parse_resume(analysis_id):
    """
    Parse optimized resume into structured format for template rendering.
    Uses AI to extract contact, experience, education, skills, etc.
    """
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({
                'status': 'error',
                'message': 'Analysis not found'
            }), 404

        # Check if we have an optimized resume to parse
        resume_text = analysis.optimized_resume or analysis.resume_text

        if not resume_text:
            return jsonify({
                'status': 'error',
                'message': 'No resume text available. Please generate an optimized resume first.'
            }), 400

        # Parse the resume
        logger.info(f"Parsing resume for analysis {analysis_id}")
        structured_resume = resume_parser.parse_resume(resume_text)

        # Save to database
        analysis.structured_resume = structured_resume
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Resume parsed successfully',
            'data': {
                'structured_resume': structured_resume
            }
        })

    except ValueError as e:
        logger.warning(f"Validation error parsing resume: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error parsing resume for analysis {analysis_id}: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to parse resume. Please try again.'
        }), 500


@templates_bp.route('/analyze/<int:analysis_id>/structured-resume', methods=['GET'])
@jwt_required()
def get_structured_resume(analysis_id):
    """Get the parsed/structured resume data."""
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({
                'status': 'error',
                'message': 'Analysis not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'structured_resume': analysis.structured_resume,
                'has_optimized_resume': bool(analysis.optimized_resume),
                'has_cover_letter': bool(analysis.cover_letter),
                'job_title': analysis.job_title,
                'company_name': analysis.company_name,
                'selected_resume_template': analysis.selected_resume_template,
                'selected_cover_letter_template': analysis.selected_cover_letter_template
            }
        })

    except Exception as e:
        logger.error(f"Error fetching structured resume: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch resume data'
        }), 500


@templates_bp.route('/analyze/<int:analysis_id>/structured-resume', methods=['PUT'])
@jwt_required()
def update_structured_resume(analysis_id):
    """
    Update the structured resume data (after user edits).
    """
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({
                'status': 'error',
                'message': 'Analysis not found'
            }), 404

        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        # Update structured resume
        if 'structured_resume' in data:
            analysis.structured_resume = data['structured_resume']

        # Update template selections if provided
        if 'selected_resume_template' in data:
            template_id = data['selected_resume_template']
            if template_id in RESUME_TEMPLATES:
                analysis.selected_resume_template = template_id

        if 'selected_cover_letter_template' in data:
            template_id = data['selected_cover_letter_template']
            if template_id in COVER_LETTER_TEMPLATES:
                analysis.selected_cover_letter_template = template_id

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Resume data updated successfully',
            'data': {
                'structured_resume': analysis.structured_resume
            }
        })

    except Exception as e:
        logger.error(f"Error updating structured resume: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update resume data'
        }), 500


# ============================================================================
# PDF Generation Endpoints
# ============================================================================

@templates_bp.route('/analyze/<int:analysis_id>/download-pdf', methods=['POST'])
@jwt_required()
def download_pdf(analysis_id):
    """
    Generate and download a PDF (resume or cover letter).

    Request body:
    {
        "document_type": "resume" | "cover_letter",
        "template_id": "modern" | "classic" | "professional" | "simple"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({
                'status': 'error',
                'message': 'Analysis not found'
            }), 404

        data = request.get_json() or {}
        document_type = data.get('document_type', 'resume')
        template_id = data.get('template_id')

        if document_type == 'resume':
            return _generate_resume_pdf(analysis, template_id)
        elif document_type == 'cover_letter':
            return _generate_cover_letter_pdf(analysis, template_id)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid document type. Use "resume" or "cover_letter".'
            }), 400

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate PDF: {str(e)}'
        }), 500


def _generate_resume_pdf(analysis: Analysis, template_id: str = None):
    """Generate resume PDF."""
    if not analysis.structured_resume:
        return jsonify({
            'status': 'error',
            'message': 'Resume not parsed. Please parse the resume first.'
        }), 400

    # Use provided template or saved preference
    template_id = template_id or analysis.selected_resume_template or 'modern'

    # Validate template
    if template_id not in RESUME_TEMPLATES:
        template_id = 'modern'

    # Generate PDF
    pdf_bytes = pdf_generator.generate_resume_pdf(
        analysis.structured_resume,
        template_id
    )

    # Create filename
    contact_name = analysis.structured_resume.get('contact', {}).get('name', 'resume')
    safe_name = ''.join(c for c in contact_name if c.isalnum() or c in ' -_').strip()
    filename = f"{safe_name or 'resume'}_{template_id}.pdf"

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def _generate_cover_letter_pdf(analysis: Analysis, template_id: str = None):
    """Generate cover letter PDF."""
    if not analysis.cover_letter:
        return jsonify({
            'status': 'error',
            'message': 'No cover letter available. Please generate one first.'
        }), 400

    # Get contact info from structured resume or create minimal contact
    contact = {}
    if analysis.structured_resume:
        contact = analysis.structured_resume.get('contact', {})

    # Use provided template or saved preference
    template_id = template_id or analysis.selected_cover_letter_template or 'professional'

    # Validate template
    if template_id not in COVER_LETTER_TEMPLATES:
        template_id = 'professional'

    # Generate PDF
    pdf_bytes = pdf_generator.generate_cover_letter_pdf(
        cover_letter_text=analysis.cover_letter,
        contact=contact,
        job_title=analysis.job_title or 'Position',
        company_name=analysis.company_name or 'Company',
        template_id=template_id
    )

    # Create filename
    company_name = analysis.company_name or 'company'
    safe_company = ''.join(c for c in company_name if c.isalnum() or c in ' -_').strip()
    filename = f"cover_letter_{safe_company or 'company'}_{template_id}.pdf"

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


# ============================================================================
# HTML Preview Endpoints (for frontend preview)
# ============================================================================

@templates_bp.route('/analyze/<int:analysis_id>/preview-html', methods=['POST'])
@jwt_required()
def preview_html(analysis_id):
    """
    Generate HTML preview for frontend display.

    Request body:
    {
        "document_type": "resume" | "cover_letter",
        "template_id": "modern" | "classic" | etc.
    }
    """
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({
                'status': 'error',
                'message': 'Analysis not found'
            }), 404

        data = request.get_json() or {}
        document_type = data.get('document_type', 'resume')
        template_id = data.get('template_id', 'modern')

        if document_type == 'resume':
            if not analysis.structured_resume:
                return jsonify({
                    'status': 'error',
                    'message': 'Resume not parsed yet'
                }), 400

            html = pdf_generator.preview_html(
                analysis.structured_resume,
                template_id
            )
        elif document_type == 'cover_letter':
            if not analysis.cover_letter:
                return jsonify({
                    'status': 'error',
                    'message': 'No cover letter available'
                }), 400

            contact = {}
            if analysis.structured_resume:
                contact = analysis.structured_resume.get('contact', {})

            html = pdf_generator.preview_cover_letter_html(
                analysis.cover_letter,
                contact,
                analysis.job_title or 'Position',
                analysis.company_name or 'Company',
                template_id
            )
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid document type'
            }), 400

        return jsonify({
            'status': 'success',
            'data': {
                'html': html
            }
        })

    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate preview'
        }), 500
