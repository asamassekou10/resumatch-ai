"""
Abuse Prevention System
Prevents credit system exploitation and API misuse
"""

from models import db, User, Analysis
from datetime import datetime, timedelta
import logging

# Tier-based daily credit limits (to prevent abuse)
DAILY_CREDIT_LIMITS = {
    'free': 5,      # Free tier: 5 credits per day (1 analysis)
    'pro': 100,     # Pro tier: 100 credits per day (capped daily)
    'elite': 1000   # Elite tier: 1000 credits per day (capped daily)
}

# Tier-based operation costs (in credits)
OPERATION_COSTS = {
    'analyze': 1,              # Resume analysis
    'feedback': 1,             # AI feedback generation
    'optimize': 2,             # Resume optimization
    'cover_letter': 2,         # Cover letter generation
    'skill_suggestions': 1,    # Skill suggestions
}

# Tier-based rate limits (operations per hour)
RATE_LIMITS = {
    'free': {
        'analyze': 2,           # 2 analyses per hour
        'feedback': 2,          # 2 feedback requests per hour
        'optimize': 1,          # 1 optimization per hour
        'cover_letter': 1,      # 1 cover letter per hour
        'skill_suggestions': 2, # 2 suggestions per hour
    },
    'pro': {
        'analyze': 10,          # 10 analyses per hour
        'feedback': 5,          # 5 feedback requests per hour
        'optimize': 5,          # 5 optimizations per hour
        'cover_letter': 5,      # 5 cover letters per hour
        'skill_suggestions': 10, # 10 suggestions per hour
    },
    'elite': {
        'analyze': 50,          # 50 analyses per hour (generous limit)
        'feedback': 20,         # 20 feedback requests per hour
        'optimize': 20,         # 20 optimizations per hour
        'cover_letter': 20,     # 20 cover letters per hour
        'skill_suggestions': 50, # 50 suggestions per hour
    }
}


def check_daily_credit_limit(user_id: int, operation: str) -> tuple[bool, str]:
    """
    Check if user has exceeded daily credit limit.
    Returns (allowed: bool, message: str)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        # Get daily limit for this tier
        daily_limit = DAILY_CREDIT_LIMITS.get(user.subscription_tier, 5)

        # Calculate credits used today
        today = datetime.utcnow().date()
        operations_today = Analysis.query.filter(
            Analysis.user_id == user_id,
            db.func.date(Analysis.created_at) == today
        ).count()

        # For now, count operations. Later could track actual credit usage per operation
        # Each operation uses 1-2 credits on average
        avg_cost = OPERATION_COSTS.get(operation, 1)
        estimated_credits_used = operations_today * avg_cost

        if estimated_credits_used >= daily_limit:
            return False, f"Daily credit limit reached ({daily_limit} credits). Try again tomorrow."

        return True, ""

    except Exception as e:
        logging.error(f"Error checking daily credit limit: {str(e)}", exc_info=True)
        return True, ""  # Allow if check fails (fail open)


def check_abuse_pattern(user_id: int, operation: str) -> tuple[bool, str]:
    """
    Detect suspicious patterns like rapid-fire requests.
    Returns (allowed: bool, message: str)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        # Check for suspicious rapid requests (more than 10 in 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_ops = Analysis.query.filter(
            Analysis.user_id == user_id,
            Analysis.created_at >= five_minutes_ago
        ).count()

        if recent_ops > 10:
            logging.warning(f"Suspicious activity detected for user {user_id}: {recent_ops} operations in 5 minutes")
            return False, "Too many requests. Please wait before trying again."

        return True, ""

    except Exception as e:
        logging.error(f"Error checking abuse pattern: {str(e)}", exc_info=True)
        return True, ""  # Allow if check fails


def has_sufficient_credits(user_id: int, operation: str) -> tuple[bool, dict]:
    """
    Check if user has sufficient credits for an operation.
    Returns (has_credits: bool, info_dict)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, {'error': 'User not found'}

        required_credits = OPERATION_COSTS.get(operation, 1)

        if user.credits < required_credits:
            upgrade_url = "/dashboard/upgrade"
            return False, {
                'error': f'Insufficient credits ({required_credits} required, {user.credits} available)',
                'required_credits': required_credits,
                'current_credits': user.credits,
                'subscription_tier': user.subscription_tier,
                'upgrade_url': upgrade_url
            }

        return True, {
            'required_credits': required_credits,
            'current_credits': user.credits,
            'remaining_after': user.credits - required_credits
        }

    except Exception as e:
        logging.error(f"Error checking credits: {str(e)}", exc_info=True)
        return False, {'error': 'Could not verify credits'}


def deduct_credits(user_id: int, operation: str) -> tuple[bool, str]:
    """
    Deduct credits for an operation.
    Returns (success: bool, message: str)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        required_credits = OPERATION_COSTS.get(operation, 1)

        # Double-check they have credits
        if user.credits < required_credits:
            return False, "Insufficient credits"

        user.credits -= required_credits
        db.session.commit()

        logging.info(f"Deducted {required_credits} credits from user {user_id} for {operation} operation")

        return True, f"{required_credits} credits deducted"

    except Exception as e:
        logging.error(f"Error deducting credits: {str(e)}", exc_info=True)
        db.session.rollback()
        return False, "Could not deduct credits"


def get_tier_rate_limit(user_id: int, operation: str) -> int:
    """
    Get the rate limit for a user's tier and operation.
    Returns the limit as "X per hour"
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return 5  # Default

        tier_limits = RATE_LIMITS.get(user.subscription_tier, RATE_LIMITS['free'])
        return tier_limits.get(operation, 5)

    except Exception as e:
        logging.error(f"Error getting rate limit: {str(e)}", exc_info=True)
        return 5  # Default


def get_tier_info(subscription_tier: str) -> dict:
    """
    Get pricing and feature info for a tier.
    """
    tier_data = {
        'free': {
            'name': 'Free',
            'price': '$0',
            'monthly_credits': DAILY_CREDIT_LIMITS['free'],
            'daily_limit': DAILY_CREDIT_LIMITS['free'],
            'description': '5 credits on signup',
            'features': [
                'Resume analysis',
                'Basic feedback',
                'Limited features'
            ]
        },
        'pro': {
            'name': 'Pro',
            'price': '$9.99/month',
            'monthly_credits': 100,
            'daily_limit': DAILY_CREDIT_LIMITS['pro'],
            'description': '100 credits per month',
            'features': [
                'Unlimited resume analysis',
                'AI feedback generation',
                'Resume optimization',
                'Skill gap analysis',
                'Priority support'
            ]
        },
        'elite': {
            'name': 'Elite',
            'price': '$49.99/month',
            'monthly_credits': 1000,
            'daily_limit': DAILY_CREDIT_LIMITS['elite'],
            'description': '1000 credits per month',
            'features': [
                'Everything in Pro',
                'Unlimited API access',
                'Custom integrations',
                'Advanced analytics',
                'Dedicated support',
                'API webhooks'
            ]
        }
    }

    return tier_data.get(subscription_tier, tier_data['free'])


def log_security_event(user_id: int, event_type: str, details: str, severity: str = 'warning'):
    """
    Log security/abuse events for monitoring.
    severity: 'info', 'warning', 'critical'
    """
    log_func = getattr(logging, severity, logging.warning)
    log_func(f"[SECURITY] User {user_id} - {event_type}: {details}")
