# Market Intelligence Pages - Comprehensive Improvement Plan

## Executive Summary
Transform the Market Intelligence pages from static data displays into an AI-powered, real-time job market intelligence platform exclusively for subscribed users. This plan focuses on providing actionable insights that directly help job seekers succeed.

---

## 1. Subscription Access Control

### Frontend Implementation
**File:** `frontend/src/App.jsx`

**Changes Needed:**
```javascript
// Add subscription check before rendering MarketIntelligenceDashboard
const canAccessMarketPages = () => {
  return user && user.subscription_status === 'active';
};

// Wrap route with subscription check
{canAccessMarketPages() ? (
  <Route path="/market" element={<MarketIntelligenceDashboard />} />
) : (
  <Route path="/market" element={<SubscriptionRequired feature="Market Intelligence" />} />
)}
```

### Backend Implementation
**File:** `backend/routes.py` (new endpoint group)

**Add Middleware:**
```python
def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)

        if not user or user.subscription_status != 'active':
            return jsonify({
                'error': 'Active subscription required',
                'error_type': 'SUBSCRIPTION_REQUIRED',
                'upgrade_url': '/pricing'
            }), 403

        return f(*args, **kwargs)
    return decorated_function

# Apply to all market intelligence routes
@bp.route('/api/market/*')
@jwt_required()
@subscription_required
def market_routes():
    pass
```

**New Component:** `frontend/src/components/SubscriptionRequired.jsx`
- Beautiful upgrade prompt
- List of premium features
- Direct link to pricing page
- Show what they're missing out on

---

## 2. AI-Powered Features Using Gemini

### Feature 1: Real-Time Job Market Trends Analysis
**What It Does:** Analyzes current job market conditions for the user's industry/role

**Implementation:**
- **Backend:** `backend/gemini_service.py` - New function `analyze_market_trends()`
- **Prompt:** "Analyze current job market trends for [role] in [location]. Consider hiring velocity, salary trends, skill demand, and remote work availability. Provide actionable insights."
- **Data Sources:** Combine user's profile + web scraping + cached statistics
- **Update Frequency:** Daily cache, refresh on demand

**UI Display:**
```
📈 Market Trend Alert
"Software Engineer roles in San Francisco show 23% increase in demand this month.
Remote positions up 15%. Top hiring companies: Google, Meta, Stripe.
Average salary range: $140K-$180K (+8% from last quarter)."

🎯 Action: Companies are prioritizing React & TypeScript skills - your resume is well-positioned!
```

---

### Feature 2: AI-Powered Company Intelligence
**What It Does:** Deep dive into any company before applying

**Implementation:**
- **File:** `backend/routes_market.py` - New endpoint `/api/market/company-intel`
- **Input:** Company name
- **Gemini Prompt:**
  ```
  Research [Company Name] and provide job seekers with:
  1. Company culture and values
  2. Interview process insights
  3. Common interview questions for [role]
  4. Employee satisfaction signals
  5. Growth trajectory and stability
  6. Best departments to target
  7. Application tips specific to this company
  ```

**UI Display:**
- Searchable company database
- Save companies to watchlist
- Get alerts when new jobs posted
- See AI-generated interview prep guide

---

### Feature 3: Intelligent Salary Negotiation Assistant
**What It Does:** Provides real-time salary data + negotiation strategies

**Implementation:**
- **Endpoint:** `/api/market/salary-intel`
- **Data Sources:**
  - Glassdoor API (if available)
  - H1B salary database (public data)
  - Bureau of Labor Statistics
  - Gemini analysis of trends

**Gemini Analysis:**
```python
def get_salary_intelligence(job_title, location, years_experience, skills):
    prompt = f"""
    As a salary negotiation expert, analyze the market for:
    - Role: {job_title}
    - Location: {location}
    - Experience: {years_experience} years
    - Key Skills: {', '.join(skills)}

    Provide:
    1. Realistic salary range (25th, 50th, 75th percentile)
    2. Factors that increase/decrease offers
    3. Negotiation talking points
    4. Red flags in offers
    5. Total compensation breakdown (equity, bonus, benefits)
    6. Location-specific cost of living adjustments
    """
```

**UI Display:**
```
💰 Salary Intelligence for "Senior Data Scientist, NYC"

Market Range: $130K - $185K (based on 847 data points)
Your Target: $160K - $175K (based on your 5 years experience + Python, ML, SQL)

🎯 Negotiation Strategy:
• Lead with your ML model deployment experience (high-value skill)
• Mention your GitHub contributions (shows thought leadership)
• Ask about equity: typical range is 0.05%-0.15% for your level
• Request sign-on bonus if salary is lower end ($10K-$25K standard)

⚠️ Red Flags:
• Offers below $130K are 20% under market
• Watch for unpaid overtime expectations
• Clarify remote work policy in writing
```

---

### Feature 4: Skills Gap Analysis with Learning Paths
**What It Does:** Compare user's skills against market demand + provide learning roadmap

**Implementation:**
- **Endpoint:** `/api/market/skills-gap`
- **Analysis:** User's resume skills vs. top demanded skills in their industry
- **Gemini Integration:** Generate personalized learning path

**UI Display:**
```
🎯 Your Skills Competitiveness Score: 78/100

✅ Strong Skills (in high demand):
• Python (mentioned in 89% of Data Science jobs)
• SQL (mentioned in 76% of jobs)
• Machine Learning (mentioned in 71% of jobs)

⚠️ Skills to Add (high ROI):
• PyTorch (mentioned in 54% of jobs, you have TensorFlow)
• Cloud Platforms - AWS/GCP (mentioned in 62% of jobs)
• Docker/Kubernetes (mentioned in 48% of jobs)

📚 Personalized Learning Path (Est. 3 months to close gaps):

Week 1-4: PyTorch Fundamentals
→ Free Course: "PyTorch for Deep Learning" (fast.ai)
→ Project: Port your TensorFlow model to PyTorch
→ Add to resume: "Implemented neural networks in PyTorch and TensorFlow"

Week 5-8: AWS Certified Cloud Practitioner
→ Course: AWS Training (free tier)
→ Project: Deploy ML model on AWS SageMaker
→ Certification: Take AWS CCP exam ($100)

Week 9-12: Docker & Kubernetes Basics
→ Course: "Docker & Kubernetes: The Complete Guide" (Udemy)
→ Project: Containerize your portfolio projects
→ Add to resume: "Containerized applications using Docker, orchestrated with K8s"

💡 Expected Impact: +15% match score on average job posting
```

---

### Feature 5: Job Application Tracker with AI Insights
**What It Does:** Track applications + get AI-powered follow-up recommendations

**Database Schema:**
```sql
CREATE TABLE job_applications (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_name VARCHAR(200),
    job_title VARCHAR(200),
    job_url TEXT,
    application_date TIMESTAMP,
    status VARCHAR(50), -- applied, screening, interview, offer, rejected
    resume_version_id UUID,
    cover_letter_id UUID,
    contacts JSONB, -- [{name, email, linkedin, interaction_date}]
    notes TEXT,
    follow_up_dates JSONB,
    ai_insights TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Gemini AI Insights:**
```python
def generate_application_insights(application):
    prompt = f"""
    The user applied to {application.company_name} for {application.job_title}
    on {application.application_date}. Current status: {application.status}.

    Provide:
    1. Optimal follow-up timing (if not heard back)
    2. Suggested follow-up message template
    3. Red flags to watch for
    4. Interview preparation tips for this specific company
    5. Likelihood of success based on timing and status
    """
```

**UI Display:**
```
📊 Applications Dashboard

Active Applications: 12
Interviews Scheduled: 3
Offers: 1
Success Rate: 8% (industry avg: 5%)

Recent Applications:
┌─────────────────────────────────────────────────────┐
│ Google - Senior ML Engineer                         │
│ Applied: 5 days ago                                 │
│ Status: Application Under Review                    │
│                                                     │
│ 🤖 AI Insight:                                      │
│ • Average response time: 7-10 business days        │
│ • 68% of applicants don't hear back (high volume)  │
│ • Recommendation: Connect with recruiter on        │
│   LinkedIn (Sarah Chen - ML Recruiting)            │
│ • Follow-up: Wait 2 more days, then send polite   │
│   inquiry email                                    │
│                                                     │
│ 📝 Suggested Follow-up (ready to send):            │
│ "Hi [Recruiter], I applied for the Senior ML      │
│ Engineer role on [date]. I'm very excited about   │
│ the opportunity to contribute to Google's AI      │
│ initiatives. Would you be able to share any       │
│ updates on my application status? Happy to        │
│ provide additional information."                   │
└─────────────────────────────────────────────────────┘
```

---

### Feature 6: Interview Preparation with Company-Specific Questions
**What It Does:** AI-generated interview questions based on company + role

**Implementation:**
```python
def generate_interview_prep(company_name, job_title, job_description):
    prompt = f"""
    Generate a comprehensive interview preparation guide for:
    Company: {company_name}
    Role: {job_title}

    Job Description:
    {job_description}

    Provide:
    1. 10 technical questions they're likely to ask (with answer frameworks)
    2. 5 behavioral questions specific to company culture
    3. Questions YOU should ask them (shows research)
    4. Common mistakes to avoid for this company
    5. What they value most in candidates (based on company values)
    6. Dress code and interview format expectations
    """
```

**UI Display:**
```
🎯 Interview Prep: Google - Senior ML Engineer

📚 Technical Questions (10):

Q1: "Explain the bias-variance tradeoff and how you'd diagnose it in production"
💡 Answer Framework:
• Definition: Bias = underfitting, Variance = overfitting
• Diagnosis: Learning curves, cross-validation scores
• Real example: "In my previous role, I noticed high training accuracy
  but poor validation accuracy (high variance). I addressed this by..."
• Google-specific angle: Mention scalability and production monitoring

Q2: "How would you design a recommendation system for YouTube?"
💡 Answer Framework:
• Clarify scope: Cold start? Real-time? Personalization level?
• Architecture: Candidate generation → Ranking → Re-ranking
• ML approach: Collaborative filtering + content-based + deep learning
• Mention: A/B testing, feedback loops, diversity vs. engagement

[...8 more questions...]

🗣️ Behavioral Questions (5):

Q1: "Tell me about a time you disagreed with a teammate"
💡 Google's Focus: Psychological safety, respectful disagreement
Your Angle: Show you can challenge ideas while maintaining relationships

[...4 more questions...]

❓ Questions YOU Should Ask (5):

1. "How does the ML team balance research exploration with product deadlines?"
   Why: Shows you understand Google's research culture

2. "What metrics define success for this role in the first 6 months?"
   Why: Shows goal-orientation

[...3 more questions...]

⚠️ Common Mistakes at Google:
• Don't focus only on technical skills - they value communication
• Avoid saying "I don't know" - instead say "Here's how I'd approach finding out"
• Don't badmouth previous employers (they ask behavioral questions to test this)
```

---

### Feature 7: Real-Time Job Alerts with Match Scoring
**What It Does:** Personalized job recommendations with AI-powered match analysis

**Implementation:**
- Scrape job boards daily (Indeed, LinkedIn, Glassdoor)
- Store in database with embeddings
- Match against user profile
- Gemini scores each job + explains why it's a good fit

**Database Schema:**
```sql
CREATE TABLE job_postings (
    id UUID PRIMARY KEY,
    title VARCHAR(300),
    company VARCHAR(200),
    location VARCHAR(200),
    job_description TEXT,
    requirements TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    remote_type VARCHAR(50), -- remote, hybrid, onsite
    posted_date TIMESTAMP,
    source VARCHAR(100), -- indeed, linkedin, etc
    source_url TEXT,
    embedding VECTOR(768), -- for similarity search
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE job_matches (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_posting_id UUID REFERENCES job_postings(id),
    match_score INTEGER, -- 0-100
    ai_explanation TEXT,
    status VARCHAR(50), -- new, saved, applied, dismissed
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Gemini Match Scoring:**
```python
def score_job_match(user_resume, user_preferences, job_posting):
    prompt = f"""
    Score how well this job matches the candidate (0-100):

    CANDIDATE PROFILE:
    {user_resume}

    Preferences:
    - Desired roles: {user_preferences.target_roles}
    - Locations: {user_preferences.locations}
    - Remote: {user_preferences.remote_preference}
    - Min salary: {user_preferences.min_salary}

    JOB POSTING:
    {job_posting.title} at {job_posting.company}
    {job_posting.job_description}

    Provide:
    1. Match score (0-100)
    2. 3 reasons this is a good fit
    3. 2 potential concerns
    4. Recommended action (apply now, save for later, skip)
    5. Estimated competition level (low/medium/high)
    """
```

**UI Display:**
```
🔔 New Job Matches Today: 7

┌─────────────────────────────────────────────────────┐
│ Senior Data Scientist - Stripe                      │
│ San Francisco, CA (Remote-friendly) • $160K-$200K   │
│ Posted: 2 hours ago                                 │
│                                                     │
│ 🎯 Match Score: 94/100 - Excellent Fit             │
│                                                     │
│ ✅ Why this is great for you:                      │
│ 1. Your Python + ML experience directly matches    │
│    their core requirements                         │
│ 2. They need fraud detection expertise - you       │
│    have anomaly detection projects                 │
│ 3. Salary is 15% above your target range          │
│                                                     │
│ ⚠️ Considerations:                                 │
│ 1. Requires 6 years experience (you have 5)       │
│    → Still apply, your projects are strong         │
│ 2. Preference for distributed systems (not your   │
│    strongest area)                                 │
│    → Emphasize your scalability work               │
│                                                     │
│ 🤖 AI Recommendation: APPLY NOW                    │
│ Competition: Medium (posted recently, well-known   │
│ company attracts many applicants)                  │
│                                                     │
│ 📄 Use Your: "ML_Engineer_Resume_v3.pdf" (92%     │
│ match to job requirements)                         │
│                                                     │
│ [Apply] [Save for Later] [Dismiss]                │
└─────────────────────────────────────────────────────┘
```

---

### Feature 8: Career Path Visualization
**What It Does:** Show career progression paths with AI-powered recommendations

**Gemini Implementation:**
```python
def generate_career_path(current_role, years_experience, skills):
    prompt = f"""
    Create a career progression roadmap for:
    Current: {current_role} ({years_experience} years experience)
    Skills: {', '.join(skills)}

    Provide 3 potential career paths with:
    1. Next logical role (1-2 years)
    2. Mid-term goal (3-5 years)
    3. Long-term goal (5-10 years)
    4. Skills needed for each transition
    5. Typical salary progression
    6. Companies known for this path
    """
```

**UI Display:**
```
🚀 Your Career Paths

Path 1: Technical Leadership Track (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Now                1-2 Years          3-5 Years         5-10 Years
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data Scientist  →  Senior DS      →  ML Lead       →  Director of ML
$120K              $160K              $220K             $300K+

Skills to Build:
• Next: Team leadership, mentoring, system design
• 3-5yr: Product strategy, stakeholder management
• 5-10yr: Org building, budget management, vision setting

Companies: Google, Meta, Airbnb (strong IC-to-leadership paths)

Path 2: Deep Technical Specialist Track
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data Scientist  →  ML Engineer   →  Staff ML Eng  →  Principal/Distinguished
$120K              $170K              $250K             $350K+

Skills to Build:
• Next: MLOps, production deployment, optimization
• 3-5yr: Novel research, open-source contributions
• 5-10yr: Industry thought leadership, conference speaking

Companies: OpenAI, DeepMind, NVIDIA (research-focused)

Path 3: Business/Product Track
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data Scientist  →  Product DS    →  DS Manager    →  VP of Analytics
$120K              $150K              $200K             $280K+

Skills to Build:
• Next: SQL, business metrics, A/B testing
• 3-5yr: Product sense, roadmap planning
• 5-10yr: Cross-functional leadership, P&L ownership

Companies: Spotify, Netflix, Uber (data-driven product companies)

💡 Based on your profile, Path 1 is recommended because:
• You have 2 mentorship experiences already
• Your communication skills are strong
• You've led cross-functional projects
```

---

### Feature 9: Networking Opportunity Finder
**What It Does:** Suggests networking events, people to connect with, communities to join

**Gemini Implementation:**
```python
def find_networking_opportunities(user_location, user_industry, user_goals):
    prompt = f"""
    Find networking opportunities for:
    Location: {user_location}
    Industry: {user_industry}
    Goals: {user_goals}

    Suggest:
    1. Local meetups and conferences
    2. Online communities to join
    3. Types of people to connect with on LinkedIn
    4. Coffee chat script templates
    5. How to add value before asking for help
    """
```

**UI Display:**
```
🤝 Networking Opportunities

This Month in San Francisco:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Mar 15: SF Machine Learning Meetup
   Topic: "Production ML at Scale"
   Why attend: Netflix ML engineer speaking (potential contact)
   Action: RSVP + prepare 1 question to ask

📅 Mar 22: DataEngConf 2025
   $199 ticket (worth it - major companies recruiting)
   Action: Apply for diversity scholarship (deadline Mar 10)

Online Communities:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• r/MachineLearning - 2.8M members
  Post your projects, get feedback

• MLOps Community Slack - 45K members
  Active job board, great for learning

• Kaggle - Competitions + networking
  Current: Prediction challenge (use for portfolio)

LinkedIn Strategy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connect with (15 per week max):
1. Alumni from your university in target companies
2. Recruiters at companies you want to work for
3. People who comment on posts in your industry

Connection message template:
"Hi [Name], I saw your post about [topic] and really appreciated
your insight on [specific point]. I'm a data scientist working
on similar problems. Would love to connect and learn from your
experience at [Company]."

☕ Coffee Chat Guide:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Learn + build relationship (not ask for job)

Opening: "Thanks for taking the time! I'm exploring career
paths in ML and would love to hear about your journey."

Questions to ask:
• How did you break into [company]?
• What do you wish you knew earlier in your career?
• What skills are most valuable for [role]?
• Any advice for someone in my position?

Closing: "This was incredibly helpful. I'd love to stay in
touch. Would it be okay if I send you updates as I progress?"

Follow-up: Send thank you email within 24 hours + LinkedIn connection
```

---

## 3. Real-Time Data Integration

### Data Sources

**Job Postings:**
- Indeed API (if available)
- LinkedIn Jobs scraper (with rate limiting)
- GitHub Jobs
- Hacker News Who's Hiring threads
- Company career pages (direct scraping)

**Salary Data:**
- H1B Salary Database (public, free)
- Glassdoor (web scraping)
- Levels.fyi (web scraping)
- Payscale API

**Company Data:**
- Glassdoor reviews
- LinkedIn company pages
- Crunchbase (funding, growth)
- Built In (company culture)

**Industry Trends:**
- Stack Overflow Developer Survey
- GitHub trending repositories
- Google Trends for technologies
- Bureau of Labor Statistics

### Caching Strategy

**To minimize Gemini API costs:**

```python
# Cache expensive AI analyses
CACHE_DURATIONS = {
    'market_trends': 24 * 60 * 60,  # 24 hours
    'company_intel': 7 * 24 * 60 * 60,  # 7 days
    'salary_data': 30 * 24 * 60 * 60,  # 30 days
    'skills_demand': 24 * 60 * 60,  # 24 hours
    'interview_questions': 30 * 24 * 60 * 60,  # 30 days (company-specific)
}

# Use Redis for caching
def get_cached_or_generate(cache_key, generator_function, ttl):
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = generator_function()
    redis_client.setex(cache_key, ttl, json.dumps(result))
    return result
```

**Smart Cache Invalidation:**
- User can force refresh (costs 1 credit or has daily limit)
- Auto-refresh when data is likely stale (e.g., job posting > 7 days old)
- Background jobs refresh popular queries daily

---

## 4. Technical Architecture

### New Backend Files

**`backend/routes_market.py`** - All market intelligence endpoints
```python
from flask import Blueprint
from decorators import jwt_required, subscription_required

market_bp = Blueprint('market', __name__, url_prefix='/api/market')

@market_bp.route('/trends', methods=['GET'])
@jwt_required()
@subscription_required
def get_market_trends():
    pass

@market_bp.route('/company-intel/<company_name>', methods=['GET'])
@jwt_required()
@subscription_required
def get_company_intelligence(company_name):
    pass

@market_bp.route('/salary-intel', methods=['POST'])
@jwt_required()
@subscription_required
def get_salary_intelligence():
    pass

@market_bp.route('/skills-gap', methods=['GET'])
@jwt_required()
@subscription_required
def analyze_skills_gap():
    pass

@market_bp.route('/job-matches', methods=['GET'])
@jwt_required()
@subscription_required
def get_job_matches():
    pass

@market_bp.route('/interview-prep', methods=['POST'])
@jwt_required()
@subscription_required
def generate_interview_prep():
    pass

@market_bp.route('/career-path', methods=['GET'])
@jwt_required()
@subscription_required
def generate_career_path():
    pass

@market_bp.route('/networking', methods=['GET'])
@jwt_required()
@subscription_required
def get_networking_opportunities():
    pass
```

**`backend/job_scraper.py`** - Scrape job postings
```python
import requests
from bs4 import BeautifulSoup
import time

class JobScraper:
    def scrape_indeed(self, query, location):
        # Rate-limited scraping
        pass

    def scrape_linkedin(self, query, location):
        # Requires LinkedIn API or careful scraping
        pass

    def scrape_ycombinator_jobs(self):
        # Hacker News Who's Hiring
        pass
```

**`backend/gemini_market.py`** - Gemini functions for market intelligence
```python
from gemini_service import get_gemini_model

def analyze_market_trends(role, location):
    model = get_gemini_model()
    # ... implementation

def generate_company_intel(company_name, role):
    # ... implementation

def score_job_match(resume, job_description):
    # ... implementation
```

### New Frontend Components

**`frontend/src/components/SubscriptionRequired.jsx`**
```javascript
export default function SubscriptionRequired({ feature }) {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 border border-purple-700 rounded-xl p-12 text-center">
        <Lock className="w-16 h-16 text-purple-400 mx-auto mb-6" />
        <h2 className="text-3xl font-bold text-white mb-4">
          {feature} is a Premium Feature
        </h2>
        <p className="text-slate-300 mb-8">
          Unlock AI-powered market intelligence and advanced features
        </p>
        <Link to="/pricing">
          <button className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600
                           hover:from-purple-700 hover:to-blue-700 text-white rounded-lg">
            View Pricing Plans
          </button>
        </Link>
      </div>
    </div>
  );
}
```

**Enhanced `frontend/src/components/MarketIntelligenceDashboard.jsx`**
- Add new tabs: Job Matches, Company Intel, Salary Intel, Skills Gap, Interview Prep, Career Path
- Real-time data displays with loading states
- Interactive charts and visualizations
- Search and filter capabilities

---

## 5. Cost Optimization

### Gemini API Usage Limits

**To prevent excessive costs:**

```python
# Rate limiting per user
USER_DAILY_LIMITS = {
    'market_trends': 5,  # 5 refreshes per day
    'company_intel': 10,  # 10 companies per day
    'salary_intel': 10,
    'job_match_scoring': 50,  # 50 jobs per day
    'interview_prep': 5,
}

# Track usage in database
class UserApiUsage(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    endpoint = db.Column(db.String(100))
    usage_date = db.Column(db.Date)
    count = db.Column(db.Integer, default=0)
```

**Caching Strategy:**
- Market trends: Update every 24 hours (shared across users in same industry/location)
- Company intel: Update every 7 days (shared across all users)
- Salary data: Update every 30 days (shared across users)
- Job matches: Real-time for new jobs, cached for 24 hours
- Interview prep: Generate once per company+role combination (shared)

**Estimated Cost Per User Per Month:**
- Market trends: 5 calls × $0.01 = $0.05
- Company intel: 10 calls × $0.02 = $0.20
- Salary intel: 10 calls × $0.02 = $0.20
- Job matching: 50 calls × $0.01 = $0.50
- Interview prep: 5 calls × $0.03 = $0.15

**Total: ~$1.10 per active user per month** (acceptable with $29/month subscription)

---

## 6. Database Schema Changes

```sql
-- Job Postings
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(300),
    company VARCHAR(200),
    location VARCHAR(200),
    remote_type VARCHAR(50),
    job_description TEXT,
    requirements TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    posted_date TIMESTAMP,
    source VARCHAR(100),
    source_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_job_postings_title ON job_postings(title);
CREATE INDEX idx_job_postings_company ON job_postings(company);
CREATE INDEX idx_job_postings_location ON job_postings(location);
CREATE INDEX idx_job_postings_posted_date ON job_postings(posted_date DESC);

-- Job Matches (personalized for each user)
CREATE TABLE job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_posting_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
    match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
    ai_explanation TEXT,
    reasons_good_fit JSONB,
    reasons_concerns JSONB,
    recommended_action VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new', -- new, saved, applied, dismissed
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, job_posting_id)
);

CREATE INDEX idx_job_matches_user ON job_matches(user_id, match_score DESC);
CREATE INDEX idx_job_matches_status ON job_matches(user_id, status);

-- Job Applications Tracker
CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_posting_id UUID REFERENCES job_postings(id) ON DELETE SET NULL,
    company_name VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    job_url TEXT,
    application_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'applied',
    resume_version TEXT,
    cover_letter_used TEXT,
    contacts JSONB,
    notes TEXT,
    follow_up_dates JSONB,
    ai_insights TEXT,
    next_action VARCHAR(200),
    next_action_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_job_applications_user ON job_applications(user_id, application_date DESC);
CREATE INDEX idx_job_applications_status ON job_applications(user_id, status);

-- Company Intelligence Cache
CREATE TABLE company_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(200) UNIQUE,
    culture_analysis TEXT,
    interview_process TEXT,
    common_questions JSONB,
    employee_satisfaction_score INTEGER,
    growth_trajectory TEXT,
    best_departments JSONB,
    application_tips TEXT,
    generated_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_intelligence_name ON company_intelligence(company_name);

-- Salary Intelligence Cache
CREATE TABLE salary_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_title VARCHAR(200),
    location VARCHAR(200),
    years_experience_min INTEGER,
    years_experience_max INTEGER,
    percentile_25 INTEGER,
    percentile_50 INTEGER,
    percentile_75 INTEGER,
    data_points_count INTEGER,
    negotiation_tips TEXT,
    factors_increase JSONB,
    factors_decrease JSONB,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_title, location, years_experience_min, years_experience_max)
);

CREATE INDEX idx_salary_intelligence_lookup ON salary_intelligence(job_title, location);

-- User API Usage Tracking (cost control)
CREATE TABLE user_api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100),
    usage_date DATE DEFAULT CURRENT_DATE,
    count INTEGER DEFAULT 0,
    UNIQUE(user_id, endpoint, usage_date)
);

CREATE INDEX idx_user_api_usage_lookup ON user_api_usage(user_id, usage_date);

-- User Preferences for Job Matching
CREATE TABLE user_job_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    target_roles JSONB, -- ["Data Scientist", "ML Engineer"]
    locations JSONB, -- ["San Francisco", "Remote"]
    remote_preference VARCHAR(50), -- remote, hybrid, onsite, any
    min_salary INTEGER,
    max_salary INTEGER,
    must_have_skills JSONB,
    nice_to_have_skills JSONB,
    company_size_preference JSONB, -- ["startup", "midsize", "enterprise"]
    industries JSONB,
    email_alerts BOOLEAN DEFAULT true,
    alert_frequency VARCHAR(50) DEFAULT 'daily', -- daily, weekly, instant
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Subscription access control + basic UI structure

- [ ] Add subscription_status column to users table (if not exists)
- [ ] Create `subscription_required` decorator
- [ ] Update frontend routing with subscription checks
- [ ] Create `SubscriptionRequired.jsx` component
- [ ] Add new tabs to MarketIntelligenceDashboard
- [ ] Test subscription flow

**Deliverable:** Non-subscribed users see upgrade prompt, subscribed users see new (empty) tabs

---

### Phase 2: Job Matching System (Week 2-3)
**Goal:** Real-time job scraping + AI-powered matching

- [ ] Create database tables: job_postings, job_matches, user_job_preferences
- [ ] Build job scraper for Indeed, LinkedIn, HN
- [ ] Set up daily cron job for scraping
- [ ] Implement Gemini-based job matching
- [ ] Create Job Matches UI component
- [ ] Add save/dismiss/apply functionality
- [ ] Test with real job data

**Deliverable:** Users see personalized job recommendations with match scores

---

### Phase 3: Company & Salary Intelligence (Week 4)
**Goal:** Research tools for informed applications

- [ ] Create company_intelligence and salary_intelligence tables
- [ ] Implement company research Gemini prompts
- [ ] Implement salary analysis Gemini prompts
- [ ] Create Company Intel UI (searchable)
- [ ] Create Salary Intel UI (with filters)
- [ ] Set up caching (Redis)
- [ ] Test accuracy of AI insights

**Deliverable:** Users can research any company and get salary intelligence

---

### Phase 4: Application Tracker (Week 5)
**Goal:** Help users manage their job search

- [ ] Create job_applications table
- [ ] Build Application Tracker UI (Kanban-style)
- [ ] Implement AI-powered follow-up recommendations
- [ ] Add note-taking and contact tracking
- [ ] Create analytics dashboard (application success rate, etc.)
- [ ] Email reminders for follow-ups
- [ ] Test workflow end-to-end

**Deliverable:** Users can track all applications with AI guidance

---

### Phase 5: Skills & Career Development (Week 6)
**Goal:** Long-term career planning

- [ ] Implement skills gap analysis
- [ ] Create learning path generation
- [ ] Build Career Path visualization
- [ ] Create Skills Gap UI
- [ ] Create Career Path UI (interactive tree)
- [ ] Test recommendations quality

**Deliverable:** Users see personalized career roadmaps and learning paths

---

### Phase 6: Interview Prep & Networking (Week 7)
**Goal:** Help users succeed in interviews

- [ ] Implement interview question generation
- [ ] Create Interview Prep UI (per company)
- [ ] Implement networking opportunity finder
- [ ] Create Networking UI
- [ ] Add bookmarking and note-taking
- [ ] Test interview questions relevance

**Deliverable:** Users get company-specific interview prep and networking tips

---

### Phase 7: Polish & Optimization (Week 8)
**Goal:** Performance, UX, cost optimization

- [ ] Implement comprehensive caching
- [ ] Add loading states and skeletons
- [ ] Optimize Gemini prompts for cost
- [ ] Add user API usage limits
- [ ] Performance testing
- [ ] Bug fixes
- [ ] User testing with beta group

**Deliverable:** Production-ready Market Intelligence platform

---

## 8. Success Metrics

### User Engagement
- **Daily Active Users:** % of subscribed users accessing market pages daily
- **Feature Usage:** Which features are most popular
- **Time Spent:** Average session duration on market pages
- **Job Applications:** Number of applications tracked per user

### Business Impact
- **Subscription Conversions:** % of users who subscribe after seeing market features
- **Churn Reduction:** Do market features reduce subscription cancellations
- **Revenue Impact:** Additional revenue from market-driven subscriptions

### Job Seeker Outcomes
- **Application Success Rate:** % of applications leading to interviews
- **Time to Job:** Average days from signup to job offer (survey data)
- **User Satisfaction:** NPS score for market intelligence features
- **Job Match Quality:** User feedback on AI-recommended jobs

### Technical Performance
- **API Costs:** Gemini API costs per user per month
- **Response Times:** Average latency for AI-powered features
- **Cache Hit Rate:** % of requests served from cache
- **Error Rate:** % of failed AI generations

---

## 9. Future Enhancements (Post-Launch)

### Advanced Features
1. **Resume A/B Testing:** Upload multiple resume versions, see which performs better
2. **Mock Interviews:** AI-powered interview practice with feedback
3. **Salary Negotiation Simulator:** Role-play negotiation scenarios
4. **LinkedIn Profile Optimizer:** AI suggestions for LinkedIn optimization
5. **Portfolio Review:** AI feedback on GitHub/portfolio projects
6. **Email Templates:** AI-generated cold outreach emails to recruiters
7. **Referral Finder:** Find connections who can refer you to target companies
8. **Job Market Predictions:** ML model predicting hiring trends 3-6 months out
9. **Company Culture Match:** Assess cultural fit based on values/preferences
10. **Recruiter Insights:** Tips on what recruiters look for (based on industry data)

### Integrations
- **Calendar Integration:** Auto-schedule interview prep time
- **Email Integration:** Auto-track application emails
- **LinkedIn API:** Auto-import profile data
- **GitHub API:** Auto-analyze portfolio projects
- **Slack/Discord:** Job alert notifications
- **Zapier:** Integrate with user's workflow tools

---

## 10. Risk Mitigation

### Technical Risks

**Risk 1: Gemini API Costs Spiral Out of Control**
- Mitigation: Strict per-user rate limits, aggressive caching, usage monitoring alerts
- Fallback: Reduce free tier features, add pay-per-use option for power users

**Risk 2: Job Scraping Gets Blocked**
- Mitigation: Rotate IPs, use proxies, respect robots.txt, add delays
- Fallback: Partner with job board APIs (Indeed API, LinkedIn API)

**Risk 3: AI Generates Low-Quality or Inaccurate Insights**
- Mitigation: Extensive prompt engineering, user feedback loop, human review samples
- Fallback: Add "Report Inaccuracy" button, mix AI with curated content

### Business Risks

**Risk 1: Users Don't Find Value (Low Engagement)**
- Mitigation: User testing before launch, iterate based on feedback, A/B test features
- Fallback: Focus on most popular features, deprecate unused ones

**Risk 2: Free Users Abuse System (Cost Issue)**
- Mitigation: Make market intelligence subscription-only (already planned)
- Fallback: Add stricter rate limits, require email verification

**Risk 3: Competition (Other Platforms Launch Similar Features)**
- Mitigation: Focus on quality over quantity, personalized experience, integrate with resume analyzer
- Fallback: Differentiate with unique features (e.g., AI-powered application tracker)

### Legal/Compliance Risks

**Risk 1: Web Scraping Legal Issues**
- Mitigation: Only scrape public data, respect robots.txt, add user-agent, terms of service
- Fallback: Use official APIs only, reduce data sources

**Risk 2: Data Privacy (GDPR, CCPA)**
- Mitigation: Clear privacy policy, user consent, data encryption, right to deletion
- Fallback: Limit data collection, anonymize stored data

**Risk 3: AI-Generated Content Liability**
- Mitigation: Add disclaimers ("AI-generated, verify independently"), user feedback loops
- Fallback: Mix AI content with human-curated sources, cite sources

---

## 11. Competitive Analysis

### Existing Solutions

**LinkedIn Premium ($39.99/month):**
- ✅ Job matching
- ✅ Salary insights
- ✅ InMail credits
- ❌ No AI-powered interview prep
- ❌ No application tracker with AI
- ❌ No skills gap analysis with learning paths

**Huntr ($40/month):**
- ✅ Application tracker
- ✅ Job board aggregation
- ❌ No AI-powered insights
- ❌ No interview prep
- ❌ No salary intelligence

**Teal ($79/month):**
- ✅ Resume builder
- ✅ Job tracker
- ✅ LinkedIn optimization
- ❌ No real-time market intelligence
- ❌ No AI interview prep
- ❌ No career path visualization

**Our Advantage:**
- ✅ **Integrated:** Resume analysis + market intelligence in one platform
- ✅ **AI-Powered:** Gemini integration for personalized insights
- ✅ **Comprehensive:** Covers entire job search journey
- ✅ **Affordable:** $29/month vs. $40-80/month competitors
- ✅ **Real-Time:** Fresh data, not static reports

---

## 12. Summary

This plan transforms the Market Intelligence pages into a comprehensive, AI-powered job search platform that:

1. ✅ **Subscription-Only Access:** Drives revenue and prevents abuse
2. ✅ **Real-Time Intelligence:** Fresh job postings, salary data, company insights
3. ✅ **Gemini AI Integration:** Personalized recommendations and insights
4. ✅ **Job Seeker-Focused:** Covers every step from skill development to offer negotiation
5. ✅ **Cost-Effective:** Smart caching keeps Gemini API costs under $1.10/user/month
6. ✅ **Competitive Advantage:** Features competitors don't have (AI interview prep, career paths)

**Estimated Development Time:** 8 weeks (2 months)

**Expected Impact:**
- +30% subscription conversions (users see value immediately)
- +20% user engagement (more time spent on platform)
- -15% churn (valuable ongoing resource for job seekers)

**Next Steps:**
1. Get user feedback on this plan
2. Prioritize features (start with highest impact)
3. Begin Phase 1 implementation
4. Set up analytics tracking
5. Launch beta with small user group
6. Iterate based on real usage data
