# Guest Mode Implementation Plan
## Free 5-Credit Access Without Login

---

## Executive Summary

Enable new users to perform **one free resume analysis with 5 credits** without creating an account. This reduces friction while encouraging signup through quality conversion funnels.

**Key Principle:** Guests are temporary, stateless users. Their data doesn't persist. When they signup, they get a fresh account with 5 credits + whatever they earned as guests.

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Guest vs Authenticated User Flow

```
┌─────────────────────────────────────────┐
│         Visitor Lands on App            │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼─────┐      ┌────▼──────┐
   │ Anonymous │      │ Logged In │
   │  Guest    │      │   User    │
   │  (Token:  │      │  (Real    │
   │  'guest') │      │  Token)   │
   └────┬─────┘      └────┬──────┘
        │                 │
        │ 5 Free          │ Use Credits
        │ Credits         │ from Plan
        │                 │
   ┌────▼─────┐      ┌────▼──────┐
   │ Analyze  │      │  Analyze  │
   │ Once     │      │ Unlimited │
   │ (Demo)   │      │ (Paid)    │
   └────┬─────┘      └────┬──────┘
        │                 │
        │                 │
   ┌────▼─────────────────▼──────┐
   │   Results Page              │
   │   (Guest: Limited Sharing)  │
   │   (User: Full Features)     │
   └────┬─────────────────┬──────┘
        │                 │
   ┌────▼──────────┐     │
   │ "Join to Save"│     │
   │ CTA           │     │
   └──────────────┘     │
                        │
                   ┌────▼──────┐
                   │ Dashboard │
                   │ + History │
                   └───────────┘
```

### 1.2 Storage Strategy

**Guest Session Data (Short-lived):**
- Store in **Redis** (ideal) or **in-memory cache** with 24-hour TTL
- Key: `guest_session:{session_id}`
- Contains: credits used, analysis history (temporary), timestamp

**Alternative (if Redis unavailable):**
- Store in **PostgreSQL `guest_sessions` table** with auto-cleanup job
- Simpler to implement but requires DB cleanup

**Chosen Approach:** PostgreSQL table (matches existing infrastructure)

---

## 2. DATABASE CHANGES

### 2.1 New Tables

#### `guest_sessions` Table
```sql
CREATE TABLE guest_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    credits_used INTEGER DEFAULT 0,
    credits_remaining INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours',
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    status ENUM('active', 'expired', 'converted') DEFAULT 'active',
    converted_user_id INTEGER,  -- If converted to user
    INDEX idx_session_token (session_token),
    INDEX idx_expires_at (expires_at)
);
```

#### `guest_analyses` Table
```sql
CREATE TABLE guest_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_session_id UUID NOT NULL REFERENCES guest_sessions(id) ON DELETE CASCADE,
    resume_content TEXT,
    job_description TEXT,
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_guest_session_id (guest_session_id)
);
```

### 2.2 Schema Modifications

Add to `user_account` table:
```sql
ALTER TABLE user_account ADD COLUMN guest_session_id UUID REFERENCES guest_sessions(id);
```

This allows converting a guest session to a user account.

---

## 3. BACKEND CHANGES

### 3.1 New Endpoints

#### POST `/api/guest/session`
**Create a guest session**

Request:
```json
{
  "device_id": "optional_device_fingerprint"
}
```

Response:
```json
{
  "guest_token": "guest_xyz123...",
  "credits": 5,
  "expires_at": "2024-11-27T12:00:00Z",
  "session_id": "uuid"
}
```

Implementation:
- Generate unique `session_token`
- Create entry in `guest_sessions` table
- Return token to frontend (store in localStorage as `guest_token`)
- No authentication required

---

#### POST `/api/guest/analyze`
**Analyze resume as guest**

Request:
```json
{
  "resume": "base64_or_text",
  "job_description": "...",
  "job_title": "...",
  "company_name": "..."
}
```

Headers:
```
Authorization: Bearer guest_xyz123...
```

Implementation:
- Verify guest token exists and not expired
- Check `credits_remaining > 0`
- Run analysis (reuse existing logic)
- Deduct 1 credit (5 credits = 1 analysis or 5 pieces of feedback)
- Store in `guest_analyses` table
- Return results + remaining credits

Response:
```json
{
  "analysis_id": "uuid",
  "results": { ... },
  "credits_remaining": 0,
  "message": "You've used your free analysis. Create account to unlock more!"
}
```

---

#### POST `/api/guest/convert`
**Convert guest session to user account**

Request:
```json
{
  "email": "user@example.com",
  "password": "...",
  "guest_token": "guest_xyz123..."
}
```

Implementation:
- Verify guest token valid and not already converted
- Create new user with fresh 5 credits (IMPORTANT: not from guest)
- Link guest session to user: `user.guest_session_id = session.id`
- Update guest session: `status = 'converted'`, `converted_user_id = user.id`
- Optionally: save guest analysis to user's history (feature expansion)
- Return auth token

---

#### GET `/api/guest/analysis/{analysis_id}`
**Retrieve guest analysis results (limited)**

Implementation:
- No authentication required (public results)
- Verify guest token matches analysis
- Return analysis result only (not downloadable resume optimization)
- Show watermark: "Create account to download optimized resume"

---

### 3.2 Middleware Changes

#### New Middleware: `guest_or_auth_required()`
```python
def guest_or_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        # Try authenticated user first
        try:
            token = auth_header.split(' ')[1]
            identity = verify_jwt(token)
            g.user_id = int(identity)
            g.is_guest = False
            return f(*args, **kwargs)
        except:
            pass

        # Fall back to guest session
        try:
            guest_token = auth_header.split(' ')[1]
            guest_session = verify_guest_session(guest_token)
            g.guest_session_id = guest_session.id
            g.is_guest = True
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'Unauthorized'}), 401

    return decorated_function
```

---

### 3.3 Modified Endpoints

#### `/api/analyze` - Support Guest Mode
Currently: requires JWT token

Change to: use `@guest_or_auth_required()` middleware

Implementation:
```python
@app.route('/api/analyze', methods=['POST'])
@guest_or_auth_required()
def analyze():
    if g.is_guest:
        # Delegate to guest analyze endpoint
        return analyze_as_guest()
    else:
        # Existing user logic
        return analyze_as_user()
```

#### `/api/user/profile` - Add Guest Profile
Response for guests:
```json
{
  "id": "guest",
  "type": "guest",
  "email": null,
  "credits": 5,
  "analyses_count": 1,
  "expires_at": "2024-11-27T12:00:00Z",
  "message": "Guest access - create account to save your history"
}
```

---

### 3.4 Credit System Updates

**Credit Usage Rules:**
- Guest: 1 analysis = 5 credits (uses all credits)
- User: Various credits depending on feature:
  - Analysis = 1 credit
  - AI Feedback = 5 credits
  - Optimization = 10 credits
  - Cover Letter = 15 credits

This ensures guests get substantial value from 5 credits.

---

### 3.5 Rate Limiting & Abuse Prevention

#### Guest Rate Limiting
```python
# Limit to 1 analysis per 24-hour session
# Limit to 10 guest sessions per IP per day
# Require minimum 30 seconds between requests

@limiter.limit("1 per day", key_func=lambda: g.guest_session_id)
@limiter.limit("10 per day", key_func=lambda: request.remote_addr)
@limiter.limit("30 per minute")
@app.route('/api/guest/analyze', methods=['POST'])
@guest_or_auth_required()
def analyze():
    ...
```

#### IP-Based Tracking
- Track IP address in `guest_sessions`
- If same IP creates 10+ sessions in 24h, flag suspicious
- Implement CAPTCHA or cooldown

---

## 4. FRONTEND CHANGES

### 4.1 App.jsx Modifications

#### 1. Initialize Guest Session on Landing Page

```javascript
useEffect(() => {
  const initializeGuestMode = async () => {
    const existingGuest = localStorage.getItem('guest_token');

    if (!token && !existingGuest) {
      // Create guest session
      try {
        const response = await fetch(`${API_URL}/guest/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        localStorage.setItem('guest_token', data.guest_token);
        setGuestToken(data.guest_token);
        setGuestCredits(data.credits);
      } catch (err) {
        console.error('Failed to init guest mode:', err);
      }
    }
  };

  initializeGuestMode();
}, [token]);
```

#### 2. Modify Authorization Headers

```javascript
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  const guestToken = localStorage.getItem('guest_token');

  if (token) {
    return `Bearer ${token}`;
  } else if (guestToken) {
    return `Bearer ${guestToken}`;
  }
  return null;
};
```

#### 3. Update Analyze Page Access

**Current:** Shows "Must Login" screen
**New:** Allow analyze without login

```javascript
if (view === 'analyze') {
  return (
    <div className="min-h-screen ...">
      <Navigation ... />
      <div className="max-w-7xl mx-auto">
        {/* Show guest banner if no auth */}
        {!token && guestToken && (
          <motion.div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-4">
            <span className="text-blue-400">
              Guest Mode: 5 free credits • Results will not be saved
            </span>
            <button onClick={() => setView('register')} className="ml-auto">
              Create Account
            </button>
          </motion.div>
        )}

        <AnalyzeForm />
      </div>
    </div>
  );
}
```

#### 4. Modify Result Page for Guests

```javascript
if (view === 'result') {
  const isGuest = !token && guestToken;

  return (
    <div>
      {isGuest && (
        <div className="bg-amber-900/20 border border-amber-700 rounded-lg p-4 mb-4">
          <p className="text-amber-400">
            This analysis will be deleted in 24 hours.
            Create an account to save your results forever.
          </p>
          <button onClick={() => setView('register')}>
            Save & Create Account
          </button>
        </div>
      )}

      {/* Show results */}
      {/* Disable download/export buttons for guests */}
      {!isGuest && (
        <button>Download Optimized Resume</button>
      )}
    </div>
  );
}
```

### 4.2 Navigation Component Changes

```javascript
// Show different navigation for guests
if (!token && guestToken) {
  return (
    <nav>
      <div>Guest Mode • 5 Credits</div>
      <button onClick={() => setView('login')}>Login</button>
      <button onClick={() => setView('register')}>Sign Up</button>
    </nav>
  );
}

// Normal nav for logged-in users
return (
  <nav>
    {/* existing nav */}
  </nav>
);
```

### 4.3 Guest Banner Component (New)

Create `frontend/src/components/GuestModeBanner.jsx`

```javascript
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';

export const GuestModeBanner = ({ creditsRemaining, onCreateAccount }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-700 rounded-lg p-4 mb-6"
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-white font-semibold">Guest Mode</h3>
          <p className="text-blue-300 text-sm mt-1">
            You're using free guest access with {creditsRemaining} credits remaining.
            Results will be deleted in 24 hours.
          </p>
        </div>
        <button
          onClick={onCreateAccount}
          className="px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 whitespace-nowrap"
        >
          Create Account
        </button>
      </div>
    </motion.div>
  );
};
```

### 4.4 Update AnalyzeForm Component

```javascript
const handleAnalyze = async (e) => {
  // ... existing code ...

  const headers = {
    'Authorization': getAuthHeader(),
    'Content-Type': 'application/json'
  };

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers,
    body: formData
  });

  const data = await response.json();

  if (response.status === 402) {
    // Payment required
    setShowUpgradeModal(true);
  } else if (response.ok) {
    // For guests, show conversion CTA
    if (isGuest && data.credits_remaining === 0) {
      setShowConversionCTA(true);
    }
    setResults(data);
  }
};
```

### 4.5 Guest Conversion Flow (New)

Create `frontend/src/components/GuestConversionCTA.jsx`

```javascript
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

export const GuestConversionCTA = ({ onCreateAccount, onContinueGuest }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div className="bg-slate-800 rounded-2xl p-8 max-w-md border border-slate-700">
        <div className="text-center">
          <Zap className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">
            Free Analysis Complete!
          </h2>
          <p className="text-slate-300 mb-6">
            Create an account to unlock:
            <ul className="mt-4 space-y-2 text-left text-sm">
              <li>✓ 5 free credits monthly</li>
              <li>✓ Save all your analyses</li>
              <li>✓ Download optimized resume</li>
              <li>✓ Track job applications</li>
            </ul>
          </p>

          <div className="space-y-3">
            <button
              onClick={onCreateAccount}
              className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg"
            >
              Create Free Account
            </button>
            <button
              onClick={onContinueGuest}
              className="w-full bg-slate-700 text-white py-3 rounded-lg hover:bg-slate-600"
            >
              View Results as Guest
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
```

---

## 5. IMPLEMENTATION PHASES

### Phase 1: Backend Foundation (Week 1)
- [ ] Create `guest_sessions` and `guest_analyses` tables
- [ ] Add `guest_session_id` to `user_account`
- [ ] Implement `/api/guest/session` endpoint
- [ ] Implement `/api/guest/analyze` endpoint
- [ ] Add `guest_or_auth_required()` middleware
- [ ] Add rate limiting

### Phase 2: Frontend Integration (Week 2)
- [ ] Initialize guest session on landing
- [ ] Modify analyze page to accept guests
- [ ] Create GuestModeBanner component
- [ ] Create GuestConversionCTA component
- [ ] Update result page (hide premium features)
- [ ] Add guest auth headers

### Phase 3: Conversion Flow (Week 3)
- [ ] Implement `/api/guest/convert` endpoint
- [ ] Create signup flow that accepts guest_token
- [ ] Link guest analyses to new user
- [ ] Test conversion workflow

### Phase 4: Polish & Security (Week 4)
- [ ] Rate limiting testing
- [ ] IP-based abuse prevention
- [ ] Session cleanup cronjob
- [ ] Analytics tracking
- [ ] A/B test conversion messaging

---

## 6. CONSEQUENCES & MITIGATION

### 6.1 Negative Consequences

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Server load spike | High | Rate limiting, IP tracking, credit limit |
| Abuse (fake analyses) | Medium | CAPTCHA after 3 sessions, IP cooldown |
| Data storage | Medium | 24h auto-cleanup, aggressive pruning |
| Conversion rate confusion | Low | Clear analytics, separate funnels |
| Support tickets | Medium | Prominent "Results deleted in 24h" messages |
| Bot attacks | Medium | Device fingerprinting, IP blocking |

### 6.2 Positive Consequences

✅ **Lower barrier to entry** = more signups
✅ **Users experience value** = higher conversion
✅ **Natural funnel** = pays for itself in conversions
✅ **Competitive advantage** = stand out from similar apps
✅ **User validation** = gather feedback before signup

---

## 7. ANALYTICS & METRICS

Track these metrics:

```
Guest Mode:
- guest_sessions_created (daily)
- guest_analyses_completed (daily)
- guest_to_user_conversion_rate (%)
- time_to_signup (minutes)
- guest_session_duration (minutes)
- conversion_cta_clicks (count)
- premium_upgrade_rate (post-signup %)

Comparison:
- Direct signup rate vs. guest-then-signup rate
- Guest lifetime value vs. direct signup LTV
```

---

## 8. CLEANUP & MAINTENANCE

### Cronjob: Cleanup Expired Sessions
```python
# Run every 6 hours
@scheduler.scheduled_job('interval', hours=6)
def cleanup_expired_guest_sessions():
    expired = GuestSession.query.filter(
        GuestSession.expires_at < datetime.now()
    ).all()

    for session in expired:
        # Delete related analyses first
        GuestAnalysis.query.filter_by(
            guest_session_id=session.id
        ).delete()

        # Mark as expired
        session.status = 'expired'
        db.session.commit()

    # Hard delete after 30 days
    GuestSession.query.filter(
        GuestSession.expires_at < datetime.now() - timedelta(days=30),
        GuestSession.status == 'expired'
    ).delete()
    db.session.commit()
```

---

## 9. SECURITY CONSIDERATIONS

### 9.1 Guest Token Generation
```python
import secrets

guest_token = 'guest_' + secrets.token_urlsafe(32)
# Example: guest_9pX7bC-_jK2mL9nQ4rT5uV6wX8yZ...
```

### 9.2 CORS for Guest Endpoints
```python
@app.route('/api/guest/*')
def guest_routes():
    # Allow guest endpoints from any origin (public signup funnel)
    # But rate limit by IP
    pass
```

### 9.3 Guest Token Rotation
- Don't rotate guest tokens (one per session)
- Auto-expire after 24 hours
- No refresh needed

### 9.4 Prevent Privilege Escalation
```python
# Guest tokens can ONLY access /api/guest/* endpoints
# Cannot access /api/user/* or /api/admin/*
# Each endpoint validates guest token separately
```

---

## 10. FUTURE ENHANCEMENTS

1. **Guest Analytics:** Track guest behavior patterns
2. **Social Sharing:** Let guests share results (with watermark)
3. **Email Capture:** Collect email before analysis for re-engagement
4. **Timed Offers:** "Sign up now and get 10 credits instead of 5"
5. **Guest Team Mode:** Multiple analyses before signup
6. **Resume Comparison:** Guest compares multiple resumes

---

## 11. ROLLOUT PLAN

### Soft Launch (Internal Testing)
1. Enable for 10% of traffic
2. Monitor metrics for 1 week
3. Check conversion rate, abuse, server load

### Gradual Rollout
1. 25% of traffic (1 week)
2. 50% of traffic (1 week)
3. 100% rollout with monitoring

### Monitoring
- Ping ops/DevOps every 6 hours
- Set alerts on: error rate > 1%, response time > 2s, CPU > 80%
- Daily metrics review for 2 weeks post-launch

---

## 12. TESTING CHECKLIST

- [ ] Create guest session without login
- [ ] Perform analysis as guest
- [ ] Verify 1 analysis = 5 credits used
- [ ] Verify results don't persist after 24h
- [ ] Verify guest can't access premium features
- [ ] Test guest-to-user conversion
- [ ] Test rate limiting (10 sessions/day per IP)
- [ ] Test token expiration
- [ ] Test multiple guest sessions
- [ ] Verify guest banner messaging
- [ ] Test CTA conversions
- [ ] Load test: 100 concurrent guests
- [ ] Test cleanup cronjob

---

## Summary

This plan enables **frictionless onboarding** while maintaining **security** and **sustainability**. Guest mode is temporary, non-persistent, and naturally funnels users to signup through perceived value.

**Expected Impact:**
- +30-50% increase in landing page engagement
- +20-30% increase in signup rate
- +15-25% conversion rate from guest to paid user
