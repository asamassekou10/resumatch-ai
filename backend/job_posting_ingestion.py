"""
Job Posting Data Ingestion Framework

Provides infrastructure to ingest job posting data from multiple sources:
- Indeed API
- LinkedIn API
- Glassdoor
- Custom data sources

Normalizes job posting data and extracts skills for market intelligence.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Standardized job posting data structure"""
    job_title: str
    company_name: str
    job_description: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = 'USD'
    industry: Optional[str] = None
    source: str = 'unknown'
    job_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    extracted_at: datetime = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.utcnow()


class JobPostingSource(ABC):
    """Abstract base class for job posting data sources"""

    @abstractmethod
    def fetch_postings(self, limit: int = 100, **kwargs) -> List[JobPosting]:
        """
        Fetch job postings from source.

        Args:
            limit: Maximum number of postings to fetch
            **kwargs: Source-specific parameters

        Returns:
            List of normalized JobPosting objects
        """
        pass


class JobPostingIngestionManager:
    """Manages job posting data ingestion and skill extraction"""

    def __init__(self, db=None):
        """Initialize ingestion manager"""
        self.db = db

    def ingest_postings(self, postings: List[JobPosting], extract_skills: bool = True) -> Dict:
        """
        Ingest job postings into the system.

        Args:
            postings: List of JobPosting objects
            extract_skills: Whether to extract skills from job descriptions

        Returns:
            Dictionary with ingestion results
        """
        if not self.db:
            return {'error': 'Database not available', 'postings_ingested': 0}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from skill_extractor import get_skill_extractor

            with app.app_context():
                ingested = 0
                skipped = 0
                errors = 0
                extracted_skills = 0

                # Get skill extractor if skills should be extracted
                if extract_skills:
                    extractor = get_skill_extractor(self.db)

                for posting in postings:
                    try:
                        # Check if posting already exists (by URL or title+company+date)
                        if posting.job_url:
                            existing = JobPostingKeyword.query.filter_by(
                                job_posting_url=posting.job_url
                            ).first()
                            if existing:
                                skipped += 1
                                continue

                        # Extract skills from job description
                        if extract_skills and posting.job_description:
                            skills = extractor.extract_skills(posting.job_description)
                            logger.info(f"Extracted {len(skills)} skills from {posting.job_title}")

                            # Create JobPostingKeyword records for each skill
                            for skill in skills:
                                # Skip skills without a matched keyword in database
                                if skill.matched_keyword is None:
                                    logger.debug(f"Skipping unmatched skill: {skill.skill_name}")
                                    continue

                                try:
                                    job_posting_keyword = JobPostingKeyword(
                                        job_posting_url=posting.job_url,
                                        job_title=posting.job_title,
                                        company_name=posting.company_name,
                                        keyword_id=skill.matched_keyword,
                                        frequency=1,
                                        salary_min=posting.salary_min,
                                        salary_max=posting.salary_max,
                                        salary_currency=posting.salary_currency,
                                        location=posting.location,
                                        industry=posting.industry,
                                        source=posting.source,
                                        extracted_at=posting.extracted_at
                                    )
                                    self.db.session.add(job_posting_keyword)
                                    extracted_skills += 1

                                except Exception as e:
                                    logger.warning(f"Error storing skill {skill.skill_name}: {str(e)}")
                                    errors += 1

                        ingested += 1

                    except Exception as e:
                        logger.error(f"Error ingesting posting {posting.job_title}: {str(e)}")
                        errors += 1

                self.db.session.commit()

                return {
                    'postings_ingested': ingested,
                    'postings_skipped': skipped,
                    'errors': errors,
                    'skills_extracted': extracted_skills,
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            return {'error': str(e), 'postings_ingested': 0}

    def extract_salary_from_text(self, text: str, currency: str = 'USD') -> Tuple[Optional[int], Optional[int]]:
        """
        Extract salary range from job description text.

        Supports formats like:
        - $50,000 - $80,000
        - $50000 to $80000
        - $50K - $80K
        - $50k-$80k

        Args:
            text: Text to search for salary information
            currency: Currency code (default USD)

        Returns:
            Tuple of (min_salary, max_salary) or (None, None)
        """
        if not text:
            return None, None

        # Patterns for salary extraction
        patterns = [
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:to|-|and)\s*\$?([\d,]+(?:\.\d{2})?)',  # $50,000 - $80,000
            r'\$?([\d,]+)k\s*(?:to|-)\s*\$?([\d,]+)k',  # $50K - $80K
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    min_val = int(match.group(1).replace(',', '').replace('k', '000'))
                    max_val = int(match.group(2).replace(',', '').replace('k', '000'))

                    # Validate salary range (between $20K and $500K)
                    if 20000 <= min_val <= 500000 and 20000 <= max_val <= 500000 and min_val <= max_val:
                        return min_val, max_val
                except (ValueError, AttributeError):
                    continue

        return None, None

    def identify_industry(self, job_title: str, job_description: str) -> Optional[str]:
        """
        Identify industry from job title and description.

        Args:
            job_title: Job title
            job_description: Job description

        Returns:
            Industry name or None
        """
        # Industry keywords mapping
        industry_keywords = {
            'Technology': ['software', 'engineer', 'developer', 'python', 'java', 'cloud', 'devops', 'data scientist'],
            'Finance': ['finance', 'accounting', 'banker', 'trader', 'analyst', 'audit', 'cpa'],
            'Healthcare': ['nurse', 'doctor', 'physician', 'medical', 'clinical', 'hospital', 'healthcare'],
            'Sales': ['sales', 'business development', 'account executive', 'sales manager'],
            'Marketing': ['marketing', 'content', 'seo', 'digital', 'brand', 'advertising'],
            'Design': ['designer', 'ux', 'ui', 'graphic', 'product design', 'creative'],
            'Education': ['teacher', 'professor', 'instructor', 'education', 'tutor', 'curriculum'],
            'Manufacturing': ['manufacturing', 'production', 'operations', 'supply chain', 'logistics'],
            'Construction': ['construction', 'civil', 'architect', 'contractor', 'builder'],
            'Retail': ['retail', 'store manager', 'cashier', 'merchandiser', 'customer service'],
        }

        combined_text = f"{job_title} {job_description}".lower()

        # Score each industry
        best_industry = None
        best_score = 0

        for industry, keywords in industry_keywords.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > best_score:
                best_score = score
                best_industry = industry

        return best_industry if best_score > 0 else None


# Global instance
_ingestion_manager = None


def get_ingestion_manager(db=None) -> JobPostingIngestionManager:
    """Get or create the global ingestion manager instance"""
    global _ingestion_manager
    if _ingestion_manager is None:
        _ingestion_manager = JobPostingIngestionManager(db=db)
    return _ingestion_manager
