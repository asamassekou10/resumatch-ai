# 7-Day Free Trial Flow Analysis

## Current Flow

### Step 1: User Clicks "7 Days Free"
- **Location**: Multiple places in the UI:
  - `FreeTrialBanner.jsx` - Links to `/register`
  - `PromotionBanner.jsx` - Links to `/register`
  - `GuestAnalyze.jsx` - Links to `/register`
  - `AuthPage.jsx` - Shows "Start your 7-day free trial" text

### Step 2: User Lands on Registration Page (`/register`)
- **Component**: `AuthPage.jsx` with `mode='register'`
- **UI Message**: "Start your 7-day free trial - No credit card required"
- User can register via:
  - Email/Password
  - Google OAuth
  - LinkedIn OAuth

### Step 3: User Submits Registration
- **Backend Endpoint**: `POST /api/auth/register` (line 489 in `app.py`)
- **What Happens**:
  1. User is created with:
     - `subscription_tier = 'free'` (default)
     - `credits = 5` (free tier allocation)
     - `email_verified = False`
  2. Verification email is sent
  3. Response indicates email verification is required

### Step 4: Email Verification
- User must verify email before they can login
- **Backend**: Checks `email_verified` flag on login (line 619 in `app.py`)
- If not verified, login is blocked with 403 error

### Step 5: After Login
- User is redirected to Dashboard
- **User Status**:
  - `subscription_tier = 'free'`
  - `credits = 5`
  - No trial period active
  - No trial expiration date tracked

## ❌ **THE PROBLEM**

**There is NO automatic 7-day free trial implementation!**

The current flow:
1. ✅ User clicks "7 days free" → Goes to registration
2. ✅ User registers → Gets free tier with 5 credits
3. ❌ **NO TRIAL ACTIVATION** - User just gets regular free tier
4. ❌ **NO TRIAL PERIOD TRACKING** - No start/end dates
5. ❌ **NO AUTOMATIC UPGRADE** - User stays on free tier

### What's Missing:

1. **Trial Subscription Logic**: No code to automatically grant a trial subscription
2. **Trial Period Tracking**: No database fields for `trial_start_date` or `trial_end_date`
3. **Trial Credits**: Should get Pro/Elite tier credits during trial, not just 5 free credits
4. **Trial Expiration**: No logic to downgrade after 7 days
5. **Stripe Trial Configuration**: No Stripe trial period configured in checkout sessions

## Recommended Solution

### Option 1: Automatic Trial on Registration (Recommended)
When user registers, automatically:
1. Set `subscription_tier = 'trial'` or `'pro'` (trial mode)
2. Set `trial_start_date = now()`
3. Set `trial_end_date = now() + 7 days`
4. Grant trial credits (e.g., 100 credits like Pro tier)
5. Track trial status in database

### Option 2: Stripe Trial Period
Configure Stripe checkout with trial period:
- Use Stripe's built-in trial functionality
- Set `subscription_data.trial_period_days = 7` in checkout session
- Handle trial expiration via webhook

### Option 3: Manual Trial Activation
Add a separate endpoint to activate trial:
- User must explicitly click "Start Trial" after registration
- More control but worse UX

## Database Changes Needed

Add to User model:
```python
trial_start_date = db.Column(db.DateTime, nullable=True)
trial_end_date = db.Column(db.DateTime, nullable=True)
is_trial_active = db.Column(db.Boolean, default=False)
trial_credits_granted = db.Column(db.Integer, default=0)
```

## Code Changes Needed

1. **Registration Endpoint** (`app.py` line 489):
   - Add trial activation logic
   - Set trial dates
   - Grant trial credits

2. **Login/Dashboard**:
   - Check if trial expired
   - Auto-downgrade if trial ended

3. **Stripe Checkout** (if using Option 2):
   - Add `trial_period_days: 7` to checkout session

4. **Webhook Handler**:
   - Handle trial expiration events

## Current User Experience

**What users expect**: "7 days free" → Get Pro/Elite features for 7 days

**What users actually get**: Regular free tier with 5 credits, no trial

**Result**: Misleading marketing, poor user experience, potential churn
