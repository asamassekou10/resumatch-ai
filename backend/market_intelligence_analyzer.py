"""
Market Intelligence Analyzer

Analyzes job posting data to provide:
1. Market demand scores for skills
2. Salary trend analysis
3. Skill gap analysis (what's missing from resumes vs. job market)
4. Industry-specific skill insights
5. Location-based salary and demand trends
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging
import statistics

logger = logging.getLogger(__name__)


class MarketIntelligenceAnalyzer:
    """Analyzes market trends and job posting data"""

    def __init__(self, db=None):
        """Initialize analyzer with database access"""
        self.db = db

    def get_skill_market_demand(self, limit_days: int = 90, industry: Optional[str] = None) -> Dict[int, Dict]:
        """
        Calculate market demand score for each skill based on job postings.

        Args:
            limit_days: Analyze job postings from last N days
            industry: Optional industry filter (e.g., 'Technology', 'Healthcare', 'Security')

        Returns:
            Dictionary with skill_id -> market demand data
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from sqlalchemy import func
            from sqlalchemy.orm import joinedload

            with app.app_context():
                # Get cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=limit_days)

                # Query job postings with skills - EAGERLY LOAD keywords to avoid N+1 queries
                query = JobPostingKeyword.query.options(
                    joinedload(JobPostingKeyword.keyword)
                ).filter(JobPostingKeyword.extracted_at >= cutoff_date)

                # Apply industry filter if specified
                if industry:
                    # Try exact match first, then case-insensitive partial match
                    query = query.filter(
                        JobPostingKeyword.industry.ilike(f'%{industry}%')
                    )

                postings = query.all()

                if not postings:
                    return {}

                # Aggregate by keyword and build keyword map (no N+1 queries!)
                skill_data = defaultdict(lambda: {
                    'occurrences': 0,
                    'total_frequency': 0,
                    'salary_values': [],
                    'sources': Counter(),
                    'industries': Counter(),
                    'locations': Counter()
                })
                keyword_map = {}  # Cache keywords to avoid repeated queries

                for posting in postings:
                    kid = posting.keyword_id

                    # Store keyword object (already loaded via joinedload)
                    if kid not in keyword_map and posting.keyword:
                        keyword_map[kid] = posting.keyword

                    skill_data[kid]['occurrences'] += 1
                    skill_data[kid]['total_frequency'] += posting.frequency

                    # Collect salary data
                    if posting.salary_min and posting.salary_max:
                        avg_salary = (posting.salary_min + posting.salary_max) / 2
                        skill_data[kid]['salary_values'].append(avg_salary)

                    # Track sources and industries
                    if posting.source:
                        skill_data[kid]['sources'][posting.source] += 1
                    if posting.industry:
                        skill_data[kid]['industries'][posting.industry] += 1
                    if posting.location:
                        skill_data[kid]['locations'][posting.location] += 1

                # Calculate demand scores
                result = {}
                total_postings = len(postings)

                for skill_id, data in skill_data.items():
                    # Use cached keyword (no database query!)
                    keyword = keyword_map.get(skill_id)
                    if not keyword:
                        continue

                    # Market demand = (occurrences / total postings) * 100
                    demand_percentage = (data['occurrences'] / total_postings) * 100

                    # Salary statistics
                    if data['salary_values']:
                        avg_salary = statistics.mean(data['salary_values'])
                        median_salary = statistics.median(data['salary_values'])
                        salary_range = max(data['salary_values']) - min(data['salary_values'])
                    else:
                        avg_salary = None
                        median_salary = None
                        salary_range = None

                    # Demand score (0-100)
                    demand_score = min(100, demand_percentage * 2)  # Scale up for visibility

                    result[skill_id] = {
                        'skill_id': skill_id,
                        'skill_name': keyword.keyword,
                        'market_demand_score': round(demand_score, 2),
                        'demand_percentage': round(demand_percentage, 2),
                        'postings_count': data['occurrences'],
                        'average_salary': round(avg_salary, 2) if avg_salary else None,
                        'median_salary': round(median_salary, 2) if median_salary else None,
                        'salary_range': round(salary_range, 2) if salary_range else None,
                        'top_sources': dict(data['sources'].most_common(3)),
                        'top_industries': dict(data['industries'].most_common(3)),
                        'top_locations': dict(data['locations'].most_common(3))
                    }

                return result

        except Exception as e:
            logger.error(f"Error calculating market demand: {str(e)}")
            return {}

    def get_salary_trends(self, skill_id: int, limit_days: int = 180) -> Dict:
        """
        Get salary trends over time for a specific skill.

        Args:
            skill_id: Skill to analyze
            limit_days: Analyze last N days

        Returns:
            Dictionary with salary trend data
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from datetime import date

            with app.app_context():
                # Verify skill exists
                keyword = Keyword.query.get(skill_id)
                if not keyword:
                    return {}

                cutoff_date = datetime.utcnow() - timedelta(days=limit_days)

                # Get postings with this skill
                postings = (
                    JobPostingKeyword.query
                    .filter(JobPostingKeyword.keyword_id == skill_id)
                    .filter(JobPostingKeyword.extracted_at >= cutoff_date)
                    .all()
                )

                if not postings:
                    return {'skill_id': skill_id, 'skill_name': keyword.keyword, 'message': 'No data'}

                # Group by month
                monthly_data = defaultdict(lambda: {'salaries': [], 'count': 0})

                for posting in postings:
                    month_key = posting.extracted_at.strftime('%Y-%m')

                    if posting.salary_min and posting.salary_max:
                        avg = (posting.salary_min + posting.salary_max) / 2
                        monthly_data[month_key]['salaries'].append(avg)

                    monthly_data[month_key]['count'] += 1

                # Calculate monthly statistics
                trend_data = []
                for month in sorted(monthly_data.keys()):
                    data = monthly_data[month]
                    if data['salaries']:
                        avg_salary = statistics.mean(data['salaries'])
                        median_salary = statistics.median(data['salaries'])
                    else:
                        avg_salary = None
                        median_salary = None

                    trend_data.append({
                        'month': month,
                        'postings': data['count'],
                        'average_salary': round(avg_salary, 2) if avg_salary else None,
                        'median_salary': round(median_salary, 2) if median_salary else None
                    })

                # Calculate trend direction
                if len(trend_data) >= 2:
                    first_avg = trend_data[0].get('average_salary') or 0
                    last_avg = trend_data[-1].get('average_salary') or 0

                    if last_avg > first_avg:
                        trend_direction = 'increasing'
                    elif last_avg < first_avg:
                        trend_direction = 'decreasing'
                    else:
                        trend_direction = 'stable'
                else:
                    trend_direction = 'insufficient_data'

                return {
                    'skill_id': skill_id,
                    'skill_name': keyword.keyword,
                    'trend_direction': trend_direction,
                    'monthly_data': trend_data,
                    'total_postings': sum(d['count'] for d in trend_data),
                    'period_days': limit_days
                }

        except Exception as e:
            logger.error(f"Error analyzing salary trends: {str(e)}")
            return {}

    def get_skill_gap_analysis(self, user_skills: List[str], job_title: Optional[str] = None) -> Dict:
        """
        Analyze gap between user skills and market demand.

        Args:
            user_skills: List of skills user has (from resume)
            job_title: Optional target job title

        Returns:
            Dictionary with skill gap analysis
        """
        if not self.db or not user_skills:
            return {}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from sqlalchemy import func

            with app.app_context():
                # Get market demand for all skills
                market_demand = self.get_skill_market_demand()

                # Find user skill IDs
                user_skill_ids = set()
                for skill_name in user_skills:
                    keyword = Keyword.query.filter_by(keyword=skill_name.lower()).first()
                    if keyword:
                        user_skill_ids.add(keyword.id)

                # Get top demanded skills
                top_skills = sorted(
                    market_demand.values(),
                    key=lambda x: x['market_demand_score'],
                    reverse=True
                )[:20]

                # Analyze gaps
                have_skills = []
                missing_skills = []
                high_demand_missing = []

                for skill_data in top_skills:
                    if skill_data['skill_id'] in user_skill_ids:
                        have_skills.append(skill_data)
                    else:
                        missing_skills.append(skill_data)
                        if skill_data['market_demand_score'] >= 70:  # High demand threshold
                            high_demand_missing.append(skill_data)

                # Calculate gap score
                gap_score = (len(high_demand_missing) / max(1, len(top_skills))) * 100

                return {
                    'user_skill_count': len(user_skills),
                    'matched_skills': len(have_skills),
                    'missing_skills': len(missing_skills),
                    'high_demand_gaps': len(high_demand_missing),
                    'gap_score': round(gap_score, 1),  # 0-100, lower is better
                    'have_skills': have_skills[:10],
                    'missing_high_demand': high_demand_missing[:10],
                    'recommendation': self._get_gap_recommendation(gap_score)
                }

        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {str(e)}")
            return {}

    def _get_gap_recommendation(self, gap_score: float) -> str:
        """Get recommendation based on gap score"""
        if gap_score < 20:
            return "Excellent match with market demand! Your skills align well."
        elif gap_score < 40:
            return "Good match. Consider learning 1-2 additional high-demand skills."
        elif gap_score < 60:
            return "Moderate match. Several high-demand skills are missing."
        elif gap_score < 80:
            return "Significant skills gap. Focus on learning top-demanded skills."
        else:
            return "Large skills gap. Comprehensive skill development recommended."

    def get_industry_skill_requirements(self, industry: str, limit_days: int = 90) -> Dict:
        """
        Get most in-demand skills for a specific industry.

        Args:
            industry: Industry name (e.g., 'Technology', 'Finance')
            limit_days: Analyze last N days

        Returns:
            Dictionary with industry-specific skill requirements
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from sqlalchemy.orm import joinedload

            with app.app_context():
                cutoff_date = datetime.utcnow() - timedelta(days=limit_days)

                # Get postings for this industry - EAGERLY LOAD keywords to avoid N+1 queries
                postings = (
                    JobPostingKeyword.query
                    .options(joinedload(JobPostingKeyword.keyword))
                    .filter(JobPostingKeyword.industry.ilike(f"%{industry}%"))
                    .filter(JobPostingKeyword.extracted_at >= cutoff_date)
                    .all()
                )

                if not postings:
                    return {'industry': industry, 'message': 'No data available'}

                # Count skill occurrences and build keyword map (no N+1 queries!)
                skill_counts = Counter()
                skill_salaries = defaultdict(list)
                keyword_map = {}  # Cache keywords to avoid repeated queries

                for posting in postings:
                    skill_counts[posting.keyword_id] += posting.frequency

                    # Store keyword object (already loaded via joinedload)
                    if posting.keyword_id not in keyword_map and posting.keyword:
                        keyword_map[posting.keyword_id] = posting.keyword

                    if posting.salary_min and posting.salary_max:
                        avg_salary = (posting.salary_min + posting.salary_max) / 2
                        skill_salaries[posting.keyword_id].append(avg_salary)

                # Get top skills
                top_skills = []
                for skill_id, count in skill_counts.most_common(15):
                    # Use cached keyword (no database query!)
                    keyword = keyword_map.get(skill_id)
                    if not keyword:
                        continue

                    # Calculate average salary for this skill in this industry
                    if skill_salaries[skill_id]:
                        avg_salary = statistics.mean(skill_salaries[skill_id])
                    else:
                        avg_salary = None

                    top_skills.append({
                        'skill_id': skill_id,
                        'skill_name': keyword.keyword,
                        'demand_frequency': count,
                        'average_salary': round(avg_salary, 2) if avg_salary else None,
                        'category': keyword.category
                    })

                return {
                    'industry': industry,
                    'postings_analyzed': len(postings),
                    'top_skills': top_skills,
                    'period_days': limit_days
                }

        except Exception as e:
            logger.error(f"Error analyzing industry requirements: {str(e)}")
            return {}

    def get_location_salary_insights(self, location: str, skill_id: Optional[int] = None) -> Dict:
        """
        Get salary insights for a location, optionally for a specific skill.

        Args:
            location: Location (e.g., 'San Francisco, CA')
            skill_id: Optional skill ID for location-specific salary

        Returns:
            Dictionary with location-based salary data
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import JobPostingKeyword, Keyword
            from sqlalchemy import func
            from sqlalchemy.orm import joinedload

            with app.app_context():
                # Build query with eager loading
                query = JobPostingKeyword.query.options(
                    joinedload(JobPostingKeyword.keyword)
                ).filter(
                    JobPostingKeyword.location.ilike(f"%{location}%")
                )

                if skill_id:
                    query = query.filter(JobPostingKeyword.keyword_id == skill_id)

                postings = query.all()

                if not postings:
                    return {'location': location, 'message': 'No data available'}

                # Collect salary data
                salaries = []
                for posting in postings:
                    if posting.salary_min and posting.salary_max:
                        avg = (posting.salary_min + posting.salary_max) / 2
                        salaries.append(avg)

                if salaries:
                    avg_salary = statistics.mean(salaries)
                    median_salary = statistics.median(salaries)
                    min_salary = min(salaries)
                    max_salary = max(salaries)
                else:
                    avg_salary = median_salary = min_salary = max_salary = None

                result = {
                    'location': location,
                    'postings_count': len(postings),
                    'average_salary': round(avg_salary, 2) if avg_salary else None,
                    'median_salary': round(median_salary, 2) if median_salary else None,
                    'min_salary': round(min_salary, 2) if min_salary else None,
                    'max_salary': round(max_salary, 2) if max_salary else None
                }

                # If skill-specific, add skill name (use cached keyword, no database query!)
                if skill_id and postings:
                    keyword = postings[0].keyword  # Use eagerly loaded keyword
                    if keyword:
                        result['skill_name'] = keyword.keyword

                return result

        except Exception as e:
            logger.error(f"Error analyzing location salaries: {str(e)}")
            return {}


# Global instance
_analyzer = None


def get_market_intelligence_analyzer(db=None) -> MarketIntelligenceAnalyzer:
    """Get or create the global market intelligence analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = MarketIntelligenceAnalyzer(db=db)
    return _analyzer
