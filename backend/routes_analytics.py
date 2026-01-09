"""
Analytics Routes
Provides endpoints for tracking user signups, activity, and engagement metrics
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from models import db, User, Analysis, GuestSession, GuestAnalysis
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')

def is_admin():
    """Check if current user is admin"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return user and user.is_admin
    except:
        return False

@analytics_bp.route('/analytics/founding-members-count', methods=['GET'])
def get_founding_members_count():
    """
    Get count of Founding Members (public endpoint for banner)
    Returns: Number of users subscribed to pro_founding tier
    """
    try:
        count = User.query.filter_by(subscription_tier='pro_founding').count()
        remaining = max(0, 100 - count)

        return jsonify({
            'count': count,
            'remaining': remaining,
            'total': 100,
            'percentage_claimed': round((count / 100) * 100, 1)
        }), 200

    except Exception as e:
        logger.error(f"Error getting founding members count: {str(e)}")
        return jsonify({'error': 'Failed to get founding members count'}), 500

@analytics_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """
    Get high-level analytics overview
    Includes: total users, signups today/week/month, active users, etc.

    Only accessible by admin users
    """
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Get time ranges
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        # Total users
        total_users = User.query.count()

        # New signups
        signups_today = User.query.filter(User.created_at >= today_start).count()
        signups_week = User.query.filter(User.created_at >= week_start).count()
        signups_month = User.query.filter(User.created_at >= month_start).count()

        # Active users (logged in within last 30 days)
        active_users = User.query.filter(User.last_login >= month_start).count()

        # Email verified users
        verified_users = User.query.filter_by(email_verified=True).count()

        # Subscription breakdown
        subscription_breakdown = db.session.query(
            User.subscription_tier,
            func.count(User.id).label('count')
        ).group_by(User.subscription_tier).all()

        # Auth provider breakdown
        auth_breakdown = db.session.query(
            User.auth_provider,
            func.count(User.id).label('count')
        ).group_by(User.auth_provider).all()

        # Total analyses
        total_analyses = Analysis.query.count()
        analyses_today = Analysis.query.filter(Analysis.created_at >= today_start).count()
        analyses_week = Analysis.query.filter(Analysis.created_at >= week_start).count()
        analyses_month = Analysis.query.filter(Analysis.created_at >= month_start).count()

        # Guest analytics
        total_guest_sessions = GuestSession.query.count()
        total_guest_analyses = GuestAnalysis.query.count()
        active_guest_sessions = GuestSession.query.filter(
            GuestSession.expires_at > now,
            GuestSession.status == 'active'
        ).count()

        return jsonify({
            'success': True,
            'data': {
                'users': {
                    'total': total_users,
                    'signups_today': signups_today,
                    'signups_week': signups_week,
                    'signups_month': signups_month,
                    'active_last_30_days': active_users,
                    'email_verified': verified_users,
                    'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 2)
                },
                'subscriptions': {
                    tier: count for tier, count in subscription_breakdown
                },
                'auth_providers': {
                    provider: count for provider, count in auth_breakdown
                },
                'analyses': {
                    'total': total_analyses,
                    'today': analyses_today,
                    'week': analyses_week,
                    'month': analyses_month,
                    'avg_per_user': round(total_analyses / total_users, 2) if total_users > 0 else 0
                },
                'guest_activity': {
                    'total_sessions': total_guest_sessions,
                    'active_sessions': active_guest_sessions,
                    'total_analyses': total_guest_analyses,
                    'conversion_rate': round((total_users / total_guest_sessions * 100) if total_guest_sessions > 0 else 0, 2)
                },
                'timestamp': now.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching analytics overview: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500


@analytics_bp.route('/analytics/signups/timeline', methods=['GET'])
@jwt_required()
def get_signup_timeline():
    """
    Get user signup timeline (daily signups for last 30 days)

    Query params:
    - days: number of days to include (default: 30, max: 365)
    """
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        days = int(request.args.get('days', 30))
        days = min(days, 365)  # Cap at 1 year

        start_date = datetime.utcnow() - timedelta(days=days)

        # Query signups grouped by date
        signups_by_day = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).order_by('date').all()

        # Format response
        timeline = [
            {
                'date': date.isoformat() if date else None,
                'signups': count
            }
            for date, count in signups_by_day
        ]

        return jsonify({
            'success': True,
            'data': {
                'timeline': timeline,
                'total_signups': sum(item['signups'] for item in timeline),
                'days_requested': days
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching signup timeline: {str(e)}")
        return jsonify({'error': 'Failed to fetch signup timeline'}), 500


@analytics_bp.route('/analytics/recent-users', methods=['GET'])
@jwt_required()
def get_recent_users():
    """
    Get list of recently registered users

    Query params:
    - limit: number of users to return (default: 20, max: 100)
    """
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        limit = int(request.args.get('limit', 20))
        limit = min(limit, 100)  # Cap at 100

        recent_users = User.query.order_by(User.created_at.desc()).limit(limit).all()

        users_data = [
            {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'auth_provider': user.auth_provider,
                'subscription_tier': user.subscription_tier,
                'email_verified': user.email_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            for user in recent_users
        ]

        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'count': len(users_data)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching recent users: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent users'}), 500


@analytics_bp.route('/analytics/user/<int:user_id>/activity', methods=['GET'])
@jwt_required()
def get_user_activity(user_id):
    """
    Get detailed activity for a specific user
    """
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        user = User.query.get_or_404(user_id)

        # Get user's analyses
        analyses_count = Analysis.query.filter_by(user_id=user_id).count()
        recent_analyses = Analysis.query.filter_by(user_id=user_id).order_by(
            Analysis.created_at.desc()
        ).limit(10).all()

        analyses_data = [
            {
                'id': analysis.id,
                'job_title': analysis.job_title,
                'company_name': analysis.company_name,
                'match_score': analysis.match_score,
                'created_at': analysis.created_at.isoformat() if analysis.created_at else None
            }
            for analysis in recent_analyses
        ]

        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'subscription_tier': user.subscription_tier,
                    'credits': user.credits,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'activity': {
                    'total_analyses': analyses_count,
                    'recent_analyses': analyses_data
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user activity: {str(e)}")
        return jsonify({'error': 'Failed to fetch user activity'}), 500
