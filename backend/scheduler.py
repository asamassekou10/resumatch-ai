"""
Background scheduler for periodic tasks
Handles monthly credit resets, trial expirations, and other recurring jobs
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.subscription_service import SubscriptionService
import logging

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()


def setup_scheduler():
    """Setup and start all scheduled jobs"""

    # Daily credit reset check (runs at 2 AM UTC daily)
    scheduler.add_job(
        func=reset_monthly_credits_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='reset_monthly_credits',
        name='Reset monthly credits for subscribers',
        replace_existing=True
    )

    # Daily trial expiration check (runs at 3 AM UTC daily)
    scheduler.add_job(
        func=check_trial_expirations_job,
        trigger=CronTrigger(hour=3, minute=0),
        id='check_trial_expirations',
        name='Check and expire trials',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started with the following jobs:")
    logger.info("  - Monthly credit reset: Daily at 2:00 AM UTC")
    logger.info("  - Trial expiration check: Daily at 3:00 AM UTC")


def reset_monthly_credits_job():
    """Job wrapper for monthly credit reset"""
    try:
        logger.info("Starting monthly credit reset job...")
        count = SubscriptionService.reset_monthly_credits()
        logger.info(f"Monthly credit reset job completed: {count} users updated")
    except Exception as e:
        logger.error(f"Error in monthly credit reset job: {str(e)}")


def check_trial_expirations_job():
    """Job wrapper for trial expiration check"""
    try:
        logger.info("Starting trial expiration check job...")
        count = SubscriptionService.check_trial_expirations()
        logger.info(f"Trial expiration check job completed: {count} trials expired")
    except Exception as e:
        logger.error(f"Error in trial expiration check job: {str(e)}")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
