# Job Posting Ingestion & Market Intelligence API Integration Guide

## Overview

The AI Resume Analyzer now includes a comprehensive job posting ingestion and market intelligence system. This system allows you to:

1. **Ingest Job Postings** from multiple sources (API, CSV, databases)
2. **Extract Skills** from job descriptions automatically using Spacy NER
3. **Calculate Market Demand** scores for each skill
4. **Analyze Salary Trends** over time
5. **Compare Resume Skills** against market requirements
6. **Get Industry Insights** for specific job sectors
7. **Understand Location-Based Compensation** patterns

---

## API Endpoints

### 1. Job Posting Ingestion

#### **POST /api/jobs/ingest**

Ingest job postings and automatically extract skills from descriptions.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "postings": [
    {
      "job_title": "Senior Python Developer",
      "company_name": "TechCorp Inc",
      "job_description": "We're looking for an experienced Python developer with expertise in Django, PostgreSQL, Docker, and AWS. Must have 5+ years of experience.",
      "location": "San Francisco, CA",
      "salary_min": 150000,
      "salary_max": 200000,
      "salary_currency": "USD",
      "industry": "Technology",
      "source": "indeed",
      "job_url": "https://indeed.com/viewjob?jk=abc123"
    }
  ],
  "extract_skills": true
}
```

**Field Definitions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| job_title | string | Yes | Job position title |
| company_name | string | Yes | Company/Organization name |
| job_description | string | Yes | Full job description (for skill extraction) |
| location | string | No | Geographic location (e.g., "San Francisco, CA") |
| salary_min | number | No | Minimum annual salary |
| salary_max | number | No | Maximum annual salary |
| salary_currency | string | No | Currency code (default: "USD") |
| industry | string | No | Industry category (e.g., "Technology", "Finance") |
| source | string | No | Data source (e.g., "indeed", "linkedin", "glassdoor") |
| job_url | string | No | URL to original job posting |

**Response:**
```json
{
  "success": true,
  "message": "Job postings ingested successfully",
  "details": {
    "postings_ingested": 1,
    "skills_extracted": 12,
    "timestamp": "2025-11-22T02:35:00.000000"
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request (missing required fields, too many postings)
- `401`: Unauthorized (missing/invalid JWT token)
- `500`: Server error during ingestion

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/jobs/ingest \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "postings": [{
      "job_title": "Senior Developer",
      "company_name": "TechCorp",
      "job_description": "Python, Django, PostgreSQL required...",
      "location": "San Francisco, CA",
      "salary_min": 150000,
      "salary_max": 200000,
      "industry": "Technology",
      "source": "indeed"
    }],
    "extract_skills": true
  }'
```

**Constraints:**
- Maximum 1000 postings per request
- Duplicate detection by job_url (prevents re-ingestion)
- Automatic skill extraction if `extract_skills: true`

---

### 2. Load Sample Data

#### **POST /api/jobs/load-sample-data**

Load pre-configured realistic sample job postings for testing and demonstration.

**Authentication:** Required (JWT)

**Request Body:** Empty

**Response:**
```json
{
  "success": true,
  "message": "Sample job postings loaded successfully",
  "details": {
    "postings_ingested": 11,
    "skills_extracted": 127,
    "timestamp": "2025-11-22T02:40:00.000000"
  }
}
```

**Sample Data Includes:**
- **Technology** (5 postings):
  - Senior Python Developer (TechCorp) - SF, $150-200K
  - Full Stack JavaScript Developer (WebInnovations) - NYC, $120-160K
  - Data Scientist (DataAnalytics Pro) - Seattle, $130-190K
  - DevOps Engineer (CloudSystems Ltd) - Boston, $140-180K
  - Cloud Software Engineer (CloudSoftware Inc) - Austin, $90-130K

- **Finance** (2 postings):
  - Financial Analyst (InvestBank Corp) - NYC, $80-120K
  - BI Manager (RetailChain Global) - Chicago, $100-150K

- **Other Industries** (4 postings):
  - Digital Marketing Manager (MarketingHub) - LA, $70-100K
  - UX/UI Designer (DesignStudio Pro) - San Diego, $75-115K
  - Clinical Nurse (City Medical Center) - Houston, $60-85K
  - High School Math Teacher (Central Academy) - Denver, $50-70K

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/jobs/load-sample-data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

---

### 3. Job Posting Statistics

#### **GET /api/jobs/statistics**

Get statistics about ingested job postings (sources, industries, salary data).

**Authentication:** Required (JWT)

**Query Parameters:** None

**Response:**
```json
{
  "total_postings": 23,
  "sources": {
    "indeed": 8,
    "api": 15
  },
  "industries": {
    "Technology": 12,
    "Finance": 3,
    "Marketing": 2,
    "Design": 2,
    "Healthcare": 2,
    "Education": 1,
    "Sales": 1
  },
  "salary_statistics": {
    "average": 117043.48,
    "median": 115000.00,
    "min": 50000.00,
    "max": 200000.00,
    "postings_with_salary": 23
  }
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/api/jobs/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Market Intelligence Endpoints

### 4. Skill Market Demand

#### **GET /api/market/skills/demand**

Get top demanded skills across all job postings with demand scores (0-100).

**Authentication:** Required (JWT)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 20 | Number of top skills to return |
| days | integer | 90 | Analyze postings from last N days |

**Response:**
```json
{
  "total_postings": 23,
  "analysis_period_days": 90,
  "top_skills": [
    {
      "skill_id": 45,
      "skill_name": "Python",
      "market_demand_score": 95.65,
      "demand_percentage": 47.83,
      "postings_count": 11,
      "average_salary": 156250.00,
      "median_salary": 150000.00,
      "salary_range": 50000.00,
      "top_sources": {
        "indeed": 6,
        "api": 5
      },
      "top_industries": {
        "Technology": 10,
        "Finance": 1
      },
      "top_locations": {
        "San Francisco, CA": 3,
        "Seattle, WA": 2,
        "Boston, MA": 1
      }
    },
    {
      "skill_id": 67,
      "skill_name": "SQL",
      "market_demand_score": 78.26,
      "demand_percentage": 39.13,
      "postings_count": 9,
      "average_salary": 118500.00,
      "median_salary": 115000.00,
      "salary_range": 60000.00,
      "top_sources": {},
      "top_industries": {},
      "top_locations": {}
    }
  ]
}
```

**Example cURL:**
```bash
curl -X GET 'http://localhost:5000/api/market/skills/demand?limit=10&days=90' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 5. Specific Skill Demand

#### **GET /api/market/skills/demand/{skill_id}**

Get detailed demand data for a specific skill.

**Authentication:** Required (JWT)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| skill_id | integer | ID of the skill to analyze |

**Response:**
```json
{
  "skill_id": 45,
  "skill_name": "Python",
  "market_demand_score": 95.65,
  "demand_percentage": 47.83,
  "postings_count": 11,
  "average_salary": 156250.00,
  "median_salary": 150000.00,
  "salary_range": 50000.00,
  "top_sources": {
    "indeed": 6,
    "api": 5
  },
  "top_industries": {
    "Technology": 10,
    "Finance": 1
  },
  "top_locations": {
    "San Francisco, CA": 3,
    "Seattle, WA": 2
  }
}
```

---

### 6. Salary Trends

#### **GET /api/market/skills/{skill_id}/salary-trends**

Get salary trend analysis for a skill over time (monthly breakdown).

**Authentication:** Required (JWT)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| skill_id | integer | ID of the skill to analyze |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | integer | 180 | Analyze last N days |

**Response:**
```json
{
  "skill_id": 45,
  "skill_name": "Python",
  "trend_direction": "increasing",
  "total_postings": 11,
  "period_days": 180,
  "monthly_data": [
    {
      "month": "2025-05",
      "postings": 2,
      "average_salary": 150000.00,
      "median_salary": 150000.00
    },
    {
      "month": "2025-06",
      "postings": 3,
      "average_salary": 155000.00,
      "median_salary": 155000.00
    },
    {
      "month": "2025-07",
      "postings": 6,
      "average_salary": 160000.00,
      "median_salary": 160000.00
    }
  ]
}
```

**Trend Direction Values:**
- `increasing`: Salary trend going up
- `decreasing`: Salary trend going down
- `stable`: Salary trend relatively flat
- `insufficient_data`: Less than 2 months of data

---

### 7. Skill Gap Analysis

#### **POST /api/market/skills/gap-analysis**

Compare user's resume skills against market demand to identify skill gaps.

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "skills": ["Python", "Django", "PostgreSQL", "Docker"],
  "job_title": "Senior Backend Developer"
}
```

**Field Definitions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| skills | array | Yes | List of skills from user's resume |
| job_title | string | No | Target job title for context |

**Response:**
```json
{
  "user_skill_count": 4,
  "matched_skills": 4,
  "missing_skills": 16,
  "high_demand_gaps": 6,
  "gap_score": 30.0,
  "recommendation": "Good match. Consider learning 1-2 additional high-demand skills.",
  "have_skills": [
    {
      "skill_id": 45,
      "skill_name": "Python",
      "market_demand_score": 95.65,
      "demand_percentage": 47.83,
      "average_salary": 156250.00
    }
  ],
  "missing_high_demand": [
    {
      "skill_id": 78,
      "skill_name": "Kubernetes",
      "market_demand_score": 72.50,
      "demand_percentage": 36.25,
      "average_salary": 168750.00
    },
    {
      "skill_id": 89,
      "skill_name": "AWS",
      "market_demand_score": 85.20,
      "demand_percentage": 42.60,
      "average_salary": 175000.00
    }
  ]
}
```

**Gap Score Interpretation:**
- **0-20**: Excellent match with market demand
- **20-40**: Good match, consider learning 1-2 additional skills
- **40-60**: Moderate match, several high-demand skills missing
- **60-80**: Significant gap, focus on top-demanded skills
- **80-100**: Large gap, comprehensive skill development recommended

---

### 8. Industry Skill Requirements

#### **GET /api/market/industries/{industry}/skills**

Get most in-demand skills for a specific industry.

**Authentication:** Required (JWT)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| industry | string | Industry name (e.g., "Technology", "Finance") |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | integer | 90 | Analyze postings from last N days |

**Response:**
```json
{
  "industry": "Technology",
  "postings_analyzed": 12,
  "period_days": 90,
  "top_skills": [
    {
      "skill_id": 45,
      "skill_name": "Python",
      "demand_frequency": 8,
      "average_salary": 160000.00,
      "category": "Programming Language"
    },
    {
      "skill_id": 72,
      "skill_name": "JavaScript",
      "demand_frequency": 7,
      "average_salary": 145000.00,
      "category": "Programming Language"
    },
    {
      "skill_id": 67,
      "skill_name": "SQL",
      "demand_frequency": 6,
      "average_salary": 155000.00,
      "category": "Database"
    }
  ]
}
```

---

### 9. Location Salary Insights

#### **GET /api/market/locations/{location}/salaries**

Get salary statistics for a specific location, optionally for a specific skill.

**Authentication:** Required (JWT)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| location | string | Location (e.g., "San Francisco, CA") |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| skill_id | integer | Optional: Filter by specific skill |

**Response (without skill filter):**
```json
{
  "location": "San Francisco, CA",
  "postings_count": 5,
  "average_salary": 175000.00,
  "median_salary": 175000.00,
  "min_salary": 150000.00,
  "max_salary": 200000.00
}
```

**Response (with skill filter):**
```json
{
  "location": "San Francisco, CA",
  "skill_name": "Python",
  "postings_count": 3,
  "average_salary": 165000.00,
  "median_salary": 165000.00,
  "min_salary": 150000.00,
  "max_salary": 180000.00
}
```

---

### 10. Market Dashboard Summary

#### **GET /api/market/dashboard/summary**

Get high-level market intelligence summary for dashboard display.

**Authentication:** Required (JWT)

**Response:**
```json
{
  "summary": {
    "total_postings": 23,
    "total_unique_skills": 45,
    "avg_salary_all": 117043.48,
    "top_demanded_skill": {
      "skill_name": "Python",
      "demand_score": 95.65
    },
    "fastest_growing_skill": {
      "skill_name": "Kubernetes",
      "trend": "increasing"
    }
  },
  "industry_breakdown": {
    "Technology": {
      "postings": 12,
      "avg_salary": 155000.00
    },
    "Finance": {
      "postings": 3,
      "avg_salary": 105000.00
    }
  },
  "location_insights": {
    "San Francisco, CA": {
      "postings": 5,
      "avg_salary": 175000.00
    },
    "New York, NY": {
      "postings": 4,
      "avg_salary": 120000.00
    }
  }
}
```

---

## Integration Patterns

### Pattern 1: Daily Job Posting Ingestion

Schedule daily job posting ingestion from external sources:

```python
# backend/scheduled_jobs.py
from apscheduler.schedulers.background import BackgroundScheduler
from job_posting_ingestion import get_ingestion_manager

def scheduled_ingest_jobs():
    """Run daily job ingestion"""
    db = current_app.extensions['sqlalchemy'].db
    manager = get_ingestion_manager(db)

    # Fetch jobs from external API
    jobs = fetch_from_indeed_api()  # Custom implementation

    # Ingest and extract skills
    result = manager.ingest_postings(jobs, extract_skills=True)
    print(f"Ingested {result['postings_ingested']} postings")

# Initialize scheduler in app.py
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_ingest_jobs, 'cron', hour=2, minute=0)  # Daily at 2 AM
scheduler.start()
```

### Pattern 2: Real-Time Skill Demand Updates

Update skill demand scores after each ingestion:

```python
# In /api/jobs/ingest endpoint
from market_intelligence_analyzer import get_market_intelligence_analyzer

manager = get_ingestion_manager(db)
result = manager.ingest_postings(postings, extract_skills=True)

# Recalculate market demand
analyzer = get_market_intelligence_analyzer(db)
demand_scores = analyzer.get_skill_market_demand()

return jsonify({
    'success': True,
    'postings_ingested': result['postings_ingested'],
    'demand_scores_updated': len(demand_scores)
})
```

### Pattern 3: Custom Data Source Integration

Implement custom job posting sources:

```python
# backend/job_posting_sources/linkedin_source.py
from job_posting_ingestion import JobPostingSource, JobPosting

class LinkedInJobSource(JobPostingSource):
    """Fetch job postings from LinkedIn"""

    def fetch_jobs(self, **kwargs):
        """Fetch and parse LinkedIn jobs"""
        jobs = []

        # Your LinkedIn API integration
        for item in linkedin_api.search_jobs(**kwargs):
            posting = JobPosting(
                job_title=item['title'],
                company_name=item['company'],
                job_description=item['description'],
                location=item['location'],
                salary_min=item.get('salary_min'),
                salary_max=item.get('salary_max'),
                industry=self.detect_industry(item['title']),
                source='linkedin',
                job_url=item['url']
            )
            jobs.append(posting)

        return jobs

# Usage
source = LinkedInJobSource()
jobs = source.fetch_jobs(keywords=['Python', 'Developer'], locations=['San Francisco'])
manager.ingest_postings(jobs, extract_skills=True)
```

### Pattern 4: Salary Comparison Dashboard

Build a salary comparison view:

```python
# Frontend integration
const skillId = 45; // Python
const location = 'San Francisco, CA';

// Get salary trend
const trends = await fetch(`/api/market/skills/${skillId}/salary-trends`)
  .then(r => r.json());

// Get location-specific salary
const locSalary = await fetch(
  `/api/market/locations/${location}/salaries?skill_id=${skillId}`
).then(r => r.json());

// Display comparison
console.log(`Python salary trend: ${trends.trend_direction}`);
console.log(`SF Python average: $${locSalary.average_salary}`);
```

---

## External API Integration Examples

### Integrating with Indeed

```python
# backend/indeed_integration.py
import requests
from job_posting_ingestion import JobPosting

def fetch_from_indeed(query, location, pages=5):
    """Fetch job postings from Indeed (via third-party API)"""
    jobs = []

    for page in range(pages):
        response = requests.get('https://api.indeed.com/v1/search', params={
            'q': query,
            'l': location,
            'start': page * 25,
            'limit': 25,
            'api_key': os.getenv('INDEED_API_KEY')
        })

        for item in response.json()['results']:
            posting = JobPosting(
                job_title=item['jobtitle'],
                company_name=item['company'],
                job_description=item['snippet'],
                location=item['locations'][0] if item['locations'] else location,
                salary_min=item.get('salary_min'),
                salary_max=item.get('salary_max'),
                industry='Technology',  # Detect from title/description
                source='indeed',
                job_url=item['url'],
                posted_date=datetime.fromtimestamp(item['date'] / 1000)
            )
            jobs.append(posting)

    return jobs
```

### Integrating with LinkedIn

```python
# backend/linkedin_integration.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from job_posting_ingestion import JobPosting

def fetch_from_linkedin(keyword, location):
    """Scrape job postings from LinkedIn"""
    driver = webdriver.Chrome()
    jobs = []

    try:
        url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
        driver.get(url)

        # Scroll and collect job listings
        for job_elem in driver.find_elements(By.CLASS_NAME, "job-card"):
            posting = JobPosting(
                job_title=job_elem.find_element(By.CLASS_NAME, "job-title").text,
                company_name=job_elem.find_element(By.CLASS_NAME, "company-name").text,
                job_description=job_elem.find_element(By.CLASS_NAME, "job-description").text,
                location=location,
                industry='Technology',
                source='linkedin'
            )
            jobs.append(posting)

    finally:
        driver.quit()

    return jobs
```

---

## Best Practices

### 1. Batch Processing
- Ingest large datasets in batches of 100-500 postings per request
- Use background jobs for processing >1000 postings

### 2. Error Handling
- Implement retry logic for failed skill extractions
- Log all ingestion errors with timestamp and posting data
- Validate job postings before ingestion

### 3. Data Quality
- Standardize location names (use canonical formats)
- Validate salary ranges (min < max)
- Clean job descriptions (remove HTML, normalize whitespace)

### 4. Performance
- Index job_posting_url for deduplication queries
- Cache market demand scores (recalculate every 6 hours)
- Batch skill extraction requests

### 5. Data Privacy
- Don't store personally identifiable information (PII)
- Anonymize company names if required
- Implement data retention policies (e.g., delete postings >1 year old)

---

## Troubleshooting

### Issue: Skill Extraction Returns Empty Results
**Solution:** Check if Spacy model is installed:
```bash
docker-compose exec backend python -m spacy download en_core_web_sm
```

### Issue: Duplicate Postings Being Ingested
**Solution:** Ensure `job_url` is unique and properly formatted:
```json
{
  "job_url": "https://indeed.com/viewjob?jk=abc123"
}
```

### Issue: Salary Statistics Show NULL Values
**Solution:** Ensure salary fields are numeric integers:
```json
{
  "salary_min": 150000,
  "salary_max": 200000
}
```

### Issue: Market Demand Scores Are 0
**Solution:** Ensure postings have been ingested and skills extracted:
```bash
# Verify postings exist
curl -X GET http://localhost:5000/api/jobs/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Advanced Features (Future)

- **Trend Analysis**: Use time-series analysis to predict emerging skills
- **Skill Correlation**: Build co-occurrence matrices for skill combinations
- **Geo-Salary Mapping**: Visualize salary variations by region
- **Competitor Analysis**: Compare skill requirements across industries
- **ML-Based Recommendations**: Use ML to suggest skills based on career path
- **Custom Job Sources**: Build connectors for Glassdoor, LinkedIn, etc.

---

## Support & Resources

- **API Base URL**: `http://localhost:5000` (development)
- **API Documentation**: `/api/docs` (Swagger/OpenAPI)
- **Sample Data**: Load via `POST /api/jobs/load-sample-data`
- **Database Schema**: See `models.py` for JobPostingKeyword model

---

**Last Updated:** 2025-11-22
**Version:** 1.0
