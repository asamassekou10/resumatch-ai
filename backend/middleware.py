"""Admin and authorization middleware"""
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User, AdminLog
from datetime import datetime


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_admin:
                return jsonify({
                    'status': 'error',
                    'message': 'Admin access required',
                    'error_type': 'UNAUTHORIZED'
                }), 403

            g.user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Authentication failed',
                'error_type': 'AUTHENTICATION_ERROR'
            }), 401

    return decorated_function


def require_permission(permission_name):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user or not user.has_permission(permission_name):
                    return jsonify({
                        'status': 'error',
                        'message': f'Permission required: {permission_name}',
                        'error_type': 'FORBIDDEN'
                    }), 403

                g.user = user
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication failed',
                    'error_type': 'AUTHENTICATION_ERROR'
                }), 401

        return decorated_function
    return decorator


def admin_action_log(action_name, resource_type):
    """Decorator to log admin actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user or not user.is_admin:
                    return jsonify({
                        'status': 'error',
                        'message': 'Admin access required',
                        'error_type': 'UNAUTHORIZED'
                    }), 403

                g.user = user

                # Store action info in g for logging after response
                g.admin_action = {
                    'action': action_name,
                    'resource_type': resource_type,
                    'timestamp': datetime.utcnow()
                }

                result = f(*args, **kwargs)

                # Log the action
                try:
                    from app import db
                    ip_address = request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')

                    log_entry = AdminLog(
                        admin_user_id=user.id,
                        action=action_name,
                        resource_type=resource_type,
                        resource_id=kwargs.get('id'),
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                except Exception as log_error:
                    print(f"Error logging admin action: {log_error}")

                return result
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication failed',
                    'error_type': 'AUTHENTICATION_ERROR'
                }), 401

        return decorated_function
    return decorator
