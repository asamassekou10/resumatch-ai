"""
Subscription management service
Handles credit resets, trial management, and subscription lifecycle
"""

from datetime import datetime, timedelta
from models import db, User, SubscriptionTier
from config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)
config_manager = ConfigManager()


class SubscriptionService:
    """Service for managing subscriptions and credits"""

    @staticmethod
    def reset_monthly_credits():
        """
        Reset credits for all active subscribers on their billing anniversary
        This should be run daily via a scheduler
        """
        try:
            today = datetime.utcnow()
            current_day = today.day

            # Find users whose subscription started on this day of the month
            # Also handle edge case where current month doesn't have the day (e.g., Feb 31)
            users = User.query.filter(
                User.subscription_status == 'active',
                User.subscription_tier.in_(['starter', 'pro', 'pro_annual', 'elite', 'student'])
            ).all()

            reset_count = 0
            for user in users:
                # Check if it's their billing anniversary
                if user.subscription_start_date:
                    subscription_day = user.subscription_start_date.day

                    # Handle end-of-month edge cases
                    # If subscribed on 29-31 and current month is shorter, reset on last day
                    import calendar
                    last_day_of_month = calendar.monthrange(today.year, today.month)[1]

                    should_reset = (subscription_day == current_day) or \
                                 (subscription_day > last_day_of_month and current_day == last_day_of_month)

                    if should_reset:
                        tier = config_manager.get_subscription_tier(user.subscription_tier)
                        if tier:
                            user.credits = tier.monthly_credits
                            user.last_credit_reset = today
                            reset_count += 1
                            logger.info(f"Reset credits for user {user.id} ({user.subscription_tier}): {tier.monthly_credits} credits")

            db.session.commit()
            logger.info(f"Monthly credit reset complete: {reset_count} users updated")
            return reset_count

        except Exception as e:
            logger.error(f"Error in monthly credit reset: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def start_trial(user_id: int, trial_days: int = 7, trial_credits: int = 10):
        """
        Start a trial period for a user

        Args:
            user_id: User ID
            trial_days: Number of days for trial (default 7)
            trial_credits: Credits to grant (default 10)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Check if user already had a trial
            if user.trial_expired_date:
                raise ValueError("User has already used their trial")

            # Start trial
            user.is_trial_active = True
            user.trial_start_date = datetime.utcnow()
            user.trial_end_date = datetime.utcnow() + timedelta(days=trial_days)
            user.trial_credits_granted = trial_credits
            user.credits += trial_credits
            user.subscription_tier = 'pro'  # Give Pro access during trial
            user.subscription_status = 'active'

            db.session.commit()
            logger.info(f"Started {trial_days}-day trial for user {user_id} with {trial_credits} credits")

            return {
                'trial_start': user.trial_start_date,
                'trial_end': user.trial_end_date,
                'credits_granted': trial_credits
            }

        except Exception as e:
            logger.error(f"Error starting trial for user {user_id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def start_mega_launch_trial(user_id: int):
        """
        Start a 30-day Pro trial for early adopters (launch period only)
        More generous than standard 7-day trial to drive conversions

        Args:
            user_id: User ID

        Returns:
            dict: Trial details including start, end dates and credits
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Check if user already had a trial
            if user.trial_expired_date:
                raise ValueError("User has already used their trial")

            # Check if already on trial
            if user.is_trial_active:
                raise ValueError("User is already on a trial")

            # 30-day trial with 30 credits
            trial_days = 30
            trial_credits = 30

            user.is_trial_active = True
            user.trial_start_date = datetime.utcnow()
            user.trial_end_date = datetime.utcnow() + timedelta(days=trial_days)
            user.trial_credits_granted = trial_credits
            user.credits += trial_credits
            user.subscription_tier = 'pro'
            user.subscription_status = 'active'

            db.session.commit()
            logger.info(f"Started MEGA 30-day launch trial for user {user_id} with {trial_credits} credits")

            return {
                'trial_type': 'mega_launch',
                'trial_days': trial_days,
                'trial_start': user.trial_start_date,
                'trial_end': user.trial_end_date,
                'credits_granted': trial_credits,
                'message': '🎉 Welcome to your 30-day Pro trial! You have 30 analyses to optimize your job search.'
            }

        except Exception as e:
            logger.error(f"Error starting mega trial for user {user_id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def check_trial_expirations():
        """
        Check for expired trials and downgrade users
        This should be run daily via a scheduler
        """
        try:
            now = datetime.utcnow()

            # Find users with expired trials
            expired_trials = User.query.filter(
                User.is_trial_active == True,
                User.trial_end_date <= now
            ).all()

            expired_count = 0
            for user in expired_trials:
                # End trial
                user.is_trial_active = False
                user.trial_expired_date = now

                # Check if user has a paid subscription
                if not user.subscription_id or user.subscription_tier == 'free':
                    # Downgrade to free tier
                    user.subscription_tier = 'free'
                    user.subscription_status = 'inactive'
                    user.credits = 3  # Free tier credits
                    logger.info(f"Trial expired for user {user.id}, downgraded to free tier")
                else:
                    logger.info(f"Trial expired for user {user.id}, but has active subscription")

                expired_count += 1

                # TODO: Send trial expiration email

            db.session.commit()
            logger.info(f"Trial expiration check complete: {expired_count} trials expired")
            return expired_count

        except Exception as e:
            logger.error(f"Error checking trial expirations: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def deduct_credits(user_id: int, operation: str, amount: int = None):
        """
        Deduct credits from user for an operation

        Args:
            user_id: User ID
            operation: Operation name (e.g., 'resume_analysis', 'feedback_generation')
            amount: Credits to deduct (if None, looks up from RateLimitConfig)

        Returns:
            dict: {'success': bool, 'credits_remaining': int, 'message': str}
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}

            # Get credit cost for this operation and tier
            if amount is None:
                rate_limit = config_manager.get_rate_limit(operation, user.subscription_tier)
                if rate_limit:
                    amount = rate_limit.cost_in_credits
                else:
                    amount = 1  # Default cost

            # Check if user has enough credits
            if user.credits < amount:
                return {
                    'success': False,
                    'credits_remaining': user.credits,
                    'credits_needed': amount,
                    'message': f'Insufficient credits. Need {amount}, have {user.credits}.'
                }

            # Deduct credits
            user.credits -= amount
            db.session.commit()

            logger.info(f"Deducted {amount} credits from user {user_id} for {operation}. Remaining: {user.credits}")

            return {
                'success': True,
                'credits_remaining': user.credits,
                'credits_deducted': amount,
                'message': f'Successfully deducted {amount} credits'
            }

        except Exception as e:
            logger.error(f"Error deducting credits for user {user_id}: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def check_credit_limit(user_id: int, operation: str, amount: int = None):
        """
        Check if user has enough credits for an operation without deducting

        Args:
            user_id: User ID
            operation: Operation name
            amount: Credits needed (if None, looks up from RateLimitConfig)

        Returns:
            dict: {'has_credits': bool, 'credits_available': int, 'credits_needed': int}
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {'has_credits': False, 'message': 'User not found'}

            # Get credit cost
            if amount is None:
                rate_limit = config_manager.get_rate_limit(operation, user.subscription_tier)
                if rate_limit:
                    amount = rate_limit.cost_in_credits
                else:
                    amount = 1

            return {
                'has_credits': user.credits >= amount,
                'credits_available': user.credits,
                'credits_needed': amount,
                'tier': user.subscription_tier
            }

        except Exception as e:
            logger.error(f"Error checking credits for user {user_id}: {str(e)}")
            return {'has_credits': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def add_credits(user_id: int, amount: int, reason: str = None):
        """
        Add credits to a user (for purchases, refunds, promotions, etc.)

        Args:
            user_id: User ID
            amount: Credits to add
            reason: Reason for credit addition (for logging)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            user.credits += amount
            db.session.commit()

            logger.info(f"Added {amount} credits to user {user_id}. Reason: {reason}. New balance: {user.credits}")

            return {
                'success': True,
                'credits_added': amount,
                'credits_total': user.credits
            }

        except Exception as e:
            logger.error(f"Error adding credits to user {user_id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_subscription_info(user_id: int):
        """
        Get comprehensive subscription information for a user

        Returns:
            dict: Subscription details including tier, credits, trial status, etc.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None

            tier = config_manager.get_subscription_tier(user.subscription_tier)

            return {
                'user_id': user.id,
                'subscription_tier': user.subscription_tier,
                'subscription_status': user.subscription_status,
                'credits': user.credits,
                'monthly_credits': tier.monthly_credits if tier else 0,
                'is_trial_active': user.is_trial_active,
                'trial_end_date': user.trial_end_date.isoformat() if user.trial_end_date else None,
                'subscription_start_date': user.subscription_start_date.isoformat() if user.subscription_start_date else None,
                'stripe_customer_id': user.stripe_customer_id,
                'subscription_id': user.subscription_id,
                'tier_features': tier.features if tier else {},
                'max_file_size_mb': tier.max_file_size_mb if tier else 5,
                'max_analyses_per_month': tier.max_analyses_per_month if tier else 3
            }

        except Exception as e:
            logger.error(f"Error getting subscription info for user {user_id}: {str(e)}")
            return None
