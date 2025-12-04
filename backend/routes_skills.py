"""
Skill Extraction API Routes

Provides endpoints for:
- Retrieving extracted skills for an analysis
- Getting skill statistics and trends
- Confirming/rejecting extracted skills (feedback loop)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

# Create blueprint
skill_bp = Blueprint('skills', __name__, url_prefix='/api/skills')

logger = logging.getLogger(__name__)


@skill_bp.route('/extract/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_extracted_skills(analysis_id):
    """
    Get all extracted skills for a specific analysis.

    Returns:
        - List of extracted skills with confidence scores
        - Grouped by extraction method for insight into extraction sources
    """
    from models import Analysis, SkillExtraction, Keyword, User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get current user to check if admin
        user = User.query.get(user_id)
        is_admin = user and user.is_admin

        # Verify user owns this analysis (or is admin)
        if is_admin:
            # Admins can see all analyses
            analysis = Analysis.query.get(analysis_id)
        else:
            # Regular users can only see their own
            analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        # Get all extracted skills for this analysis
        extractions = (
            SkillExtraction.query
            .filter_by(analysis_id=analysis_id)
            .order_by(SkillExtraction.confidence.desc())
            .all()
        )

        # Build response with skill details
        skills_by_method = {}
        total_skills = []

        for extraction in extractions:
            skill_data = {
                'id': extraction.id,
                'name': extraction.extracted_text,
                'matched_keyword_id': extraction.matched_keyword_id,
                'confidence': round(extraction.confidence, 3),
                'method': extraction.extraction_method,
                'user_confirmed': extraction.user_confirmed,
                'user_rejected': extraction.user_rejected,
                'extraction_quality': round(extraction.extraction_quality, 3) if extraction.extraction_quality else None,
                'created_at': extraction.created_at.isoformat()
            }

            # If matched to a keyword, add keyword details
            if extraction.matched_keyword_id:
                keyword = Keyword.query.get(extraction.matched_keyword_id)
                if keyword:
                    skill_data['matched_keyword'] = {
                        'id': keyword.id,
                        'name': keyword.keyword,
                        'category': keyword.category,
                        'priority': keyword.priority
                    }

            total_skills.append(skill_data)

            # Group by extraction method
            method = extraction.extraction_method or 'unknown'
            if method not in skills_by_method:
                skills_by_method[method] = []
            skills_by_method[method].append(skill_data)

        # Calculate statistics
        stats = {
            'total_extracted': len(extractions),
            'confirmed': sum(1 for e in extractions if e.user_confirmed),
            'rejected': sum(1 for e in extractions if e.user_rejected),
            'pending_feedback': sum(1 for e in extractions if e.user_confirmed is None and e.user_rejected is None),
            'average_confidence': round(sum(e.confidence for e in extractions) / len(extractions), 3) if extractions else 0,
            'by_method': {method: len(skills) for method, skills in skills_by_method.items()}
        }

        return jsonify({
            'analysis_id': analysis_id,
            'stats': stats,
            'skills': total_skills,
            'skills_by_method': skills_by_method
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving extracted skills: {str(e)}")
        return jsonify({'error': 'Failed to retrieve skills'}), 500


@skill_bp.route('/extract/<int:analysis_id>/summary', methods=['GET'])
@jwt_required()
def get_skills_summary(analysis_id):
    """
    Get a summary of extracted skills with high-level statistics.

    Returns:
        - Top extracted skills
        - Skills by confidence level (high/medium/low)
        - Method distribution
    """
    from models import Analysis, SkillExtraction, User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get current user to check if admin
        user = User.query.get(user_id)
        is_admin = user and user.is_admin

        # Verify user owns this analysis (or is admin)
        if is_admin:
            analysis = Analysis.query.get(analysis_id)
        else:
            analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        # Get all extracted skills
        extractions = SkillExtraction.query.filter_by(analysis_id=analysis_id).all()

        if not extractions:
            return jsonify({
                'analysis_id': analysis_id,
                'total': 0,
                'high_confidence': [],
                'medium_confidence': [],
                'low_confidence': [],
                'method_breakdown': {}
            }), 200

        # Categorize by confidence level
        high_conf = [e for e in extractions if e.confidence >= 0.85]
        med_conf = [e for e in extractions if 0.60 <= e.confidence < 0.85]
        low_conf = [e for e in extractions if e.confidence < 0.60]

        # Method breakdown
        methods = {}
        for e in extractions:
            method = e.extraction_method or 'unknown'
            methods[method] = methods.get(method, 0) + 1

        return jsonify({
            'analysis_id': analysis_id,
            'total': len(extractions),
            'high_confidence': {
                'count': len(high_conf),
                'skills': [e.extracted_text for e in sorted(high_conf, key=lambda x: x.confidence, reverse=True)[:10]]
            },
            'medium_confidence': {
                'count': len(med_conf),
                'skills': [e.extracted_text for e in sorted(med_conf, key=lambda x: x.confidence, reverse=True)[:10]]
            },
            'low_confidence': {
                'count': len(low_conf),
                'skills': [e.extracted_text for e in sorted(low_conf, key=lambda x: x.confidence, reverse=True)[:10]]
            },
            'method_breakdown': methods
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving skills summary: {str(e)}")
        return jsonify({'error': 'Failed to retrieve summary'}), 500


@skill_bp.route('/extract/<int:extraction_id>/feedback', methods=['POST'])
@jwt_required()
def submit_skill_feedback(extraction_id):
    """
    Submit user feedback on an extracted skill (confirm or reject).

    Request body:
        {
            "confirmed": true/false,
            "rejected": true/false
        }

    Returns:
        - Updated extraction record
        - Quality score after feedback
    """
    from models import SkillExtraction, Analysis, User
    from app import db

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Get the extraction
        extraction = SkillExtraction.query.get(extraction_id)
        if not extraction:
            return jsonify({'error': 'Extraction not found'}), 404

        # Verify user owns the analysis
        analysis = Analysis.query.filter_by(id=extraction.analysis_id, user_id=user_id).first()
        if not analysis:
            return jsonify({'error': 'Unauthorized'}), 403

        # Update feedback
        confirmed = data.get('confirmed')
        rejected = data.get('rejected')

        if confirmed and rejected:
            return jsonify({'error': 'Cannot confirm and reject simultaneously'}), 400

        if confirmed:
            extraction.user_confirmed = True
            extraction.user_rejected = False
            # Boost quality score when user confirms
            extraction.extraction_quality = min(1.0, (extraction.confidence or 0) * 1.1)
        elif rejected:
            extraction.user_confirmed = False
            extraction.user_rejected = True
            # Lower quality score when user rejects
            extraction.extraction_quality = max(0.0, (extraction.confidence or 0) * 0.7)
        else:
            return jsonify({'error': 'Must specify confirmed or rejected'}), 400

        db.session.commit()

        logger.info(f"Feedback recorded for extraction {extraction_id}: confirmed={confirmed}, rejected={rejected}")

        return jsonify({
            'id': extraction.id,
            'extracted_text': extraction.extracted_text,
            'confidence': round(extraction.confidence, 3),
            'user_confirmed': extraction.user_confirmed,
            'user_rejected': extraction.user_rejected,
            'extraction_quality': round(extraction.extraction_quality, 3) if extraction.extraction_quality else None,
            'message': 'Feedback recorded successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Failed to record feedback'}), 500


@skill_bp.route('/analyze/<int:analysis_id>/extraction-quality', methods=['GET'])
@jwt_required()
def get_extraction_quality_metrics(analysis_id):
    """
    Get quality metrics for skill extraction on an analysis.

    Returns:
        - Extraction accuracy metrics
        - Confidence distribution
        - Feedback statistics
    """
    from models import Analysis, SkillExtraction, User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get current user to check if admin
        user = User.query.get(user_id)
        is_admin = user and user.is_admin

        # Verify user owns this analysis (or is admin)
        if is_admin:
            analysis = Analysis.query.get(analysis_id)
        else:
            analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        # Get all extractions
        extractions = SkillExtraction.query.filter_by(analysis_id=analysis_id).all()

        if not extractions:
            return jsonify({
                'analysis_id': analysis_id,
                'total_extractions': 0,
                'message': 'No skills extracted'
            }), 200

        # Calculate metrics
        total = len(extractions)
        confirmed = sum(1 for e in extractions if e.user_confirmed)
        rejected = sum(1 for e in extractions if e.user_rejected)
        pending = sum(1 for e in extractions if e.user_confirmed is None and e.user_rejected is None)

        # Accuracy (if there's user feedback)
        if confirmed + rejected > 0:
            accuracy = confirmed / (confirmed + rejected)
        else:
            accuracy = None

        # Confidence statistics
        confidences = [e.confidence for e in extractions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        max_confidence = max(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0

        return jsonify({
            'analysis_id': analysis_id,
            'total_extractions': total,
            'feedback_stats': {
                'confirmed': confirmed,
                'rejected': rejected,
                'pending': pending
            },
            'accuracy_metrics': {
                'user_accuracy': round(accuracy, 3) if accuracy is not None else None,
                'confirmed_percentage': round((confirmed / total) * 100, 1) if total > 0 else 0,
                'rejected_percentage': round((rejected / total) * 100, 1) if total > 0 else 0
            },
            'confidence_metrics': {
                'average': round(avg_confidence, 3),
                'max': round(max_confidence, 3),
                'min': round(min_confidence, 3)
            },
            'extraction_methods': {
                method: sum(1 for e in extractions if e.extraction_method == method)
                for method in set(e.extraction_method for e in extractions if e.extraction_method)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving quality metrics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve metrics'}), 500


@skill_bp.route('/methods/accuracy', methods=['GET'])
@jwt_required()
def get_methods_accuracy():
    """
    Get overall accuracy metrics for all extraction methods globally.

    Returns:
        - Accuracy for each extraction method
        - Total extractions per method
        - Confirmation rates
    """
    from models import SkillExtraction
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get all extraction methods
        methods = db.session.query(
            SkillExtraction.extraction_method,
            db.func.count(SkillExtraction.id).label('total'),
            db.func.sum(db.cast(SkillExtraction.user_confirmed, db.Integer)).label('confirmed'),
            db.func.sum(db.cast(SkillExtraction.user_rejected, db.Integer)).label('rejected'),
            db.func.avg(SkillExtraction.confidence).label('avg_confidence')
        ).group_by(SkillExtraction.extraction_method).all()

        results = []
        for method, total, confirmed, rejected, avg_conf in methods:
            confirmed = confirmed or 0
            rejected = rejected or 0

            if confirmed + rejected > 0:
                accuracy = confirmed / (confirmed + rejected)
            else:
                accuracy = None

            results.append({
                'method': method or 'unknown',
                'total_extractions': total,
                'confirmed': confirmed,
                'rejected': rejected,
                'accuracy': round(accuracy, 3) if accuracy else None,
                'average_confidence': round(float(avg_conf), 3) if avg_conf else 0,
                'confirmation_rate': round((confirmed / total) * 100, 1) if total > 0 else 0
            })

        # Sort by total extractions descending
        results.sort(key=lambda x: x['total_extractions'], reverse=True)

        return jsonify({
            'extraction_methods_performance': results,
            'total_extractions_across_system': sum(r['total_extractions'] for r in results)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving methods accuracy: {str(e)}")
        return jsonify({'error': 'Failed to retrieve accuracy data'}), 500


@skill_bp.route('/relationships/skill/<int:skill_id>', methods=['GET'])
@jwt_required()
def get_skill_relationships(skill_id):
    """
    Get skills that frequently co-occur with a given skill.

    Query parameters:
        - top_n: Number of related skills to return (default: 10)
        - min_strength: Minimum co-occurrence count (default: 2)

    Returns:
        - Related skills with co-occurrence strength
        - Skill category information
    """
    from skill_relationship_analyzer import get_skill_relationship_analyzer
    from models import Keyword

    try:
        user_id = int(get_jwt_identity())

        # Verify skill exists
        keyword = Keyword.query.get(skill_id)
        if not keyword:
            return jsonify({'error': 'Skill not found'}), 404

        # Get parameters
        top_n = request.args.get('top_n', 10, type=int)
        min_strength = request.args.get('min_strength', 2, type=int)

        # Get analyzer and find relationships
        analyzer = get_skill_relationship_analyzer()
        related_skills = analyzer.get_related_skills(
            skill_id,
            top_n=top_n,
            min_strength=min_strength
        )

        return jsonify({
            'skill_id': skill_id,
            'skill_name': keyword.keyword,
            'category': keyword.category,
            'related_skills': related_skills,
            'total_related': len(related_skills)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving skill relationships: {str(e)}")
        return jsonify({'error': 'Failed to retrieve relationships'}), 500


@skill_bp.route('/relationships/analyze', methods=['GET'])
@jwt_required()
def analyze_skill_relationships():
    """
    Get overall skill relationship analysis.

    Returns:
        - Category-to-category relationships
        - Cross-domain skill associations
        - Relationship strength distribution
    """
    from skill_relationship_analyzer import get_skill_relationship_analyzer

    try:
        user_id = int(get_jwt_identity())

        # Get analyzer
        analyzer = get_skill_relationship_analyzer()

        # Analyze category relationships
        category_relationships = analyzer.analyze_skill_category_relationships()

        return jsonify({
            'category_relationships': category_relationships,
            'total_category_pairs': len(category_relationships),
            'message': 'Based on confirmed skill extractions'
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing relationships: {str(e)}")
        return jsonify({'error': 'Failed to analyze relationships'}), 500


@skill_bp.route('/relationships/recommend', methods=['POST'])
@jwt_required()
def recommend_related_skills():
    """
    Get skill recommendations based on a set of input skills.

    Request body:
        {
            "skills": ["Python", "Django", "PostgreSQL"],
            "top_n": 5
        }

    Returns:
        - List of recommended skills
        - Recommendation scores
        - Skill categories
    """
    from skill_relationship_analyzer import get_skill_relationship_analyzer

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Validate input
        skills = data.get('skills', [])
        if not skills or not isinstance(skills, list):
            return jsonify({'error': 'skills must be a non-empty array'}), 400

        if len(skills) > 20:
            return jsonify({'error': 'Maximum 20 skills allowed'}), 400

        top_n = data.get('top_n', 5)
        if top_n < 1 or top_n > 50:
            top_n = 5

        # Get recommendations
        analyzer = get_skill_relationship_analyzer()
        recommendations = analyzer.recommend_related_skills(skills, top_n=top_n)

        return jsonify({
            'input_skills': skills,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        }), 200

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500


@skill_bp.route('/relationships/persist', methods=['POST'])
@jwt_required()
def persist_skill_relationships():
    """
    Persist/update skill relationships based on current co-occurrence data.

    This endpoint should be called periodically (e.g., daily) to update
    the skill relationship graph with new co-occurrence patterns.

    Returns:
        - Number of relationships persisted
        - Last update timestamp
    """
    from skill_relationship_analyzer import get_skill_relationship_analyzer
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Only allow admin users or system operations
        from models import User
        user = User.query.get(user_id)

        # For now, allow any authenticated user (in production, restrict to admin)
        logger.info(f"User {user_id} initiated skill relationship persistence")

        # Get analyzer and persist relationships
        analyzer = get_skill_relationship_analyzer(db)
        count = analyzer.persist_skill_relationships()

        return jsonify({
            'message': 'Skill relationships updated successfully',
            'relationships_persisted': count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error persisting relationships: {str(e)}")
        return jsonify({'error': 'Failed to persist relationships'}), 500
