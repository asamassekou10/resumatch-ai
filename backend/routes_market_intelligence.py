"""
Market Intelligence API Routes

Provides endpoints for:
- Skill market demand analysis
- Salary trend analysis
- Skill gap analysis
- Industry-specific insights
- Location-based salary data
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

# Create blueprint
market_bp = Blueprint('market', __name__, url_prefix='/api/market')

logger = logging.getLogger(__name__)


@market_bp.route('/skills/demand', methods=['GET'])
@jwt_required()
def get_skills_market_demand():
    """
    Get market demand scores for all skills based on job postings.
    Now personalized based on user preferences.

    Query parameters:
        - limit_days: Analyze last N days (default: 90)
        - top_n: Return top N skills by demand (default: 20)
        - min_score: Minimum demand score to include (default: 0)
        - industry: Override industry filter (optional)

    Returns:
        - Skill market demand scores
        - Salary data
        - Job sources and industries
        - User's industry context
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from models import User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get parameters
        limit_days = request.args.get('limit_days', 90, type=int)
        top_n = request.args.get('top_n', 20, type=int)
        min_score = request.args.get('min_score', 0, type=float)

        # Validate parameters
        limit_days = min(max(limit_days, 7), 365)  # 7 to 365 days
        top_n = min(max(top_n, 1), 100)

        # Get user preferences for industry filter
        user = User.query.get(user_id)
        user_industry = None
        if user:
            user_industry = request.args.get('industry') or user.preferred_industry
            if not user_industry and user.detected_industries:
                user_industry = user.detected_industries[0].get('industry') if user.detected_industries else None

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)
        all_skills = analyzer.get_skill_market_demand(limit_days=limit_days, industry=user_industry)

        # Filter and sort
        filtered_skills = [
            s for s in all_skills.values()
            if s['market_demand_score'] >= min_score
        ]
        sorted_skills = sorted(
            filtered_skills,
            key=lambda x: x['market_demand_score'],
            reverse=True
        )[:top_n]

        return jsonify({
            'period_days': limit_days,
            'skills_analyzed': len(sorted_skills),
            'skills': sorted_skills,
            'top_demanded': [s['skill_name'] for s in sorted_skills[:5]],
            'industry_filter': user_industry,
            'top_skills': sorted_skills[:15]
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving market demand: {str(e)}")
        return jsonify({'error': 'Failed to retrieve market demand data'}), 500


@market_bp.route('/skills/demand/<int:skill_id>', methods=['GET'])
@jwt_required()
def get_skill_market_demand(skill_id):
    """
    Get detailed market demand data for a specific skill.

    Returns:
        - Demand score and percentage
        - Salary statistics
        - Top sources and industries
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from models import Keyword
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Verify skill exists
        keyword = Keyword.query.get(skill_id)
        if not keyword:
            return jsonify({'error': 'Skill not found'}), 404

        # Get demand data (use default 90 days for consistency)
        analyzer = get_market_intelligence_analyzer(db)
        all_demand = analyzer.get_skill_market_demand(limit_days=90)

        if skill_id not in all_demand:
            return jsonify({
                'skill_id': skill_id,
                'skill_name': keyword.keyword,
                'message': 'No market data available'
            }), 200

        return jsonify(all_demand[skill_id]), 200

    except Exception as e:
        logger.error(f"Error retrieving skill demand: {str(e)}")
        return jsonify({'error': 'Failed to retrieve demand data'}), 500


@market_bp.route('/skills/<int:skill_id>/salary-trends', methods=['GET'])
@jwt_required()
def get_salary_trends(skill_id):
    """
    Get salary trend data over time for a specific skill.

    Query parameters:
        - limit_days: Analyze last N days (default: 180)

    Returns:
        - Monthly salary statistics
        - Trend direction (increasing/decreasing/stable)
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from models import Keyword
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Verify skill exists
        keyword = Keyword.query.get(skill_id)
        if not keyword:
            return jsonify({'error': 'Skill not found'}), 404

        # Get parameters
        limit_days = request.args.get('limit_days', 180, type=int)
        limit_days = min(max(limit_days, 30), 730)  # 30 to 730 days

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)
        trends = analyzer.get_salary_trends(skill_id, limit_days=limit_days)

        if not trends or 'message' in trends:
            return jsonify({
                'skill_id': skill_id,
                'skill_name': keyword.keyword,
                'message': 'No salary data available'
            }), 200

        return jsonify(trends), 200

    except Exception as e:
        logger.error(f"Error retrieving salary trends: {str(e)}")
        return jsonify({'error': 'Failed to retrieve salary trends'}), 500


@market_bp.route('/skills/gap-analysis', methods=['POST'])
@jwt_required()
def analyze_skill_gap():
    """
    Analyze skill gap between user's resume and market demand.

    Request body:
        {
            "skills": ["Python", "Django", "PostgreSQL"],
            "job_title": "Senior Backend Engineer"  // optional
        }

    Returns:
        - Matched skills from market demand
        - Missing high-demand skills
        - Gap score (0-100)
        - Recommendations
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from app import db

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Validate input
        skills = data.get('skills', [])
        if not skills or not isinstance(skills, list):
            return jsonify({'error': 'skills must be a non-empty array'}), 400

        if len(skills) > 50:
            return jsonify({'error': 'Maximum 50 skills allowed'}), 400

        job_title = data.get('job_title')

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)
        gap_analysis = analyzer.get_skill_gap_analysis(skills, job_title=job_title)

        return jsonify({
            'user_skills': skills,
            'job_title': job_title,
            'analysis': gap_analysis
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing skill gap: {str(e)}")
        return jsonify({'error': 'Failed to analyze skill gap'}), 500


@market_bp.route('/industries/<industry>/skills', methods=['GET'])
@jwt_required()
def get_industry_skill_requirements(industry):
    """
    Get most in-demand skills for a specific industry.

    Query parameters:
        - limit_days: Analyze last N days (default: 90)

    Returns:
        - Top skills for the industry
        - Demand frequency
        - Average salaries
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Validate industry name
        if not industry or len(industry) < 2:
            return jsonify({'error': 'Industry name too short'}), 400

        # Get parameters
        limit_days = request.args.get('limit_days', 90, type=int)
        limit_days = min(max(limit_days, 7), 365)

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)
        requirements = analyzer.get_industry_skill_requirements(industry, limit_days=limit_days)

        return jsonify(requirements), 200

    except Exception as e:
        logger.error(f"Error retrieving industry requirements: {str(e)}")
        return jsonify({'error': 'Failed to retrieve industry data'}), 500


@market_bp.route('/locations/<path:location>/salaries', methods=['GET'])
@jwt_required()
def get_location_salary_insights(location):
    """
    Get salary insights for a specific location.

    Query parameters:
        - skill_id: Optional skill ID for location-specific salary data

    Returns:
        - Average, median, min, max salaries
        - Posting count
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Validate location
        if not location or len(location) < 2:
            return jsonify({'error': 'Location name too short'}), 400

        # Get optional skill_id
        skill_id = request.args.get('skill_id', type=int)

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)
        insights = analyzer.get_location_salary_insights(location, skill_id=skill_id)

        return jsonify(insights), 200

    except Exception as e:
        logger.error(f"Error retrieving location salary insights: {str(e)}")
        return jsonify({'error': 'Failed to retrieve location data'}), 500


@market_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
def get_market_dashboard_summary():
    """
    Get summary dashboard of market intelligence data.
    Now personalized based on user preferences.

    Query parameters:
        - industry: Override industry filter (optional)

    Returns:
        - Top 10 most demanded skills (filtered by user's industry if set)
        - Fastest growing skills
        - Average salaries by category
        - Market statistics
        - User's industry context
    """
    from market_intelligence_analyzer import get_market_intelligence_analyzer
    from models import User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Get user preferences
        user = User.query.get(user_id)
        user_industry = None
        detected_industries = []

        if user:
            # Use explicit preference first, then detected industries
            user_industry = request.args.get('industry') or user.preferred_industry
            detected_industries = user.detected_industries or []
            if not user_industry and detected_industries:
                # Use top detected industry
                user_industry = detected_industries[0].get('industry') if detected_industries else None

        # Get analyzer
        analyzer = get_market_intelligence_analyzer(db)

        # Get market demand with optional industry filter
        all_demand = analyzer.get_skill_market_demand(limit_days=90, industry=user_industry)

        if not all_demand:
            return jsonify({
                'message': 'No market data available',
                'timestamp': datetime.utcnow().isoformat()
            }), 200

        # Sort by demand
        sorted_skills = sorted(
            all_demand.values(),
            key=lambda x: x['market_demand_score'],
            reverse=True
        )

        # Get by category
        from models import Keyword
        categories = {}
        for skill in sorted_skills[:50]:
            cat = skill.get('skill_name', 'Unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill)

        # Get top skills
        top_skills = sorted_skills[:10]
        highest_paying = sorted_skills[:20]
        highest_paying_sorted = sorted(
            highest_paying,
            key=lambda x: x.get('average_salary') or 0,
            reverse=True
        )[:5]

        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'total_skills_analyzed': len(all_demand),
            'top_demanded_skills': top_skills,
            'highest_paying_skills': highest_paying_sorted,
            'overall_statistics': {
                'skills_with_market_data': len(all_demand),
                'average_demand_score': round(
                    sum(s['market_demand_score'] for s in all_demand.values()) / len(all_demand),
                    2
                ) if all_demand else 0
            },
            'industry_context': {
                'current_industry': user_industry,
                'detected_industries': detected_industries[:3] if detected_industries else [],
                'preferences_set': user.preferences_completed if user else False
            }
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving dashboard summary: {str(e)}")
        return jsonify({'error': 'Failed to retrieve dashboard data'}), 500


# ============== NEW: INDUSTRY MANAGEMENT ENDPOINTS ==============

@market_bp.route('/industries', methods=['GET'])
@jwt_required()
def get_all_industries():
    """
    Get list of all available industries with descriptions

    Returns:
        List of industries with metadata
    """
    try:
        from services import industry_service

        industries = industry_service.get_all_industries()
        industry_data = []

        for industry in industries:
            industry_data.append({
                'name': industry,
                'description': industry_service.get_industry_description(industry),
                'categories': industry_service.get_industry_categories(industry),
                'job_titles': industry_service.get_industry_job_titles(industry)[:5]
            })

        return jsonify({
            'industries': industry_data,
            'total': len(industry_data)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching industries: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch industries',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@market_bp.route('/user/industry', methods=['GET'])
@jwt_required()
def get_current_user_industry():
    """
    Get current user's industry preference and context

    Returns:
        User's industry information
    """
    try:
        from services import industry_service
        from models import User

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        industry = industry_service.get_user_industry(user)

        return jsonify({
            'industry': industry,
            'preferred_industry': user.preferred_industry,
            'detected_industries': user.detected_industries or [],
            'job_titles': industry_service.get_industry_job_titles(industry),
            'top_skills': industry_service.get_industry_skills(industry, 'high_demand')[:10],
            'description': industry_service.get_industry_description(industry)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user industry: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch user industry',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@market_bp.route('/user/industry', methods=['PUT'])
@jwt_required()
def update_current_user_industry():
    """
    Update user's industry preferences

    Request body:
        {
            "industry": "Technology",
            "job_titles": ["Software Engineer"],
            "location": "San Francisco, CA",
            "experience_level": "Mid"
        }

    Returns:
        Updated user profile
    """
    try:
        from services import industry_service
        from models import User
        from app import db

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Validate and update industry
        if 'industry' in data:
            if not industry_service.is_valid_industry(data['industry']):
                return jsonify({
                    'error': f'Invalid industry: {data["industry"]}',
                    'valid_industries': industry_service.get_all_industries()
                }), 400
            user.preferred_industry = data['industry']

        # Update job titles
        if 'job_titles' in data:
            user.preferred_job_titles = data['job_titles']

        # Update location
        if 'location' in data:
            user.preferred_location = data['location']

        # Update experience level
        if 'experience_level' in data:
            valid_levels = ['Entry', 'Mid', 'Senior', 'Lead', 'Executive']
            if data['experience_level'] in valid_levels:
                user.experience_level = data['experience_level']

        # Mark preferences as completed
        user.preferences_completed = True

        db.session.commit()

        logger.info(f"User {user.id} updated industry preferences to {user.preferred_industry}")

        return jsonify({
            'message': 'Industry preferences updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error updating user industry: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update industry preferences',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500


@market_bp.route('/detect-industry', methods=['POST'])
@jwt_required()
def detect_industry_from_resume():
    """
    Detect industry from resume text or job description

    Request body:
        {
            "text": "resume or job description text"
        }

    Returns:
        Detected industry with confidence
    """
    try:
        from services import industry_service

        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                'error': 'Text is required for industry detection',
                'error_type': 'INVALID_REQUEST'
            }), 400

        text = data['text']
        detected_industry = industry_service.detect_industry_from_text(text)

        return jsonify({
            'detected_industry': detected_industry,
            'confidence': 'high',
            'description': industry_service.get_industry_description(detected_industry),
            'suggested_skills': industry_service.get_industry_skills(detected_industry, 'high_demand')[:10],
            'salary_range': industry_service.get_industry_salary_range(detected_industry, 'Mid')
        }), 200

    except Exception as e:
        logger.error(f"Error detecting industry: {str(e)}")
        return jsonify({
            'error': 'Failed to detect industry',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
