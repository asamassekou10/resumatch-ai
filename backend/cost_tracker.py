"""
Cost Tracking and Budget Enforcement System
Prevents runaway API spending by enforcing daily budget limits
"""
import redis
import os
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks API usage costs and enforces daily budget limits.
    Uses Redis for distributed tracking across multiple workers.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the cost tracker.

        Args:
            redis_url: Redis connection URL. If None, uses REDIS_URL from env
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL')

        if not self.redis_url:
            logger.warning("REDIS_URL not configured - cost tracking disabled in development")
            self.redis_client = None
        else:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Cost tracker initialized with Redis")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self.redis_client = None

        # Configuration
        self.daily_budget_usd = float(os.getenv('DAILY_API_BUDGET_USD', '2.0'))
        self.estimated_cost_per_analysis = float(os.getenv('COST_PER_ANALYSIS_USD', '0.60'))

        logger.info(f"Daily budget: ${self.daily_budget_usd}, Cost per analysis: ${self.estimated_cost_per_analysis}")

    def can_process_guest_analysis(self) -> Tuple[bool, str]:
        """
        Check if we can process a guest analysis without exceeding daily budget.

        Returns:
            (allowed: bool, message: str) - (True, "") if allowed, (False, reason) if blocked
        """
        if not self.redis_client:
            # Fail open in development
            logger.warning("Redis not available - allowing analysis (development mode)")
            return True, ""

        try:
            today_key = self._get_daily_key()
            count = int(self.redis_client.get(today_key) or 0)

            estimated_cost_today = count * self.estimated_cost_per_analysis

            # Check if we're at or over budget
            if estimated_cost_today >= self.daily_budget_usd:
                logger.critical(
                    f"DAILY BUDGET EXCEEDED: ${estimated_cost_today:.2f} / ${self.daily_budget_usd} "
                    f"({count} analyses today)"
                )
                return False, "Daily analysis limit reached due to high demand. Please try again tomorrow or create a free account for guaranteed access."

            # Check if this analysis would put us over budget
            estimated_cost_after = (count + 1) * self.estimated_cost_per_analysis
            if estimated_cost_after > self.daily_budget_usd:
                logger.warning(
                    f"Analysis would exceed budget: ${estimated_cost_after:.2f} > ${self.daily_budget_usd}"
                )
                return False, "Daily analysis limit reached. Please try again tomorrow or sign up for free unlimited access."

            return True, ""

        except Exception as e:
            logger.error(f"Error checking budget: {e}", exc_info=True)
            # Fail open on error to avoid blocking legitimate users
            return True, ""

    def record_guest_analysis(self) -> None:
        """
        Record that a guest analysis was completed.
        Increments the daily counter for cost tracking.
        """
        if not self.redis_client:
            logger.warning("Redis not available - cannot record analysis")
            return

        try:
            today_key = self._get_daily_key()

            # Increment counter
            count = self.redis_client.incr(today_key)

            # Set expiration to end of tomorrow (ensure we don't lose data on midnight)
            tomorrow_end = datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(days=1)
            seconds_until_tomorrow_end = int((tomorrow_end - datetime.utcnow()).total_seconds())
            self.redis_client.expire(today_key, seconds_until_tomorrow_end)

            estimated_cost = count * self.estimated_cost_per_analysis
            logger.info(
                f"Guest analysis recorded. Today: {count} analyses, "
                f"estimated cost: ${estimated_cost:.2f} / ${self.daily_budget_usd}"
            )

            # Alert if approaching budget (80% threshold)
            if estimated_cost >= self.daily_budget_usd * 0.8:
                logger.warning(
                    f"⚠️ BUDGET ALERT: {(estimated_cost/self.daily_budget_usd)*100:.1f}% of daily budget used"
                )

        except Exception as e:
            logger.error(f"Error recording analysis: {e}", exc_info=True)

    def get_daily_stats(self) -> Dict[str, any]:
        """
        Get today's usage statistics.

        Returns:
            Dictionary with analyses count, costs, and budget info
        """
        if not self.redis_client:
            return {
                'analyses_today': 0,
                'estimated_cost_usd': 0.0,
                'budget_usd': self.daily_budget_usd,
                'remaining_budget_usd': self.daily_budget_usd,
                'budget_exhausted': False,
                'percentage_used': 0.0,
                'redis_available': False
            }

        try:
            today_key = self._get_daily_key()
            count = int(self.redis_client.get(today_key) or 0)
            estimated_cost = count * self.estimated_cost_per_analysis
            remaining = max(0, self.daily_budget_usd - estimated_cost)
            percentage = (estimated_cost / self.daily_budget_usd * 100) if self.daily_budget_usd > 0 else 0

            return {
                'date': datetime.utcnow().date().isoformat(),
                'analyses_today': count,
                'estimated_cost_usd': round(estimated_cost, 2),
                'budget_usd': self.daily_budget_usd,
                'remaining_budget_usd': round(remaining, 2),
                'budget_exhausted': estimated_cost >= self.daily_budget_usd,
                'percentage_used': round(percentage, 1),
                'redis_available': True
            }

        except Exception as e:
            logger.error(f"Error getting daily stats: {e}", exc_info=True)
            return {
                'error': str(e),
                'redis_available': False
            }

    def get_weekly_stats(self) -> Dict[str, any]:
        """
        Get 7-day cost trend statistics.

        Returns:
            Dictionary with weekly totals and daily breakdown
        """
        if not self.redis_client:
            return {
                'period': '7_days',
                'total_cost_usd': 0.0,
                'total_analyses': 0,
                'daily_average_usd': 0.0,
                'projected_monthly_usd': 0.0,
                'daily_breakdown': [],
                'redis_available': False
            }

        try:
            weekly_data = []
            total_cost = 0.0
            total_analyses = 0

            for days_ago in range(7):
                date = datetime.utcnow().date() - timedelta(days=days_ago)
                date_key = f"api_cost:guest:{date}"

                count = int(self.redis_client.get(date_key) or 0)
                cost = count * self.estimated_cost_per_analysis

                total_cost += cost
                total_analyses += count

                weekly_data.append({
                    'date': date.isoformat(),
                    'analyses': count,
                    'cost_usd': round(cost, 2)
                })

            daily_average = total_cost / 7
            projected_monthly = daily_average * 30

            return {
                'period': '7_days',
                'total_cost_usd': round(total_cost, 2),
                'total_analyses': total_analyses,
                'daily_average_usd': round(daily_average, 2),
                'projected_monthly_usd': round(projected_monthly, 2),
                'daily_breakdown': weekly_data,
                'redis_available': True
            }

        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}", exc_info=True)
            return {
                'error': str(e),
                'redis_available': False
            }

    def _get_daily_key(self) -> str:
        """Get Redis key for today's counter."""
        today = datetime.utcnow().date()
        return f"api_cost:guest:{today}"

    def reset_daily_counter(self) -> bool:
        """
        Reset today's counter (admin function for emergencies).

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            today_key = self._get_daily_key()
            self.redis_client.delete(today_key)
            logger.warning("Daily cost counter RESET by admin")
            return True
        except Exception as e:
            logger.error(f"Error resetting counter: {e}")
            return False


# Global instance (initialized on first import)
cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    """
    Get the global cost tracker instance.

    Returns:
        CostTracker instance
    """
    return cost_tracker
