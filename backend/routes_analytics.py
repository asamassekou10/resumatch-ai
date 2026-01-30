"""
Analytics Routes
Provides endpoints for tracking user signups, activity, and engagement metrics
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from models import db, User, Analysis, GuestSession, GuestAnalysis, ConversionEvent
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

@analytics_bp.route('/analytics/verification-stats', methods=['GET'])
@jwt_required()
def get_verification_stats():
    """Get email verification statistics"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        now = datetime.utcnow()
        
        # Total users
        total_users = User.query.filter(User.auth_provider == 'email').count()
        verified_users = User.query.filter(
            User.auth_provider == 'email',
            User.email_verified == True
        ).count()
        unverified_users = total_users - verified_users
        
        # Verification rate
        verification_rate = (verified_users / total_users * 100) if total_users > 0 else 0
        
        # Users by days since registration (unverified)
        unverified_by_days = {}
        for days in [1, 3, 7, 14]:
            cutoff_date = now - timedelta(days=days)
            count = User.query.filter(
                User.auth_provider == 'email',
                User.email_verified == False,
                User.created_at <= cutoff_date
            ).count()
            unverified_by_days[f'{days}_days'] = count
        
        # Average time to verify (for verified users)
        verified_with_times = db.session.query(
            func.avg(
                func.extract('epoch', User.last_verification_email_sent - User.created_at) / 3600
            )
        ).filter(
            User.email_verified == True,
            User.last_verification_email_sent.isnot(None),
            User.created_at.isnot(None)
        ).scalar()
        
        avg_hours_to_verify = verified_with_times if verified_with_times else None
        
        # Reminder effectiveness
        users_with_reminders = User.query.filter(
            User.verification_reminder_count > 0
        ).count()
        
        users_verified_after_reminder = User.query.filter(
            User.email_verified == True,
            User.verification_reminder_count > 0
        ).count()
        
        reminder_effectiveness = (users_verified_after_reminder / users_with_reminders * 100) if users_with_reminders > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'verified_users': verified_users,
                'unverified_users': unverified_users,
                'verification_rate': round(verification_rate, 2),
                'unverified_by_days': unverified_by_days,
                'avg_hours_to_verify': round(avg_hours_to_verify, 2) if avg_hours_to_verify else None,
                'reminder_stats': {
                    'users_with_reminders': users_with_reminders,
                    'users_verified_after_reminder': users_verified_after_reminder,
                    'effectiveness_rate': round(reminder_effectiveness, 2)
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching verification stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch verification stats'}), 500

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


@analytics_bp.route('/analytics/track-event', methods=['POST'])
@jwt_required(optional=True)
def track_conversion_event():
    """
    Track a conversion event
    Can be called with or without authentication (for guest tracking)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        event_type = data.get('event_type')
        if not event_type:
            return jsonify({'error': 'event_type is required'}), 400

        # Get user ID if authenticated
        user_id = None
        try:
            user_id = int(get_jwt_identity()) if get_jwt_identity() else None
        except:
            pass

        # Get metadata
        metadata = data.get('metadata', {})
        session_id = metadata.get('session_id')
        page_url = metadata.get('page_url')
        referrer = metadata.get('referrer')

        # Create event
        event = ConversionEvent(
            user_id=user_id,
            event_type=event_type,
            session_id=session_id,
            page_url=page_url,
            referrer=referrer,
            event_metadata=metadata
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({
            'success': True,
            'event_id': event.id
        }), 200

    except Exception as e:
        logger.error(f"Error tracking conversion event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to track event'}), 500


@analytics_bp.route('/analytics/conversion-funnel', methods=['GET'])
@jwt_required()
def get_conversion_funnel():
    """
    Get conversion funnel data showing drop-off at each stage
    Only accessible by admin users
    """
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        days = int(request.args.get('days', 30))
        days = min(days, 365)  # Cap at 1 year

        start_date = datetime.utcnow() - timedelta(days=days)

        # Define funnel stages
        funnel_stages = [
            'landing_page_view',
            'signup_started',
            'signup_completed',
            'first_analysis_started',
            'first_analysis_completed',
            'pricing_page_view',
            'checkout_started',
            'payment_completed'
        ]

        # Get event counts for each stage
        funnel_data = []
        previous_count = None

        for stage in funnel_stages:
            count = ConversionEvent.query.filter(
                ConversionEvent.event_type == stage,
                ConversionEvent.created_at >= start_date
            ).count()

            # Calculate conversion rate from previous stage
            conversion_rate = None
            drop_off_rate = None
            if previous_count is not None and previous_count > 0:
                conversion_rate = round((count / previous_count) * 100, 2)
                drop_off_rate = round(100 - conversion_rate, 2)

            funnel_data.append({
                'stage': stage,
                'count': count,
                'conversion_rate': conversion_rate,
                'drop_off_rate': drop_off_rate
            })

            previous_count = count

        # Calculate overall conversion rate (landing to payment)
        landing_views = funnel_data[0]['count'] if funnel_data else 0
        payments = funnel_data[-1]['count'] if funnel_data else 0
        overall_conversion = round((payments / landing_views * 100), 2) if landing_views > 0 else 0

        # Get daily breakdown for first 3 stages (most important)
        daily_breakdown = {}
        for stage in ['landing_page_view', 'signup_completed', 'first_analysis_completed']:
            daily_events = db.session.query(
                func.date(ConversionEvent.created_at).label('date'),
                func.count(ConversionEvent.id).label('count')
            ).filter(
                ConversionEvent.event_type == stage,
                ConversionEvent.created_at >= start_date
            ).group_by(
                func.date(ConversionEvent.created_at)
            ).order_by('date').all()

            daily_breakdown[stage] = [
                {
                    'date': date.isoformat() if date else None,
                    'count': count
                }
                for date, count in daily_events
            ]

        return jsonify({
            'success': True,
            'data': {
                'funnel': funnel_data,
                'overall_conversion_rate': overall_conversion,
                'total_landing_views': landing_views,
                'total_payments': payments,
                'daily_breakdown': daily_breakdown,
                'period_days': days,
                'start_date': start_date.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching conversion funnel: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversion funnel'}), 500


@analytics_bp.route('/analytics/track-abandoned-cart', methods=['POST'])
@jwt_required()
def track_abandoned_cart():
    """
    Track when user opens payment modal but doesn't complete purchase
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        plan_type = data.get('plan_type')
        price = data.get('price')

        # Only track if user hasn't completed purchase yet
        if user.subscription_tier == 'free':
            user.cart_abandoned_at = datetime.utcnow()
            user.cart_abandoned_plan = plan_type
            user.cart_abandoned_price = price
            db.session.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error tracking abandoned cart: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to track abandoned cart'}), 500


@analytics_bp.route('/analytics/clear-abandoned-cart', methods=['POST'])
@jwt_required()
def clear_abandoned_cart():
    """
    Clear abandoned cart tracking when user completes purchase
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.cart_abandoned_at = None
        user.cart_abandoned_plan = None
        user.cart_abandoned_price = None
        db.session.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error clearing abandoned cart: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to clear abandoned cart'}), 500
