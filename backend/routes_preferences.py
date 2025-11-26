"""
User Preferences API Routes
Handles user market preferences for personalized job market insights
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
import logging

preferences_bp = Blueprint('preferences', __name__)
logger = logging.getLogger(__name__)

# Available industries for selection
INDUSTRIES = [
    'Technology',
    'Healthcare',
    'Finance',
    'Security',
    'Marketing',
    'Sales',
    'Human Resources',
    'Education',
    'Manufacturing',
    'Retail',
    'Hospitality',
    'Construction',
    'Transportation',
    'Legal',
    'Government',
    'Non-Profit',
    'Media & Entertainment',
    'Real Estate',
    'Energy',
    'Agriculture',
    'Other'
]

# Experience levels
EXPERIENCE_LEVELS = [
    'Entry Level (0-2 years)',
    'Mid Level (3-5 years)',
    'Senior Level (6-10 years)',
    'Executive (10+ years)'
]

# Industry keyword mapping for auto-detection
INDUSTRY_KEYWORDS = {
    'Technology': ['software', 'developer', 'engineer', 'programming', 'coding', 'devops', 'cloud', 'data', 'machine learning', 'ai', 'web', 'mobile', 'database', 'api', 'frontend', 'backend', 'fullstack', 'python', 'java', 'javascript'],
    'Healthcare': ['nurse', 'doctor', 'medical', 'hospital', 'patient', 'clinical', 'pharmacy', 'healthcare', 'health', 'dental', 'therapy', 'diagnosis', 'treatment', 'emt', 'paramedic'],
    'Security': ['security', 'cybersecurity', 'penetration', 'vulnerability', 'firewall', 'encryption', 'compliance', 'risk', 'threat', 'incident', 'soc', 'siem', 'forensics', 'malware'],
    'Finance': ['finance', 'accounting', 'banking', 'investment', 'trading', 'audit', 'tax', 'financial', 'budget', 'portfolio', 'risk management', 'compliance', 'cpa', 'cfa'],
    'Marketing': ['marketing', 'seo', 'social media', 'content', 'brand', 'advertising', 'digital marketing', 'campaign', 'analytics', 'email marketing', 'ppc', 'growth'],
    'Sales': ['sales', 'account executive', 'business development', 'lead generation', 'crm', 'pipeline', 'quota', 'revenue', 'customer', 'negotiation', 'closing'],
    'Human Resources': ['hr', 'human resources', 'recruiting', 'talent', 'onboarding', 'benefits', 'payroll', 'employee', 'training', 'performance', 'compensation'],
    'Education': ['teacher', 'professor', 'education', 'curriculum', 'instruction', 'student', 'academic', 'school', 'university', 'training', 'learning'],
    'Manufacturing': ['manufacturing', 'production', 'assembly', 'quality control', 'lean', 'six sigma', 'supply chain', 'logistics', 'warehouse', 'inventory'],
    'Legal': ['attorney', 'lawyer', 'legal', 'paralegal', 'litigation', 'contract', 'compliance', 'regulatory', 'court', 'law firm'],
    'Government': ['government', 'public sector', 'federal', 'state', 'municipal', 'policy', 'administration', 'civil service'],
}


@preferences_bp.route('/api/user/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get current user's market preferences"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'preferred_industry': user.preferred_industry,
        'preferred_job_titles': user.preferred_job_titles or [],
        'preferred_location': user.preferred_location,
        'experience_level': user.experience_level,
        'preferences_completed': user.preferences_completed,
        'detected_industries': user.detected_industries or [],
        'available_industries': INDUSTRIES,
        'available_experience_levels': EXPERIENCE_LEVELS
    }), 200


@preferences_bp.route('/api/user/preferences', methods=['POST', 'PUT'])
@jwt_required()
def update_preferences():
    """Update user's market preferences"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Update preferences
    if 'preferred_industry' in data:
        user.preferred_industry = data['preferred_industry']

    if 'preferred_job_titles' in data:
        # Ensure it's a list
        titles = data['preferred_job_titles']
        if isinstance(titles, str):
            titles = [t.strip() for t in titles.split(',') if t.strip()]
        user.preferred_job_titles = titles

    if 'preferred_location' in data:
        user.preferred_location = data['preferred_location']

    if 'experience_level' in data:
        user.experience_level = data['experience_level']

    # Mark preferences as completed
    user.preferences_completed = True

    try:
        db.session.commit()
        logger.info(f"User {user_id} updated preferences: industry={user.preferred_industry}")

        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': {
                'preferred_industry': user.preferred_industry,
                'preferred_job_titles': user.preferred_job_titles or [],
                'preferred_location': user.preferred_location,
                'experience_level': user.experience_level,
                'preferences_completed': user.preferences_completed
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update preferences for user {user_id}: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500


@preferences_bp.route('/api/user/preferences/skip', methods=['POST'])
@jwt_required()
def skip_preferences():
    """Skip preference setup (use auto-detection instead)"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Mark as completed but don't set specific preferences
    # Will rely on detected_industries from resume analysis
    user.preferences_completed = True

    try:
        db.session.commit()
        return jsonify({
            'message': 'Preference setup skipped. Market insights will be based on your resume content.',
            'preferences_completed': True
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to skip preferences'}), 500


@preferences_bp.route('/api/user/preferences/reset', methods=['POST'])
@jwt_required()
def reset_preferences():
    """Reset user preferences to show questionnaire again"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.preferred_industry = None
    user.preferred_job_titles = []
    user.preferred_location = None
    user.experience_level = None
    user.preferences_completed = False

    try:
        db.session.commit()
        return jsonify({'message': 'Preferences reset successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset preferences'}), 500


@preferences_bp.route('/api/preferences/industries', methods=['GET'])
def get_industries():
    """Get list of available industries"""
    return jsonify({
        'industries': INDUSTRIES,
        'experience_levels': EXPERIENCE_LEVELS
    }), 200


def detect_industry_from_text(text):
    """
    Detect industry from resume or job description text.
    Returns a list of detected industries with confidence scores.
    """
    if not text:
        return []

    text_lower = text.lower()
    industry_scores = {}

    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = 0
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 1
                matched_keywords.append(keyword)

        if score > 0:
            industry_scores[industry] = {
                'score': score,
                'matched_keywords': matched_keywords,
                'confidence': min(score / 5, 1.0)  # Normalize to 0-1
            }

    # Sort by score and return top industries
    sorted_industries = sorted(
        industry_scores.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )

    return [
        {
            'industry': ind,
            'confidence': data['confidence'],
            'matched_keywords': data['matched_keywords'][:5]  # Top 5 keywords
        }
        for ind, data in sorted_industries[:3]  # Top 3 industries
    ]


def update_user_detected_industries(user_id, detected):
    """Update user's detected industries based on resume analysis"""
    try:
        user = User.query.get(user_id)
        if not user:
            return

        current = user.detected_industries or []

        # Add new detections
        for detection in detected:
            industry = detection['industry']
            if industry not in [d.get('industry') for d in current]:
                current.append(detection)

        # Keep only top 5 most confident detections
        current = sorted(current, key=lambda x: x.get('confidence', 0), reverse=True)[:5]

        user.detected_industries = current
        db.session.commit()

        logger.info(f"Updated detected industries for user {user_id}: {[d['industry'] for d in current]}")

    except Exception as e:
        logger.error(f"Failed to update detected industries: {str(e)}")
        db.session.rollback()
