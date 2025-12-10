"""
Job Matching Service - AI-powered job matching using Google Gemini
Integrates with Adzuna API for real-time job postings
"""

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import google.generativeai as genai
from models import User, JobPosting, JobMatch, Analysis, db
from services import industry_service
from services.adzuna_service import get_adzuna_service

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set - job matching will use fallback logic")


class JobMatchingService:
    """AI-powered job matching service using Gemini 1.5 Flash"""

    def __init__(self):
        """Initialize the job matching service"""
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.ai_enabled = True
        else:
            self.model = None
            self.ai_enabled = False
            logger.info("Job matching running in fallback mode (no AI)")

        # Initialize Adzuna service
        self.adzuna = get_adzuna_service()

    def fetch_and_store_adzuna_jobs(
        self,
        industry: str = None,
        location: str = "us",
        max_results: int = 20,
        force_refresh: bool = False
    ) -> int:
        """
        Fetch jobs from Adzuna API and store them in the database

        Args:
            industry: Industry to filter jobs
            location: Country code for job search
            max_results: Maximum number of jobs to fetch
            force_refresh: Force refetch even if recent jobs exist

        Returns:
            Number of jobs fetched and stored
        """
        if not self.adzuna.enabled:
            logger.warning("Adzuna API not enabled - skipping job fetch")
            return 0

        try:
            # Check if we have recent Adzuna jobs for this industry (within 6 hours)
            if not force_refresh:
                recent_count = JobPosting.query.filter(
                    JobPosting.source == 'adzuna',
                    JobPosting.industry == industry,
                    JobPosting.created_at >= datetime.utcnow() - timedelta(hours=6)
                ).count()

                if recent_count >= 10:
                    logger.info(f"Found {recent_count} recent Adzuna jobs for {industry}, skipping fetch")
                    return 0

            # Fetch jobs from Adzuna
            logger.info(f"Fetching Adzuna jobs for industry: {industry}")
            adzuna_response = self.adzuna.search_jobs(
                industry=industry,
                location=location,
                results_per_page=max_results,
                max_days_old=30
            )

            if 'error' in adzuna_response:
                logger.error(f"Adzuna API error: {adzuna_response['error']}")
                return 0

            jobs = adzuna_response.get('jobs', [])
            stored_count = 0

            # Store each job in database
            for job_data in jobs:
                try:
                    # Check for duplicate (same external_id or similar title+company)
                    existing = None
                    if job_data.get('external_id'):
                        existing = JobPosting.query.filter_by(
                            source='adzuna',
                            external_url=job_data.get('application_url')
                        ).first()

                    if existing:
                        # Update existing job
                        existing.updated_at = datetime.utcnow()
                        existing.is_active = True
                        logger.debug(f"Updated existing job: {existing.title}")
                    else:
                        # Parse salary
                        salary_min = None
                        salary_max = None
                        if job_data.get('salary_range'):
                            # Extract numbers from salary range
                            salary_match = re.findall(r'\$?([\d,]+)', job_data['salary_range'])
                            if len(salary_match) >= 2:
                                salary_min = int(salary_match[0].replace(',', ''))
                                salary_max = int(salary_match[1].replace(',', ''))
                            elif len(salary_match) == 1:
                                salary_min = int(salary_match[0].replace(',', ''))

                        # Create new job posting
                        new_job = JobPosting(
                            title=job_data.get('title', 'Untitled Position'),
                            company=job_data.get('company', 'Unknown Company'),
                            location=job_data.get('location', 'Remote'),
                            remote_type=self._detect_remote_type(job_data.get('location', '')),
                            industry=job_data.get('industry') or industry,
                            description=job_data.get('description', ''),
                            requirements=job_data.get('requirements', []) or job_data.get('skills_required', []),
                            responsibilities=job_data.get('responsibilities', []),
                            salary_min=salary_min,
                            salary_max=salary_max,
                            salary_currency='USD',
                            employment_type=job_data.get('job_type', 'Full-time'),
                            experience_level=job_data.get('experience_level', 'Mid Level'),
                            posted_date=self._parse_date(job_data.get('posted_date')),
                            expires_date=datetime.utcnow() + timedelta(days=7),  # Expire after 7 days
                            source='adzuna',
                            external_url=job_data.get('application_url', ''),
                            is_active=True
                        )

                        db.session.add(new_job)
                        stored_count += 1
                        logger.debug(f"Stored new job: {new_job.title} at {new_job.company}")

                except Exception as e:
                    logger.error(f"Error storing job: {e}")
                    continue

            # Commit all jobs at once
            db.session.commit()
            logger.info(f"Successfully stored {stored_count} new jobs from Adzuna")

            return stored_count

        except Exception as e:
            logger.error(f"Error fetching Adzuna jobs: {e}")
            db.session.rollback()
            return 0

    def _detect_remote_type(self, location: str) -> str:
        """Detect if job is remote, hybrid, or onsite from location string"""
        location_lower = location.lower()
        if 'remote' in location_lower:
            return 'remote'
        elif 'hybrid' in location_lower:
            return 'hybrid'
        else:
            return 'onsite'

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime, default to now if invalid"""
        if not date_str:
            return datetime.utcnow()

        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                from dateutil import parser
                return parser.parse(date_str)
            except:
                return datetime.utcnow()

    def generate_job_matches(
        self,
        user_id: int,
        industry: Optional[str] = None,
        limit: int = 20,
        min_score: float = 50.0,
        force_refresh: bool = False,
        use_adzuna: bool = True
    ) -> List[Dict]:
        """
        Generate AI-powered job matches for a user

        Args:
            user_id: User ID
            industry: Filter by industry (optional)
            limit: Maximum number of matches to return
            min_score: Minimum match score threshold (0-100)
            force_refresh: Force regeneration of matches
            use_adzuna: Fetch fresh jobs from Adzuna API (default: True)

        Returns:
            List of job match dictionaries with scores and explanations
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Get user's industry if not specified
            if not industry:
                industry = industry_service.get_user_industry(user)

            # Fetch fresh jobs from Adzuna if enabled
            if use_adzuna:
                adzuna_count = self.fetch_and_store_adzuna_jobs(
                    industry=industry,
                    max_results=20,
                    force_refresh=force_refresh
                )
                if adzuna_count > 0:
                    logger.info(f"Fetched {adzuna_count} fresh jobs from Adzuna for {industry}")

            # Check for existing recent matches (cached for 1 hour)
            if not force_refresh:
                recent_matches = JobMatch.query.filter(
                    JobMatch.user_id == user_id,
                    JobMatch.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).order_by(JobMatch.match_score.desc()).limit(limit).all()

                if recent_matches and len(recent_matches) >= limit // 2:
                    logger.info(f"Using cached matches for user {user_id}")
                    return [match.to_dict() for match in recent_matches]

            # Get user's skills and experience from latest resume analysis
            user_skills, user_experience = self._get_user_profile(user_id)

            # Find relevant jobs
            query = JobPosting.query.filter(
                JobPosting.is_active == True,
                JobPosting.posted_date >= datetime.utcnow() - timedelta(days=30)
            )

            if industry and industry != 'General':
                query = query.filter(JobPosting.industry == industry)

            # Reduced to 15 jobs to prevent worker timeout (was 100, then 30)
            jobs = query.order_by(JobPosting.posted_date.desc()).limit(15).all()

            if not jobs:
                logger.warning(f"No active jobs found for industry: {industry}")
                return []  # Return empty list to maintain consistent API

            # Generate matches for each job
            matches = []
            for job in jobs:
                # Early exit if we have enough matches (changed from limit * 2 to limit)
                if len(matches) >= limit:
                    logger.info(f"Reached {len(matches)} matches (limit={limit}), stopping early")
                    break

                try:
                    match_data = self._calculate_match_score(
                        user, job, user_skills, user_experience
                    )

                    if match_data['match_score'] >= min_score:
                        # Save or update match in database
                        existing_match = JobMatch.query.filter_by(
                            user_id=user_id,
                            job_posting_id=job.id
                        ).first()

                        if existing_match:
                            # Update existing match
                            existing_match.match_score = match_data['match_score']
                            existing_match.ai_explanation = match_data['explanation']
                            existing_match.matching_skills = match_data['matching_skills']
                            existing_match.missing_skills = match_data['missing_skills']
                            existing_match.skill_match_percentage = match_data['skill_match_percentage']
                            existing_match.updated_at = datetime.utcnow()
                            match_obj = existing_match
                        else:
                            # Create new match
                            match_obj = JobMatch(
                                user_id=user_id,
                                job_posting_id=job.id,
                                match_score=match_data['match_score'],
                                ai_explanation=match_data['explanation'],
                                matching_skills=match_data['matching_skills'],
                                missing_skills=match_data['missing_skills'],
                                skill_match_percentage=match_data['skill_match_percentage']
                            )
                            db.session.add(match_obj)

                        db.session.commit()
                        matches.append(match_obj.to_dict())

                except Exception as e:
                    logger.error(f"Error matching job {job.id}: {str(e)}")
                    continue

            # Sort by match score and return top N
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            return matches[:limit]

        except Exception as e:
            logger.error(f"Error generating job matches: {str(e)}")
            raise

    def _get_user_profile(self, user_id: int) -> tuple:
        """
        Get user's skills and experience from their resume analyses

        Returns:
            Tuple of (skills_list, experience_level)
        """
        # Get latest resume analysis
        latest_analysis = Analysis.query.filter_by(
            user_id=user_id
        ).order_by(Analysis.created_at.desc()).first()

        skills = []
        experience_level = 'Mid'  # Default

        if latest_analysis:
            # Extract skills from keywords_found
            if latest_analysis.keywords_found:
                skills = latest_analysis.keywords_found

            # Try to infer experience level from resume text or user profile
            user = User.query.get(user_id)
            if user and user.experience_level:
                experience_level = user.experience_level

        return skills, experience_level

    def _calculate_match_score(
        self,
        user: User,
        job: JobPosting,
        user_skills: List[str],
        user_experience: str
    ) -> Dict:
        """
        Calculate AI-powered match score between user and job

        Args:
            user: User object
            job: JobPosting object
            user_skills: List of user's skills
            user_experience: User's experience level

        Returns:
            Dict with match_score, explanation, matching_skills, missing_skills
        """
        if self.ai_enabled:
            return self._calculate_match_with_ai(user, job, user_skills, user_experience)
        else:
            return self._calculate_match_fallback(user, job, user_skills, user_experience)

    def _calculate_match_with_ai(
        self,
        user: User,
        job: JobPosting,
        user_skills: List[str],
        user_experience: str
    ) -> Dict:
        """Use Gemini AI to calculate match score"""
        try:
            # Build prompt for Gemini
            prompt = f"""
Analyze the match between this candidate and job posting. Provide a match score and explanation.

**Candidate Profile:**
- Skills: {', '.join(user_skills) if user_skills else 'Not specified'}
- Experience Level: {user_experience}
- Industry: {user.preferred_industry or 'Not specified'}

**Job Posting:**
- Title: {job.title}
- Company: {job.company}
- Industry: {job.industry}
- Experience Level Required: {job.experience_level or 'Not specified'}
- Requirements: {', '.join(job.requirements) if job.requirements else 'Not specified'}
- Description: {job.description[:500] if job.description else 'Not specified'}

**Task:**
Analyze how well this candidate matches the job requirements. Consider:
1. Skill alignment (technical and soft skills)
2. Experience level match
3. Industry fit
4. Growth potential

**Output Format (JSON only):**
```json
{{
    "match_score": 85,
    "explanation": "Brief 2-3 sentence explanation of why this is a good match",
    "matching_skills": ["Python", "React", "AWS"],
    "missing_skills": ["Docker", "Kubernetes"],
    "skill_match_percentage": 75
}}
```

Provide ONLY the JSON, no other text.
"""

            # Call Gemini API
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Extract JSON from response
            match_data = self._parse_ai_response(result_text)

            # Validate and sanitize
            match_data['match_score'] = max(0, min(100, match_data.get('match_score', 50)))
            match_data['explanation'] = match_data.get('explanation', 'AI-generated match')[:500]
            match_data['matching_skills'] = match_data.get('matching_skills', [])[:10]
            match_data['missing_skills'] = match_data.get('missing_skills', [])[:10]
            match_data['skill_match_percentage'] = max(0, min(100, match_data.get('skill_match_percentage', 0)))

            return match_data

        except Exception as e:
            logger.error(f"AI matching failed, using fallback: {str(e)}")
            return self._calculate_match_fallback(user, job, user_skills, user_experience)

    def _calculate_match_fallback(
        self,
        user: User,
        job: JobPosting,
        user_skills: List[str],
        user_experience: str
    ) -> Dict:
        """Fallback algorithm-based matching (no AI required)"""
        score = 0
        matching_skills = []
        missing_skills = []

        # Normalize skills for comparison
        user_skills_lower = [s.lower() for s in user_skills] if user_skills else []
        job_requirements_lower = [r.lower() for r in job.requirements] if job.requirements else []

        # Calculate skill match
        if job_requirements_lower:
            for req in job.requirements:
                req_lower = req.lower()
                if any(req_lower in skill or skill in req_lower for skill in user_skills_lower):
                    matching_skills.append(req)
                    score += 5  # 5 points per matching skill
                else:
                    missing_skills.append(req)

            skill_match_pct = (len(matching_skills) / len(job.requirements)) * 100 if job.requirements else 0
        else:
            skill_match_pct = 50  # Default if no requirements specified

        # Experience level match (20 points max)
        experience_levels = ['Entry', 'Mid', 'Senior', 'Lead', 'Executive']
        if job.experience_level and user_experience:
            try:
                user_level_idx = experience_levels.index(user_experience)
                job_level_idx = experience_levels.index(job.experience_level)
                level_diff = abs(user_level_idx - job_level_idx)

                if level_diff == 0:
                    score += 20  # Perfect match
                elif level_diff == 1:
                    score += 15  # Close match
                elif level_diff == 2:
                    score += 10  # Acceptable
                else:
                    score += 5  # Significant gap
            except ValueError:
                score += 10  # Default if levels don't match exactly

        # Industry match (15 points)
        if user.preferred_industry and job.industry:
            if user.preferred_industry.lower() == job.industry.lower():
                score += 15

        # Location preference (10 points)
        if job.remote_type == 'remote':
            score += 10  # Remote is always a plus

        # Recency bonus (10 points max)
        if job.posted_date:
            days_ago = (datetime.utcnow() - job.posted_date).days
            if days_ago <= 7:
                score += 10
            elif days_ago <= 14:
                score += 5

        # Normalize score to 0-100
        score = min(100, score)

        # Generate explanation
        if score >= 80:
            explanation = f"Excellent match! You have {len(matching_skills)} of the required skills and your experience aligns well with this {job.experience_level or 'position'}."
        elif score >= 60:
            explanation = f"Good match. You match {len(matching_skills)} key skills. Consider learning: {', '.join(missing_skills[:3])} to strengthen your application."
        else:
            explanation = f"Moderate match. This role requires skills in {', '.join(missing_skills[:3])}. Good opportunity to grow your skillset."

        return {
            'match_score': round(score, 1),
            'explanation': explanation,
            'matching_skills': matching_skills[:10],
            'missing_skills': missing_skills[:10],
            'skill_match_percentage': round(skill_match_pct, 1)
        }

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response and extract JSON"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                # Remove markdown code blocks if present
                json_str = re.sub(r'```json\s*|\s*```', '', json_str)
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Return default structure
            return {
                'match_score': 50,
                'explanation': 'Unable to generate AI match analysis',
                'matching_skills': [],
                'missing_skills': [],
                'skill_match_percentage': 0
            }


# Singleton instance
_job_matcher_instance = None

def get_job_matcher() -> JobMatchingService:
    """Get singleton instance of JobMatchingService"""
    global _job_matcher_instance
    if _job_matcher_instance is None:
        _job_matcher_instance = JobMatchingService()
    return _job_matcher_instance
