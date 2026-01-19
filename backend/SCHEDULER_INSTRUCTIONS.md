# Scheduled Announcement Email - Instructions

## Overview
This scheduler will automatically send the feature announcement email to all active users at **January 19, 2026 at 2:45 AM**.

## Quick Start

### Step 1: Run the Scheduler

Open a terminal and run:

```bash
cd backend
python schedule_announcement.py
```

The script will:
1. Connect to your database and get admin authentication
2. Calculate time until scheduled send (2:45 AM on Jan 19)
3. Wait until that time
4. Automatically send the announcement to all users

### Step 2: Keep the Terminal Open

**IMPORTANT**: You must keep the terminal window open until 2:45 AM on January 19th for the email to send.

The script will show a countdown every minute so you can track progress.

---

## Alternative: Run in Background (Recommended)

If you don't want to keep a terminal open, you can run this as a background task.

### Windows (PowerShell - Run as Administrator):

Create a scheduled task:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\Users\alhas\AI RESUME ANALYZER\backend\schedule_announcement.py" -WorkingDirectory "c:\Users\alhas\AI RESUME ANALYZER\backend"

$trigger = New-ScheduledTaskTrigger -Once -At "2026-01-19T02:44:00"

Register-ScheduledTask -TaskName "ResumeAI_FeatureAnnouncement" -Action $action -Trigger $trigger -Description "Send feature announcement email to all users"
```

To check if it's scheduled:
```powershell
Get-ScheduledTask -TaskName "ResumeAI_FeatureAnnouncement"
```

To remove the scheduled task:
```powershell
Unregister-ScheduledTask -TaskName "ResumeAI_FeatureAnnouncement" -Confirm:$false
```

---

## Alternative: Deploy to Server

If you want to ensure this runs even if your computer is off, deploy the scheduler to your Render backend.

### Option 1: Add to Render (One-time job)

1. Push the `schedule_announcement.py` to your git repository
2. SSH into your Render instance or use Render's console
3. Run: `python schedule_announcement.py`

### Option 2: Use APScheduler in your main app

Add this to your `app.py` to schedule from your production backend:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def scheduled_announcement_job():
    """Job to send feature announcement"""
    with app.app_context():
        from models import User
        from email_service import email_service

        # Get all active, verified users
        users = User.query.filter(
            User.is_active == True,
            User.email_verified == True
        ).all()

        sent = 0
        failed = 0

        for user in users:
            # Check email preferences
            prefs = user.email_preferences or {}
            if prefs.get('marketing') == False:
                continue

            # Send email
            success = email_service.send_feature_announcement_email(
                recipient_email=user.email,
                recipient_name=user.full_name or user.email.split('@')[0],
                unsubscribe_link=None  # Add unsubscribe link generation
            )

            if success:
                sent += 1
            else:
                failed += 1

        logger.info(f"Feature announcement sent: {sent} succeeded, {failed} failed")

# Initialize scheduler
scheduler = BackgroundScheduler()

# Schedule job for January 19, 2026 at 2:45 AM
scheduler.add_job(
    func=scheduled_announcement_job,
    trigger='date',
    run_date=datetime(2026, 1, 19, 2, 45, 0),
    id='feature_announcement',
    name='Send feature announcement email'
)

scheduler.start()
```

---

## Verify It Will Work

Before the scheduled time, you can test that the script works:

1. Edit `schedule_announcement.py` and change the scheduled time to 2 minutes from now:
   ```python
   # Test: Send in 2 minutes
   scheduled_time = datetime.now() + timedelta(minutes=2)
   ```

2. Run the script:
   ```bash
   python schedule_announcement.py
   ```

3. Wait 2 minutes and verify the email is sent

4. Change the time back to January 19 at 2:45 AM

---

## What Gets Sent

The announcement email includes:
1. **Smart Job Description Import** - Paste URLs to auto-extract job descriptions
2. **Application Tracker** - Track applications with status and notes
3. **Download Optimized Resume as PDF** - Modern & Classic templates

**Recipients**: All active, verified users who haven't opted out of marketing emails.

---

## Troubleshooting

### "Admin user not found"
- Make sure your email `alhassane.samassekou@gmail.com` is marked as `is_admin=True` in the database

### Script stopped working
- The scheduler needs to run continuously until the scheduled time
- Use Windows Task Scheduler or deploy to server for reliability

### Check if email will send
- Run the script and it will tell you how long until the scheduled time
- If the time has passed, it will offer to send immediately

---

## Support

If you encounter any issues, check the terminal output for error messages. The script will provide detailed feedback about what's happening.
