# Phase 2: AI-Powered Market Intelligence - Implementation Plan

**Status:** Ready to Start
**Estimated Duration:** 8-10 weeks
**Priority:** High
**Dependencies:** Phase 1 Complete ✅

---

## Executive Summary

Phase 2 will implement all 4 "Coming Soon" features from the Market Intelligence Dashboard, transforming them from preview tabs into fully functional AI-powered tools. All features will be personalized to the user's job industry for maximum relevance.

### Features to Implement:
1. **Job Matches** - AI-powered job matching with smart scoring
2. **Company Intel** - Deep company research and insights
3. **Interview Prep** - Company-specific interview preparation
4. **Career Path** - Career progression planning and visualization

### Key Requirements:
- ✅ Industry personalization based on user profile
- ✅ Gemini AI integration for intelligent content
- ✅ Real-time data where applicable
- ✅ Cost-optimized caching strategy
- ✅ Beautiful, modern UI matching Phase 1 design

---

## Implementation Strategy

### Recommended Order (Dependencies-Based):

```
Week 1: Industry Personalization Foundation
        ↓
Week 2-3: Skills Gap Enhancement (builds on existing feature)
        ↓
Week 4-5: Job Matching System (uses skills gap data)
        ↓
Week 6-7: Interview Prep (uses job matches + company data)
        ↓
Week 7-8: Company Intel (supports interview prep)
        ↓
Week 9-10: Career Path (uses all previous data)
```

### Why This Order?

1. **Industry Personalization First** - Foundation for all other features
2. **Skills Gap Next** - Builds on existing code, quick win
3. **Job Matching** - Core feature that feeds interview prep
4. **Interview Prep + Company Intel** - Can develop in parallel
5. **Career Path Last** - Most complex, benefits from all previous features

---

## Phase 2.1: Industry Personalization Foundation (Week 1)

### Objective
Make all market intelligence data filter by user's industry

### Backend Changes

#### 1. Update User Profile Schema
**File:** `backend/models.py`

```python
# Add new fields to User model
industry_preference = db.Column(db.String(100))  # Primary industry filter
industry_experience = db.Column(db.JSON)  # ["Technology", "Healthcare"]
location_preference = db.Column(db.String(100))  # "San Francisco, CA"
```

#### 2. Create Industry Helper Service
**File:** `backend/services/industry_service.py` (NEW)

```python
"""
Service for industry-based data filtering and personalization
"""

def get_user_industry(user):
    """Get user's primary industry from profile or resume analysis"""
    # Priority order:
    # 1. industry_preference (user explicitly set)
    # 2. detected_industries[0] (from resume analysis)
    # 3. "General" (fallback)

def filter_market_data_by_industry(data, industry):
    """Filter market data to match user's industry"""

def get_industry_keywords(industry):
    """Get relevant skills/keywords for industry"""
```

#### 3. Update Market Intelligence Routes
**File:** `backend/app.py`

```python
@app.route('/api/market/dashboard', methods=['GET'])
@jwt_required()
@subscription_required
def get_market_dashboard():
    user = g.current_user
    industry = get_user_industry(user)

    # Filter all data by industry
    skills_data = get_top_skills(industry=industry)
    salary_data = get_salary_data(industry=industry)
    trends_data = get_market_trends(industry=industry)

    return jsonify({
        'industry': industry,
        'skills': skills_data,
        'salaries': salary_data,
        'trends': trends_data
    })
```

### Frontend Changes

#### 1. Add Industry Selector Component
**File:** `frontend/src/components/IndustrySelector.jsx` (NEW)

```javascript
const IndustrySelector = ({ currentIndustry, onChange }) => {
  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Marketing',
    'Sales', 'Education', 'Engineering', 'Design',
    'Product Management', 'Data Science', 'General'
  ];

  return (
    <div className="industry-selector">
      <label>Filter by Industry:</label>
      <select value={currentIndustry} onChange={(e) => onChange(e.target.value)}>
        {industries.map(ind => (
          <option key={ind} value={ind}>{ind}</option>
        ))}
      </select>
    </div>
  );
};
```

#### 2. Update Market Dashboard to Use Industry
**File:** `frontend/src/components/MarketIntelligenceDashboard.jsx`

```javascript
const [selectedIndustry, setSelectedIndustry] = useState(userProfile.industry_preference || 'General');

// Add industry selector to dashboard header
<div className="dashboard-header">
  <h1>Market Intelligence</h1>
  <IndustrySelector
    currentIndustry={selectedIndustry}
    onChange={setSelectedIndustry}
  />
</div>

// Pass industry to all API calls
useEffect(() => {
  fetchMarketData(selectedIndustry);
}, [selectedIndustry]);
```

### Database Changes

```sql
-- Add industry fields to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS industry_preference VARCHAR(100),
ADD COLUMN IF NOT EXISTS industry_experience JSON,
ADD COLUMN IF NOT EXISTS location_preference VARCHAR(100);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_industry ON users(industry_preference);
```

### Deliverables
- ✅ Industry-based data filtering across all market features
- ✅ Industry selector UI component
- ✅ Database migration for industry fields
- ✅ Updated API endpoints with industry parameter

---

## Phase 2.2: Job Matches - AI-Powered Job Matching (Weeks 2-3)

### Objective
Match users with relevant job opportunities using AI scoring

### Backend Implementation

#### 1. Database Schema
**File:** `backend/models.py`

```python
class JobPosting(db.Model):
    """Job postings scraped or provided by partners"""
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    remote_type = db.Column(db.String(50))  # remote, hybrid, onsite
    industry = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    requirements = db.Column(db.JSON)  # ["Python", "React", "5 years exp"]
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(100))  # "LinkedIn", "Indeed", etc.
    external_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobMatch(db.Model):
    """AI-generated job matches for users"""
    __tablename__ = 'job_matches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    match_score = db.Column(db.Float)  # 0-100
    ai_explanation = db.Column(db.Text)  # Why this is a good match
    skill_matches = db.Column(db.JSON)  # {"Python": true, "React": true}
    missing_skills = db.Column(db.JSON)  # ["Docker", "AWS"]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_saved = db.Column(db.Boolean, default=False)
    is_applied = db.Column(db.Boolean, default=False)
```

#### 2. AI Job Matching Service
**File:** `backend/services/job_matcher.py` (NEW)

```python
import google.generativeai as genai
from models import User, JobPosting, JobMatch

class JobMatchingService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_job_matches(self, user_id, industry, limit=20):
        """Generate AI-powered job matches for user"""
        user = User.query.get(user_id)

        # Get user's resume analysis
        resume_analysis = self._get_latest_resume_analysis(user_id)
        user_skills = resume_analysis.get('skills', [])

        # Find relevant jobs
        jobs = JobPosting.query.filter(
            JobPosting.industry == industry,
            JobPosting.posted_date >= datetime.utcnow() - timedelta(days=30)
        ).limit(50).all()

        matches = []
        for job in jobs:
            # Calculate match score with AI
            match_data = self._calculate_match_score(user, job, user_skills)
            matches.append(match_data)

        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:limit]

    def _calculate_match_score(self, user, job, user_skills):
        """Use Gemini to calculate match score and explanation"""
        prompt = f"""
        Analyze job match quality:

        User Profile:
        - Skills: {', '.join(user_skills)}
        - Experience Level: {user.experience_level or 'Not specified'}
        - Industry: {user.industry_preference}

        Job Posting:
        - Title: {job.title}
        - Company: {job.company}
        - Requirements: {', '.join(job.requirements or [])}
        - Description: {job.description[:500]}

        Provide:
        1. Match score (0-100)
        2. Brief explanation (2-3 sentences)
        3. Matching skills
        4. Missing critical skills

        Format: JSON
        {{
            "match_score": 85,
            "explanation": "...",
            "matching_skills": ["Python", "React"],
            "missing_skills": ["Docker"]
        }}
        """

        response = self.model.generate_content(prompt)
        return self._parse_ai_response(response.text)

    def _parse_ai_response(self, response_text):
        """Parse AI response into structured data"""
        # Extract JSON from response
        import json
        import re

        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {
            "match_score": 50,
            "explanation": "Unable to analyze match",
            "matching_skills": [],
            "missing_skills": []
        }
```

#### 3. Job Matches API Routes
**File:** `backend/app.py`

```python
@app.route('/api/market/job-matches', methods=['GET'])
@jwt_required()
@subscription_required
def get_job_matches():
    """Get AI-powered job matches for user"""
    user = g.current_user
    industry = request.args.get('industry', get_user_industry(user))

    # Check cache first (1 hour expiry)
    cache_key = f"job_matches_{user.id}_{industry}"
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify(cached)

    # Generate fresh matches
    matcher = JobMatchingService()
    matches = matcher.generate_job_matches(user.id, industry)

    # Cache results
    set_cache(cache_key, matches, expiry=3600)

    return jsonify({
        'matches': matches,
        'total': len(matches),
        'industry': industry
    })

@app.route('/api/market/job-matches/<int:job_id>/save', methods=['POST'])
@jwt_required()
@subscription_required
def save_job_match(job_id):
    """Save a job match for later"""
    user = g.current_user

    match = JobMatch.query.filter_by(
        user_id=user.id,
        job_posting_id=job_id
    ).first()

    if match:
        match.is_saved = True
    else:
        match = JobMatch(
            user_id=user.id,
            job_posting_id=job_id,
            is_saved=True
        )
        db.session.add(match)

    db.session.commit()
    return jsonify({'success': True})
```

### Frontend Implementation

#### 1. Job Matches Component
**File:** `frontend/src/components/JobMatches.jsx` (NEW)

```javascript
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, MapPin, DollarSign, Clock, Bookmark, ExternalLink, Sparkles } from 'lucide-react';
import axios from 'axios';

const JobMatches = ({ industry }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, saved, high-match

  useEffect(() => {
    fetchJobMatches();
  }, [industry]);

  const fetchJobMatches = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `http://localhost:5000/api/market/job-matches?industry=${industry}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMatches(response.data.matches);
    } catch (error) {
      console.error('Error fetching job matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveJob = async (jobId) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:5000/api/market/job-matches/${jobId}/save`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Update local state
      setMatches(matches.map(m =>
        m.job_id === jobId ? { ...m, is_saved: true } : m
      ));
    } catch (error) {
      console.error('Error saving job:', error);
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const filteredMatches = matches.filter(match => {
    if (filter === 'saved') return match.is_saved;
    if (filter === 'high-match') return match.match_score >= 70;
    return true;
  });

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Finding your perfect job matches with AI...</p>
      </div>
    );
  }

  return (
    <div className="job-matches-container">
      {/* Filter Bar */}
      <div className="filter-bar">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All Matches ({matches.length})
        </button>
        <button
          className={filter === 'high-match' ? 'active' : ''}
          onClick={() => setFilter('high-match')}
        >
          High Match ({matches.filter(m => m.match_score >= 70).length})
        </button>
        <button
          className={filter === 'saved' ? 'active' : ''}
          onClick={() => setFilter('saved')}
        >
          Saved ({matches.filter(m => m.is_saved).length})
        </button>
      </div>

      {/* Job Cards */}
      <div className="job-cards-grid">
        {filteredMatches.map((match, index) => (
          <motion.div
            key={match.job_id}
            className="job-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            {/* Match Score Badge */}
            <div
              className="match-score-badge"
              style={{ background: getMatchScoreColor(match.match_score) }}
            >
              <Sparkles className="w-4 h-4" />
              {Math.round(match.match_score)}% Match
            </div>

            {/* Job Header */}
            <div className="job-header">
              <h3>{match.title}</h3>
              <button
                className={`save-btn ${match.is_saved ? 'saved' : ''}`}
                onClick={() => saveJob(match.job_id)}
              >
                <Bookmark className="w-5 h-5" fill={match.is_saved ? 'currentColor' : 'none'} />
              </button>
            </div>

            <p className="company-name">{match.company}</p>

            {/* Job Details */}
            <div className="job-details">
              <div className="detail">
                <MapPin className="w-4 h-4" />
                <span>{match.location || 'Remote'}</span>
              </div>
              {match.salary_range && (
                <div className="detail">
                  <DollarSign className="w-4 h-4" />
                  <span>{match.salary_range}</span>
                </div>
              )}
              <div className="detail">
                <Clock className="w-4 h-4" />
                <span>Posted {match.posted_days_ago} days ago</span>
              </div>
            </div>

            {/* AI Explanation */}
            <div className="ai-explanation">
              <div className="ai-badge">
                <Sparkles className="w-3 h-3" />
                AI Analysis
              </div>
              <p>{match.ai_explanation}</p>
            </div>

            {/* Skills Match */}
            <div className="skills-match">
              <div className="matching-skills">
                <p className="label">Your Matching Skills:</p>
                <div className="skills-tags">
                  {match.matching_skills.map(skill => (
                    <span key={skill} className="skill-tag match">{skill}</span>
                  ))}
                </div>
              </div>

              {match.missing_skills.length > 0 && (
                <div className="missing-skills">
                  <p className="label">Skills to Learn:</p>
                  <div className="skills-tags">
                    {match.missing_skills.map(skill => (
                      <span key={skill} className="skill-tag missing">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="job-actions">
              <button className="btn-primary" onClick={() => window.open(match.external_url, '_blank')}>
                View Job
                <ExternalLink className="w-4 h-4" />
              </button>
              <button className="btn-secondary">
                Track Application
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredMatches.length === 0 && (
        <div className="no-matches">
          <Briefcase className="w-16 h-16 text-slate-400" />
          <h3>No matches found</h3>
          <p>Try adjusting your filters or updating your resume to get more matches</p>
        </div>
      )}
    </div>
  );
};

export default JobMatches;
```

#### 2. Job Matches Styles
**File:** `frontend/src/styles/JobMatches.css` (NEW)

```css
.job-matches-container {
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  padding: 12px;
  background: rgba(51, 65, 85, 0.3);
  border-radius: 12px;
}

.filter-bar button {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-bar button.active {
  background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
  border-color: transparent;
  color: white;
}

.job-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.job-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 24px;
  position: relative;
  transition: all 0.3s;
}

.job-card:hover {
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(139, 92, 246, 0.2);
}

.match-score-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.job-header h3 {
  font-size: 1.25rem;
  color: white;
  margin: 0;
  flex: 1;
}

.save-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  transition: all 0.2s;
}

.save-btn:hover {
  color: #8b5cf6;
  transform: scale(1.1);
}

.save-btn.saved {
  color: #8b5cf6;
}

.company-name {
  color: #06b6d4;
  font-size: 1rem;
  margin-bottom: 16px;
}

.job-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.job-details .detail {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 0.875rem;
}

.ai-explanation {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
  border-radius: 12px;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.ai-explanation p {
  color: #cbd5e1;
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.5;
}

.skills-match {
  margin-bottom: 20px;
}

.skills-match .label {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-bottom: 8px;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.skill-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.skill-tag.match {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.skill-tag.missing {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.job-actions {
  display: flex;
  gap: 12px;
}

.job-actions button {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
  border: none;
  color: white;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.btn-secondary {
  background: rgba(51, 65, 85, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
}

.btn-secondary:hover {
  border-color: rgba(148, 163, 184, 0.4);
  background: rgba(51, 65, 85, 0.8);
}

.no-matches {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.no-matches h3 {
  color: white;
  margin: 16px 0 8px;
}
```

### Deliverables
- ✅ Job postings database with industry filtering
- ✅ AI-powered job matching service using Gemini
- ✅ Job matches API with caching
- ✅ Beautiful job cards UI with match scores
- ✅ Save jobs functionality
- ✅ Skills match visualization

---

## Phase 2.3: Interview Prep - Company-Specific Preparation (Weeks 4-5)

### Objective
Provide AI-generated interview questions and answers tailored to specific companies

### Backend Implementation

#### 1. Database Schema
**File:** `backend/models.py`

```python
class InterviewPrep(db.Model):
    """AI-generated interview preparation content"""
    __tablename__ = 'interview_prep'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200))
    questions = db.Column(db.JSON)  # [{"question": "...", "answer": "...", "tips": "..."}]
    company_culture = db.Column(db.Text)  # AI analysis of company culture
    interview_tips = db.Column(db.JSON)  # Company-specific tips
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cached_until = db.Column(db.DateTime)  # Cache expiry
```

#### 2. Interview Prep Service
**File:** `backend/services/interview_prep_service.py` (NEW)

```python
class InterviewPrepService:
    def generate_interview_prep(self, user_id, company, job_title):
        """Generate AI interview prep for specific company/role"""
        user = User.query.get(user_id)
        resume_analysis = self._get_latest_resume_analysis(user_id)

        prompt = f"""
        Generate interview preparation for:

        Company: {company}
        Role: {job_title}

        Candidate Background:
        - Skills: {', '.join(resume_analysis.get('skills', []))}
        - Experience: {user.experience_level}

        Provide:
        1. 10 likely interview questions (mix of technical, behavioral, company-specific)
        2. Suggested answer frameworks for each question
        3. Company culture insights (based on known info about {company})
        4. 5 tips specific to {company}'s interview process

        Format as JSON.
        """

        response = self.model.generate_content(prompt)
        return self._parse_interview_response(response.text)
```

### Frontend Component
**File:** `frontend/src/components/InterviewPrep.jsx` (NEW)

Beautiful accordion-style Q&A interface with:
- Company selector
- Question categories (Technical, Behavioral, Culture Fit)
- Expandable answers with AI tips
- "Mark as practiced" functionality
- Download prep sheet as PDF

### Deliverables
- ✅ Interview prep database
- ✅ AI question/answer generation
- ✅ Company-specific insights
- ✅ Beautiful Q&A interface
- ✅ Download functionality

---

## Phase 2.4: Company Intel - Deep Company Research (Weeks 6-7)

### Objective
Provide comprehensive company intelligence for job seekers

### Features
1. **Company Culture Analysis**
   - AI-generated culture insights
   - Employee reviews summary
   - Work-life balance indicators

2. **Salary Intelligence**
   - Role-specific salary ranges
   - Negotiation strategies
   - Benefits comparison

3. **Interview Process Insights**
   - Typical interview rounds
   - Common questions asked
   - Timeline expectations

4. **Growth & Stability Metrics**
   - Company growth trajectory
   - Funding information
   - Market position

### Backend Implementation

```python
class CompanyIntel(db.Model):
    """Company intelligence data"""
    __tablename__ = 'company_intel'

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # "50-200", "1000-5000", etc.
    culture_analysis = db.Column(db.Text)  # AI-generated
    salary_data = db.Column(db.JSON)  # {"Software Engineer": {"min": 120000, "max": 180000}}
    interview_insights = db.Column(db.JSON)
    benefits_summary = db.Column(db.JSON)
    growth_metrics = db.Column(db.JSON)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
```

### Frontend Component
**File:** `frontend/src/components/CompanyIntel.jsx` (NEW)

Features:
- Company search bar
- Tabbed interface (Culture, Salaries, Interview Process, Growth)
- Comparison tool (compare up to 3 companies)
- Save favorite companies

### Deliverables
- ✅ Company intelligence database
- ✅ AI company analysis
- ✅ Salary data by role
- ✅ Company comparison tool
- ✅ Search and save functionality

---

## Phase 2.5: Career Path - Career Planning & Visualization (Weeks 8-10)

### Objective
Visualize career progression and create personalized roadmaps

### Features
1. **Career Path Visualization**
   - Interactive node-based graph
   - Current role → Target roles
   - Multiple path options

2. **Skills Roadmap**
   - Skills needed for each step
   - Learning resources
   - Estimated timeline

3. **Salary Progression**
   - Expected salary at each stage
   - ROI on skill investment

4. **Industry-Specific Paths**
   - Common career progressions in user's industry
   - Alternative paths (e.g., management vs. IC)

### Backend Implementation

```python
class CareerPath(db.Model):
    """Career path recommendations"""
    __tablename__ = 'career_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_role = db.Column(db.String(200))
    target_role = db.Column(db.String(200))
    path_steps = db.Column(db.JSON)  # [{"role": "Senior Dev", "timeline": "1-2 years", "skills": [...]}]
    total_timeline = db.Column(db.String(50))  # "3-5 years"
    ai_recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Frontend Component
**File:** `frontend/src/components/CareerPath.jsx` (NEW)

Uses **React Flow** library for interactive node-based visualization.

### Deliverables
- ✅ Career path database
- ✅ AI path generation
- ✅ Interactive visualization
- ✅ Skills roadmap
- ✅ Salary progression estimates

---

## Industry Personalization Implementation

### User Profile Enhancement

```python
# On user registration or profile update
def detect_industry_from_resume(resume_text):
    """Use Gemini to detect user's industry"""
    prompt = f"""
    Analyze this resume and determine:
    1. Primary industry (Technology, Healthcare, Finance, etc.)
    2. Related industries
    3. Job level (Entry, Mid, Senior, Lead, Executive)

    Resume:
    {resume_text[:2000]}

    Return JSON: {{"primary_industry": "...", "related_industries": [...], "level": "..."}}
    """
    # ... Gemini API call
```

### Data Filtering Strategy

All market data will be filtered by industry:

```python
# Example: Get top skills by industry
def get_top_skills(industry):
    if industry == "Technology":
        return ["Python", "React", "AWS", "Docker", "Kubernetes"]
    elif industry == "Healthcare":
        return ["HIPAA Compliance", "EMR Systems", "Patient Care", "Medical Terminology"]
    # ... etc
```

### UI Industry Indicator

Show user's current industry filter prominently:

```javascript
<div className="industry-badge">
  <Target className="w-4 h-4" />
  Showing data for: {selectedIndustry}
</div>
```

---

## Cost Optimization & Caching Strategy

### Gemini API Cost Management

1. **Aggressive Caching**
   - Job matches: Cache for 1 hour
   - Interview prep: Cache for 1 week
   - Company intel: Cache for 1 month
   - Career paths: Cache for 2 weeks

2. **Batch Processing**
   - Generate job matches in batches
   - Process during off-peak hours

3. **Use Gemini 1.5 Flash**
   - Cheaper than Pro
   - Fast enough for most use cases
   - Switch to Pro only for complex analysis

4. **Rate Limiting**
   - Max 10 AI requests per user per hour
   - Queue system for batch jobs

### Cache Implementation

```python
import redis
import pickle

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_from_cache(key):
    data = redis_client.get(key)
    return pickle.loads(data) if data else None

def set_cache(key, value, expiry=3600):
    redis_client.setex(key, expiry, pickle.dumps(value))
```

---

## Database Migrations

### Migration Order

1. **Week 1:** Industry fields + indexes
2. **Week 2:** Job postings & job matches tables
3. **Week 4:** Interview prep table
4. **Week 6:** Company intel table
5. **Week 8:** Career paths table

### Migration Script Template

```python
# backend/migrations/phase_2_week_X.py
from sqlalchemy import create_engine, text
import os

def run_migration():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Add tables
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ...
        """))

        # Add indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ...
        """))

        conn.commit()
```

---

## Testing Strategy

### Each Feature Must Have

1. **Unit Tests**
   - AI service response parsing
   - Match score calculations
   - Data filtering logic

2. **Integration Tests**
   - API endpoints
   - Database operations
   - Cache behavior

3. **User Testing**
   - UI/UX feedback
   - Performance testing
   - Mobile responsiveness

### Test Data

Create seed data:
- 50+ sample job postings across industries
- 10+ sample companies with full intel
- Sample career paths for common roles

---

## Performance Targets

### Response Times
- Job matches: < 2 seconds (cached), < 10 seconds (fresh)
- Interview prep: < 5 seconds (cached), < 15 seconds (fresh)
- Company intel: < 1 second (cached), < 8 seconds (fresh)
- Career path: < 3 seconds (cached), < 12 seconds (fresh)

### Caching Hit Rate
- Target: > 80% cache hit rate
- Monitor with Redis stats

### Gemini API Usage
- Budget: $100/month maximum
- ~3,000 requests/month at $0.03/request
- Monitor daily usage

---

## Timeline Summary

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Industry Personalization | Industry filtering across all features |
| 2-3 | Job Matches | AI job matching with scores |
| 4-5 | Interview Prep | Company-specific Q&A |
| 6-7 | Company Intel | Deep company research |
| 8-10 | Career Path | Career visualization & roadmaps |

**Total Duration:** 10 weeks
**Can compress to 8 weeks with parallel frontend/backend work**

---

## Risk Mitigation

### Technical Risks

1. **Gemini API Costs**
   - Mitigation: Aggressive caching, rate limiting
   - Backup: Fall back to rule-based matching if over budget

2. **Job Data Availability**
   - Mitigation: Start with manual seed data
   - Future: Integrate job board APIs (Indeed, LinkedIn)

3. **Performance Issues**
   - Mitigation: Caching, lazy loading, pagination
   - Monitor response times continuously

### Business Risks

1. **Low User Engagement**
   - Mitigation: A/B test features, gather feedback early
   - Iterate based on usage analytics

2. **Subscription Conversion**
   - Mitigation: Show value early, offer free trial
   - Track conversion funnel

---

## Success Metrics

### Phase 2 Success = All of These

- ✅ All 4 tabs functional and beautiful
- ✅ Industry personalization working
- ✅ < 3 second average response time (cached)
- ✅ > 80% cache hit rate
- ✅ < $100/month Gemini costs
- ✅ Zero breaking bugs in production
- ✅ Positive user feedback (>4/5 stars)
- ✅ 20%+ increase in subscription conversions

---

## Next Steps

### Immediate Actions (This Week)

1. **Set Up Infrastructure**
   - Add Redis for caching
   - Configure Gemini API key
   - Create database backup strategy

2. **Start Week 1: Industry Personalization**
   - Run database migration
   - Implement industry service
   - Update MarketIntelligenceDashboard
   - Test with real user data

3. **Prepare Job Data**
   - Create 50 sample job postings
   - Distribute across industries
   - Add realistic requirements and descriptions

### Weekly Check-ins

- Review progress against timeline
- Adjust scope if needed
- Test deployed features
- Gather user feedback

---

## Appendix: Job Board APIs (Future Integration)

### Potential Partners

1. **Indeed API**
   - Pros: Largest job board, good coverage
   - Cons: Requires publisher account

2. **LinkedIn Jobs API**
   - Pros: High-quality data, professional network
   - Cons: Expensive, strict rate limits

3. **Adzuna API**
   - Pros: Free tier available, good docs
   - Cons: Limited to certain countries

4. **JSearch (RapidAPI)**
   - Pros: Aggregates multiple sources
   - Cons: Cost per request

**Recommendation:** Start with manual seed data, integrate APIs in Phase 3

---

## Conclusion

This plan implements all 4 "Coming Soon" features with industry personalization, transforming the Market Intelligence Dashboard into a comprehensive AI-powered job search platform.

**Key Strengths:**
- Phased approach reduces risk
- Industry personalization adds major value
- Cost-optimized with caching
- Beautiful UI matching Phase 1 design
- Scalable architecture

**Timeline:** 8-10 weeks
**Estimated Cost:** < $100/month for Gemini
**Expected Impact:** 20-30% increase in subscription conversions

**Ready to start Week 1!**
