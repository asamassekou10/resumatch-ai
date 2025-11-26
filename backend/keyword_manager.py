"""
Intelligent Keyword Management Service

Replaces hardcoded keyword lists with dynamic, semantic keyword matching.
Handles fuzzy matching, synonym resolution, priority weighting, and industry-specific mappings.
"""

from flask import current_app
from models import (
    Keyword, KeywordSimilarity, KeywordDatabase, KeywordMatchingRule,
    UserSkillHistory, db
)
from difflib import SequenceMatcher
import re
from functools import lru_cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class KeywordManager:
    """Intelligent keyword management with caching and semantic matching"""

    def __init__(self, cache_timeout=300):  # 5 minute cache
        self.cache_timeout = cache_timeout
        self.cache = {}
        self.cache_times = {}

    def _is_cache_valid(self, key):
        """Check if cache entry is still valid"""
        if key not in self.cache_times:
            return False
        elapsed = (datetime.utcnow() - self.cache_times[key]).total_seconds()
        return elapsed < self.cache_timeout

    def _get_cached(self, key):
        """Get value from cache if valid"""
        if self._is_cache_valid(key):
            return self.cache.get(key)
        return None

    def _set_cache(self, key, value):
        """Store value in cache"""
        self.cache[key] = value
        self.cache_times[key] = datetime.utcnow()

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_times.clear()
        logger.info("Keyword manager cache cleared")

    # ==================== KEYWORD RETRIEVAL ====================

    def get_all_keywords(self, category=None, priority=None, include_deprecated=False):
        """Get all keywords, optionally filtered by category or priority"""
        cache_key = f"keywords:{category}:{priority}:{include_deprecated}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        query = Keyword.query

        if not include_deprecated:
            query = query.filter_by(is_deprecated=False)

        if category:
            query = query.filter_by(category=category)

        if priority:
            query = query.filter_by(priority=priority)

        keywords = query.all()
        self._set_cache(cache_key, keywords)
        return keywords

    def get_keyword_by_text(self, text):
        """Get keyword by exact text match"""
        text_lower = text.lower().strip()
        cache_key = f"keyword:{text_lower}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Try exact match
        keyword = Keyword.query.filter_by(keyword=text_lower).first()
        self._set_cache(cache_key, keyword)
        return keyword

    def get_keywords_by_category(self, category):
        """Get all keywords in a specific category"""
        return self.get_all_keywords(category=category)

    def get_keywords_by_priority(self, priority):
        """Get keywords by priority level (critical, important, medium, optional)"""
        return self.get_all_keywords(priority=priority)

    # ==================== SEMANTIC MATCHING ====================

    def get_keyword_similarities(self, keyword_id, match_types=None):
        """Get all similar keywords for a given keyword"""
        cache_key = f"similarities:{keyword_id}:{str(match_types)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        query = KeywordSimilarity.query.filter_by(keyword_1_id=keyword_id)

        if match_types:
            query = query.filter(KeywordSimilarity.match_type.in_(match_types))

        similarities = query.order_by(KeywordSimilarity.similarity_score.desc()).all()
        self._set_cache(cache_key, similarities)
        return similarities

    def find_synonym(self, text):
        """Find canonical keyword from text (handles synonyms)"""
        # First try exact match
        keyword = self.get_keyword_by_text(text)
        if keyword:
            return keyword

        # Try matching against synonym lists
        keywords = self.get_all_keywords(include_deprecated=True)
        for kw in keywords:
            if kw.synonyms and text.lower() in [s.lower() for s in kw.synonyms]:
                return kw

        return None

    def find_similar_keywords(self, text, threshold=0.8):
        """Find keywords similar to input text using fuzzy matching"""
        keywords = self.get_all_keywords()
        similar = []

        for keyword in keywords:
            # Check exact match
            if keyword.keyword.lower() == text.lower():
                similar.append((keyword, 1.0))
                continue

            # Check synonym match
            if keyword.synonyms:
                for syn in keyword.synonyms:
                    ratio = SequenceMatcher(None, text.lower(), syn.lower()).ratio()
                    if ratio >= threshold:
                        similar.append((keyword, ratio))
                        break

            # Fuzzy match on keyword name
            ratio = SequenceMatcher(None, text.lower(), keyword.keyword.lower()).ratio()
            if ratio >= threshold:
                similar.append((keyword, ratio))

        # Sort by similarity score descending
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    # ==================== FUZZY MATCHING ====================

    def apply_matching_rules(self, text):
        """Apply fuzzy matching rules to normalize text to canonical keyword"""
        text_lower = text.lower().strip()

        # Check matching rules
        rules = KeywordMatchingRule.query.all()

        for rule in rules:
            try:
                if rule.match_type == 'regex':
                    if re.match(rule.pattern, text_lower):
                        keyword = Keyword.query.get(rule.normalized_keyword_id)
                        if keyword and not keyword.is_deprecated:
                            return keyword, rule.confidence

                elif rule.match_type == 'substring':
                    if rule.pattern.lower() in text_lower:
                        keyword = Keyword.query.get(rule.normalized_keyword_id)
                        if keyword and not keyword.is_deprecated:
                            return keyword, rule.confidence

                elif rule.match_type == 'fuzzy':
                    ratio = SequenceMatcher(None, rule.pattern.lower(), text_lower).ratio()
                    if ratio >= 0.85:
                        keyword = Keyword.query.get(rule.normalized_keyword_id)
                        if keyword and not keyword.is_deprecated:
                            return keyword, rule.confidence

                elif rule.match_type == 'version_variant':
                    # Handle version variants like "python3" -> "python", "c++" -> "c++"
                    pattern = rule.pattern.lower().replace('[version]', r'\d+\.?\d*')
                    if re.match(pattern, text_lower):
                        keyword = Keyword.query.get(rule.normalized_keyword_id)
                        if keyword and not keyword.is_deprecated:
                            return keyword, rule.confidence

            except Exception as e:
                logger.warning(f"Error applying matching rule {rule.id}: {str(e)}")
                continue

        return None, 0.0

    # ==================== PRIORITY AND WEIGHTING ====================

    def get_priority_weight(self, priority):
        """Get numerical weight for priority level"""
        weights = {
            'critical': 1.0,
            'important': 0.8,
            'medium': 0.6,
            'optional': 0.4
        }
        return weights.get(priority, 0.6)

    def get_difficulty_weight(self, difficulty):
        """Get weight for difficulty level (harder skills valued higher)"""
        weights = {
            'beginner': 0.6,
            'intermediate': 0.8,
            'advanced': 0.95,
            'expert': 1.0
        }
        return weights.get(difficulty, 0.8)

    # ==================== INDUSTRY-SPECIFIC MATCHING ====================

    def get_expected_keywords_for_role(self, job_title, role_level='mid', industry=None):
        """Get expected keywords for a specific job role"""
        cache_key = f"role_keywords:{job_title}:{role_level}:{industry}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        query = KeywordDatabase.query.filter_by(
            job_role=job_title,
            role_level=role_level
        )

        if industry:
            query = query.filter_by(industry_tag=industry)

        databases = query.all()

        result = {
            'keywords': {},
            'confidence': 0.8
        }

        for db_entry in databases:
            for category, keywords in db_entry.keywords.items():
                if category not in result['keywords']:
                    result['keywords'][category] = []
                result['keywords'][category].extend(keywords)

            result['confidence'] = max(result['confidence'], db_entry.confidence)

        self._set_cache(cache_key, result)
        return result

    def get_industry_relevance(self, keyword_id, industry):
        """Get relevance score of a keyword for a specific industry"""
        keyword = Keyword.query.get(keyword_id)
        if not keyword or not keyword.industry_relevance:
            return 0.5  # Default neutral relevance

        return keyword.industry_relevance.get(industry, 0.5)

    # ==================== SCORING AND RANKING ====================

    def calculate_keyword_score(self, keyword, matched_text, job_role=None, industry=None):
        """
        Calculate comprehensive score for a keyword match

        Factors:
        - Base confidence score
        - Priority weight
        - Difficulty weight
        - Industry relevance
        - Match quality (fuzzy matching accuracy)
        """
        base_score = keyword.confidence_score or 1.0

        # Apply priority weight
        priority_weight = self.get_priority_weight(keyword.priority)

        # Apply difficulty weight
        difficulty_weight = self.get_difficulty_weight(keyword.difficulty_level or 'intermediate')

        # Apply industry relevance
        industry_relevance = 1.0
        if industry:
            industry_relevance = self.get_industry_relevance(keyword.id, industry)

        # Match quality based on fuzzy similarity
        match_quality = SequenceMatcher(None, keyword.keyword.lower(),
                                       matched_text.lower()).ratio()

        # Combine scores (weighted average)
        final_score = (
            base_score * 0.2 +
            priority_weight * 0.3 +
            difficulty_weight * 0.2 +
            industry_relevance * 0.15 +
            match_quality * 0.15
        )

        return min(1.0, max(0.0, final_score))

    def rank_keywords(self, keywords, job_role=None, industry=None):
        """Rank a list of keyword matches by calculated score"""
        scored = []

        for keyword, match_text in keywords:
            score = self.calculate_keyword_score(
                keyword, match_text, job_role, industry
            )
            scored.append({
                'keyword': keyword,
                'score': score,
                'priority': keyword.priority,
                'category': keyword.category
            })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    # ==================== KEYWORD EXTRACTION PIPELINE ====================

    def normalize_text(self, text):
        """Normalize text for keyword matching (preserve important characters)"""
        # Keep alphanumeric, spaces, and important symbols like + # - .
        text = re.sub(r'[^\w\s+#\-.]', '', text, flags=re.UNICODE)
        return text.lower().strip()

    def extract_and_match_keywords(self, text, job_role=None, industry=None,
                                   max_results=30, min_score=0.4):
        """
        Extract keywords from text with intelligent matching

        Process:
        1. Normalize text
        2. Split into potential keywords (words and technical terms)
        3. For each token:
           - Try fuzzy matching rules
           - Try synonym matching
           - Try similar keyword matching
        4. Score and rank results
        5. Remove duplicates and low-confidence matches
        6. Return ranked list
        """
        if not text:
            return []

        normalized = self.normalize_text(text)

        # Split into tokens (handle multi-word terms)
        tokens = self._smart_tokenize(normalized)

        matched_keywords = {}  # keyword_id -> best match info

        for token in tokens:
            if len(token) < 2:  # Skip single characters
                continue

            # Try exact matching rules first
            matched_kw, confidence = self.apply_matching_rules(token)
            if matched_kw and matched_kw.id not in matched_keywords:
                matched_keywords[matched_kw.id] = {
                    'keyword': matched_kw,
                    'matched_text': token,
                    'confidence': confidence,
                    'method': 'matching_rule'
                }
                continue

            # Try synonym matching
            synonym_kw = self.find_synonym(token)
            if synonym_kw and synonym_kw.id not in matched_keywords:
                matched_keywords[synonym_kw.id] = {
                    'keyword': synonym_kw,
                    'matched_text': token,
                    'confidence': 0.95,
                    'method': 'synonym'
                }
                continue

            # Try fuzzy matching with threshold
            similar = self.find_similar_keywords(token, threshold=0.75)
            if similar and similar[0][0].id not in matched_keywords:
                keyword, similarity = similar[0]
                matched_keywords[keyword.id] = {
                    'keyword': keyword,
                    'matched_text': token,
                    'confidence': similarity,
                    'method': 'fuzzy_match'
                }

        # Score and rank
        keyword_list = [(m['keyword'], m['matched_text']) for m in matched_keywords.values()]
        ranked = self.rank_keywords(keyword_list, job_role, industry)

        # Filter by score threshold and limit results
        results = [
            r for r in ranked
            if r['score'] >= min_score
        ][:max_results]

        return results

    def _smart_tokenize(self, text):
        """Intelligently tokenize text, handling multi-word terms and special chars"""
        # First, split by whitespace
        tokens = text.split()

        # Handle multi-word technical terms (e.g., "machine learning", "full stack")
        expanded = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Try two-word combinations
            if i + 1 < len(tokens):
                two_word = f"{token} {tokens[i + 1]}"
                if self.get_keyword_by_text(two_word):
                    expanded.append(two_word)
                    i += 2
                    continue

            expanded.append(token)
            i += 1

        return expanded

    # ==================== USER FEEDBACK AND LEARNING ====================

    def record_keyword_feedback(self, user_id, keyword_id, confirmed=None,
                                rejected=None, analysis_id=None, context=None):
        """Record user feedback on keyword matches for ML training"""
        try:
            history = UserSkillHistory(
                user_id=user_id,
                keyword_id=keyword_id,
                analysis_id=analysis_id,
                user_confirmed=confirmed,
                user_rejected=rejected,
                context=context
            )
            db.session.add(history)
            db.session.commit()

            # Clear cache as user feedback may affect future matches
            self.clear_cache()
            logger.info(f"Recorded feedback for user {user_id} on keyword {keyword_id}")

        except Exception as e:
            logger.error(f"Error recording keyword feedback: {str(e)}")
            db.session.rollback()

    def get_user_skill_history(self, user_id):
        """Get user's confirmed and rejected keywords for improved matching"""
        history = UserSkillHistory.query.filter_by(user_id=user_id).all()

        confirmed_keywords = [h.keyword_id for h in history if h.user_confirmed]
        rejected_keywords = [h.keyword_id for h in history if h.user_rejected]

        return {
            'confirmed': confirmed_keywords,
            'rejected': rejected_keywords,
            'count': len(history)
        }

    # ==================== STATISTICS ====================

    def get_keyword_stats(self):
        """Get keyword database statistics"""
        return {
            'total_keywords': Keyword.query.count(),
            'by_priority': {
                'critical': Keyword.query.filter_by(priority='critical').count(),
                'important': Keyword.query.filter_by(priority='important').count(),
                'medium': Keyword.query.filter_by(priority='medium').count(),
                'optional': Keyword.query.filter_by(priority='optional').count(),
            },
            'by_category': self._count_by_category(),
            'deprecated': Keyword.query.filter_by(is_deprecated=True).count(),
            'with_salary_premium': Keyword.query.filter(Keyword.average_salary_premium.isnot(None)).count(),
            'cache_size': len(self.cache),
        }

    def _count_by_category(self):
        """Count keywords by category"""
        from sqlalchemy import func
        result = db.session.query(
            Keyword.category,
            func.count(Keyword.id)
        ).group_by(Keyword.category).all()
        return {category: count for category, count in result}


# Global instance
_keyword_manager = None


def get_keyword_manager():
    """Get or create the global keyword manager instance"""
    global _keyword_manager
    if _keyword_manager is None:
        _keyword_manager = KeywordManager()
    return _keyword_manager


def init_keyword_manager():
    """Initialize keyword manager (call from app.py)"""
    global _keyword_manager
    _keyword_manager = KeywordManager()
    logger.info("Keyword manager initialized")
    return _keyword_manager
