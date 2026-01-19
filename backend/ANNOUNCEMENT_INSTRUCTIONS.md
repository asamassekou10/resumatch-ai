# Feature Announcement Email Instructions

## Quick Start

### Step 1: Test the Email (IMPORTANT - Do this first!)

```bash
cd backend
python send_announcement.py --mode test
```

Enter your admin email and password when prompted. This will send the email **only to your email** so you can review it.

### Step 2: Send to All Users (Production)

Once you've verified the test email looks good:

```bash
python send_announcement.py --mode production
```

- You'll need to type `SEND` to confirm
- This will send to all active, verified users who haven't opted out of marketing emails
- The script will show you a summary of sent/failed emails

## Using a Different API URL

If your API is not at localhost:5000, specify the URL:

```bash
python send_announcement.py --mode test --api-url https://your-api.com
```

Or set the environment variable:

```bash
export BACKEND_URL=https://your-api.com
python send_announcement.py --mode test
```

## Alternative: Using curl Directly

### Test with your email:

```bash
curl -X POST https://your-api.com/api/admin/send-feature-announcement \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_email": "your-email@example.com"}'
```

### Send to all users:

```bash
curl -X POST https://your-api.com/api/admin/send-feature-announcement \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"send_to_all": true}'
```

## What the Email Contains

The announcement email includes:
1. **Smart Job Description Import** - Paste job URLs to auto-extract descriptions
2. **Application Tracker** - Track job applications with status and notes
3. **Download Optimized Resume as PDF** - Modern & Classic templates

## Who Receives the Email

✅ **Will receive:**
- Active users (`is_active=True`)
- Verified email addresses (`email_verified=True`)
- Users who haven't opted out of marketing emails

❌ **Will NOT receive:**
- Inactive accounts
- Unverified email addresses
- Users who opted out of marketing emails (`email_preferences.marketing=False`)

## Troubleshooting

### "Admin access required" error
- Make sure your account has `is_admin=True` in the database
- Check: `SELECT email, is_admin FROM users WHERE email='your-email@example.com';`

### "Resend not configured" error
- Make sure `RESEND_API_KEY` is set in your environment variables
- Check Resend dashboard to verify API key is valid

### Some emails failed
- Check the error list in the response
- Common issues: bounced emails, invalid addresses
- These users will automatically be skipped

## Email Delivery Time

- Sending to 100 users: ~30-60 seconds
- Sending to 1000 users: ~5-10 minutes
- Emails are sent sequentially to avoid rate limits

## Need Help?

Check the logs:
```bash
# Backend logs will show email sending progress
tail -f logs/app.log
```
