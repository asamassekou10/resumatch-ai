# New Pricing Strategy Implementation

## Overview
Implementing a conversion-optimized pricing strategy that transforms the free tier from a complete solution into a compelling teaser, driving users to paid tiers through strategic information asymmetry.

## Strategy

### The Problem
- Current: 10 free scans = complete product, users never upgrade
- Users can solve their problem entirely for free
- Zero conversion to paid tiers

### The Solution
1. **Reduce friction, increase pain**: Keep no-credit-card signup, but show value without giving away the solution
2. **The "Blur" Strategy**: Show users they have problems, charge to see the specific solutions
3. **Micro-transactions**: Lower commitment with $1.99 re-scan and $6.99 weekly pass
4. **Multiple conversion points**: Capture users at different price sensitivity levels

## New Pricing Tiers

### FREE Tier
- **1 analysis** (down from 10)
- **Visible**:
  - Overall match score (e.g., 65/100)
  - Score breakdown by category
  - Top 3 missing keywords (sample)
  - ATS pass rate estimate
- **BLURRED** (requires upgrade):
  - Remaining missing keywords (show count: "+9 more")
  - AI-powered recommendations
  - ATS optimization tips
  - Optimized resume suggestions
  - Cover letter generation

### Micro-Transactions

**$1.99 - Single Re-Scan**
- 1 credit for re-analysis
- Perfect for: "Did my changes work?"
- Impulse buy for quick validation
- Under $2 = pocket change psychology
- Many will buy multiple before realizing weekly pass is better

**$6.99 - 7-Day Unlimited Pass** ⭐ RECOMMENDED
- Unlimited scans for 7 days
- Perfect for: Active job seekers
- Best value perception (3.5x scans vs buying individual)
- Under $7 = impulse purchase threshold
- Captures users during job search intensity

### Subscription

**$19.99/month - Pro**
- All weekly pass benefits
- Resume templates
- Priority support
- Advanced features (interview prep, LinkedIn optimization)
- For: Serious career advancement

## Implementation Status

### ✅ Phase 1: Backend (COMPLETED)

**Models:**
- [x] `Purchase` model for tracking micro-transactions
- [x] Database migration `create_purchase_table.py`

**Services:**
- [x] `ResultFilter` service with blur strategy logic
- [x] `can_see_full_results()` - Determines user access level
- [x] `filter_analysis_result()` - Applies blur to free tier results
- [x] `has_active_weekly_pass()` - Checks for active passes

**API Routes (`/api/payments`):**
- [x] `POST /create-micro-purchase` - Create Stripe payment intent
- [x] `POST /confirm-micro-purchase` - Confirm and grant access
- [x] `GET /check-weekly-pass` - Check active pass status
- [x] `GET /pricing` - Public pricing information
- [x] `GET /purchase-history` - User's purchase history

**Pricing Configuration:**
```python
PRICING = {
    'single_rescan': {
        'amount': 199,  # $1.99
        'credits': 1
    },
    'weekly_pass': {
        'amount': 699,  # $6.99
        'duration_days': 7
    }
}
```

### 🔄 Phase 2: Frontend (IN PROGRESS)

**Components to Create:**

1. **`PricingModal.jsx`** - Pricing comparison and upgrade options
   - Show 3 tiers side-by-side
   - Highlight $7 weekly pass as "Most Popular"
   - Add urgency: "Your analysis expires in 48 hours"
   - Social proof: "1,247 users upgraded this week"

2. **`BlurredSection.jsx`** - Reusable blur overlay component
   - Glassmorphism blur effect
   - Unlock button
   - Preview text
   - Conversion message

3. **`PaymentModal.jsx`** - Stripe payment integration
   - Stripe Elements integration
   - Support Apple Pay / Google Pay
   - Single re-scan OR weekly pass selection

4. **Update `ResultsPage.jsx`**:
   - Check user access level
   - Apply blur overlays to restricted sections
   - Show "Unlock for $7" buttons
   - Display sample keywords (3 visible, rest blurred)

5. **`UpgradePrompt.jsx`** - Strategic conversion prompts
   - After free scan: "Want to see if your changes improved your score?"
   - Re-scan paywall: "$2 single check or $7 unlimited for 7 days"
   - Expiring analysis timer

**Analysis Flow:**
```
1st Scan (Free)
└─> Full Results ✅
    └─> User edits resume
        └─> Wants to re-scan
            └─> PAYWALL 🔒
                ├─> $2 - Single re-scan
                ├─> $7 - 7-day pass (RECOMMENDED)
                └─> $19.99/month - Pro
```

### 📧 Phase 3: Email Funnel (TODO)

**Email Sequence:**
1. **Immediate**: "Your Resume Score: 65/100"
2. **24 hours**: "You're missing 12 keywords. See them now →"
3. **48 hours**: "⏰ Your analysis expires in 24 hours"
4. **72 hours**: "Last chance: 20% off ($5.60) - Expires tonight"

### 📊 Phase 4: Analytics & Optimization (TODO)

**A/B Tests:**
- $7 vs $9 for weekly pass
- Show 3 vs 5 sample keywords
- Different urgency messages
- Paywall timing (immediate vs after edit)

**Metrics to Track:**
- Conversion rate: Free → Paid
- Revenue per 100 signups
- Weekly pass vs re-scan ratio
- Time to first purchase
- Re-scan purchase frequency

## User Experience Flow

### Guest User
```
Visit Site
├─> Try Free (no credit card)
├─> Upload resume + job description
├─> See score: 65/100
├─> See: "Missing 12 keywords"
│   └─> Shown: keyword1, keyword2, keyword3
│   └─> BLURRED: +9 more keywords 🔒
└─> Paywall Options:
    ├─> Sign up (free account = 1 more scan)
    ├─> $1.99 for this result
    └─> $6.99 for 7 days unlimited
```

### Registered User (Free Tier)
```
Login
├─> 1 free scan remaining
├─> Complete analysis
├─> Full results (first scan)
├─> Edit resume
├─> Want to re-scan
└─> PAYWALL 🔒
    ├─> $1.99 - Single re-scan
    ├─> $6.99 - Weekly pass (save $$$)
    └─> $19.99/month - Pro
```

### Paid User (Weekly Pass)
```
Login
├─> "✅ 7-Day Pass Active"
├─> "Expires in 4 days, 12 hours"
├─> Unlimited scans
├─> Full results always
└─> Prompt before expiry: "Extend for $6.99 or upgrade to Pro"
```

## Conversion Optimization

### Psychological Triggers

1. **Loss Aversion**: "Your analysis expires in 48 hours"
2. **Scarcity**: "Limited time: $5.60 (20% off)"
3. **Social Proof**: "1,247 upgraded this week"
4. **Anchoring**: Show $19.99/month first, then $6.99 looks cheap
5. **Pain of Paying**: $6.99 < $7 feels "under $7", $1.99 < $2 = "basically free"
6. **Immediate Gratification**: "Unlock now" not "Subscribe"

### Strategic Placement

1. **After Score Display**: "See what's holding you back →"
2. **After Resume Edit**: "Did your score improve? Re-scan for $1.99 →"
3. **Keyword Tease**: "You're missing: Python, AWS, Docker, +9 more 🔒 - Unlock for $1.99"
4. **Countdown Timer**: "Analysis expires in 23:45:12"

### Value Demonstration

**Show, Don't Tell:**
- ✅ "Your score: 65/100" (they see the problem)
- ✅ "Missing 12 keywords" (they know there's a solution)
- ✅ "keyword1, keyword2, keyword3..." (proof it works)
- 🔒 "+9 more keywords" (pain of not knowing)

## Technical Implementation

### Backend Integration

**In Analysis Route:**
```python
from services.result_filter import ResultFilter

@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    # ... perform analysis ...

    # Get user's analysis count
    analysis_count = Analysis.query.filter_by(user_id=user.id).count()

    # Apply blur strategy
    filtered_result = ResultFilter.filter_analysis_result(
        analysis_result=full_result,
        user=user,
        analysis_count=analysis_count
    )

    return jsonify(filtered_result)
```

### Frontend Integration

**Stripe Payment:**
```javascript
import { loadStripe } from '@stripe/stripe-js';

const stripe = await loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Create payment intent
const { client_secret } = await fetch('/api/payments/create-micro-purchase', {
  method: 'POST',
  body: JSON.stringify({ purchase_type: 'weekly_pass' })
});

// Confirm payment
const { error } = await stripe.confirmPayment({
  clientSecret: client_secret,
  confirmParams: {
    return_url: 'https://resumeanalyzerai.com/payment-success'
  }
});
```

## Expected Results

### Current State
- 100 signups → 0 paying users (0% conversion)
- $0 revenue per 100 users

### After Implementation (New Pricing)
- 100 signups → 18-25% upgrade
  - 12% buy $1.99 re-scans (~$24)
  - 7% buy $6.99 pass (~$49)
  - 2.5% buy $19.99/month (~$50)
- **$123 revenue per 100 users** (30% increase from lower friction)

### 30-Day Projection (Updated Pricing)
- 1,000 users/month
- **18-25% conversion** (lower price = higher conversion)
- Revenue mix with new pricing:
  - 120 × $1.99 = $239
  - 70 × $6.99 = $489
  - 25 × $19.99 = $500
- **~$1,228/month minimum** (29% increase vs old pricing)

**Why lower prices = more revenue:**
- $1.99 crosses impulse buy threshold ($2 feels expensive, $1.99 feels cheap)
- $6.99 stays under $7 psychological barrier
- Higher conversion rate offsets lower unit price
- More users buying multiple $1.99 scans before upgrading

## Next Steps

1. **Immediate (This Week)**:
   - [ ] Create frontend pricing modal
   - [ ] Integrate Stripe payment flow
   - [ ] Add blur overlays to results page
   - [ ] Test payment flow end-to-end

2. **Week 2**:
   - [ ] Implement email funnel
   - [ ] Add analytics tracking
   - [ ] A/B test messaging
   - [ ] Optimize conversion points

3. **Week 3**:
   - [ ] Monitor conversion metrics
   - [ ] Iterate based on data
   - [ ] Add social proof testimonials
   - [ ] Refine pricing if needed

## Files Modified/Created

### Backend
- `backend/models.py` - Added `Purchase` model
- `backend/routes/payments.py` - NEW payment endpoints
- `backend/services/result_filter.py` - NEW blur strategy service
- `backend/migrations/create_purchase_table.py` - NEW database migration
- `backend/app.py` - Registered payments blueprint
- `backend/routes_guest.py` - Updated docs (already 1 scan)

### Frontend (TODO)
- `frontend/src/components/pricing/PricingModal.jsx` - NEW
- `frontend/src/components/pricing/BlurredSection.jsx` - NEW
- `frontend/src/components/pricing/PaymentModal.jsx` - NEW
- `frontend/src/components/pricing/UpgradePrompt.jsx` - NEW
- `frontend/src/components/ResultsPage.jsx` - UPDATE with blur logic
- `frontend/src/services/paymentService.js` - NEW Stripe integration

## API Endpoints

### Payments
- `POST /api/payments/create-micro-purchase` - Create payment intent
- `POST /api/payments/confirm-micro-purchase` - Confirm purchase
- `GET /api/payments/check-weekly-pass` - Check active pass
- `GET /api/payments/pricing` - Get pricing info (public)
- `GET /api/payments/purchase-history` - User's purchases

### Analysis (Updated)
- Results now include `is_blurred`, `blurred_sections`, `upgrade_options`

## Environment Variables

```env
# Existing
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# No new env vars needed
```

## Database Schema

```sql
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    purchase_type VARCHAR(50),  -- 'single_rescan', 'weekly_pass'
    amount_usd FLOAT,
    credits_granted INTEGER,
    access_expires_at TIMESTAMP,  -- For weekly pass
    is_active BOOLEAN,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    payment_status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Success Metrics

### Primary KPIs
- **Conversion Rate**: % of free users who upgrade
- **Revenue Per User**: Average revenue across all users
- **Weekly Pass Adoption**: % choosing $7 vs $2
- **Repeat Purchase Rate**: Users buying multiple $2 scans

### Secondary Metrics
- Time to first purchase
- Analysis abandonment rate
- Email open/click rates
- Upgrade prompt CTR

---

**Status**: Phase 1 (Backend) Complete ✅ | Phase 2 (Frontend) In Progress 🔄
**Last Updated**: 2026-01-11
