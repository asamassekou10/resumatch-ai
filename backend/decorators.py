"""
Custom decorators for route protection and access control
"""

from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def subscription_required(f):
    """
    Decorator to require active subscription for route access

    Usage:
        @app.route('/api/market/premium-feature')
        @jwt_required()
        @subscription_required
        def premium_feature():
            # Only accessible to users with active subscription
            pass

    Returns 403 Forbidden if user doesn't have active subscription
    Admins bypass subscription requirements
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure JWT is verified first
        verify_jwt_in_request()

        # Get current user from JWT
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'error': 'User not found',
                'error_type': 'UNAUTHORIZED'
            }), 401

        # Admins bypass subscription requirements
        if user.is_admin:
            g.current_user = user
            return f(*args, **kwargs)

        # Check if user has active subscription
        if user.subscription_status != 'active':
            return jsonify({
                'error': 'Active subscription required to access this feature',
                'error_type': 'SUBSCRIPTION_REQUIRED',
                'subscription_status': user.subscription_status,
                'subscription_tier': user.subscription_tier,
                'upgrade_url': '/pricing',
                'message': 'Upgrade to a premium plan to unlock Market Intelligence and advanced features'
            }), 403

        # Store user in g for use in route
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin access for route

    Usage:
        @app.route('/api/admin/users')
        @jwt_required()
        @admin_required
        def admin_users():
            # Only accessible to admins
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'error': 'User not found',
                'error_type': 'UNAUTHORIZED'
            }), 401

        if not user.is_admin:
            return jsonify({
                'error': 'Admin access required',
                'error_type': 'FORBIDDEN'
            }), 403

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def role_required(role_name):
    """
    Decorator to require specific role for route access

    Usage:
        @app.route('/api/moderator/content')
        @jwt_required()
        @role_required('moderator')
        def moderate_content():
            # Only accessible to users with 'moderator' role
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()

            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({
                    'error': 'User not found',
                    'error_type': 'UNAUTHORIZED'
                }), 401

            # Admins bypass role requirements
            if user.is_admin:
                g.current_user = user
                return f(*args, **kwargs)

            # Check if user has required role
            if not user.has_role(role_name):
                return jsonify({
                    'error': f'Role "{role_name}" required',
                    'error_type': 'FORBIDDEN'
                }), 403

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function
    return decorator
