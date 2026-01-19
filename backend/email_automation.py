"""
Email Automation System
Handles scheduled emails for trial users using APScheduler
"""
import os
import logging
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

# Global scheduler instance
_email_scheduler = None

# Configurable schedule hours (UTC)
EMAIL_CHECK_HOUR = int(os.getenv('EMAIL_CHECK_HOUR', 9))
TRIAL_EXPIRY_CHECK_HOUR = int(os.getenv('TRIAL_EXPIRY_CHECK_HOUR', 10))
GRACE_PERIOD_CHECK_HOUR = int(os.getenv('GRACE_PERIOD_CHECK_HOUR', 11))
REENGAGEMENT_CHECK_HOUR = int(os.getenv('REENGAGEMENT_CHECK_HOUR', 12))


def can_send_email(user, email_type):
    """Check if user has opted in for a given email type"""
    prefs = user.email_preferences or {}
    if email_type == 'weekly':
        return prefs.get('weekly', True)
    if email_type == 'trial_updates':
        return prefs.get('trial_updates', True)
    if email_type == 'marketing':
        return prefs.get('marketing', True)
    return True


def send_feature_announcement(app, db, User, email_service):
    """
    Send feature announcement email to all active, verified users.
    This is a one-time scheduled job for announcing new features.
    """
    with app.app_context():
        logger.info("Starting scheduled feature announcement send")

        # Get all active, verified users
        users = User.query.filter(
            User.is_active == True,
            User.email_verified == True
        ).all()

        sent = 0
        failed = 0
        errors = []

        for user in users:
            # Check if user opted out of marketing emails
            if not can_send_email(user, 'marketing'):
                logger.info(f"Skipping {user.email} - opted out of marketing")
                continue

            try:
                # Generate unsubscribe link
                from itsdangerous import URLSafeTimedSerializer
                serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                token = serializer.dumps(user.email, salt='email-unsubscribe')
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                unsubscribe_link = f"{frontend_url}/unsubscribe?token={token}"

                # Send email
                success = send_email_with_retry(
                    email_service,
                    email_service.send_feature_announcement_email,
                    recipient_email=user.email,
                    recipient_name=user.full_name or user.email.split('@')[0],
                    unsubscribe_link=unsubscribe_link
                )

                if success:
                    sent += 1
                    logger.info(f"Feature announcement sent to {user.email}")
                else:
                    failed += 1
                    errors.append(f"Failed to send to {user.email}")

            except Exception as e:
                failed += 1
                error_msg = f"Error sending to {user.email}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        logger.info(f"Feature announcement complete: {sent} sent, {failed} failed")

        if errors and len(errors) > 0:
            logger.error(f"First 10 errors: {errors[:10]}")

        return {"sent": sent, "failed": failed, "errors": errors}


def send_email_with_retry(email_service, method, *args, max_retries=3, **kwargs):
    """Send email with retries and exponential backoff"""
    for attempt in range(max_retries):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to send email after {max_retries} attempts: {e}")
                return False
            sleep_for = 2 ** attempt
            logger.warning(f"Email send failed (attempt {attempt + 1}/{max_retries}). Retrying in {sleep_for}s...")
            time.sleep(sleep_for)
    return False


def process_users_in_batches(query, batch_size=100):
    """Yield users in batches to reduce memory usage"""
    offset = 0
    while True:
        users = query.offset(offset).limit(batch_size).all()
        if not users:
            break
        yield users
        offset += batch_size


def should_send_weekly_email(user, today):
    """
    Determine if a weekly email should be sent today.
    Returns (should_send: bool, days_remaining: int|None)
    """
    if not can_send_email(user, 'weekly'):
        return False, None

    if user.email_bounce_count and user.email_bounce_count >= 3:
        return False, None

    # Trial users: weekly emails start after 2-day follow-up (day 9)
    if user.is_trial_active and user.trial_start_date:
        trial_start = user.trial_start_date.date()
        days_since_trial_start = (today - trial_start).days
        if days_since_trial_start < 9:
            return False, None

        days_since_reference = days_since_trial_start - 2
        if days_since_reference < 7 or days_since_reference % 7 != 0:
            return False, None

        days_remaining = None
        if user.trial_end_date:
            trial_end = user.trial_end_date.date()
            days_remaining = (trial_end - today).days if trial_end else None
        return True, days_remaining

    # Non-trial users: use weekly_email_start_date or created_at
    reference = user.weekly_email_start_date or user.created_at
    if not reference:
        return False, None

    reference_date = reference.date()
    days_since_reference = (today - reference_date).days
    if days_since_reference < 7:
        return False, None
    if days_since_reference % 7 != 0:
        return False, None

    return True, None


def build_unsubscribe_link(user, email_service):
    """Generate unsubscribe link for a user"""
    try:
        token = email_service.generate_unsubscribe_token(user.id)
        if not token:
            return None
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/unsubscribe?token={token}"
    except Exception:
        return None

def init_email_scheduler(app, db, User, email_service):
    """
    Initialize email automation scheduler
    
    Args:
        app: Flask app instance
        db: SQLAlchemy database instance
        User: User model class
        email_service: EmailService instance
    """
    global _email_scheduler
    
    if _email_scheduler is not None:
        logger.warning("Email scheduler already initialized")
        return _email_scheduler
    
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    # Daily job to check and send scheduled emails
    scheduler.add_job(
        lambda: check_and_send_scheduled_emails(app, db, User, email_service),
        trigger=CronTrigger(hour=EMAIL_CHECK_HOUR, minute=0),
        id='daily_email_check',
        replace_existing=True
    )
    
    # Trial expiry checker
    scheduler.add_job(
        lambda: check_trial_expiry(app, db, User, email_service),
        trigger=CronTrigger(hour=TRIAL_EXPIRY_CHECK_HOUR, minute=0),
        id='trial_expiry_check',
        replace_existing=True
    )
    
    # Grace period handler
    scheduler.add_job(
        lambda: handle_grace_period_end(app, db, User, email_service),
        trigger=CronTrigger(hour=GRACE_PERIOD_CHECK_HOUR, minute=0),
        id='grace_period_check',
        replace_existing=True
    )

    # Re-engagement checker
    scheduler.add_job(
        lambda: check_inactive_users(app, db, User, email_service),
        trigger=CronTrigger(hour=REENGAGEMENT_CHECK_HOUR, minute=0),
        id='reengagement_check',
        replace_existing=True
    )

    # ONE-TIME: Feature announcement - send 1 minute after backend starts
    try:
        from datetime import datetime, timedelta
        # Schedule for 1 minute from now
        announcement_time = datetime.now() + timedelta(minutes=1)

        scheduler.add_job(
            lambda: send_feature_announcement(app, db, User, email_service),
            trigger='date',
            run_date=announcement_time,
            id='feature_announcement_jan19',
            replace_existing=True
        )
        logger.info(f"⚠️  FEATURE ANNOUNCEMENT scheduled for {announcement_time} (1 minute from now)")
    except Exception as e:
        logger.error(f"Failed to schedule feature announcement: {e}")

    _email_scheduler = scheduler
    logger.info("Email automation scheduler initialized")
    return scheduler

def check_and_send_scheduled_emails(app, db, User, email_service):
    """Check for users needing scheduled emails and send them"""
    with app.app_context():
        try:
            now = datetime.utcnow()
            today = now.date()
            
            emails_sent = 0
            emails_skipped_prefs = 0
            emails_skipped_engagement = 0
            updated_users = False

            # Find users with active trials for trial-specific emails (batch)
            active_trial_query = User.query.filter(
                and_(
                    User.is_trial_active == True,
                    User.trial_start_date.isnot(None),
                    User.trial_end_date.isnot(None)
                )
            )

            for batch in process_users_in_batches(active_trial_query):
                for user in batch:
                    try:
                        if not user.email_verified:
                            continue
                        if not can_send_email(user, 'trial_updates'):
                            emails_skipped_prefs += 1
                            continue
                        if user.email_bounce_count and user.email_bounce_count >= 3:
                            emails_skipped_engagement += 1
                            continue

                        trial_start = user.trial_start_date.date() if user.trial_start_date else None
                        days_since_start = (today - trial_start).days if trial_start else None

                        # 2-day follow-up email (trial-specific)
                        if days_since_start == 2 and user.email_sequence_step < 2:
                            feedback_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/help?feedback=true"
                            recipient_name = user.name or user.email.split('@')[0]
                            unsubscribe_link = build_unsubscribe_link(user, email_service)

                            if send_email_with_retry(email_service, email_service.send_followup_email, user.email, recipient_name, feedback_link, unsubscribe_link):
                                user.email_sequence_step = 2
                                user.last_email_sent_date = now
                                emails_sent += 1
                                logger.info(f"Sent 2-day follow-up email to {user.email}")

                    except Exception as e:
                        logger.error(f"Error processing trial email for user {user.email}: {str(e)}", exc_info=True)
                        continue

            # Weekly emails for ALL active users (trial and non-trial) in batches
            weekly_query = User.query.filter(
                and_(
                    User.email_verified == True,
                    User.is_active == True,
                    or_(User.weekly_email_start_date.isnot(None), User.created_at.isnot(None))
                )
            )

            for batch in process_users_in_batches(weekly_query):
                for user in batch:
                    try:
                        # Initialize weekly_email_start_date if missing
                        if not user.weekly_email_start_date and user.created_at:
                            user.weekly_email_start_date = user.created_at
                            updated_users = True

                        should_send, days_remaining = should_send_weekly_email(user, today)
                        if not should_send:
                            continue

                        # Check duplicate window (last 6 days)
                        last_email_date = user.last_email_sent_date.date() if user.last_email_sent_date else None
                        if last_email_date and (today - last_email_date).days < 6:
                            continue

                        # Engagement checks: skip if no opens in last 30 days
                        last_open_date = user.last_email_opened_date.date() if user.last_email_opened_date else None
                        if not last_open_date or (today - last_open_date).days > 30:
                            emails_skipped_engagement += 1
                            continue

                        # If no clicks in 60+ days, reduce frequency (require 14 days since last send)
                        last_click_date = user.last_email_clicked_date.date() if user.last_email_clicked_date else None
                        if (not last_click_date or (today - last_click_date).days > 60) and last_email_date and (today - last_email_date).days < 14:
                            emails_skipped_engagement += 1
                            continue

                        recipient_name = user.name or user.email.split('@')[0]
                        unsubscribe_link = build_unsubscribe_link(user, email_service)
                        if send_email_with_retry(email_service, email_service.send_weekly_checkin_email, user.email, recipient_name, days_remaining, unsubscribe_link):
                            user.last_email_sent_date = now
                            emails_sent += 1
                            logger.info(f"Sent weekly check-in email to {user.email} (trial: {user.is_trial_active})")

                    except Exception as e:
                        logger.error(f"Error processing weekly email for user {user.email}: {str(e)}", exc_info=True)
                        continue

            if emails_sent > 0 or updated_users:
                db.session.commit()
                logger.info(f"Sent {emails_sent} scheduled emails (skipped prefs: {emails_skipped_prefs}, skipped engagement: {emails_skipped_engagement})")
            
        except Exception as e:
            logger.error(f"Error in scheduled email check: {str(e)}", exc_info=True)
            db.session.rollback()

def check_trial_expiry(app, db, User, email_service):
    """Check for expired trials and send expiry emails"""
    with app.app_context():
        try:
            now = datetime.utcnow()
            today = now.date()
            
            # Find users whose trial expired today (trial_end_date is today or earlier)
            expired_trials = User.query.filter(
                and_(
                    User.is_trial_active == True,
                    User.trial_end_date.isnot(None),
                    User.trial_end_date <= now,
                    or_(
                        User.trial_expired_date.is_(None),  # Haven't sent expiry email yet
                        User.trial_expired_date > User.trial_end_date  # Expired but not processed
                    )
                )
            ).all()
            
            emails_sent = 0
            
            for user in expired_trials:
                try:
                    if not user.email_verified:
                        continue
                    
                    # Check if user has already subscribed (shouldn't happen, but safety check)
                    if user.subscription_status == 'active' and user.subscription_tier in ['pro', 'elite']:
                        # User subscribed, mark trial as inactive
                        user.is_trial_active = False
                        continue
                    
                    # Send expiry email
                    recipient_name = user.name or user.email.split('@')[0]
                    trial_end_date = user.trial_end_date
                    unsubscribe_link = build_unsubscribe_link(user, email_service)
                    
                    if email_service.send_trial_expiry_email(user.email, recipient_name, trial_end_date, unsubscribe_link):
                        user.trial_expired_date = now
                        user.email_sequence_step = 4  # Expiry email sent
                        user.last_email_sent_date = now
                        emails_sent += 1
                        logger.info(f"Sent trial expiry email to {user.email}")
                
                except Exception as e:
                    logger.error(f"Error processing trial expiry for user {user.email}: {str(e)}", exc_info=True)
                    continue
            
            if emails_sent > 0:
                db.session.commit()
                logger.info(f"Processed {emails_sent} expired trials")
            
        except Exception as e:
            logger.error(f"Error in trial expiry check: {str(e)}", exc_info=True)
            db.session.rollback()

def handle_grace_period_end(app, db, User, email_service):
    """Handle grace period end - downgrade users who didn't subscribe"""
    with app.app_context():
        try:
            now = datetime.utcnow()
            grace_period_end = now - timedelta(days=3)
            
            # Find users whose trial expired 3+ days ago and haven't subscribed
            users_to_downgrade = User.query.filter(
                and_(
                    User.is_trial_active == True,
                    User.trial_end_date.isnot(None),
                    User.trial_end_date <= grace_period_end,
                    User.subscription_status != 'active',  # Not subscribed
                    or_(
                        User.subscription_tier == 'pro',  # Still on pro (trial)
                        User.subscription_tier == 'trial'
                    )
                )
            ).all()
            
            downgraded = 0
            emails_sent = 0
            
            for user in users_to_downgrade:
                try:
                    # Send final email before downgrade
                    if user.email_sequence_step < 5:  # Haven't sent final email
                        recipient_name = user.name or user.email.split('@')[0]
                        unsubscribe_link = build_unsubscribe_link(user, email_service)
                        if email_service.send_trial_expired_email(user.email, recipient_name, unsubscribe_link):
                            user.email_sequence_step = 5
                            user.last_email_sent_date = now
                            emails_sent += 1
                            logger.info(f"Sent final trial expired email to {user.email}")
                    
                    # Downgrade to free tier
                    user.subscription_tier = 'free'
                    user.subscription_status = 'inactive'
                    user.credits = 5  # Free tier credits
                    user.is_trial_active = False
                    downgraded += 1
                    logger.info(f"Downgraded user {user.email} from trial to free tier")
                
                except Exception as e:
                    logger.error(f"Error downgrading user {user.email}: {str(e)}", exc_info=True)
                    continue
            
            if downgraded > 0 or emails_sent > 0:
                db.session.commit()
                logger.info(f"Downgraded {downgraded} users and sent {emails_sent} final emails")
            
        except Exception as e:
            logger.error(f"Error in grace period handler: {str(e)}", exc_info=True)
            db.session.rollback()


def check_inactive_users(app, db, User, email_service):
    """Send re-engagement emails to inactive users"""
    with app.app_context():
        try:
            now = datetime.utcnow()
            today = now.date()
            inactivity_threshold = now - timedelta(days=14)

            inactive_query = User.query.filter(
                and_(
                    User.email_verified == True,
                    User.is_active == True,
                    User.last_login.isnot(None),
                    User.last_login <= inactivity_threshold,
                    User.email_bounce_count < 3
                )
            )

            emails_sent = 0
            emails_skipped_prefs = 0

            for batch in process_users_in_batches(inactive_query):
                for user in batch:
                    try:
                        if not can_send_email(user, 'marketing'):
                            emails_skipped_prefs += 1
                            continue

                        # Avoid spamming: skip if we sent any email in last 5 days
                        if user.last_email_sent_date and (today - user.last_email_sent_date.date()).days < 5:
                            continue

                        days_inactive = (today - user.last_login.date()).days if user.last_login else None
                        recipient_name = user.name or user.email.split('@')[0]
                        unsubscribe_link = build_unsubscribe_link(user, email_service)

                        if send_email_with_retry(email_service, email_service.send_reengagement_email, user.email, recipient_name, days_inactive, unsubscribe_link):
                            user.last_email_sent_date = now
                            emails_sent += 1
                            logger.info(f"Sent re-engagement email to {user.email} after {days_inactive} days inactive")

                    except Exception as e:
                        logger.error(f"Error processing re-engagement for user {user.email}: {str(e)}", exc_info=True)
                        continue

            if emails_sent > 0:
                db.session.commit()
                logger.info(f"Sent {emails_sent} re-engagement emails (skipped prefs: {emails_skipped_prefs})")

        except Exception as e:
            logger.error(f"Error in re-engagement check: {str(e)}", exc_info=True)
            db.session.rollback()


def get_scheduler():
    """Get the global email scheduler instance"""
    return _email_scheduler

def shutdown_scheduler():
    """Shutdown the email scheduler"""
    global _email_scheduler
    if _email_scheduler:
        _email_scheduler.shutdown()
        _email_scheduler = None
        logger.info("Email scheduler shut down")
