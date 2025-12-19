from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from models import db, User, Analysis
from errors import NotFoundError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')

def create_success_response(message: str, data: dict = None, status_code: int = 200):
    """Create standardized success response"""
    response = {
        'status': 'success',
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data:
        response['data'] = data
    return jsonify(response), status_code

def get_current_user():
    """Get current user from JWT token"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        raise NotFoundError("User not found")
    if not user.is_active:
        raise ValidationError("Account is disabled")
    return user

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get user dashboard statistics"""
    try:
        user = get_current_user()
        
        # Get all user analyses
        analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
        
        if not analyses:
            return create_success_response(
                "Dashboard stats retrieved",
                {
                    'total_analyses': 0,
                    'average_score': 0,
                    'score_trend': [],
                    'top_missing_skills': [],
                    'recent_analyses': [],
                    'score_distribution': {
                        'excellent': 0,  # 80-100%
                        'good': 0,       # 60-79%
                        'fair': 0,       # 40-59%
                        'poor': 0        # 0-39%
                    },
                    'analyses_by_month': []
                }
            )
        
        # Calculate basic statistics
        total_analyses = len(analyses)
        avg_score = sum(a.match_score for a in analyses) / total_analyses
        
        # Score trend (last 10 analyses)
        score_trend = [{
            'date': a.created_at.isoformat(),
            'score': a.match_score,
            'job_title': a.job_title or 'Untitled',
            'analysis_id': a.id
        } for a in analyses[:10]]
        
        # Score distribution
        score_distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        for analysis in analyses:
            score = analysis.match_score
            if score >= 80:
                score_distribution['excellent'] += 1
            elif score >= 60:
                score_distribution['good'] += 1
            elif score >= 40:
                score_distribution['fair'] += 1
            else:
                score_distribution['poor'] += 1
        
        # Aggregate missing skills
        skill_counts = {}
        for analysis in analyses:
            if analysis.keywords_missing:
                for skill in analysis.keywords_missing:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_missing_skills = [
            {'skill': skill, 'count': count, 'frequency': round((count / total_analyses) * 100, 1)}
            for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Recent analyses (last 5)
        recent_analyses = [{
            'id': a.id,
            'job_title': a.job_title,
            'company_name': a.company_name,
            'match_score': a.match_score,
            'created_at': a.created_at.isoformat()
        } for a in analyses[:5]]
        
        # Analyses by month (last 12 months)
        monthly_counts = {}
        for analysis in analyses:
            month_key = analysis.created_at.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        analyses_by_month = [
            {'month': month, 'count': count}
            for month, count in sorted(monthly_counts.items())[-12:]
        ]
        
        # Improvement trend (comparing first half vs second half)
        improvement_trend = None
        if len(analyses) >= 4:
            midpoint = len(analyses) // 2
            first_half_avg = sum(a.match_score for a in analyses[midpoint:]) / midpoint
            second_half_avg = sum(a.match_score for a in analyses[:midpoint]) / midpoint
            improvement = second_half_avg - first_half_avg
            improvement_trend = {
                'improvement': round(improvement, 2),
                'trend': 'improving' if improvement > 0 else 'declining' if improvement < 0 else 'stable'
            }
        
        return create_success_response(
            "Dashboard stats retrieved successfully",
            {
                'total_analyses': total_analyses,
                'average_score': round(avg_score, 2),
                'score_trend': score_trend,
                'top_missing_skills': top_missing_skills,
                'recent_analyses': recent_analyses,
                'score_distribution': score_distribution,
                'analyses_by_month': analyses_by_month,
                'improvement_trend': improvement_trend,
                'last_analysis_date': analyses[0].created_at.isoformat() if analyses else None
            }
        )
        
    except Exception as e:
        logger.error(f"Get dashboard stats error: {e}")
        raise

@dashboard_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """Get personalized insights and recommendations"""
    try:
        user = get_current_user()
        
        # Get analyses from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_analyses = Analysis.query.filter(
            Analysis.user_id == user.id,
            Analysis.created_at >= thirty_days_ago
        ).order_by(Analysis.created_at.desc()).all()
        
        insights = []
        
        if not recent_analyses:
            insights.append({
                'type': 'encouragement',
                'title': 'Get Started',
                'message': 'Upload your first resume to get personalized insights and improve your job applications!',
                'action': 'Start analyzing'
            })
            return create_success_response(
                "Insights retrieved",
                {'insights': insights}
            )
        
        # Calculate average score for recent analyses
        recent_avg = sum(a.match_score for a in recent_analyses) / len(recent_analyses)
        
        # Score-based insights
        if recent_avg < 40:
            insights.append({
                'type': 'improvement',
                'title': 'Focus on Alignment',
                'message': f'Your recent analyses average {recent_avg:.1f}% match. Consider tailoring your resume more closely to job descriptions.',
                'action': 'Optimize resume'
            })
        elif recent_avg < 70:
            insights.append({
                'type': 'improvement',
                'title': 'Good Progress',
                'message': f'Your recent match score of {recent_avg:.1f}% shows good alignment. Small tweaks could improve your success rate.',
                'action': 'Fine-tune approach'
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Excellent Alignment',
                'message': f'Outstanding! Your recent analyses average {recent_avg:.1f}% match. Keep up the great work!',
                'action': 'Continue strategy'
            })
        
        # Skill gap insights
        all_missing_skills = []
        for analysis in recent_analyses:
            if analysis.keywords_missing:
                all_missing_skills.extend(analysis.keywords_missing)
        
        if all_missing_skills:
            skill_counts = {}
            for skill in all_missing_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            most_common_missing = max(skill_counts.items(), key=lambda x: x[1])
            if most_common_missing[1] >= len(recent_analyses) * 0.5:  # Appears in 50%+ of analyses
                insights.append({
                    'type': 'skill_gap',
                    'title': 'Common Skill Gap',
                    'message': f'"{most_common_missing[0]}" appears in {most_common_missing[1]} of your recent analyses. Consider developing this skill.',
                    'action': 'Learn skill'
                })
        
        # Activity insights
        if len(recent_analyses) >= 5:
            insights.append({
                'type': 'activity',
                'title': 'Active User',
                'message': f'Great job! You\'ve analyzed {len(recent_analyses)} resumes in the last 30 days.',
                'action': 'Keep analyzing'
            })
        elif len(recent_analyses) == 1:
            insights.append({
                'type': 'encouragement',
                'title': 'Keep Going',
                'message': 'You\'ve started your journey! Try analyzing a few more resumes to get better insights.',
                'action': 'Analyze more'
            })
        
        # Trend insights
        if len(recent_analyses) >= 3:
            scores = [a.match_score for a in recent_analyses[:3]]
            if scores[0] > scores[-1] + 10:  # Recent score is 10+ points higher
                insights.append({
                    'type': 'success',
                    'title': 'Improving Trend',
                    'message': 'Your match scores are trending upward! Your resume optimization efforts are paying off.',
                    'action': 'Continue strategy'
                })
            elif scores[0] < scores[-1] - 10:  # Recent score is 10+ points lower
                insights.append({
                    'type': 'improvement',
                    'title': 'Room for Improvement',
                    'message': 'Your recent scores have been lower. Consider revisiting your resume optimization strategy.',
                    'action': 'Review approach'
                })
        
        return create_success_response(
            "Insights retrieved successfully",
            {'insights': insights}
        )
        
    except Exception as e:
        logger.error(f"Get insights error: {e}")
        raise
