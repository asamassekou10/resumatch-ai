"""
Real Job Posting Sources

Provides connectors to real job board APIs for fetching actual job postings.
Uses publicly available APIs with rate limiting and error handling.

Supported Sources:
1. JSearch (RapidAPI) - Aggregates Indeed, LinkedIn, Glassdoor, ZipRecruiter
2. Adzuna - Real-time job search API
3. RemoteOK - Remote job listings

Usage:
    source = JSearchJobSource(api_key="your_rapidapi_key")
    postings = source.fetch_postings(query="python developer", limit=50)
"""

import os
import requests
import logging
from typing import List, Optional, Dict
from datetime import datetime
from job_posting_ingestion import JobPosting, JobPostingSource

logger = logging.getLogger(__name__)


class JSearchJobSource(JobPostingSource):
    """
    Job posting source using JSearch API (via RapidAPI)

    This provides real job listings from Indeed, LinkedIn, Glassdoor,
    ZipRecruiter, and other major job boards.

    Requires: RAPIDAPI_KEY environment variable
    Free tier: 500 requests/month
    """

    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY not set - JSearch will be unavailable")

    def fetch_postings(self, limit: int = 100, **kwargs) -> List[JobPosting]:
        """
        Fetch real job postings from JSearch API

        Args:
            limit: Maximum number of postings to fetch
            query: Job search query (e.g., "python developer")
            location: Location filter (e.g., "New York, NY")
            employment_types: Filter by type (e.g., "FULLTIME", "PARTTIME")
            date_posted: Filter by date (e.g., "today", "3days", "week")

        Returns:
            List of JobPosting objects with real job data
        """
        if not self.api_key:
            logger.error("Cannot fetch from JSearch - no API key configured")
            return []

        query = kwargs.get('query', 'software developer')
        location = kwargs.get('location', 'United States')
        date_posted = kwargs.get('date_posted', 'week')

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        params = {
            "query": f"{query} in {location}",
            "page": "1",
            "num_pages": str(min(limit // 10, 10)),  # Max 10 pages
            "date_posted": date_posted
        }

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            postings = []
            for job in data.get('data', [])[:limit]:
                posting = self._parse_job(job)
                if posting:
                    postings.append(posting)

            logger.info(f"Fetched {len(postings)} real job postings from JSearch")
            return postings

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from JSearch: {str(e)}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobPosting]:
        """Parse JSearch job data into JobPosting object"""
        try:
            # Extract salary information
            salary_min = job.get('job_min_salary')
            salary_max = job.get('job_max_salary')

            # Handle string salaries
            if isinstance(salary_min, str):
                salary_min = int(float(salary_min.replace(',', '').replace('$', '')))
            if isinstance(salary_max, str):
                salary_max = int(float(salary_max.replace(',', '').replace('$', '')))

            return JobPosting(
                job_title=job.get('job_title', 'Unknown Position'),
                company_name=job.get('employer_name', 'Unknown Company'),
                job_description=job.get('job_description', '')[:5000],  # Limit size
                location=f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(', '),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=job.get('job_salary_currency', 'USD'),
                industry=job.get('employer_industry', 'Technology'),
                source='jsearch',
                job_url=job.get('job_apply_link', job.get('job_google_link')),
                posted_date=datetime.fromisoformat(job['job_posted_at_datetime_utc'].replace('Z', '+00:00'))
                    if job.get('job_posted_at_datetime_utc') else None,
                extracted_at=datetime.utcnow()
            )
        except Exception as e:
            logger.warning(f"Error parsing job: {str(e)}")
            return None


class AdzunaJobSource(JobPostingSource):
    """
    Job posting source using Adzuna API

    Provides real job listings from major markets worldwide.

    Requires: ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables
    Free tier: 250 requests/day
    """

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.app_key = app_key or os.getenv('ADZUNA_APP_KEY')
        if not self.app_id or not self.app_key:
            logger.warning("ADZUNA credentials not set - Adzuna will be unavailable")

    def fetch_postings(self, limit: int = 100, **kwargs) -> List[JobPosting]:
        """
        Fetch real job postings from Adzuna API

        Args:
            limit: Maximum number of postings to fetch
            query: Job search query
            country: Country code (us, gb, de, etc.)
            what_or: Keywords to include
        """
        if not self.app_id or not self.app_key:
            logger.error("Cannot fetch from Adzuna - credentials not configured")
            return []

        query = kwargs.get('query', 'software developer')
        country = kwargs.get('country', 'us')

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(limit, 50),
            "what": query,
            "content-type": "application/json"
        }

        try:
            url = f"{self.BASE_URL}/{country}/search/1"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            postings = []
            for job in data.get('results', [])[:limit]:
                posting = self._parse_job(job)
                if posting:
                    postings.append(posting)

            logger.info(f"Fetched {len(postings)} real job postings from Adzuna")
            return postings

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Adzuna: {str(e)}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobPosting]:
        """Parse Adzuna job data into JobPosting object"""
        try:
            return JobPosting(
                job_title=job.get('title', 'Unknown Position'),
                company_name=job.get('company', {}).get('display_name', 'Unknown Company'),
                job_description=job.get('description', '')[:5000],
                location=job.get('location', {}).get('display_name', ''),
                salary_min=int(job.get('salary_min')) if job.get('salary_min') else None,
                salary_max=int(job.get('salary_max')) if job.get('salary_max') else None,
                salary_currency='USD',
                industry=job.get('category', {}).get('label', 'General'),
                source='adzuna',
                job_url=job.get('redirect_url'),
                posted_date=datetime.fromisoformat(job['created'].replace('Z', '+00:00'))
                    if job.get('created') else None,
                extracted_at=datetime.utcnow()
            )
        except Exception as e:
            logger.warning(f"Error parsing Adzuna job: {str(e)}")
            return None


class RemoteOKJobSource(JobPostingSource):
    """
    Job posting source for RemoteOK (remote job listings)

    Provides remote tech job listings for free.
    No API key required - public API.
    """

    BASE_URL = "https://remoteok.com/api"

    def fetch_postings(self, limit: int = 100, **kwargs) -> List[JobPosting]:
        """
        Fetch remote job postings from RemoteOK

        This is a free API that provides real remote tech job listings.
        """
        try:
            headers = {
                'User-Agent': 'ResumeAnalyzer/1.0 (job-market-intelligence)'
            }
            response = requests.get(self.BASE_URL, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            postings = []
            # Skip first item (metadata) and process jobs
            for job in data[1:limit+1]:
                posting = self._parse_job(job)
                if posting:
                    postings.append(posting)

            logger.info(f"Fetched {len(postings)} real remote job postings from RemoteOK")
            return postings

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from RemoteOK: {str(e)}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobPosting]:
        """Parse RemoteOK job data into JobPosting object"""
        try:
            # Parse salary from string if available
            salary_text = job.get('salary', '')
            salary_min, salary_max = None, None
            if salary_text:
                # Try to extract salary range
                import re
                numbers = re.findall(r'[\d,]+', salary_text.replace('k', '000'))
                if len(numbers) >= 2:
                    salary_min = int(numbers[0].replace(',', ''))
                    salary_max = int(numbers[1].replace(',', ''))
                elif len(numbers) == 1:
                    salary_min = salary_max = int(numbers[0].replace(',', ''))

            # Build description from tags and description
            tags = job.get('tags', [])
            description = job.get('description', '')
            full_description = f"Skills: {', '.join(tags)}\n\n{description}"

            return JobPosting(
                job_title=job.get('position', 'Unknown Position'),
                company_name=job.get('company', 'Unknown Company'),
                job_description=full_description[:5000],
                location='Remote',
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency='USD',
                industry='Technology',
                source='remoteok',
                job_url=job.get('url'),
                posted_date=datetime.fromtimestamp(job['epoch']) if job.get('epoch') else None,
                extracted_at=datetime.utcnow()
            )
        except Exception as e:
            logger.warning(f"Error parsing RemoteOK job: {str(e)}")
            return None


def get_real_job_sources() -> List[JobPostingSource]:
    """
    Get all available real job sources based on configured API keys

    Returns list of initialized job sources that have valid credentials.
    """
    sources = []

    # Always add RemoteOK (no API key needed)
    sources.append(RemoteOKJobSource())

    # Add JSearch if configured
    if os.getenv('RAPIDAPI_KEY'):
        sources.append(JSearchJobSource())

    # Add Adzuna if configured
    if os.getenv('ADZUNA_APP_ID') and os.getenv('ADZUNA_APP_KEY'):
        sources.append(AdzunaJobSource())

    logger.info(f"Initialized {len(sources)} real job sources")
    return sources


def fetch_all_real_postings(limit_per_source: int = 50) -> List[JobPosting]:
    """
    Fetch job postings from all available real sources

    Args:
        limit_per_source: Maximum postings to fetch from each source

    Returns:
        Combined list of job postings from all sources
    """
    sources = get_real_job_sources()
    all_postings = []

    for source in sources:
        try:
            postings = source.fetch_postings(limit=limit_per_source)
            all_postings.extend(postings)
            logger.info(f"Fetched {len(postings)} from {source.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error fetching from {source.__class__.__name__}: {str(e)}")

    logger.info(f"Total real job postings fetched: {len(all_postings)}")
    return all_postings
