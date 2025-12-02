# Guest Access Security Measures

## Overview
Comprehensive multi-layered security system to prevent abuse of guest access while maintaining good user experience.

## Security Layers Implemented

### 1. **Credit Limitation**
- **Changed from 5 to 2 analyses** per guest session
- Each analysis consumes 1 credit
- After 2 analyses, users must create an account
- **Files Modified:**
  - `backend/routes_guest.py`: Lines 133, 149
  - `frontend/src/components/GuestAnalyze.jsx`: Line 11, 143

### 2. **IP-Based Rate Limiting**
Prevents users from creating multiple sessions to bypass the 2-analysis limit.

**Session Creation Limits (per IP address):**
- Max 3 active guest sessions per IP per 24 hours
- Returns `429 Rate Limit Exceeded` error if exceeded
- **Implementation:** `backend/routes_guest.py` lines 95-108

**Daily Analysis Limits (per IP address):**
- Max 5 total analyses per IP per 24 hours (across all sessions)
- This prevents someone from creating 3 sessions × 2 analyses = 6 analyses
- Returns `429 Daily Limit Exceeded` error if exceeded
- **Implementation:** `backend/routes_guest.py` lines 112-123, 197-208

### 3. **Session Tracking**
- Each session tracked by:
  - IP address (captured from X-Forwarded-For header)
  - User Agent string
  - Device fingerprint (optional)
  - Session creation timestamp
  - Expiration timestamp (24 hours)

### 4. **Defense in Depth**
Multiple checkpoints prevent abuse:
1. **Session Creation:** IP limit checked before creating session
2. **Analysis Request:** IP and credit limits rechecked before analysis
3. **Database Level:** Credits tracked and decremented atomically

### 5. **Automatic Cleanup**
- Guest sessions expire after 24 hours
- Guest analyses expire after 24 hours
- Cleanup endpoint: `/api/guest/cleanup` (should be run via cron)
- **Implementation:** `backend/routes_guest.py` lines 325-358

## Error Handling

### Frontend Error Messages
User-friendly messages that encourage account creation:

| Error Type | Message |
|------------|---------|
| No Credits | "You've used all 2 free analyses. Create an account for unlimited access!" |
| Daily Limit | "Daily guest limit reached. Create an account for unlimited analyses!" |
| Rate Limit | "Too many sessions created. Please try again in 24 hours or create an account." |

**Implementation:** `frontend/src/components/GuestAnalyze.jsx` lines 115-127

### Backend Error Responses
Structured JSON responses with error types:
```json
{
  "error": "Error message",
  "error_type": "RATE_LIMIT_EXCEEDED|DAILY_LIMIT_EXCEEDED|INSUFFICIENT_CREDITS",
  "retry_after": "24 hours",
  "upgrade_message": "Create an account for unlimited access!"
}
```

## Protection Against Common Attacks

### 1. **Session Spam**
- ❌ **Attack:** User creates 100 sessions to get 200 analyses
- ✅ **Defense:** Max 3 sessions per IP + max 5 analyses per IP per day

### 2. **IP Rotation**
- ❌ **Attack:** User switches IPs (VPN/proxy) to bypass limits
- ✅ **Defense:** Device fingerprinting (optional) + 24h time window makes this impractical

### 3. **Token Reuse**
- ❌ **Attack:** User shares guest token with others
- ✅ **Defense:** Tokens tied to IP address; credits still limited to 2 per token

### 4. **Database Flooding**
- ❌ **Attack:** Create thousands of sessions to fill database
- ✅ **Defense:** IP rate limiting + automatic 24h expiration + cleanup cron job

## Monitoring & Logging

All security events are logged:
```
logger.warning(f"Rate limit exceeded for IP {ip_address}: {count} sessions in 24h")
logger.warning(f"Analysis limit exceeded for IP {ip_address}: {count} analyses in 24h")
logger.info(f"Created guest session {session_id} from {ip_address} (2 credits)")
```

## Recommended Cron Job

Add to server crontab to clean up expired sessions:
```bash
# Run cleanup every hour
0 * * * * curl -X POST http://localhost:5000/api/guest/cleanup
```

## User Experience Flow

### First-Time Guest User
1. Lands on site → Creates guest session
2. Gets 2 free analyses (24h validity)
3. Completes 1st analysis → 1 credit remaining
4. Completes 2nd analysis → 0 credits remaining
5. Sees upgrade prompt → Creates account

### Returning Guest (Same IP)
1. Tries to create new session
2. System checks: "This IP already has 1 active session with 0 credits used"
3. Allows new session (up to 3 total)
4. Still limited to 5 analyses per day total

### Abusive User
1. Creates 3 sessions (limit reached)
2. Tries 4th session → **Blocked with 429 error**
3. Uses all analyses across sessions (5 total)
4. Tries 6th analysis → **Blocked with 429 error**
5. Must wait 24 hours OR create account

## Database Schema

### GuestSession Table
```sql
- id (UUID)
- session_token (unique, indexed)
- credits_remaining (default: 2)
- credits_used (default: 0)
- ip_address (indexed for rate limiting)
- user_agent
- device_fingerprint (optional)
- status ('active', 'expired', 'converted')
- created_at (indexed for time-based queries)
- expires_at (indexed for cleanup)
```

### GuestAnalysis Table
```sql
- id (UUID)
- guest_session_id (foreign key, indexed)
- resume_text, job_description, etc.
- created_at (indexed)
- expires_at (indexed for cleanup)
```

## Security Best Practices Applied

✅ **Rate Limiting:** Multiple layers (session, analysis, IP)
✅ **Expiration:** All guest data auto-expires in 24h
✅ **Defense in Depth:** Checks at multiple points
✅ **Graceful Degradation:** Clear error messages
✅ **Database Efficiency:** Indexed queries for rate limit checks
✅ **Logging:** All security events logged for monitoring
✅ **User Privacy:** Minimal data collection (IP, User-Agent)

## Future Enhancements (Optional)

1. **CAPTCHA:** Add on 3rd failed attempt
2. **Account Linking:** Automatically transfer analyses on signup (already implemented!)
3. **Email Verification:** Require email for guest sessions (reduces abuse)
4. **Geolocation:** Different limits for different regions
5. **Behavioral Analysis:** ML-based abuse detection

## Testing

Test scenarios:
```bash
# Test 1: Normal usage (should work)
- Create session → 2 credits
- Analyze resume 1 → 1 credit left
- Analyze resume 2 → 0 credits left
- Try analyze resume 3 → 402 INSUFFICIENT_CREDITS

# Test 2: Session spam (should block)
- Create session 1 → OK
- Create session 2 → OK
- Create session 3 → OK
- Create session 4 → 429 RATE_LIMIT_EXCEEDED

# Test 3: Analysis spam (should block)
- Session 1: 2 analyses
- Session 2: 2 analyses
- Session 3: 1 analysis
- Total: 5 analyses → OK
- Session 3: 2nd analysis → 429 DAILY_LIMIT_EXCEEDED
```

## Summary

The guest access system now provides:
- ✅ **Fair usage:** 2 free analyses per user
- ✅ **Abuse prevention:** IP-based rate limiting
- ✅ **Good UX:** Clear upgrade prompts
- ✅ **Clean data:** Auto-expiration and cleanup
- ✅ **Conversion funnel:** Encourages account creation

**Result:** Users can try the product risk-free, but must subscribe for continued use.
