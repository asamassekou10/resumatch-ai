"""
Result Filter Service
Implements blur strategy for free tier - shows value but hides details to drive conversions
"""

from datetime import datetime
from models import Purchase


class ResultFilter:
    """Filter and blur analysis results based on user tier and payment status"""

    @staticmethod
    def has_active_weekly_pass(user):
        """Check if user has an active weekly pass"""
        if not user:
            return False

        active_pass = Purchase.query.filter(
            Purchase.user_id == user.id,
            Purchase.purchase_type == 'weekly_pass',
            Purchase.is_active == True,
            Purchase.payment_status == 'succeeded',
            Purchase.access_expires_at > datetime.utcnow()
        ).first()

        return active_pass is not None

    @staticmethod
    def can_see_full_results(user):
        """
        Determine if user can see full unblurred results

        Returns True if:
        - User has active weekly pass
        - User has paid subscription (pro, elite, etc.)
        - User is admin
        """
        if not user:
            return False

        # Admin bypass
        if user.is_admin:
            return True

        # Check for active weekly pass
        if ResultFilter.has_active_weekly_pass(user):
            return True

        # Check for paid subscription
        if user.subscription_tier in ['pro', 'pro_annual', 'pro_founding', 'monthly_pro', 'elite', 'student']:
            if user.subscription_status == 'active' or user.subscription_status == 'trialing':
                return True

        # Check if user has credits (they used their free scan or bought credits)
        # Free tier with 0 credits = they used their 1 free scan
        if user.subscription_tier == 'free' and user.credits == 0:
            return False

        return False

    @staticmethod
    def filter_analysis_result(analysis_result, user, analysis_count=0):
        """
        Filter analysis results based on user tier

        For FREE tier (after 1st scan):
        - Show overall score
        - Show score breakdown
        - Show top 3 missing keywords
        - BLUR: Remaining missing keywords (show count)
        - BLUR: AI recommendations
        - BLUR: Optimized resume suggestions
        - BLUR: Cover letter

        Args:
            analysis_result: Full analysis result dict
            user: User object
            analysis_count: Number of analyses user has completed (0 = first scan)

        Returns:
            Filtered result dict with 'is_blurred' flag and 'upgrade_message'
        """
        # If user can see full results, return everything
        if ResultFilter.can_see_full_results(user):
            return {
                **analysis_result,
                'is_blurred': False,
                'can_see_full': True,
                'user_tier': user.subscription_tier if user else 'guest'
            }

        # Check if this is the user's first scan (free preview)
        if analysis_count == 0:
            # First scan - show everything (the "aha moment")
            return {
                **analysis_result,
                'is_blurred': False,
                'is_first_scan': True,
                'can_see_full': True,
                'user_tier': user.subscription_tier if user else 'guest',
                'message': 'This is your free analysis preview. Sign up to save and re-scan!'
            }

        # FREE tier - apply blur strategy
        match_analysis = analysis_result.get('match_analysis', {})
        keywords_missing = match_analysis.get('keywords_missing', [])

        # Show top 3 keywords, blur the rest
        visible_keywords = keywords_missing[:3] if keywords_missing else []
        blurred_count = max(0, len(keywords_missing) - 3)

        filtered_result = {
            # Always visible
            'overall_score': analysis_result.get('overall_score'),
            'score_breakdown': analysis_result.get('score_breakdown'),
            'interpretation': analysis_result.get('interpretation'),
            'job_industry': analysis_result.get('job_industry'),
            'job_level': analysis_result.get('job_level'),
            'resume_level': analysis_result.get('resume_level'),
            'expected_ats_pass_rate': analysis_result.get('expected_ats_pass_rate'),

            # Partially visible
            'match_analysis': {
                'keywords_present': match_analysis.get('keywords_present', []),
                'keywords_missing': visible_keywords,
                'blurred_keywords_count': blurred_count,
                'skills_match_percentage': match_analysis.get('skills_match_percentage'),
                'experience_alignment': match_analysis.get('experience_alignment')
            },

            # Blurred sections
            'ats_optimization': {'blurred': True},
            'recommendations': {
                'blurred': True,
                'preview': 'Unlock detailed AI recommendations...'
            },

            # Metadata
            'is_blurred': True,
            'can_see_full': False,
            'user_tier': user.subscription_tier if user else 'guest',
            'blurred_sections': [
                f'{blurred_count} additional missing keywords',
                'AI-powered recommendations',
                'ATS optimization tips',
                'Optimized resume suggestions'
            ],
            'upgrade_options': [
                {
                    'type': 'single_rescan',
                    'price': 1.99,
                    'description': 'Re-scan once to see improvements'
                },
                {
                    'type': 'weekly_pass',
                    'price': 6.99,
                    'description': '7 days unlimited scans',
                    'recommended': True
                },
                {
                    'type': 'monthly_pro',
                    'price': 19.99,
                    'description': 'Full Pro features + templates'
                }
            ],
            'upgrade_message': f"You're missing {blurred_count} critical keywords. Unlock them now to improve your resume!",
            'conversion_hook': f"See all {len(keywords_missing)} missing keywords and get AI recommendations"
        }

        return filtered_result

    @staticmethod
    def filter_keywords_for_display(keywords, user, max_free=3):
        """
        Filter keywords list for display

        Args:
            keywords: List of keyword objects or strings
            user: User object
            max_free: Maximum keywords to show for free tier

        Returns:
            dict with 'visible', 'blurred_count', 'requires_upgrade'
        """
        if ResultFilter.can_see_full_results(user):
            return {
                'visible': keywords,
                'blurred_count': 0,
                'requires_upgrade': False
            }

        return {
            'visible': keywords[:max_free],
            'blurred_count': max(0, len(keywords) - max_free),
            'requires_upgrade': True,
            'upgrade_message': f'Unlock {len(keywords) - max_free} more keywords'
        }

    @staticmethod
    def get_user_access_info(user):
        """
        Get comprehensive access information for user

        Returns:
            dict with access level, credits, subscription status, etc.
        """
        if not user:
            return {
                'access_level': 'guest',
                'can_see_full': False,
                'credits': 0,
                'analyses_remaining': 1,  # 1 free guest scan
                'subscription_tier': 'guest'
            }

        has_weekly_pass = ResultFilter.has_active_weekly_pass(user)
        can_see_full = ResultFilter.can_see_full_results(user)

        weekly_pass_info = None
        if has_weekly_pass:
            active_pass = Purchase.query.filter(
                Purchase.user_id == user.id,
                Purchase.purchase_type == 'weekly_pass',
                Purchase.is_active == True,
                Purchase.payment_status == 'succeeded',
                Purchase.access_expires_at > datetime.utcnow()
            ).first()

            if active_pass:
                time_remaining = active_pass.access_expires_at - datetime.utcnow()
                weekly_pass_info = {
                    'expires_at': active_pass.access_expires_at.isoformat(),
                    'hours_remaining': int(time_remaining.total_seconds() / 3600)
                }

        return {
            'access_level': 'full' if can_see_full else 'limited',
            'can_see_full': can_see_full,
            'credits': user.credits,
            'subscription_tier': user.subscription_tier,
            'subscription_status': user.subscription_status,
            'has_weekly_pass': has_weekly_pass,
            'weekly_pass_info': weekly_pass_info,
            'is_admin': user.is_admin,
            'analyses_remaining': user.credits if user.subscription_tier == 'free' else 'unlimited'
        }
