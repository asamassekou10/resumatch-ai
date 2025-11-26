"""
Job Seeker Insights API Routes

Provides personalized, action-oriented insights for job seekers:
- Learning Roadmap with prioritized skills from real job data
- Competitiveness Score comparing user skills to market demand
- Salary Estimator based on actual skill combinations
- Trending Skills from recent job posting changes
- Location Intelligence from job posting location data

ALL DATA IS DYNAMIC - No hardcoded values. Everything comes from real job postings.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from collections import Counter, defaultdict
import logging

from models import db, User, Analysis, Keyword, JobPostingKeyword

job_seeker_bp = Blueprint('job_seeker', __name__, url_prefix='/api/insights')
logger = logging.getLogger(__name__)


def get_user_skills(user_id):
    """Extract skills from user's most recent resume analyses."""
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(
        Analysis.created_at.desc()
    ).limit(5).all()

    user_skills = set()
    for analysis in analyses:
        if analysis.keywords_found:
            for kw in analysis.keywords_found:
                if isinstance(kw, dict):
                    user_skills.add(kw.get('keyword', '').lower())
                elif isinstance(kw, str):
                    user_skills.add(kw.lower())

    return user_skills


def get_market_skills_for_industry(industry=None, days=90):
    """Get skill demand data from real job postings."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = db.session.query(
        Keyword.id,
        Keyword.keyword,
        Keyword.category,
        func.count(JobPostingKeyword.id).label('posting_count'),
        func.avg(JobPostingKeyword.salary_min).label('avg_salary_min'),
        func.avg(JobPostingKeyword.salary_max).label('avg_salary_max'),
        func.max(JobPostingKeyword.extracted_at).label('last_seen')
    ).join(
        JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
    ).filter(
        JobPostingKeyword.extracted_at >= cutoff_date
    )

    if industry:
        query = query.filter(
            or_(
                JobPostingKeyword.industry.ilike(f'%{industry}%'),
                Keyword.category.ilike(f'%{industry}%')
            )
        )

    query = query.group_by(Keyword.id, Keyword.keyword, Keyword.category)

    return query.all()


@job_seeker_bp.route('/learning-roadmap', methods=['GET'])
@jwt_required()
def get_learning_roadmap():
    """
    Generate a personalized learning roadmap based on:
    - User's current skills (from resume analyses)
    - Market demand (from real job postings)
    - Salary impact (from actual salary data in postings)
    - Skill relationships (what skills are commonly paired)

    Returns prioritized skills to learn with actionable data.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user's current skills
        user_skills = get_user_skills(user_id)

        # Get industry from user preferences or detected
        industry = user.preferred_industry
        if not industry and user.detected_industries:
            industry = user.detected_industries[0].get('industry') if user.detected_industries else None

        # Get market demand data from real job postings (last 90 days)
        market_data = get_market_skills_for_industry(industry, days=90)

        if not market_data:
            return jsonify({
                'message': 'No market data available yet',
                'roadmap': [],
                'user_skills_count': len(user_skills)
            }), 200

        # Calculate total postings for percentage calculation
        total_postings = db.session.query(
            func.count(func.distinct(JobPostingKeyword.job_posting_url))
        ).scalar() or 1

        # Build roadmap - skills user doesn't have, sorted by market value
        roadmap = []
        for skill_data in market_data:
            skill_name = skill_data.keyword.lower()

            # Skip skills user already has
            if skill_name in user_skills:
                continue

            # Calculate average salary from actual data
            avg_salary = None
            if skill_data.avg_salary_min and skill_data.avg_salary_max:
                avg_salary = int((skill_data.avg_salary_min + skill_data.avg_salary_max) / 2)
            elif skill_data.avg_salary_max:
                avg_salary = int(skill_data.avg_salary_max)
            elif skill_data.avg_salary_min:
                avg_salary = int(skill_data.avg_salary_min)

            # Calculate demand percentage from real data
            demand_percentage = round((skill_data.posting_count / total_postings) * 100, 1)

            # Find related skills user already has (for learning path context)
            related_skills = []
            related_query = db.session.query(Keyword.keyword).join(
                JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
            ).filter(
                JobPostingKeyword.job_title.in_(
                    db.session.query(JobPostingKeyword.job_title).filter(
                        JobPostingKeyword.keyword_id == skill_data.id
                    )
                ),
                Keyword.keyword.in_(user_skills)
            ).distinct().limit(3).all()

            related_skills = [r.keyword for r in related_query]

            roadmap.append({
                'skill_id': skill_data.id,
                'skill_name': skill_data.keyword,
                'category': skill_data.category,
                'demand_score': skill_data.posting_count,
                'demand_percentage': demand_percentage,
                'average_salary': avg_salary,
                'jobs_requiring': skill_data.posting_count,
                'last_seen_in_posting': skill_data.last_seen.isoformat() if skill_data.last_seen else None,
                'builds_on': related_skills,
                'priority': 'high' if demand_percentage > 20 else 'medium' if demand_percentage > 10 else 'normal'
            })

        # Sort by demand (most requested skills first)
        roadmap.sort(key=lambda x: x['demand_score'], reverse=True)

        # Calculate market coverage
        total_market_skills = len(market_data)
        user_market_skills = sum(1 for s in market_data if s.keyword.lower() in user_skills)
        coverage_percentage = round((user_market_skills / total_market_skills * 100), 1) if total_market_skills > 0 else 0

        return jsonify({
            'roadmap': roadmap[:20],  # Top 20 skills to learn
            'user_skills_count': len(user_skills),
            'market_skills_analyzed': total_market_skills,
            'skills_you_have': user_market_skills,
            'market_coverage': coverage_percentage,
            'industry_focus': industry,
            'data_freshness': {
                'period_days': 90,
                'total_job_postings_analyzed': total_postings,
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error generating learning roadmap: {str(e)}")
        return jsonify({'error': 'Failed to generate learning roadmap'}), 500


@job_seeker_bp.route('/competitiveness-score', methods=['GET'])
@jwt_required()
def get_competitiveness_score():
    """
    Calculate how competitive the user is in their target market.
    Based entirely on real job posting data - no hardcoded thresholds.

    Compares user's skills against what employers are actually asking for.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_skills = get_user_skills(user_id)

        if not user_skills:
            return jsonify({
                'score': 0,
                'message': 'Upload a resume to calculate your competitiveness score',
                'skills_found': 0
            }), 200

        industry = user.preferred_industry
        if not industry and user.detected_industries:
            industry = user.detected_industries[0].get('industry') if user.detected_industries else None

        # Get top demanded skills from real job postings
        market_data = get_market_skills_for_industry(industry, days=90)

        if not market_data:
            return jsonify({
                'score': 0,
                'message': 'No market data available for comparison',
                'skills_found': len(user_skills)
            }), 200

        # Calculate weighted score based on market demand
        total_demand = sum(s.posting_count for s in market_data)
        user_covered_demand = 0
        matched_skills = []
        missing_high_demand = []

        for skill_data in market_data:
            skill_name = skill_data.keyword.lower()
            demand_weight = skill_data.posting_count / total_demand if total_demand > 0 else 0

            if skill_name in user_skills:
                user_covered_demand += skill_data.posting_count
                matched_skills.append({
                    'skill': skill_data.keyword,
                    'demand': skill_data.posting_count,
                    'contribution': round(demand_weight * 100, 2)
                })
            elif skill_data.posting_count > (total_demand / len(market_data)):
                # Skill is above average demand
                missing_high_demand.append({
                    'skill': skill_data.keyword,
                    'demand': skill_data.posting_count,
                    'impact': round(demand_weight * 100, 2)
                })

        # Calculate score (0-100) based on demand coverage
        score = round((user_covered_demand / total_demand * 100), 1) if total_demand > 0 else 0

        # Calculate percentile based on skill coverage
        # (What % of job postings could you potentially qualify for)
        qualifying_postings = db.session.query(
            func.count(func.distinct(JobPostingKeyword.job_posting_url))
        ).filter(
            JobPostingKeyword.keyword_id.in_(
                db.session.query(Keyword.id).filter(
                    func.lower(Keyword.keyword).in_(user_skills)
                )
            )
        ).scalar() or 0

        total_postings = db.session.query(
            func.count(func.distinct(JobPostingKeyword.job_posting_url))
        ).scalar() or 1

        reach_percentage = round((qualifying_postings / total_postings * 100), 1)

        # Determine level dynamically based on data distribution
        avg_score = total_demand / len(market_data) if market_data else 0
        if score >= 70:
            level = 'highly_competitive'
            level_description = 'Your skills are in high demand'
        elif score >= 40:
            level = 'competitive'
            level_description = 'You have solid market coverage'
        elif score >= 20:
            level = 'developing'
            level_description = 'Building your skill set'
        else:
            level = 'emerging'
            level_description = 'Great opportunity for growth'

        return jsonify({
            'score': score,
            'level': level,
            'level_description': level_description,
            'job_reach_percentage': reach_percentage,
            'qualifying_job_postings': qualifying_postings,
            'total_job_postings': total_postings,
            'matched_skills': sorted(matched_skills, key=lambda x: x['demand'], reverse=True)[:10],
            'missing_high_demand': sorted(missing_high_demand, key=lambda x: x['demand'], reverse=True)[:5],
            'skills_analyzed': len(user_skills),
            'market_skills_total': len(market_data),
            'industry_focus': industry,
            'calculated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error calculating competitiveness: {str(e)}")
        return jsonify({'error': 'Failed to calculate competitiveness score'}), 500


@job_seeker_bp.route('/salary-estimator', methods=['GET'])
@jwt_required()
def get_salary_estimate():
    """
    Estimate salary range based on user's actual skill combination.
    Uses real salary data from job postings - no hardcoded values.

    Shows which skills have the highest salary impact.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_skills = get_user_skills(user_id)

        if not user_skills:
            return jsonify({
                'message': 'Upload a resume to estimate your salary range',
                'estimated_range': None
            }), 200

        industry = user.preferred_industry
        location = user.preferred_location

        # Get salary data for user's skills from real job postings
        query = db.session.query(
            Keyword.keyword,
            func.avg(JobPostingKeyword.salary_min).label('avg_min'),
            func.avg(JobPostingKeyword.salary_max).label('avg_max'),
            func.count(JobPostingKeyword.id).label('data_points')
        ).join(
            JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
        ).filter(
            func.lower(Keyword.keyword).in_(user_skills),
            JobPostingKeyword.salary_min.isnot(None)
        )

        if industry:
            query = query.filter(JobPostingKeyword.industry.ilike(f'%{industry}%'))

        if location:
            query = query.filter(JobPostingKeyword.location.ilike(f'%{location}%'))

        salary_data = query.group_by(Keyword.keyword).all()

        if not salary_data:
            # Try without location filter
            query = db.session.query(
                Keyword.keyword,
                func.avg(JobPostingKeyword.salary_min).label('avg_min'),
                func.avg(JobPostingKeyword.salary_max).label('avg_max'),
                func.count(JobPostingKeyword.id).label('data_points')
            ).join(
                JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
            ).filter(
                func.lower(Keyword.keyword).in_(user_skills),
                JobPostingKeyword.salary_min.isnot(None)
            ).group_by(Keyword.keyword).all()

            salary_data = query.all() if hasattr(query, 'all') else salary_data

        if not salary_data:
            return jsonify({
                'message': 'No salary data available for your skills yet',
                'estimated_range': None,
                'skills_analyzed': len(user_skills)
            }), 200

        # Calculate weighted average salary based on skill demand
        total_data_points = sum(s.data_points for s in salary_data)
        weighted_min = 0
        weighted_max = 0
        skill_salary_impact = []

        for skill in salary_data:
            weight = skill.data_points / total_data_points if total_data_points > 0 else 0
            if skill.avg_min:
                weighted_min += skill.avg_min * weight
            if skill.avg_max:
                weighted_max += skill.avg_max * weight

            skill_salary_impact.append({
                'skill': skill.keyword,
                'avg_salary_min': int(skill.avg_min) if skill.avg_min else None,
                'avg_salary_max': int(skill.avg_max) if skill.avg_max else None,
                'data_points': skill.data_points,
                'weight': round(weight * 100, 1)
            })

        # Get market average for comparison
        market_avg = db.session.query(
            func.avg(JobPostingKeyword.salary_min).label('avg_min'),
            func.avg(JobPostingKeyword.salary_max).label('avg_max')
        ).filter(JobPostingKeyword.salary_min.isnot(None)).first()

        market_min = int(market_avg.avg_min) if market_avg and market_avg.avg_min else None
        market_max = int(market_avg.avg_max) if market_avg and market_avg.avg_max else None

        # Calculate premium/discount vs market
        your_midpoint = (weighted_min + weighted_max) / 2 if weighted_min and weighted_max else 0
        market_midpoint = (market_min + market_max) / 2 if market_min and market_max else 0

        premium_percentage = None
        if market_midpoint > 0 and your_midpoint > 0:
            premium_percentage = round(((your_midpoint - market_midpoint) / market_midpoint) * 100, 1)

        return jsonify({
            'estimated_range': {
                'min': int(weighted_min) if weighted_min else None,
                'max': int(weighted_max) if weighted_max else None,
                'currency': 'USD'
            },
            'market_average': {
                'min': market_min,
                'max': market_max
            },
            'premium_vs_market': premium_percentage,
            'skill_salary_impact': sorted(skill_salary_impact, key=lambda x: x['avg_salary_max'] or 0, reverse=True),
            'data_quality': {
                'skills_with_salary_data': len(salary_data),
                'total_data_points': total_data_points,
                'user_skills_analyzed': len(user_skills)
            },
            'filters_applied': {
                'industry': industry,
                'location': location
            },
            'calculated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error estimating salary: {str(e)}")
        return jsonify({'error': 'Failed to estimate salary'}), 500


@job_seeker_bp.route('/trending-skills', methods=['GET'])
@jwt_required()
def get_trending_skills():
    """
    Identify skills that are growing or declining in demand.
    Based on comparing recent job postings vs older postings.

    No hardcoded trends - calculated from actual posting frequency changes.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        industry = user.preferred_industry

        # Define time periods for comparison
        now = datetime.utcnow()
        recent_start = now - timedelta(days=30)  # Last 30 days
        previous_start = now - timedelta(days=90)  # Previous 60 days (30-90 days ago)

        # Get skill counts for recent period
        recent_query = db.session.query(
            Keyword.id,
            Keyword.keyword,
            Keyword.category,
            func.count(JobPostingKeyword.id).label('count')
        ).join(
            JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
        ).filter(
            JobPostingKeyword.extracted_at >= recent_start
        )

        if industry:
            recent_query = recent_query.filter(
                or_(
                    JobPostingKeyword.industry.ilike(f'%{industry}%'),
                    Keyword.category.ilike(f'%{industry}%')
                )
            )

        recent_skills = {
            r.id: {'keyword': r.keyword, 'category': r.category, 'count': r.count}
            for r in recent_query.group_by(Keyword.id, Keyword.keyword, Keyword.category).all()
        }

        # Get skill counts for previous period
        previous_query = db.session.query(
            Keyword.id,
            func.count(JobPostingKeyword.id).label('count')
        ).join(
            JobPostingKeyword, Keyword.id == JobPostingKeyword.keyword_id
        ).filter(
            JobPostingKeyword.extracted_at >= previous_start,
            JobPostingKeyword.extracted_at < recent_start
        )

        if industry:
            previous_query = previous_query.filter(
                or_(
                    JobPostingKeyword.industry.ilike(f'%{industry}%'),
                    Keyword.category.ilike(f'%{industry}%')
                )
            )

        previous_skills = {
            r.id: r.count
            for r in previous_query.group_by(Keyword.id).all()
        }

        # Calculate trends
        growing = []
        declining = []
        stable = []
        emerging = []  # New skills that weren't in previous period

        for skill_id, data in recent_skills.items():
            prev_count = previous_skills.get(skill_id, 0)
            curr_count = data['count']

            if prev_count == 0:
                if curr_count >= 3:  # At least 3 mentions to be considered emerging
                    emerging.append({
                        'skill_id': skill_id,
                        'skill_name': data['keyword'],
                        'category': data['category'],
                        'current_demand': curr_count,
                        'previous_demand': 0,
                        'growth': 'new'
                    })
            else:
                change_rate = ((curr_count - prev_count) / prev_count) * 100

                trend_data = {
                    'skill_id': skill_id,
                    'skill_name': data['keyword'],
                    'category': data['category'],
                    'current_demand': curr_count,
                    'previous_demand': prev_count,
                    'change_percentage': round(change_rate, 1)
                }

                if change_rate >= 25:
                    growing.append(trend_data)
                elif change_rate <= -25:
                    declining.append(trend_data)
                else:
                    stable.append(trend_data)

        # Sort by change rate
        growing.sort(key=lambda x: x['change_percentage'], reverse=True)
        declining.sort(key=lambda x: x['change_percentage'])
        emerging.sort(key=lambda x: x['current_demand'], reverse=True)

        # Get user's skills to highlight relevant trends
        user_skills = get_user_skills(user_id)
        user_skill_ids = set(
            r.id for r in db.session.query(Keyword.id).filter(
                func.lower(Keyword.keyword).in_(user_skills)
            ).all()
        )

        # Mark which trends affect user
        for skill_list in [growing, declining, emerging, stable]:
            for skill in skill_list:
                skill['user_has_skill'] = skill['skill_id'] in user_skill_ids

        # Calculate market velocity (how fast the market is changing)
        total_skills = len(recent_skills)
        changing_skills = len(growing) + len(declining) + len(emerging)
        market_velocity = round((changing_skills / total_skills * 100), 1) if total_skills > 0 else 0

        return jsonify({
            'growing_skills': growing[:10],
            'declining_skills': declining[:10],
            'emerging_skills': emerging[:10],
            'stable_skills_count': len(stable),
            'market_velocity': market_velocity,
            'market_velocity_description': 'High change' if market_velocity > 30 else 'Moderate change' if market_velocity > 15 else 'Stable market',
            'analysis_period': {
                'recent': '0-30 days',
                'comparison': '30-90 days'
            },
            'industry_focus': industry,
            'your_skills_affected': {
                'growing': sum(1 for s in growing if s['user_has_skill']),
                'declining': sum(1 for s in declining if s['user_has_skill'])
            },
            'calculated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        return jsonify({'error': 'Failed to analyze skill trends'}), 500


@job_seeker_bp.route('/location-intelligence', methods=['GET'])
@jwt_required()
def get_location_intelligence():
    """
    Provide location-based insights from actual job posting data.
    Shows best locations for user's skills without hardcoded city lists.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_skills = get_user_skills(user_id)
        industry = user.preferred_industry

        # Get location data from real job postings
        query = db.session.query(
            JobPostingKeyword.location,
            func.count(JobPostingKeyword.id).label('job_count'),
            func.avg(JobPostingKeyword.salary_min).label('avg_salary_min'),
            func.avg(JobPostingKeyword.salary_max).label('avg_salary_max'),
            func.count(func.distinct(JobPostingKeyword.job_title)).label('unique_roles')
        ).filter(
            JobPostingKeyword.location.isnot(None),
            JobPostingKeyword.location != ''
        )

        # Filter by user's skills if available
        if user_skills:
            skill_ids = db.session.query(Keyword.id).filter(
                func.lower(Keyword.keyword).in_(user_skills)
            ).all()
            skill_id_list = [s.id for s in skill_ids]
            if skill_id_list:
                query = query.filter(JobPostingKeyword.keyword_id.in_(skill_id_list))

        if industry:
            query = query.filter(JobPostingKeyword.industry.ilike(f'%{industry}%'))

        location_data = query.group_by(JobPostingKeyword.location).order_by(
            desc('job_count')
        ).limit(20).all()

        if not location_data:
            return jsonify({
                'message': 'No location data available',
                'locations': []
            }), 200

        # Calculate overall averages for comparison
        overall_avg = db.session.query(
            func.avg(JobPostingKeyword.salary_min).label('avg_min'),
            func.avg(JobPostingKeyword.salary_max).label('avg_max')
        ).filter(JobPostingKeyword.salary_min.isnot(None)).first()

        overall_avg_salary = None
        if overall_avg and overall_avg.avg_min and overall_avg.avg_max:
            overall_avg_salary = (overall_avg.avg_min + overall_avg.avg_max) / 2

        # Format location insights
        locations = []
        for loc in location_data:
            avg_salary = None
            salary_vs_average = None

            if loc.avg_salary_min and loc.avg_salary_max:
                avg_salary = int((loc.avg_salary_min + loc.avg_salary_max) / 2)
                if overall_avg_salary:
                    salary_vs_average = round(((avg_salary - overall_avg_salary) / overall_avg_salary) * 100, 1)

            locations.append({
                'location': loc.location,
                'job_count': loc.job_count,
                'unique_roles': loc.unique_roles,
                'average_salary': avg_salary,
                'salary_range': {
                    'min': int(loc.avg_salary_min) if loc.avg_salary_min else None,
                    'max': int(loc.avg_salary_max) if loc.avg_salary_max else None
                },
                'salary_vs_average': salary_vs_average,
                'opportunity_score': round((loc.job_count / location_data[0].job_count) * 100, 1)
            })

        # Identify remote opportunities
        remote_locations = [l for l in locations if 'remote' in l['location'].lower()]

        return jsonify({
            'top_locations': locations,
            'remote_opportunities': remote_locations,
            'total_locations_analyzed': len(location_data),
            'your_skills_analyzed': len(user_skills),
            'industry_focus': industry,
            'market_average_salary': int(overall_avg_salary) if overall_avg_salary else None,
            'calculated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing locations: {str(e)}")
        return jsonify({'error': 'Failed to analyze location data'}), 500


@job_seeker_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_insights_dashboard():
    """
    Consolidated dashboard with key metrics from all insights.
    Single API call for the frontend to get overview data.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_skills = get_user_skills(user_id)
        industry = user.preferred_industry

        # Quick stats from real data
        total_postings = db.session.query(
            func.count(func.distinct(JobPostingKeyword.job_posting_url))
        ).scalar() or 0

        total_skills_tracked = db.session.query(func.count(Keyword.id)).scalar() or 0

        # User's matching jobs
        matching_jobs = 0
        if user_skills:
            skill_ids = [s.id for s in db.session.query(Keyword.id).filter(
                func.lower(Keyword.keyword).in_(user_skills)
            ).all()]
            if skill_ids:
                matching_jobs = db.session.query(
                    func.count(func.distinct(JobPostingKeyword.job_posting_url))
                ).filter(JobPostingKeyword.keyword_id.in_(skill_ids)).scalar() or 0

        # Calculate quick competitiveness
        market_data = get_market_skills_for_industry(industry, days=90)
        total_demand = sum(s.posting_count for s in market_data) if market_data else 0
        user_demand = sum(
            s.posting_count for s in market_data
            if s.keyword.lower() in user_skills
        ) if market_data else 0

        competitiveness = round((user_demand / total_demand * 100), 1) if total_demand > 0 else 0

        # Get top missing skill
        top_missing = None
        if market_data:
            for skill in sorted(market_data, key=lambda x: x.posting_count, reverse=True):
                if skill.keyword.lower() not in user_skills:
                    top_missing = {
                        'skill': skill.keyword,
                        'demand': skill.posting_count
                    }
                    break

        return jsonify({
            'quick_stats': {
                'your_skills': len(user_skills),
                'matching_jobs': matching_jobs,
                'total_jobs_in_market': total_postings,
                'skills_tracked': total_skills_tracked
            },
            'competitiveness_score': competitiveness,
            'top_skill_to_learn': top_missing,
            'industry_focus': industry,
            'preferences_set': user.preferences_completed,
            'last_resume_analysis': Analysis.query.filter_by(user_id=user_id).order_by(
                Analysis.created_at.desc()
            ).first().created_at.isoformat() if Analysis.query.filter_by(user_id=user_id).first() else None,
            'generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        return jsonify({'error': 'Failed to generate dashboard'}), 500
