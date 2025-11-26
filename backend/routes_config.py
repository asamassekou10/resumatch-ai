"""
Configuration Management API Routes

Allows admins to manage system configurations, subscription tiers, rate limits, and scoring thresholds.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import (
    User, SystemConfiguration, SubscriptionTier, RateLimitConfig,
    ScoringThreshold, ValidationRule, db
)
from config_manager import get_config_manager
import logging

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__, url_prefix='/api/admin/config')


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


# ==================== SYSTEM CONFIGURATION ENDPOINTS ====================

@config_bp.route('/system', methods=['GET'])
@jwt_required()
@require_admin()
def get_system_configs():
    """Get all system configurations"""
    try:
        configs = SystemConfiguration.query.all()
        return jsonify({
            'status': 'success',
            'data': [c.to_dict() for c in configs]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching system configs: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch configurations',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/system/<string:config_key>', methods=['GET'])
@jwt_required()
@require_admin()
def get_system_config(config_key):
    """Get a specific system configuration"""
    try:
        config = SystemConfiguration.query.filter_by(config_key=config_key).first()
        if not config:
            return jsonify({
                'status': 'error',
                'message': 'Configuration not found',
                'error_type': 'NOT_FOUND'
            }), 404

        return jsonify({
            'status': 'success',
            'data': config.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching config {config_key}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch configuration',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/system/<string:config_key>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_system_config(config_key):
    """Update a system configuration"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or 'config_value' not in data:
            return jsonify({
                'status': 'error',
                'message': 'config_value is required',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        config = SystemConfiguration.query.filter_by(config_key=config_key).first()
        if not config:
            return jsonify({
                'status': 'error',
                'message': 'Configuration not found',
                'error_type': 'NOT_FOUND'
            }), 404

        if not config.is_editable:
            return jsonify({
                'status': 'error',
                'message': 'This configuration cannot be edited',
                'error_type': 'FORBIDDEN'
            }), 403

        config.config_value = data['config_value']
        config.updated_by_id = user_id
        db.session.commit()

        # Clear cache
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Configuration updated successfully',
            'data': config.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating config {config_key}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update configuration',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== SUBSCRIPTION TIER ENDPOINTS ====================

@config_bp.route('/tiers', methods=['GET'])
@jwt_required()
@require_admin()
def get_subscription_tiers():
    """Get all subscription tiers"""
    try:
        tiers = SubscriptionTier.query.order_by(SubscriptionTier.position).all()
        return jsonify({
            'status': 'success',
            'data': [t.to_dict() for t in tiers]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching tiers: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch subscription tiers',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/tiers/<string:tier_name>', methods=['GET'])
@jwt_required()
@require_admin()
def get_subscription_tier(tier_name):
    """Get a specific subscription tier"""
    try:
        tier = SubscriptionTier.query.filter_by(name=tier_name).first()
        if not tier:
            return jsonify({
                'status': 'error',
                'message': 'Subscription tier not found',
                'error_type': 'NOT_FOUND'
            }), 404

        return jsonify({
            'status': 'success',
            'data': tier.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching tier {tier_name}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch subscription tier',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/tiers/<string:tier_name>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_subscription_tier(tier_name):
    """Update a subscription tier"""
    try:
        data = request.get_json()

        tier = SubscriptionTier.query.filter_by(name=tier_name).first()
        if not tier:
            return jsonify({
                'status': 'error',
                'message': 'Subscription tier not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update allowed fields
        updatable_fields = [
            'display_name', 'description', 'monthly_credits', 'price_cents',
            'max_file_size_mb', 'max_analyses_per_month', 'max_concurrent_uploads',
            'features', 'rate_limits', 'is_active', 'position'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(tier, field, data[field])

        db.session.commit()
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Subscription tier updated successfully',
            'data': tier.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating tier {tier_name}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update subscription tier',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== RATE LIMIT ENDPOINTS ====================

@config_bp.route('/rate-limits', methods=['GET'])
@jwt_required()
@require_admin()
def get_rate_limits():
    """Get all rate limit configurations"""
    try:
        limits = RateLimitConfig.query.all()
        return jsonify({
            'status': 'success',
            'data': [l.to_dict() for l in limits]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching rate limits: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch rate limits',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/rate-limits', methods=['POST'])
@jwt_required()
@require_admin()
def create_rate_limit():
    """Create a new rate limit configuration"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['operation', 'subscription_tier', 'requests_per_hour', 'requests_per_day']
        if not all(field in data for field in required):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields',
                'error_type': 'VALIDATION_ERROR'
            }), 400

        # Check if already exists
        existing = RateLimitConfig.query.filter_by(
            operation=data['operation'],
            subscription_tier=data['subscription_tier']
        ).first()

        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Rate limit already exists for this operation and tier',
                'error_type': 'DUPLICATE_ERROR'
            }), 409

        limit = RateLimitConfig(**data)
        db.session.add(limit)
        db.session.commit()
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Rate limit created successfully',
            'data': limit.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating rate limit: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create rate limit',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/rate-limits/<int:limit_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_rate_limit(limit_id):
    """Update a rate limit configuration"""
    try:
        data = request.get_json()

        limit = RateLimitConfig.query.get(limit_id)
        if not limit:
            return jsonify({
                'status': 'error',
                'message': 'Rate limit not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update fields
        updatable = ['requests_per_hour', 'requests_per_day', 'requests_per_month', 'cost_in_credits', 'description']
        for field in updatable:
            if field in data:
                setattr(limit, field, data[field])

        db.session.commit()
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Rate limit updated successfully',
            'data': limit.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating rate limit {limit_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update rate limit',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== SCORING THRESHOLD ENDPOINTS ====================

@config_bp.route('/scoring-thresholds', methods=['GET'])
@jwt_required()
@require_admin()
def get_scoring_thresholds():
    """Get all scoring thresholds"""
    try:
        thresholds = ScoringThreshold.query.order_by(ScoringThreshold.min_score).all()
        return jsonify({
            'status': 'success',
            'data': [t.to_dict() for t in thresholds]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching thresholds: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch scoring thresholds',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/scoring-thresholds/<int:threshold_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_scoring_threshold(threshold_id):
    """Update a scoring threshold"""
    try:
        data = request.get_json()

        threshold = ScoringThreshold.query.get(threshold_id)
        if not threshold:
            return jsonify({
                'status': 'error',
                'message': 'Scoring threshold not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update fields
        updatable = ['feedback_text', 'color_code', 'icon', 'recommendation_weight', 'skill_extraction_keywords']
        for field in updatable:
            if field in data:
                setattr(threshold, field, data[field])

        db.session.commit()
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Scoring threshold updated successfully',
            'data': threshold.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating threshold {threshold_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update scoring threshold',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== VALIDATION RULES ENDPOINTS ====================

@config_bp.route('/validation-rules', methods=['GET'])
@jwt_required()
@require_admin()
def get_validation_rules():
    """Get all validation rules"""
    try:
        category = request.args.get('category')
        query = ValidationRule.query

        if category:
            query = query.filter_by(rule_category=category)

        rules = query.order_by(ValidationRule.priority).all()
        return jsonify({
            'status': 'success',
            'data': [r.to_dict() for r in rules]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching validation rules: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch validation rules',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@config_bp.route('/validation-rules/<int:rule_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_validation_rule(rule_id):
    """Update a validation rule"""
    try:
        data = request.get_json()

        rule = ValidationRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'status': 'error',
                'message': 'Validation rule not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Update fields
        updatable = ['rule_value', 'error_message', 'priority', 'is_active', 'applies_to_tier']
        for field in updatable:
            if field in data:
                setattr(rule, field, data[field])

        db.session.commit()
        get_config_manager().clear_cache()

        return jsonify({
            'status': 'success',
            'message': 'Validation rule updated successfully',
            'data': rule.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update validation rule',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ==================== CONFIGURATION SUMMARY ====================

@config_bp.route('/summary', methods=['GET'])
@jwt_required()
@require_admin()
def get_config_summary():
    """Get a summary of all configurations"""
    try:
        summary = {
            'system_configs': SystemConfiguration.query.count(),
            'subscription_tiers': SubscriptionTier.query.filter_by(is_active=True).count(),
            'rate_limits': RateLimitConfig.query.count(),
            'scoring_thresholds': ScoringThreshold.query.count(),
            'validation_rules': ValidationRule.query.filter_by(is_active=True).count(),
            'cache_stats': get_config_manager().get_stats()
        }

        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    except Exception as e:
        logger.error(f"Error getting config summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get configuration summary',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
