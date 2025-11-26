# Abuse Prevention & Security System

## Overview

ResuMatch AI has a comprehensive abuse prevention system to protect against:
- Credit system exploitation
- API rate limit bypass
- Malicious automation
- Service degradation attacks
- Unfair resource usage

---

## How the System Works

### 1. Credit System

Each user action consumes credits:

| Operation | Free | Pro | Elite |
|-----------|------|-----|-------|
| Resume Analysis | 1 credit | 1 credit | 1 credit |
| AI Feedback | 1 credit | 1 credit | 1 credit |
| Resume Optimization | 2 credits | 2 credits | 2 credits |
| Cover Letter | 2 credits | 2 credits | 2 credits |
| Skill Suggestions | 1 credit | 1 credit | 1 credit |

**Example:** Free user with 5 credits can do 5 analyses OR 2 optimizations + 1 analysis.

### 2. Daily Credit Limits

Even if users have monthly credits, daily limits prevent abuse:

| Tier | Daily Limit | Monthly Credits | Use Case |
|------|------------|-----------------|----------|
| Free | 5 credits | 5 total | Very limited |
| Pro | 100 credits | 100 credits | Full monthly limit available |
| Elite | 1000 credits | 1000 credits | Unrestricted |

**Example:** Pro user with 100 monthly credits can use up to 100 in one day, or spread throughout the month.

### 3. Rate Limiting (Per Hour)

Prevents rapid-fire requests:

| Operation | Free | Pro | Elite |
|-----------|------|-----|-------|
| Resume Analysis | 2/hour | 10/hour | 50/hour |
| AI Feedback | 2/hour | 5/hour | 20/hour |
| Resume Optimization | 1/hour | 5/hour | 20/hour |
| Cover Letter | 1/hour | 5/hour | 20/hour |
| Skill Suggestions | 2/hour | 10/hour | 50/hour |

**Example:** Free user cannot do more than 2 analyses per hour, even if they have credits.

### 4. Abuse Pattern Detection

The system detects suspicious patterns:

- **Rapid-fire requests:** >10 operations in 5 minutes → blocked with 429 error
- **Daily limit exceeded:** Using all daily credits → blocked until next day
- **Insufficient credits:** Not enough for operation → 402 Payment Required

**Responses:**
```json
{
  "error": "Too many requests. Please wait before trying again.",
  "remaining_seconds": 300
}
```

---

## Security Layers

### Layer 1: Authentication
- JWT tokens with 7-day expiration
- User identity verification on every request
- Session validation

### Layer 2: Credit Validation
```python
# Before any operation:
1. Check user has sufficient credits
2. Check daily limit not exceeded
3. Check hourly rate limit not exceeded
4. Perform operation
5. Deduct credits
```

### Layer 3: Rate Limiting
- Per-tier rate limits via Flask-Limiter
- Per-operation limits
- IP-based request throttling

### Layer 4: Anomaly Detection
- Detects rapid-fire requests
- Logs suspicious activity
- Can trigger account review

### Layer 5: Logging
All actions logged with:
- User ID
- Operation type
- Credits used
- Timestamp
- Client IP
- Success/failure status

---

## Pricing Impact on Revenue

### Free Tier
- No revenue
- Goal: User acquisition and conversion
- Low resource cost (5 credits worth)

### Pro Tier ($9.99/month)
- 100 credits/month = ~$0.10 per credit
- User pays ~$0.10-0.20 per analysis (2-4 analyses)
- Gemini API costs: ~$0.03-0.10 per analysis
- Profit margin: ~60-70%

### Elite Tier ($49.99/month)
- 1000 credits/month = ~$0.05 per credit
- Better profit margin for power users
- Volume discount pricing
- Target: Professionals, recruiters, coaches

---

## How to Test Abuse Prevention

### Test 1: Credit Deduction
```bash
# Login and run 1 analysis
# Check API response includes credit count
# Expected: credits decrease by 1

curl -X GET https://your-api.com/api/user \
  -H "Authorization: Bearer YOUR_TOKEN"
# Response should show: "credits": 4 (after 1 analysis from 5)
```

### Test 2: Daily Limit
```bash
# As free user, run 6 analyses (using all 5 + 1 more)
# Expected: 6th request returns 429 error

for i in {1..6}; do
  curl -X POST https://your-api.com/api/analyze \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "resume=@resume.pdf" \
    -F "job_description=test"
done

# Last request: "error": "Daily credit limit reached"
```

### Test 3: Hourly Rate Limit
```bash
# As free user, try 3 analyses in rapid succession
# Expected: 3rd request returns 429 error

for i in {1..3}; do
  curl -X POST https://your-api.com/api/analyze ... &
done
wait

# 3rd request: "error": "Too many requests. Please wait"
```

### Test 4: Abuse Pattern Detection
```bash
# Run 15 operations in 5 minutes (faster than rate limit)
# Expected: Requests blocked due to abuse pattern

# Watch logs for:
# [SECURITY] User X - Suspicious activity: 15 operations in 5 minutes
```

### Test 5: Tier Enforcement
```bash
# As Pro user:
# - Should allow 10 analyses/hour (not 2)
# - Should allow 100 daily credits
# - Should reach tier limits, not free limits

# Verify Pro can do more:
for i in {1..10}; do
  curl -X POST https://your-api.com/api/analyze \
    -H "Authorization: Bearer PRO_TOKEN" ...
done

# All 10 should succeed
```

---

## Monitoring & Alerts

### What to Monitor

Log into your Render dashboard and check:

1. **Error Logs** - Look for repeated 429 or 402 errors
2. **User Activity** - Spike in operations = potential abuse
3. **Revenue** - Track upgrade rates and ARPU (Average Revenue Per User)
4. **API Performance** - If slow, abuse may be happening

### Key Metrics

```
Healthy System:
- <1% of requests get 429 (rate limited)
- <2% of requests get 402 (insufficient credits)
- Average operations per user: 5-10/day
- Daily active users: 50-100+
- Conversion (Free→Pro): 10-20%

Red Flags:
- >5% 429 errors = abuse or aggressive crawlers
- User with 100+ operations/day = botting
- Spike in operations at specific times = automation
- Same IP making different accounts = evasion
```

---

## Admin Responses to Abuse

### Automated Response (System Handles)
- Blocks request with 429 error
- Logs suspicious activity
- No manual action needed

### Manual Response (If Needed)

**Suspected Bot Account:**
```python
# Disable user account
user = User.query.get(user_id)
user.is_active = False
db.session.commit()
# Send notification to user
```

**Abusive User Upgrade:**
```python
# Downgrade to free
user.subscription_tier = 'free'
user.credits = 5
user.subscription_id = None
db.session.commit()
# Notify them of TOS violation
```

**DDoS Attack:**
```python
# Block IP range temporarily
# Use nginx/CloudFlare rate limiting
# Alert monitoring system
```

---

## Implementation Details

### File: `backend/abuse_prevention.py`

Key functions:
- `check_daily_credit_limit()` - Enforces daily limits
- `check_abuse_pattern()` - Detects rapid requests
- `has_sufficient_credits()` - Validates credit balance
- `deduct_credits()` - Deducts after successful operation
- `get_tier_rate_limit()` - Returns tier-specific limits
- `get_tier_info()` - Returns pricing/features

### File: `backend/app.py`

Modified endpoints:
- `/api/analyze` - Added abuse prevention checks
- `/api/payments/webhook` - Tier-based credit allocation
- All AI endpoints - Credit deduction

---

## Best Practices for Users

### Free Users
- Use your 5 credits wisely
- Plan job applications before analyzing
- Upgrade to Pro for unlimited features

### Pro Users
- 100 credits/month = ~20 analyses
- Manage your daily usage (can use all in 1 day)
- Request support for higher limits if needed

### Elite Users
- 1000 credits/month = no practical limit
- Access to API webhooks for automation
- Dedicated support available

---

## Compliance & Privacy

- **No data mining:** Credit system prevents scraping
- **Fair usage:** Everyone gets the same rate limits per tier
- **Transparent:** Users see their credit count in real-time
- **Auditable:** All operations logged with timestamps
- **Compliant:** GDPR/CCPA ready with user control

---

## Future Enhancements

1. **Variable pricing:** Charge per credit (pay-as-you-go)
2. **Corporate plans:** Bulk credits for teams
3. **Usage alerts:** Notify when approaching limits
4. **White-label:** Allow partners to use as API
5. **Analytics dashboard:** Show users their usage patterns
6. **Machine learning:** Detect more sophisticated abuse patterns

---

## Support

### User Questions
- "Why can't I do more analyses?" → Daily limit reached
- "Can I get more credits?" → Upgrade to Pro/Elite
- "Why was my request blocked?" → Rate limit exceeded

### Troubleshooting
- Check credit balance: `/api/user` endpoint
- View rate limits: Returned in response headers
- Check daily usage: Visible in dashboard

---

## Summary

✅ **Multi-layer protection** against abuse
✅ **Fair pricing** for all user tiers
✅ **Transparent limits** shown to users
✅ **Automatic enforcement** (no manual work)
✅ **Detailed logging** for compliance
✅ **Scalable design** for growth

Your system is now **secure and profitable**! 🚀

