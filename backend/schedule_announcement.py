"""
Scheduler script to send feature announcement email at a specific time.
This script will run continuously and send the announcement at the scheduled time.

Usage:
    python schedule_announcement.py
"""

import sys
import os
import time
import requests
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
API_URL = "https://resumatch-backend-7qdb.onrender.com"
ADMIN_EMAIL = "alhassane.samassekou@gmail.com"

# Schedule: January 19, 2026 at 2:45 AM
SCHEDULED_YEAR = 2026
SCHEDULED_MONTH = 1
SCHEDULED_DAY = 19
SCHEDULED_HOUR = 2
SCHEDULED_MINUTE = 45

def login_and_get_token():
    """
    Login using Google OAuth simulation or direct database access.
    For production, you'll need to provide admin credentials.
    """
    from app import app, db
    from models import User
    from flask_jwt_extended import create_access_token

    with app.app_context():
        # Get admin user
        admin_user = User.query.filter_by(email=ADMIN_EMAIL, is_admin=True).first()

        if not admin_user:
            print(f"❌ Admin user not found: {ADMIN_EMAIL}")
            return None

        # Create JWT token
        token = create_access_token(identity=str(admin_user.id))
        return token

def send_announcement_now(token):
    """Send announcement email to all users"""
    print(f"\n{'='*60}")
    print(f"🚀 SENDING FEATURE ANNOUNCEMENT")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        response = requests.post(
            f"{API_URL}/api/admin/send-feature-announcement",
            json={"send_to_all": True},
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"   Sent: {data.get('data', {}).get('sent', 0)}")
            print(f"   Failed: {data.get('data', {}).get('failed', 0)}")

            errors = data.get('data', {}).get('errors', [])
            if errors:
                print(f"\n⚠️  Errors:")
                for error in errors[:10]:
                    print(f"   - {error}")
                if len(errors) > 10:
                    print(f"   ... and {len(errors) - 10} more")

            return True
        else:
            print(f"\n❌ Failed: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n❌ Error sending announcement: {e}")
        return False

def main():
    print("="*60)
    print("FEATURE ANNOUNCEMENT SCHEDULER")
    print("="*60)
    print(f"API URL: {API_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")

    # Calculate scheduled time
    scheduled_time = datetime(
        SCHEDULED_YEAR, SCHEDULED_MONTH, SCHEDULED_DAY,
        SCHEDULED_HOUR, SCHEDULED_MINUTE, 0
    )

    print(f"\n📅 Scheduled Time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if scheduled time has already passed
    now = datetime.now()
    if now > scheduled_time:
        print(f"\n⚠️  WARNING: Scheduled time has already passed!")
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        response = input("\nDo you want to send the announcement NOW instead? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled.")
            return 1

        scheduled_time = now

    # Get authentication token
    print("\n🔄 Getting authentication token...")
    token = login_and_get_token()

    if not token:
        print("❌ Failed to get authentication token.")
        return 1

    print("✅ Token obtained successfully")

    # Wait until scheduled time
    time_diff = (scheduled_time - datetime.now()).total_seconds()

    if time_diff > 0:
        print(f"\n⏰ Waiting until scheduled time...")
        print(f"   Time remaining: {int(time_diff // 3600)}h {int((time_diff % 3600) // 60)}m {int(time_diff % 60)}s")
        print(f"   Press Ctrl+C to cancel")

        try:
            # Sleep until scheduled time
            while datetime.now() < scheduled_time:
                remaining = (scheduled_time - datetime.now()).total_seconds()
                if remaining <= 0:
                    break

                # Show countdown every 60 seconds
                if remaining > 60:
                    print(f"   Time remaining: {int(remaining // 3600)}h {int((remaining % 3600) // 60)}m")
                    time.sleep(60)
                else:
                    time.sleep(remaining)

        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            return 1

    # Send announcement
    success = send_announcement_now(token)

    if success:
        print("\n✅ Announcement sent successfully!")
        return 0
    else:
        print("\n❌ Failed to send announcement")
        return 1

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
