"""
One-time script to add the feature announcement to APScheduler.
Run this once to schedule the announcement email for Jan 19 at 2:45 AM.

This will add the job to your production backend's scheduler.

Usage:
    python add_scheduled_job.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, scheduler
from datetime import datetime
from models import User
from email_service import email_service
import logging

logger = logging.getLogger(__name__)

def send_feature_announcement_job():
    """
    Scheduled job to send feature announcement to all users.
    This will be executed by APScheduler at the scheduled time.
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
            # Check email preferences
            prefs = user.email_preferences or {}
            if prefs.get('marketing') == False:
                logger.info(f"Skipping {user.email} - opted out of marketing")
                continue

            try:
                # Generate unsubscribe token
                from itsdangerous import URLSafeTimedSerializer
                serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                token = serializer.dumps(user.email, salt='email-unsubscribe')
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                unsubscribe_link = f"{frontend_url}/unsubscribe?token={token}"

                # Send email
                success = email_service.send_feature_announcement_email(
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

        if errors:
            logger.error(f"Errors: {errors[:10]}")  # Log first 10 errors

        return {"sent": sent, "failed": failed, "errors": errors}

def main():
    """Add the scheduled job to APScheduler"""
    print("="*60)
    print("ADD SCHEDULED FEATURE ANNOUNCEMENT")
    print("="*60)

    with app.app_context():
        # Check if job already exists
        existing_jobs = scheduler.get_jobs()
        job_exists = any(job.id == 'feature_announcement_jan19' for job in existing_jobs)

        if job_exists:
            print("\n⚠️  Job already scheduled!")
            response = input("Remove existing job and reschedule? (yes/no): ")
            if response.lower() == 'yes':
                scheduler.remove_job('feature_announcement_jan19')
                print("✅ Existing job removed")
            else:
                print("❌ Cancelled")
                return 1

        # Schedule the job for January 19, 2026 at 2:45 AM
        scheduled_time = datetime(2026, 1, 19, 2, 45, 0)

        print(f"\n📅 Scheduling announcement for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Check if time has passed
        if datetime.now() > scheduled_time:
            print(f"\n⚠️  WARNING: Scheduled time has already passed!")
            response = input("Schedule for 2 minutes from now instead? (yes/no): ")
            if response.lower() == 'yes':
                from datetime import timedelta
                scheduled_time = datetime.now() + timedelta(minutes=2)
                print(f"   New time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("❌ Cancelled")
                return 1

        # Add the job
        scheduler.add_job(
            func=send_feature_announcement_job,
            trigger='date',
            run_date=scheduled_time,
            id='feature_announcement_jan19',
            name='Send feature announcement email',
            replace_existing=True
        )

        print("\n✅ Job scheduled successfully!")
        print(f"   Job ID: feature_announcement_jan19")
        print(f"   Run time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📋 All scheduled jobs:")

        for job in scheduler.get_jobs():
            print(f"   - {job.id}: {job.name} (next run: {job.next_run_time})")

        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
