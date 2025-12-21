"""Admin API routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from models import db, User, Analysis, AdminLog, Role, Permission
from middleware import require_admin, admin_action_log
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


# ============== Dashboard Stats ==============

@admin_bp.route('/dashboard/stats', methods=['GET'])
@require_admin
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        # User growth (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()

        # Total analyses
        total_analyses = Analysis.query.count()
        analyses_30d = Analysis.query.filter(Analysis.created_at >= thirty_days_ago).count()

        # Average match score (optimized - limit calculation to avoid memory issues)
        try:
            # For large datasets, calculate average on recent analyses only
            if total_analyses > 5000:
                # Use recent 5000 analyses for average calculation
                avg_match_score = db.session.query(
                    func.avg(Analysis.match_score)
                ).filter(
                    Analysis.id.in_(
                        db.session.query(Analysis.id)
                        .order_by(Analysis.created_at.desc())
                        .limit(5000)
                    )
                ).scalar() or 0
            else:
                avg_match_score = db.session.query(func.avg(Analysis.match_score)).scalar() or 0
        except Exception as e:
            logger.warning(f"Error calculating average match score: {e}")
            # Fallback: calculate on recent analyses only
            try:
                avg_match_score = db.session.query(
                    func.avg(Analysis.match_score)
                ).filter(
                    Analysis.created_at >= thirty_days_ago
                ).scalar() or 0
            except:
                avg_match_score = 0

        # Users by signup date (daily for last 30 days) - optimized with limit
        try:
            daily_signups = db.session.query(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).filter(
                User.created_at >= thirty_days_ago
            ).group_by(func.date(User.created_at)).order_by(func.date(User.created_at)).limit(31).all()

            signup_trend = [{'date': str(d[0]), 'count': d[1]} for d in daily_signups]
        except Exception as e:
            logger.warning(f"Error fetching signup trend: {e}")
            signup_trend = []

        # Analyses by day (last 30 days) - optimized with limit
        try:
            daily_analyses = db.session.query(
                func.date(Analysis.created_at).label('date'),
                func.count(Analysis.id).label('count')
            ).filter(
                Analysis.created_at >= thirty_days_ago
            ).group_by(func.date(Analysis.created_at)).order_by(func.date(Analysis.created_at)).limit(31).all()

            analyses_trend = [{'date': str(d[0]), 'count': d[1]} for d in daily_analyses]
        except Exception as e:
            logger.warning(f"Error fetching analyses trend: {e}")
            analyses_trend = []

        return jsonify({
            'status': 'success',
            'data': {
                'metrics': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'admin_users': admin_users,
                    'new_users_30d': new_users_30d,
                    'total_analyses': total_analyses,
                    'analyses_30d': analyses_30d,
                    'avg_match_score': round(avg_match_score, 2)
                },
                'trends': {
                    'signup_trend': signup_trend,
                    'analyses_trend': analyses_trend
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch dashboard stats',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== User Management ==============

@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    """Get all users with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '', type=str)
        is_active = request.args.get('is_active', None, type=bool)

        query = User.query

        if search:
            query = query.filter(User.email.ilike(f'%{search}%'))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        users = query.order_by(desc(User.created_at)).paginate(
            page=page, per_page=limit, error_out=False
        )

        return jsonify({
            'status': 'success',
            'data': {
                'users': [u.to_dict() for u in users.items],
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch users',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user(user_id):
    """Get user details"""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Get user's analyses
        analyses = Analysis.query.filter_by(user_id=user_id).order_by(
            desc(Analysis.created_at)
        ).limit(10).all()

        user_data = user.to_dict()
        user_data['analyses_count'] = Analysis.query.filter_by(user_id=user_id).count()
        user_data['recent_analyses'] = [a.to_dict() for a in analyses]

        return jsonify({
            'status': 'success',
            'data': user_data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch user',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_action_log('update_user', 'user')
def update_user(user_id):
    """Update user (suspend/activate/change role)"""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found',
                'error_type': 'NOT_FOUND'
            }), 404

        data = request.get_json() or {}
        changes = {}

        if 'is_active' in data:
            old_value = user.is_active
            user.is_active = bool(data['is_active'])
            changes['is_active'] = {'old': old_value, 'new': user.is_active}

        if 'is_admin' in data:
            old_value = user.is_admin
            user.is_admin = bool(data['is_admin'])
            changes['is_admin'] = {'old': old_value, 'new': user.is_admin}

        if changes:
            db.session.commit()
            # Log the changes
            AdminLog.query.filter_by(
                admin_user_id=get_jwt_identity(),
                resource_id=user_id,
                action='update_user'
            ).order_by(desc(AdminLog.created_at)).first().changes = changes
            db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update user',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_action_log('delete_user', 'user')
def delete_user(user_id):
    """Delete user and all their data"""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found',
                'error_type': 'NOT_FOUND'
            }), 404

        # Prevent deleting the current admin
        if user_id == get_jwt_identity():
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete your own account',
                'error_type': 'FORBIDDEN'
            }), 403

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete user',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== Analytics ==============

@admin_bp.route('/analytics/user-growth', methods=['GET'])
@require_admin
def get_user_growth():
    """Get user growth analytics over time"""
    try:
        days = request.args.get('days', 90, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)

        daily_growth = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('new_users')
        ).filter(User.created_at >= start_date).group_by(
            func.date(User.created_at)
        ).order_by('date').all()

        # Calculate cumulative growth
        cumulative = 0
        data = []
        for date, count in daily_growth:
            cumulative += count
            data.append({
                'date': str(date),
                'new_users': count,
                'total_users': cumulative
            })

        return jsonify({
            'status': 'success',
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user growth: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch user growth analytics',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/analytics/engagement', methods=['GET'])
@require_admin
def get_engagement_analytics():
    """Get user engagement analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)

        # Active users per day
        active_users = db.session.query(
            func.date(Analysis.created_at).label('date'),
            func.count(func.distinct(Analysis.user_id)).label('active_users')
        ).filter(Analysis.created_at >= start_date).group_by(
            func.date(Analysis.created_at)
        ).order_by('date').all()

        # Analyses per day
        analyses_per_day = db.session.query(
            func.date(Analysis.created_at).label('date'),
            func.count(Analysis.id).label('analyses')
        ).filter(Analysis.created_at >= start_date).group_by(
            func.date(Analysis.created_at)
        ).order_by('date').all()

        # Match score distribution
        match_scores = db.session.query(
            func.round(Analysis.match_score / 10) * 10,
            func.count(Analysis.id)
        ).filter(Analysis.created_at >= start_date).group_by(
            func.round(Analysis.match_score / 10)
        ).all()

        data = {
            'active_users_trend': [
                {'date': str(d[0]), 'active_users': d[1]} for d in active_users
            ],
            'analyses_trend': [
                {'date': str(d[0]), 'analyses': d[1]} for d in analyses_per_day
            ],
            'match_score_distribution': [
                {'score_range': f'{int(d[0])}-{int(d[0])+10}', 'count': d[1]} for d in match_scores
            ]
        }

        return jsonify({
            'status': 'success',
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching engagement analytics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch engagement analytics',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== Audit Logs ==============

@admin_bp.route('/logs', methods=['GET'])
@require_admin
def get_admin_logs():
    """Get admin activity logs"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        action = request.args.get('action', '', type=str)
        admin_id = request.args.get('admin_id', None, type=int)

        query = AdminLog.query

        if action:
            query = query.filter(AdminLog.action == action)

        if admin_id:
            query = query.filter(AdminLog.admin_user_id == admin_id)

        total = query.count()
        logs = query.order_by(desc(AdminLog.created_at)).paginate(
            page=page, per_page=limit, error_out=False
        )

        return jsonify({
            'status': 'success',
            'data': {
                'logs': [log.to_dict() for log in logs.items],
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching admin logs: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch admin logs',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== System Settings ==============

@admin_bp.route('/settings', methods=['GET'])
@require_admin
def get_settings():
    """Get system settings"""
    try:
        settings = {
            'maintenance_mode': False,
            'max_file_size': 10485760,  # 10MB
            'max_analyses_per_user_monthly': 100,
            'free_tier_analyses_limit': 5
        }

        return jsonify({
            'status': 'success',
            'data': settings
        }), 200
    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch settings',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/settings', methods=['PUT'])
@admin_action_log('update_settings', 'settings')
def update_settings():
    """Update system settings"""
    try:
        data = request.get_json() or {}

        # For now, just return success
        # In a real app, you'd persist these to the database

        return jsonify({
            'status': 'success',
            'message': 'Settings updated successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update settings',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


# ============== Roles & Permissions ==============

@admin_bp.route('/roles', methods=['GET'])
@require_admin
def get_roles():
    """Get all roles"""
    try:
        roles = Role.query.all()

        return jsonify({
            'status': 'success',
            'data': [role.to_dict() for role in roles]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch roles',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@admin_bp.route('/permissions', methods=['GET'])
@require_admin
def get_permissions():
    """Get all permissions"""
    try:
        permissions = Permission.query.all()

        return jsonify({
            'status': 'success',
            'data': [p.to_dict() for p in permissions]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching permissions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch permissions',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
