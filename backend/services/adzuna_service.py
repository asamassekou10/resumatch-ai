"""
Adzuna Job Board API Integration Service
Fetches real-time job postings from Adzuna API
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Adzuna API Configuration
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"

# Industry to search keywords mapping
INDUSTRY_KEYWORDS = {
    'Technology': ['software engineer', 'developer', 'data scientist', 'devops', 'cloud engineer'],
    'Healthcare': ['nurse', 'doctor', 'medical', 'healthcare', 'clinical'],
    'Finance': ['financial analyst', 'accountant', 'finance', 'banking', 'investment'],
    'Marketing': ['marketing manager', 'digital marketing', 'marketing', 'brand', 'advertising'],
    'Sales': ['sales', 'account executive', 'business development', 'sales manager'],
    'Education': ['teacher', 'professor', 'education', 'instructor', 'academic'],
    'Engineering': ['engineer', 'mechanical engineer', 'civil engineer', 'electrical engineer'],
    'Data Science': ['data scientist', 'data analyst', 'machine learning', 'AI engineer', 'data engineer'],
    'Product Management': ['product manager', 'product owner', 'product', 'agile'],
    'Design': ['designer', 'ux designer', 'ui designer', 'graphic designer', 'creative'],
    'Human Resources': ['hr', 'recruiter', 'human resources', 'talent acquisition'],
    'Operations': ['operations manager', 'operations', 'logistics', 'supply chain'],
    'Customer Service': ['customer service', 'customer support', 'client services'],
    'Legal': ['lawyer', 'attorney', 'legal', 'paralegal', 'counsel'],
    'Consulting': ['consultant', 'consulting', 'advisory', 'strategy consultant']
}

# Experience level mapping
EXPERIENCE_MAPPING = {
    'entry': 'entry level',
    'mid': 'mid level',
    'senior': 'senior',
    'lead': 'lead',
    'manager': 'manager'
}


class AdzunaService:
    """Service for fetching jobs from Adzuna API"""

    def __init__(self):
        """Initialize Adzuna service"""
        self.app_id = ADZUNA_APP_ID
        self.app_key = ADZUNA_APP_KEY
        self.enabled = bool(self.app_id and self.app_key)

        if not self.enabled:
            logger.warning("Adzuna API credentials not configured - service disabled")
        else:
            logger.info("Adzuna API service initialized")

    def search_jobs(
        self,
        industry: str = None,
        location: str = "us",
        keywords: List[str] = None,
        results_per_page: int = 20,
        page: int = 1,
        max_days_old: int = 30
    ) -> Dict:
        """
        Search for jobs on Adzuna

        Args:
            industry: Industry category to filter by
            location: Country code (default: "us")
            keywords: Additional search keywords
            results_per_page: Number of results per page (max 50)
            page: Page number to fetch
            max_days_old: Maximum age of job postings in days

        Returns:
            Dictionary with 'jobs' list and metadata
        """
        if not self.enabled:
            logger.error("Adzuna API not configured")
            return {'jobs': [], 'count': 0, 'error': 'API not configured'}

        try:
            # Build search query
            search_terms = []

            # Add industry keywords
            if industry and industry in INDUSTRY_KEYWORDS:
                search_terms.extend(INDUSTRY_KEYWORDS[industry][:2])  # Use top 2 keywords

            # Add custom keywords
            if keywords:
                search_terms.extend(keywords[:3])  # Limit to 3 custom keywords

            # Default to general tech jobs if no terms
            if not search_terms:
                search_terms = ['software', 'engineer']

            # Construct API URL
            query = ' OR '.join(search_terms)
            url = f"{ADZUNA_BASE_URL}/{location}/search/{page}"

            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': query,
                'results_per_page': min(results_per_page, 50),  # Adzuna max is 50
                'max_days_old': max_days_old,
                'sort_by': 'date'  # Get newest jobs first
            }

            logger.info(f"Searching Adzuna for: {query} (industry: {industry})")

            # Make API request with extended timeout to prevent intermittent failures
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse and normalize job data
            jobs = self._parse_jobs(data.get('results', []), industry)

            return {
                'jobs': jobs,
                'count': len(jobs),
                'total_results': data.get('count', 0),
                'source': 'adzuna',
                'query': query,
                'location': location
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request failed: {e}")
            return {'jobs': [], 'count': 0, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error searching Adzuna jobs: {e}")
            return {'jobs': [], 'count': 0, 'error': str(e)}

    def _parse_jobs(self, raw_jobs: List[Dict], industry: str = None) -> List[Dict]:
        """
        Parse and normalize Adzuna job data to match our schema

        Args:
            raw_jobs: Raw job data from Adzuna API
            industry: Industry category for classification

        Returns:
            List of normalized job dictionaries
        """
        parsed_jobs = []

        for job in raw_jobs:
            try:
                # Extract salary information
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                salary_range = None

                if salary_min and salary_max:
                    salary_range = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                elif salary_min:
                    salary_range = f"${salary_min:,.0f}+"

                # Parse location
                location_data = job.get('location', {})
                location = location_data.get('display_name', 'Remote')

                # Determine experience level from title/description
                title = job.get('title', '')
                experience_level = self._detect_experience_level(title)

                # Build normalized job object
                parsed_job = {
                    'title': title,
                    'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                    'location': location,
                    'job_type': job.get('contract_type', 'Full-time'),
                    'experience_level': experience_level,
                    'salary_range': salary_range,
                    'description': job.get('description', ''),
                    'requirements': self._extract_requirements(job.get('description', '')),
                    'responsibilities': [],  # Adzuna doesn't separate these
                    'benefits': [],  # Not provided by Adzuna
                    'skills_required': self._extract_skills(job.get('description', '')),
                    'industry': industry or self._detect_industry(title),
                    'posted_date': job.get('created'),
                    'application_url': job.get('redirect_url', ''),
                    'source': 'adzuna',
                    'external_id': job.get('id', ''),
                    'category': job.get('category', {}).get('label', '')
                }

                parsed_jobs.append(parsed_job)

            except Exception as e:
                logger.error(f"Error parsing job: {e}")
                continue

        logger.info(f"Parsed {len(parsed_jobs)} jobs from Adzuna")
        return parsed_jobs

    def _detect_experience_level(self, title: str) -> str:
        """Detect experience level from job title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in title_lower for word in ['junior', 'jr.', 'entry', 'associate', 'graduate']):
            return 'Entry Level'
        else:
            return 'Mid Level'

    def _detect_industry(self, title: str) -> str:
        """Detect industry from job title"""
        title_lower = title.lower()

        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return industry

        return 'Technology'  # Default fallback

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract requirements from job description"""
        # Simple extraction - look for common requirement keywords
        requirements = []

        if not description:
            return requirements

        desc_lower = description.lower()

        # Common requirement patterns
        if 'bachelor' in desc_lower or 'degree' in desc_lower:
            requirements.append("Bachelor's degree or equivalent experience")

        if 'year' in desc_lower:
            # Try to extract years of experience
            import re
            years_match = re.search(r'(\d+)\+?\s*year', desc_lower)
            if years_match:
                years = years_match.group(1)
                requirements.append(f"{years}+ years of experience")

        return requirements[:5]  # Limit to 5 requirements

    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        if not description:
            return []

        # Common tech skills to look for
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS',
            'Docker', 'Kubernetes', 'Git', 'API', 'REST', 'GraphQL', 'TypeScript',
            'MongoDB', 'PostgreSQL', 'Redis', 'Machine Learning', 'AI', 'DevOps',
            'Agile', 'Scrum', 'CI/CD', 'Linux', 'Azure', 'GCP', 'Terraform'
        ]

        found_skills = []
        desc_lower = description.lower()

        for skill in common_skills:
            if skill.lower() in desc_lower:
                found_skills.append(skill)

        return found_skills[:10]  # Limit to 10 skills

    def get_job_by_id(self, job_id: str, location: str = "us") -> Optional[Dict]:
        """
        Get a specific job by ID

        Args:
            job_id: Adzuna job ID
            location: Country code

        Returns:
            Job dictionary or None if not found
        """
        if not self.enabled:
            return None

        try:
            url = f"{ADZUNA_BASE_URL}/{location}/jobs/{job_id}"
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key
            }

            # Extended timeout to prevent intermittent failures
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            job_data = response.json()
            return self._parse_jobs([job_data])[0] if job_data else None

        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            return None


# Singleton instance
_adzuna_service = None

def get_adzuna_service() -> AdzunaService:
    """Get or create Adzuna service singleton"""
    global _adzuna_service
    if _adzuna_service is None:
        _adzuna_service = AdzunaService()
    return _adzuna_service
