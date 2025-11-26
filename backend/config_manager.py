"""
Configuration Manager Service

Provides intelligent, cached access to system configuration from the database.
Eliminates hardcoded values and allows runtime configuration changes.
"""

from functools import lru_cache
from datetime import timedelta
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages system configuration with caching"""

    # Cache timeout in seconds
    CACHE_TIMEOUT = 300  # 5 minutes

    def __init__(self, db):
        """Initialize with database instance"""
        self.db = db
        self._cache = {}
        self._cache_timestamps = {}

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached value is still valid"""
        if key not in self._cache_timestamps:
            return False
        from datetime import datetime
        elapsed = (datetime.utcnow() - self._cache_timestamps[key]).total_seconds()
        return elapsed < self.CACHE_TIMEOUT

    def get_config(self, config_key: str, default: Any = None) -> Any:
        """Get a single configuration value"""
        from models import SystemConfiguration

        # Check cache first
        if self._is_cache_valid(config_key):
            return self._cache.get(config_key, default)

        try:
            config = SystemConfiguration.query.filter_by(config_key=config_key).first()
            if config:
                self._cache[config_key] = config.config_value
                from datetime import datetime
                self._cache_timestamps[config_key] = datetime.utcnow()
                return config.config_value
            return default
        except Exception as e:
            logger.warning(f"Error fetching config {config_key}: {str(e)}")
            return default

    def set_config(self, config_key: str, config_value: Any, data_type: str,
                   description: str = "", category: str = "", user_id: int = None) -> bool:
        """Set or update a configuration value"""
        from models import SystemConfiguration
        from datetime import datetime

        try:
            config = SystemConfiguration.query.filter_by(config_key=config_key).first()
            if config:
                config.config_value = config_value
                config.updated_at = datetime.utcnow()
                config.updated_by_id = user_id
            else:
                config = SystemConfiguration(
                    config_key=config_key,
                    config_value=config_value,
                    data_type=data_type,
                    description=description,
                    category=category,
                    updated_by_id=user_id
                )
                self.db.session.add(config)

            self.db.session.commit()
            # Invalidate cache
            if config_key in self._cache:
                del self._cache[config_key]
            if config_key in self._cache_timestamps:
                del self._cache_timestamps[config_key]
            return True
        except Exception as e:
            logger.error(f"Error setting config {config_key}: {str(e)}")
            self.db.session.rollback()
            return False

    def get_subscription_tier(self, tier_name: str) -> Optional[Dict]:
        """Get subscription tier configuration"""
        from models import SubscriptionTier

        try:
            tier = SubscriptionTier.query.filter_by(name=tier_name, is_active=True).first()
            return tier.to_dict() if tier else None
        except Exception as e:
            logger.warning(f"Error fetching tier {tier_name}: {str(e)}")
            return None

    def get_all_subscription_tiers(self) -> List[Dict]:
        """Get all active subscription tiers"""
        from models import SubscriptionTier

        try:
            tiers = SubscriptionTier.query.filter_by(is_active=True).order_by(SubscriptionTier.position).all()
            return [t.to_dict() for t in tiers]
        except Exception as e:
            logger.warning(f"Error fetching tiers: {str(e)}")
            return []

    def get_rate_limit(self, operation: str, subscription_tier: str = 'default') -> Optional[Dict]:
        """Get rate limit configuration for an operation and tier"""
        from models import RateLimitConfig

        try:
            # Try tier-specific limit first
            limit = RateLimitConfig.query.filter_by(
                operation=operation,
                subscription_tier=subscription_tier
            ).first()

            # Fall back to default if not found
            if not limit and subscription_tier != 'default':
                limit = RateLimitConfig.query.filter_by(
                    operation=operation,
                    subscription_tier='default'
                ).first()

            return limit.to_dict() if limit else None
        except Exception as e:
            logger.warning(f"Error fetching rate limit {operation}/{subscription_tier}: {str(e)}")
            return None

    def get_scoring_thresholds(self) -> List[Dict]:
        """Get all scoring thresholds ordered by min_score"""
        from models import ScoringThreshold

        try:
            thresholds = ScoringThreshold.query.order_by(ScoringThreshold.min_score).all()
            return [t.to_dict() for t in thresholds]
        except Exception as e:
            logger.warning(f"Error fetching scoring thresholds: {str(e)}")
            return []

    def get_scoring_threshold_for_score(self, score: float) -> Optional[Dict]:
        """Get the appropriate threshold feedback for a given score"""
        from models import ScoringThreshold

        try:
            threshold = ScoringThreshold.query.filter(
                ScoringThreshold.min_score <= score,
                ScoringThreshold.max_score >= score
            ).first()
            return threshold.to_dict() if threshold else None
        except Exception as e:
            logger.warning(f"Error fetching threshold for score {score}: {str(e)}")
            return None

    def get_validation_rules(self, category: str, applies_to_tier: Optional[str] = None) -> List[Dict]:
        """Get validation rules for a category and optionally a tier"""
        from models import ValidationRule

        try:
            query = ValidationRule.query.filter_by(
                rule_category=category,
                is_active=True
            )

            if applies_to_tier:
                query = query.filter(
                    (ValidationRule.applies_to_tier == applies_to_tier) |
                    (ValidationRule.applies_to_tier == None)
                )

            rules = query.order_by(ValidationRule.priority).all()
            return [r.to_dict() for r in rules]
        except Exception as e:
            logger.warning(f"Error fetching validation rules {category}: {str(e)}")
            return []

    def get_file_limits(self, subscription_tier: str = 'free') -> Dict[str, Any]:
        """Get file upload limits for a subscription tier"""
        tier = self.get_subscription_tier(subscription_tier)
        if tier:
            return {
                'max_file_size_mb': tier.get('max_file_size_mb', 5),
                'max_concurrent_uploads': tier.get('max_concurrent_uploads', 1),
                'allowed_extensions': self.get_config('allowed_file_extensions', ['pdf', 'docx', 'txt'])
            }
        return {
            'max_file_size_mb': 5,
            'max_concurrent_uploads': 1,
            'allowed_extensions': ['pdf', 'docx', 'txt']
        }

    def get_feature_enabled(self, feature_name: str, subscription_tier: str = 'free') -> bool:
        """Check if a feature is enabled for a subscription tier"""
        tier = self.get_subscription_tier(subscription_tier)
        if tier and 'features' in tier:
            return tier['features'].get(feature_name, False)
        return False

    def clear_cache(self) -> None:
        """Clear all cached configurations"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Configuration cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get configuration manager stats"""
        return {
            'cached_items': len(self._cache),
            'cache_timeout_seconds': self.CACHE_TIMEOUT
        }


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def init_config_manager(db) -> ConfigManager:
    """Initialize the global configuration manager"""
    global _config_manager
    _config_manager = ConfigManager(db)
    return _config_manager


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager"""
    if _config_manager is None:
        raise RuntimeError("Configuration manager not initialized. Call init_config_manager first.")
    return _config_manager


# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value"""
    return get_config_manager().get_config(key, default)


def get_file_limits(tier: str = 'free') -> Dict[str, Any]:
    """Get file limits for a tier"""
    return get_config_manager().get_file_limits(tier)


def get_rate_limit(operation: str, tier: str = 'default') -> Optional[Dict]:
    """Get rate limit for an operation"""
    return get_config_manager().get_rate_limit(operation, tier)


def get_scoring_threshold(score: float) -> Optional[Dict]:
    """Get scoring feedback for a score"""
    return get_config_manager().get_scoring_threshold_for_score(score)


def get_validation_rules(category: str, tier: Optional[str] = None) -> List[Dict]:
    """Get validation rules"""
    return get_config_manager().get_validation_rules(category, tier)
