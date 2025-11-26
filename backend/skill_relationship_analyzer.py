"""
Skill Relationship and Co-Occurrence Analyzer

Analyzes skill co-occurrences across resumes and user confirmations to:
1. Identify which skills frequently appear together
2. Build a skill relationship graph
3. Track skill association strength and patterns
4. Provide relationship-based skill recommendations
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SkillRelationshipAnalyzer:
    """Analyzes skill relationships and co-occurrences"""

    def __init__(self, db=None):
        """Initialize the analyzer with database access"""
        self.db = db
        self.min_cooccurrence_threshold = 2  # Minimum times skills must appear together

    def get_skill_cooccurrences(self, limit_days: Optional[int] = None) -> Dict[int, Dict]:
        """
        Get all skill co-occurrences from confirmed extractions.

        Args:
            limit_days: Only analyze extractions from last N days (None = all time)

        Returns:
            Dictionary mapping skill_id to co-occurrence data
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import SkillExtraction, Analysis
            from sqlalchemy import func

            with app.app_context():
                # Build query
                query = (
                    SkillExtraction.query
                    .join(Analysis, SkillExtraction.analysis_id == Analysis.id)
                    .filter(SkillExtraction.user_confirmed == True)
                )

                # Optional time limit
                if limit_days:
                    cutoff_date = datetime.utcnow() - timedelta(days=limit_days)
                    query = query.filter(SkillExtraction.created_at >= cutoff_date)

                extractions = query.all()

                if not extractions:
                    return {}

                # Group by analysis to find co-occurrences
                analysis_skills = defaultdict(set)
                for extraction in extractions:
                    if extraction.matched_keyword_id:
                        analysis_skills[extraction.analysis_id].add(extraction.matched_keyword_id)

                # Count co-occurrences
                cooccurrences = defaultdict(lambda: defaultdict(int))
                for analysis_id, skill_ids in analysis_skills.items():
                    skill_list = list(skill_ids)
                    # Count all pairs
                    for i, skill_a in enumerate(skill_list):
                        for skill_b in skill_list[i + 1:]:
                            # Store both directions
                            cooccurrences[skill_a][skill_b] += 1
                            cooccurrences[skill_b][skill_a] += 1

                # Convert to standard dict format
                result = {}
                for skill_a, co_skills in cooccurrences.items():
                    result[skill_a] = dict(co_skills)

                return result

        except Exception as e:
            logger.error(f"Error analyzing skill co-occurrences: {str(e)}")
            return {}

    def get_related_skills(self, skill_id: int, top_n: int = 10, min_strength: int = 2) -> List[Dict]:
        """
        Get skills that frequently co-occur with a given skill.

        Args:
            skill_id: ID of the skill to find relationships for
            top_n: Number of related skills to return
            min_strength: Minimum co-occurrence count to consider

        Returns:
            List of related skills with strength scores
        """
        if not self.db:
            return []

        try:
            from app import app
            from models import Keyword

            cooccurrences = self.get_skill_cooccurrences()

            if skill_id not in cooccurrences:
                return []

            # Get related skills
            related = cooccurrences[skill_id]

            # Filter by minimum strength and sort
            related_filtered = [
                (skill_id, strength) for skill_id, strength in related.items()
                if strength >= min_strength
            ]
            related_filtered.sort(key=lambda x: x[1], reverse=True)

            # Get keyword details
            with app.app_context():
                result = []
                for related_skill_id, strength in related_filtered[:top_n]:
                    keyword = Keyword.query.get(related_skill_id)
                    if keyword:
                        result.append({
                            'skill_id': related_skill_id,
                            'skill_name': keyword.keyword,
                            'co_occurrence_strength': strength,
                            'category': keyword.category
                        })

                return result

        except Exception as e:
            logger.error(f"Error getting related skills: {str(e)}")
            return []

    def analyze_skill_category_relationships(self) -> Dict[str, Dict]:
        """
        Analyze relationships between skills in different categories.

        Returns:
            Dictionary showing cross-category relationships
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import SkillExtraction, Keyword
            from sqlalchemy import func

            with app.app_context():
                # Get all confirmed extractions with keyword details
                extractions = (
                    SkillExtraction.query
                    .join(Keyword, SkillExtraction.matched_keyword_id == Keyword.id)
                    .filter(SkillExtraction.user_confirmed == True)
                    .all()
                )

                if not extractions:
                    return {}

                # Group by analysis and category
                analysis_categories = defaultdict(set)
                for extraction in extractions:
                    if extraction.matched_keyword:
                        analysis_categories[extraction.analysis_id].add(
                            extraction.matched_keyword.category
                        )

                # Count category co-occurrences
                category_pairs = Counter()
                for analysis_id, categories in analysis_categories.items():
                    cat_list = list(categories)
                    for i, cat_a in enumerate(cat_list):
                        for cat_b in cat_list[i + 1:]:
                            pair = tuple(sorted([cat_a, cat_b]))
                            category_pairs[pair] += 1

                # Format results
                result = {}
                for (cat_a, cat_b), count in category_pairs.most_common(20):
                    key = f"{cat_a} <-> {cat_b}"
                    result[key] = {
                        'category_a': cat_a,
                        'category_b': cat_b,
                        'co_occurrence_count': count
                    }

                return result

        except Exception as e:
            logger.error(f"Error analyzing category relationships: {str(e)}")
            return {}

    def persist_skill_relationships(self) -> int:
        """
        Persist skill relationships to the database.

        Analyzes current co-occurrences and updates SkillRelationship table.

        Returns:
            Number of relationships persisted
        """
        if not self.db:
            return 0

        try:
            from app import app
            from models import SkillRelationship
            from sqlalchemy import func

            cooccurrences = self.get_skill_cooccurrences()

            with app.app_context():
                count = 0

                for skill_a, related_skills in cooccurrences.items():
                    for skill_b, strength in related_skills.items():
                        if strength >= self.min_cooccurrence_threshold:
                            # Skip if relationship already exists and is newer
                            existing = SkillRelationship.query.filter(
                                ((SkillRelationship.skill_a_id == skill_a) &
                                 (SkillRelationship.skill_b_id == skill_b)) |
                                ((SkillRelationship.skill_a_id == skill_b) &
                                 (SkillRelationship.skill_b_id == skill_a))
                            ).first()

                            if existing:
                                # Update co-occurrence strength
                                existing.co_occurrence_count = strength
                                existing.last_updated = datetime.utcnow()
                            else:
                                # Create new relationship
                                # Ensure consistent ordering (lower ID first)
                                if skill_a < skill_b:
                                    rel = SkillRelationship(
                                        skill_a_id=skill_a,
                                        skill_b_id=skill_b,
                                        co_occurrence_count=strength,
                                        relationship_strength=self._calculate_strength(strength),
                                        relationship_type='co-occurrence',
                                        last_updated=datetime.utcnow()
                                    )
                                else:
                                    rel = SkillRelationship(
                                        skill_a_id=skill_b,
                                        skill_b_id=skill_a,
                                        co_occurrence_count=strength,
                                        relationship_strength=self._calculate_strength(strength),
                                        relationship_type='co-occurrence',
                                        last_updated=datetime.utcnow()
                                    )

                                self.db.session.add(rel)
                                count += 1

                self.db.session.commit()
                logger.info(f"Persisted {count} skill relationships")
                return count

        except Exception as e:
            logger.error(f"Error persisting skill relationships: {str(e)}")
            self.db.session.rollback()
            return 0

    def _calculate_strength(self, co_occurrence_count: int) -> str:
        """
        Calculate relationship strength based on co-occurrence count.

        Args:
            co_occurrence_count: Number of co-occurrences

        Returns:
            Strength level: 'very_weak', 'weak', 'moderate', 'strong', 'very_strong'
        """
        if co_occurrence_count < 2:
            return 'very_weak'
        elif co_occurrence_count < 5:
            return 'weak'
        elif co_occurrence_count < 10:
            return 'moderate'
        elif co_occurrence_count < 20:
            return 'strong'
        else:
            return 'very_strong'

    def recommend_related_skills(self, skills: List[str], top_n: int = 5) -> List[Dict]:
        """
        Recommend skills that often appear with a given set of skills.

        Args:
            skills: List of skill names
            top_n: Number of recommendations to return

        Returns:
            List of recommended skills with scores
        """
        if not self.db or not skills:
            return []

        try:
            from app import app
            from models import Keyword

            with app.app_context():
                # Find keyword IDs for input skills
                skill_ids = []
                for skill_name in skills:
                    keyword = Keyword.query.filter_by(keyword=skill_name.lower()).first()
                    if keyword:
                        skill_ids.append(keyword.id)

                if not skill_ids:
                    return []

                # Get co-occurrences
                cooccurrences = self.get_skill_cooccurrences()

                # Find skills that co-occur with any input skill
                recommendation_scores = Counter()
                for skill_id in skill_ids:
                    if skill_id in cooccurrences:
                        for related_skill, strength in cooccurrences[skill_id].items():
                            if related_skill not in skill_ids:  # Don't recommend input skills
                                recommendation_scores[related_skill] += strength

                # Get top recommendations
                result = []
                for recommended_skill_id, score in recommendation_scores.most_common(top_n):
                    keyword = Keyword.query.get(recommended_skill_id)
                    if keyword:
                        result.append({
                            'skill_id': recommended_skill_id,
                            'skill_name': keyword.keyword,
                            'recommendation_score': score,
                            'category': keyword.category
                        })

                return result

        except Exception as e:
            logger.error(f"Error recommending related skills: {str(e)}")
            return []


# Global instance
_analyzer = None


def get_skill_relationship_analyzer(db=None) -> SkillRelationshipAnalyzer:
    """Get or create the global skill relationship analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SkillRelationshipAnalyzer(db=db)
    return _analyzer
