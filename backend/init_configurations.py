"""
Initialize default system configurations in the database.

Run this after creating the database to populate default values.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from datetime import datetime


def init_system_configurations():
    """Initialize SystemConfiguration table with defaults"""
    with app.app_context():
        from models import SystemConfiguration
        # File size limits (consolidated)
        configs = [
            {
                'config_key': 'max_file_size_mb',
                'config_value': 16,
                'data_type': 'int',
                'category': 'file',
                'description': 'Maximum file size in MB (used by free tier)'
            },
            {
                'config_key': 'allowed_file_extensions',
                'config_value': ['pdf', 'docx', 'txt'],
                'data_type': 'json',
                'category': 'file',
                'description': 'Allowed file extensions'
            },
            # Password validation (now configurable)
            {
                'config_key': 'password_min_length',
                'config_value': 8,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Minimum password length'
            },
            {
                'config_key': 'password_require_uppercase',
                'config_value': True,
                'data_type': 'bool',
                'category': 'validation',
                'description': 'Require uppercase letter in password'
            },
            {
                'config_key': 'password_require_special_chars',
                'config_value': True,
                'data_type': 'bool',
                'category': 'validation',
                'description': 'Require special characters in password'
            },
            # Text validation limits
            {
                'config_key': 'max_text_length',
                'config_value': 50000,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Maximum text input length'
            },
            {
                'config_key': 'job_description_min_length',
                'config_value': 50,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Minimum job description length'
            },
            {
                'config_key': 'job_description_max_length',
                'config_value': 10000,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Maximum job description length'
            },
            {
                'config_key': 'job_title_max_length',
                'config_value': 200,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Maximum job title length'
            },
            {
                'config_key': 'company_name_max_length',
                'config_value': 200,
                'data_type': 'int',
                'category': 'validation',
                'description': 'Maximum company name length'
            },
            # Email configuration
            {
                'config_key': 'email_verification_expires_hours',
                'config_value': 24,
                'data_type': 'int',
                'category': 'email',
                'description': 'Email verification token expiration in hours'
            },
            {
                'config_key': 'from_email',
                'config_value': os.getenv('FROM_EMAIL', 'noreply@resumatch-ai.com'),
                'data_type': 'string',
                'category': 'email',
                'description': 'Sender email address'
            },
            # AI Configuration
            {
                'config_key': 'gemini_model',
                'config_value': 'models/gemini-2.5-flash',
                'data_type': 'string',
                'category': 'ai',
                'description': 'Gemini AI model to use'
            },
            {
                'config_key': 'max_ai_retries',
                'config_value': 3,
                'data_type': 'int',
                'category': 'ai',
                'description': 'Maximum retries for AI API calls'
            },
            {
                'config_key': 'ai_retry_delay_seconds',
                'config_value': 1,
                'data_type': 'int',
                'category': 'ai',
                'description': 'Retry delay for AI API calls'
            },
            # Resume excerpt limits for AI processing
            {
                'config_key': 'ai_resume_excerpt_length',
                'config_value': 2000,
                'data_type': 'int',
                'category': 'ai',
                'description': 'Maximum resume text length sent to AI for analysis'
            },
            {
                'config_key': 'ai_job_description_excerpt_length',
                'config_value': 1500,
                'data_type': 'int',
                'category': 'ai',
                'description': 'Maximum job description length sent to AI for analysis'
            },
            # JWT Configuration
            {
                'config_key': 'jwt_token_expires_days',
                'config_value': 7,
                'data_type': 'int',
                'category': 'security',
                'description': 'JWT token expiration in days'
            },
            # Analytics
            {
                'config_key': 'analytics_lookback_days',
                'config_value': 30,
                'data_type': 'int',
                'category': 'analytics',
                'description': 'Default lookback period for analytics in days'
            },
        ]

        for config_data in configs:
            existing = SystemConfiguration.query.filter_by(
                config_key=config_data['config_key']
            ).first()

            if not existing:
                config = SystemConfiguration(**config_data)
                db.session.add(config)
                print(f"✓ Created config: {config_data['config_key']}")
            else:
                print(f"  Skipped (exists): {config_data['config_key']}")

        db.session.commit()
        print(f"\n✓ System configurations initialized!")


def init_subscription_tiers():
    """Initialize default subscription tiers"""
    with app.app_context():
        from models import SubscriptionTier
        tiers = [
            {
                'name': 'free',
                'display_name': 'Free Plan',
                'description': 'Perfect for getting started with resume analysis',
                'monthly_credits': 0,
                'price_cents': 0,
                'max_file_size_mb': 5,
                'max_analyses_per_month': 5,
                'max_concurrent_uploads': 1,
                'features': {
                    'ai_feedback': False,
                    'optimization': False,
                    'cover_letter': False,
                    'skill_suggestions': False,
                    'basic_analysis': True
                },
                'rate_limits': {
                    'resume_analysis': '10 per hour',
                    'feedback': '0 per hour',
                    'optimization': '0 per hour'
                },
                'position': 1
            },
            {
                'name': 'pro',
                'display_name': 'Pro Plan',
                'description': 'Unlock advanced AI features and unlimited analyses',
                'monthly_credits': 20,
                'price_cents': 1999,  # $19.99
                'stripe_price_id': os.getenv('STRIPE_PRO_PRICE_ID', ''),
                'max_file_size_mb': 16,
                'max_analyses_per_month': 100,
                'max_concurrent_uploads': 5,
                'features': {
                    'ai_feedback': True,
                    'optimization': True,
                    'cover_letter': True,
                    'skill_suggestions': True,
                    'basic_analysis': True,
                    'priority_support': False
                },
                'rate_limits': {
                    'resume_analysis': '50 per hour',
                    'feedback': '5 per hour',
                    'optimization': '5 per hour',
                    'cover_letter': '5 per hour'
                },
                'position': 2
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise',
                'description': 'Custom solutions for large teams',
                'monthly_credits': 1000,
                'price_cents': 0,  # Custom pricing
                'max_file_size_mb': 100,
                'max_analyses_per_month': 10000,
                'max_concurrent_uploads': 20,
                'features': {
                    'ai_feedback': True,
                    'optimization': True,
                    'cover_letter': True,
                    'skill_suggestions': True,
                    'basic_analysis': True,
                    'priority_support': True,
                    'api_access': True,
                    'custom_integration': True
                },
                'rate_limits': {
                    'resume_analysis': 'unlimited',
                    'feedback': 'unlimited',
                    'optimization': 'unlimited',
                    'cover_letter': 'unlimited'
                },
                'position': 3
            }
        ]

        for tier_data in tiers:
            existing = SubscriptionTier.query.filter_by(name=tier_data['name']).first()

            if not existing:
                tier = SubscriptionTier(**tier_data)
                db.session.add(tier)
                print(f"✓ Created tier: {tier_data['name']}")
            else:
                print(f"  Skipped (exists): {tier_data['name']}")

        db.session.commit()
        print(f"\n✓ Subscription tiers initialized!")


def init_rate_limits():
    """Initialize default rate limit configurations"""
    with app.app_context():
        from models import RateLimitConfig
        rate_limits = [
            # Free tier
            {'operation': 'resume_analysis', 'subscription_tier': 'free', 'requests_per_hour': 2, 'requests_per_day': 5, 'cost_in_credits': 0},
            {'operation': 'feedback', 'subscription_tier': 'free', 'requests_per_hour': 0, 'requests_per_day': 0, 'cost_in_credits': 0},
            {'operation': 'optimization', 'subscription_tier': 'free', 'requests_per_hour': 0, 'requests_per_day': 0, 'cost_in_credits': 0},
            {'operation': 'cover_letter', 'subscription_tier': 'free', 'requests_per_hour': 0, 'requests_per_day': 0, 'cost_in_credits': 0},
            {'operation': 'skill_suggestions', 'subscription_tier': 'free', 'requests_per_hour': 0, 'requests_per_day': 0, 'cost_in_credits': 0},

            # Pro tier
            {'operation': 'resume_analysis', 'subscription_tier': 'pro', 'requests_per_hour': 50, 'requests_per_day': 100, 'cost_in_credits': 1},
            {'operation': 'feedback', 'subscription_tier': 'pro', 'requests_per_hour': 5, 'requests_per_day': 20, 'cost_in_credits': 1},
            {'operation': 'optimization', 'subscription_tier': 'pro', 'requests_per_hour': 5, 'requests_per_day': 20, 'cost_in_credits': 2},
            {'operation': 'cover_letter', 'subscription_tier': 'pro', 'requests_per_hour': 5, 'requests_per_day': 20, 'cost_in_credits': 2},
            {'operation': 'skill_suggestions', 'subscription_tier': 'pro', 'requests_per_hour': 10, 'requests_per_day': 50, 'cost_in_credits': 0},

            # Enterprise tier
            {'operation': 'resume_analysis', 'subscription_tier': 'enterprise', 'requests_per_hour': 1000, 'requests_per_day': 10000, 'requests_per_month': 100000, 'cost_in_credits': 0},
            {'operation': 'feedback', 'subscription_tier': 'enterprise', 'requests_per_hour': 1000, 'requests_per_day': 10000, 'requests_per_month': 100000, 'cost_in_credits': 0},
            {'operation': 'optimization', 'subscription_tier': 'enterprise', 'requests_per_hour': 1000, 'requests_per_day': 10000, 'requests_per_month': 100000, 'cost_in_credits': 0},
            {'operation': 'cover_letter', 'subscription_tier': 'enterprise', 'requests_per_hour': 1000, 'requests_per_day': 10000, 'requests_per_month': 100000, 'cost_in_credits': 0},
            {'operation': 'skill_suggestions', 'subscription_tier': 'enterprise', 'requests_per_hour': 1000, 'requests_per_day': 10000, 'requests_per_month': 100000, 'cost_in_credits': 0},

            # Default fallback
            {'operation': 'default', 'subscription_tier': 'default', 'requests_per_hour': 10, 'requests_per_day': 50, 'cost_in_credits': 0},
        ]

        for limit_data in rate_limits:
            existing = RateLimitConfig.query.filter_by(
                operation=limit_data['operation'],
                subscription_tier=limit_data['subscription_tier']
            ).first()

            if not existing:
                limit = RateLimitConfig(**limit_data)
                db.session.add(limit)
                print(f"✓ Created rate limit: {limit_data['operation']} - {limit_data['subscription_tier']}")
            else:
                print(f"  Skipped (exists): {limit_data['operation']} - {limit_data['subscription_tier']}")

        db.session.commit()
        print(f"\n✓ Rate limits initialized!")


def init_scoring_thresholds():
    """Initialize intelligent scoring thresholds"""
    with app.app_context():
        from models import ScoringThreshold
        thresholds = [
            {
                'threshold_name': 'very_limited',
                'min_score': 0,
                'max_score': 30,
                'feedback_text': 'Your resume has very limited alignment with the job requirements. Consider major revisions to include key skills and experience mentioned in the job description.',
                'color_code': '#EF4444',
                'icon': 'x-circle',
                'recommendation_weight': 0.5
            },
            {
                'threshold_name': 'needs_improvement',
                'min_score': 30,
                'max_score': 50,
                'feedback_text': 'Your resume needs significant improvement in alignment with the job description. Add more relevant keywords and emphasize your matching experience.',
                'color_code': '#F59E0B',
                'icon': 'alert-circle',
                'recommendation_weight': 0.75
            },
            {
                'threshold_name': 'moderately_aligned',
                'min_score': 50,
                'max_score': 70,
                'feedback_text': 'Your resume is moderately aligned with the job. Make targeted improvements to highlight the most relevant skills and experience.',
                'color_code': '#FBBF24',
                'icon': 'info-circle',
                'recommendation_weight': 1.0
            },
            {
                'threshold_name': 'well_aligned',
                'min_score': 70,
                'max_score': 85,
                'feedback_text': 'Your resume is well-aligned with the job description. Consider minor tweaks to strengthen key areas and increase your chances.',
                'color_code': '#10B981',
                'icon': 'check-circle',
                'recommendation_weight': 1.2
            },
            {
                'threshold_name': 'excellent_match',
                'min_score': 85,
                'max_score': 100,
                'feedback_text': 'Excellent match! Your resume strongly aligns with the job requirements. You are well-positioned for this role.',
                'color_code': '#059669',
                'icon': 'check-double',
                'recommendation_weight': 1.5
            }
        ]

        for threshold_data in thresholds:
            existing = ScoringThreshold.query.filter_by(
                threshold_name=threshold_data['threshold_name']
            ).first()

            if not existing:
                threshold = ScoringThreshold(**threshold_data)
                db.session.add(threshold)
                print(f"✓ Created scoring threshold: {threshold_data['threshold_name']}")
            else:
                print(f"  Skipped (exists): {threshold_data['threshold_name']}")

        db.session.commit()
        print(f"\n✓ Scoring thresholds initialized!")


def init_validation_rules():
    """Initialize validation rules"""
    with app.app_context():
        from models import ValidationRule
        rules = [
            # Password validation
            {
                'rule_name': 'password_min_length',
                'rule_category': 'password',
                'rule_type': 'min_length',
                'rule_value': 8,
                'error_message': 'Password must be at least 8 characters long',
                'priority': 1
            },
            {
                'rule_name': 'password_uppercase',
                'rule_category': 'password',
                'rule_type': 'pattern',
                'rule_value': '[A-Z]',
                'error_message': 'Password must contain at least one uppercase letter',
                'priority': 2
            },
            {
                'rule_name': 'password_special_chars',
                'rule_category': 'password',
                'rule_type': 'pattern',
                'rule_value': '[!@#$%^&*(),.?":{}|<>]',
                'error_message': 'Password must contain at least one special character',
                'priority': 3
            },
            # Email validation
            {
                'rule_name': 'email_format',
                'rule_category': 'email',
                'rule_type': 'pattern',
                'rule_value': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
                'error_message': 'Please enter a valid email address',
                'priority': 1
            },
            {
                'rule_name': 'email_max_length',
                'rule_category': 'email',
                'rule_type': 'max_length',
                'rule_value': 254,
                'error_message': 'Email address is too long',
                'priority': 2
            },
            # File validation
            {
                'rule_name': 'file_extension',
                'rule_category': 'file',
                'rule_type': 'extension',
                'rule_value': ['pdf', 'docx', 'txt'],
                'error_message': 'Only PDF, DOCX, and TXT files are allowed',
                'priority': 1
            },
            {
                'rule_name': 'file_size',
                'rule_category': 'file',
                'rule_type': 'file_size',
                'rule_value': 16777216,  # 16 MB in bytes
                'error_message': 'File size exceeds maximum allowed (16 MB)',
                'priority': 2,
                'applies_to_tier': 'free'
            },
        ]

        for rule_data in rules:
            existing = ValidationRule.query.filter_by(
                rule_name=rule_data['rule_name']
            ).first()

            if not existing:
                rule = ValidationRule(**rule_data)
                db.session.add(rule)
                print(f"✓ Created validation rule: {rule_data['rule_name']}")
            else:
                print(f"  Skipped (exists): {rule_data['rule_name']}")

        db.session.commit()
        print(f"\n✓ Validation rules initialized!")


def main():
    """Initialize all configurations"""
    print("\n" + "="*60)
    print("Initializing System Configurations")
    print("="*60 + "\n")

    try:
        init_system_configurations()
        init_subscription_tiers()
        init_rate_limits()
        init_scoring_thresholds()
        init_validation_rules()

        print("\n" + "="*60)
        print("✓ All configurations initialized successfully!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n✗ Error initializing configurations: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
