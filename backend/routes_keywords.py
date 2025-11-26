"""
Keyword Management API Routes

Provides endpoints for managing keywords, fuzzy matching rules, and industry-specific mappings.
Allows admins and users to manage the intelligent keyword system.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import (
    User, Keyword, KeywordSimilarity, KeywordDatabase,
    KeywordMatchingRule, UserSkillHistory, db
)
from keyword_manager import get_keyword_manager
import logging

logger = logging.getLogger(__name__)

keyword_bp = Blueprint('keywords', __name__, url_prefix='/api/keywords')


# ==================== ADMIN AUTH CHECK ====================

def require_admin():
    """Decorator to check if user is admin"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user or not user.is_admin:
                return jsonify({
                    'status': 'error',
                    'message': 'Admin access required',
                    'error_type': 'UNAUTHORIZED'
                }), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# ==================== KEYWORD ENDPOINTS ====================

@keyword_bp.route('/', methods=['GET'])
@jwt_required()
def get_keywords():
    """Get all keywords with optional filtering"""
    try:
        category = request.args.get('category')
        priority = request.args.get('priority')
        include_deprecated = request.args.get('deprecated', 'false').lower() == 'true'

        query = Keyword.query

        if not include_deprecated:
            query = query.filter_by(is_deprecated=False)

        if category:
            query = query.filter_by(category=category)

        if priority:
            query = query.filter_by(priority=priority)

        keywords = query.order_by(Keyword.category, Keyword.priority.desc()).all()

        return jsonify({
            'status': 'success',
            'data': [k.to_dict() for k in keywords],
            'count': len(keywords)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching keywords: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch keywords',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/<int:keyword_id>', methods=['GET'])
@jwt_required()
def get_keyword(keyword_id):
    """Get a specific keyword with details"""
    try:
        keyword = Keyword.query.get(keyword_id)
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': 'Keyword not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Get similar keywords
        similarities = KeywordSimilarity.query.filter_by(keyword_1_id=keyword_id).all()
        similar_data = [{
            'keyword_id': s.keyword_2_id,
            'similarity_score': s.similarity_score,
            'match_type': s.match_type
        } for s in similarities]

        return jsonify({
            'status': 'success',
            'data': {
                **keyword.to_dict(),
                'similar_keywords': similar_data
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching keyword {keyword_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch keyword',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/', methods=['POST'])
@jwt_required()
@require_admin()
def create_keyword():
    """Create a new keyword (admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('keyword') or not data.get('keyword_type') or not data.get('category'):
            return jsonify({
                'status': 'error',
                'message': 'keyword, keyword_type, and category are required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Check if keyword already exists
        existing = Keyword.query.filter_by(keyword=data['keyword'].lower()).first()
        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Keyword already exists',
                'error_type': 'DUPLICATE_ERROR'
            }), 409

        user_id = int(get_jwt_identity())
        keyword = Keyword(
            keyword=data['keyword'].lower(),
            keyword_type=data['keyword_type'],
            category=data['category'],
            priority=data.get('priority', 'medium'),
            industry_relevance=data.get('industry_relevance', {}),
            synonyms=data.get('synonyms', []),
            related_keywords=data.get('related_keywords', []),
            confidence_score=data.get('confidence_score', 1.0),
            difficulty_level=data.get('difficulty_level', 'intermediate'),
            updated_by_id=user_id
        )

        db.session.add(keyword)
        db.session.commit()

        # Clear cache
        get_keyword_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Keyword created successfully',
            'data': keyword.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating keyword: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create keyword',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/<int:keyword_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_keyword(keyword_id):
    """Update a keyword (admin only)"""
    try:
        data = request.get_json()

        keyword = Keyword.query.get(keyword_id)
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': 'Keyword not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update allowed fields
        updatable = ['keyword_type', 'category', 'priority', 'industry_relevance',
                    'synonyms', 'related_keywords', 'confidence_score', 'is_deprecated',
                    'difficulty_level', 'average_salary_premium', 'year_popularity']

        for field in updatable:
            if field in data:
                setattr(keyword, field, data[field])

        user_id = int(get_jwt_identity())
        keyword.updated_by_id = user_id
        db.session.commit()

        # Clear cache
        get_keyword_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Keyword updated successfully',
            'data': keyword.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating keyword {keyword_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update keyword',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== KEYWORD EXTRACTION AND MATCHING ====================

@keyword_bp.route('/extract', methods=['POST'])
@jwt_required()
def extract_keywords():
    """Extract and match keywords from text"""
    try:
        data = request.get_json()

        if not data.get('text'):
            return jsonify({
                'status': 'error',
                'message': 'text field is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        job_role = data.get('job_role')
        industry = data.get('industry')
        max_results = data.get('max_results', 30)
        min_score = data.get('min_score', 0.4)

        keyword_mgr = get_keyword_manager()
        results = keyword_mgr.extract_and_match_keywords(
            data['text'],
            job_role=job_role,
            industry=industry,
            max_results=max_results,
            min_score=min_score
        )

        # Format results for API
        formatted = []
        for result in results:
            formatted.append({
                'id': result['keyword'].id,
                'keyword': result['keyword'].keyword,
                'category': result['keyword'].category,
                'priority': result['keyword'].priority,
                'score': round(result['score'], 3),
                'difficulty_level': result['keyword'].difficulty_level,
                'industry_relevance': result['keyword'].industry_relevance.get(industry, 0.5) if industry else 0.5
            })

        return jsonify({
            'status': 'success',
            'data': formatted,
            'count': len(formatted)
        }), 200
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to extract keywords',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/match', methods=['POST'])
@jwt_required()
def match_keyword():
    """Match a single text to a keyword"""
    try:
        data = request.get_json()

        if not data.get('text'):
            return jsonify({
                'status': 'error',
                'message': 'text field is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        keyword_mgr = get_keyword_manager()

        # Try exact match first
        exact = keyword_mgr.get_keyword_by_text(data['text'])
        if exact:
            return jsonify({
                'status': 'success',
                'match_type': 'exact',
                'data': exact.to_dict()
            }), 200

        # Try synonym match
        synonym = keyword_mgr.find_synonym(data['text'])
        if synonym:
            return jsonify({
                'status': 'success',
                'match_type': 'synonym',
                'data': synonym.to_dict()
            }), 200

        # Try fuzzy match
        similar = keyword_mgr.find_similar_keywords(data['text'], threshold=0.75)
        if similar:
            keyword, score = similar[0]
            return jsonify({
                'status': 'success',
                'match_type': 'fuzzy',
                'confidence': round(score, 3),
                'data': keyword.to_dict()
            }), 200

        return jsonify({
            'status': 'success',
            'message': 'No keyword match found',
            'match_type': 'no_match'
        }), 200
    except Exception as e:
        logger.error(f"Error matching keyword: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to match keyword',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== MATCHING RULES ENDPOINTS ====================

@keyword_bp.route('/matching-rules', methods=['GET'])
@jwt_required()
@require_admin()
def get_matching_rules():
    """Get all fuzzy matching rules"""
    try:
        rules = KeywordMatchingRule.query.all()
        return jsonify({
            'status': 'success',
            'data': [{
                'id': r.id,
                'pattern': r.pattern,
                'normalized_keyword_id': r.normalized_keyword_id,
                'match_type': r.match_type,
                'confidence': r.confidence,
                'description': r.description
            } for r in rules],
            'count': len(rules)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching matching rules: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch matching rules',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/matching-rules', methods=['POST'])
@jwt_required()
@require_admin()
def create_matching_rule():
    """Create a fuzzy matching rule"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['pattern', 'normalized_keyword_id', 'match_type']
        if not all(field in data for field in required):
            return jsonify({
                'status': 'error',
                'message': 'pattern, normalized_keyword_id, and match_type are required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        rule = KeywordMatchingRule(
            pattern=data['pattern'],
            normalized_keyword_id=data['normalized_keyword_id'],
            match_type=data['match_type'],
            confidence=data.get('confidence', 0.9),
            description=data.get('description')
        )

        db.session.add(rule)
        db.session.commit()

        # Clear cache
        get_keyword_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Matching rule created successfully',
            'data': {
                'id': rule.id,
                'pattern': rule.pattern,
                'normalized_keyword_id': rule.normalized_keyword_id,
                'match_type': rule.match_type
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating matching rule: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create matching rule',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== JOB ROLE KEYWORDS ====================

@keyword_bp.route('/role-keywords', methods=['GET'])
@jwt_required()
def get_role_keywords():
    """Get expected keywords for a specific job role"""
    try:
        job_title = request.args.get('job_title')
        role_level = request.args.get('role_level', 'mid')
        industry = request.args.get('industry')

        if not job_title:
            return jsonify({
                'status': 'error',
                'message': 'job_title parameter is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        keyword_mgr = get_keyword_manager()
        result = keyword_mgr.get_expected_keywords_for_role(job_title, role_level, industry)

        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        logger.error(f"Error fetching role keywords: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch role keywords',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== USER FEEDBACK ====================

@keyword_bp.route('/feedback', methods=['POST'])
@jwt_required()
def record_keyword_feedback():
    """Record user feedback on keyword match"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data.get('keyword_id'):
            return jsonify({
                'status': 'error',
                'message': 'keyword_id is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        keyword_mgr = get_keyword_manager()
        keyword_mgr.record_keyword_feedback(
            user_id=user_id,
            keyword_id=data['keyword_id'],
            confirmed=data.get('confirmed'),
            rejected=data.get('rejected'),
            analysis_id=data.get('analysis_id'),
            context=data.get('context')
        )

        return jsonify({
            'status': 'success',
            'message': 'Feedback recorded successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to record feedback',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@keyword_bp.route('/user-history', methods=['GET'])
@jwt_required()
def get_user_skill_history():
    """Get user's confirmed and rejected keywords"""
    try:
        user_id = int(get_jwt_identity())
        keyword_mgr = get_keyword_manager()
        history = keyword_mgr.get_user_skill_history(user_id)

        return jsonify({
            'status': 'success',
            'data': history
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch user history',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== STATISTICS ====================

@keyword_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_admin()
def get_keyword_stats():
    """Get keyword system statistics"""
    try:
        keyword_mgr = get_keyword_manager()
        stats = keyword_mgr.get_keyword_stats()

        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        logger.error(f"Error fetching keyword stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch keyword stats',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
