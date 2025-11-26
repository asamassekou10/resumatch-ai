"""
Intelligent Skill Extraction Service

This module provides intelligent skill extraction that works for ANY job field:
1. Spacy Named Entity Recognition (NER)
2. Pattern-based extraction using common skill indicators
3. Noun phrase extraction for potential skills
4. Auto-learning: new skills are added to database dynamically
5. Industry detection from text content
6. Context-aware extraction and confidence scoring
"""

import spacy
import logging
from fuzzywuzzy import fuzz
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import re

logger = logging.getLogger(__name__)

# Comprehensive skill indicators that work across ALL industries
SKILL_INDICATORS = {
    # Universal patterns - works for any field
    'prefixes': [
        'experience with', 'experience in', 'proficient in', 'skilled in',
        'expertise in', 'knowledge of', 'certified in', 'trained in',
        'competent in', 'familiar with', 'understanding of', 'ability to',
        'capable of', 'qualified in', 'specialized in', 'background in'
    ],
    'suffixes': [
        'skills', 'experience', 'certification', 'certified', 'proficiency',
        'expertise', 'knowledge', 'training', 'license', 'licensed'
    ],
    # Context patterns that indicate skills
    'context_patterns': [
        r'(?:required|preferred|must have|should have|need)[:\s]+([^.]+)',
        r'skills?[:\s]+([^.]+)',
        r'qualifications?[:\s]+([^.]+)',
        r'requirements?[:\s]+([^.]+)',
        r'proficien(?:t|cy) (?:in|with) ([^,.]+)',
        r'experience (?:in|with) ([^,.]+)',
        r'knowledge of ([^,.]+)',
        r'certified (?:in|as) ([^,.]+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:certification|license|degree)',
    ]
}

# Industry keywords for auto-detection (covers major fields)
INDUSTRY_DETECTION = {
    'Technology': ['software', 'developer', 'programming', 'api', 'database', 'cloud', 'devops', 'frontend', 'backend', 'fullstack', 'code', 'github', 'agile', 'scrum'],
    'Healthcare': ['patient', 'clinical', 'medical', 'hospital', 'nursing', 'healthcare', 'diagnosis', 'treatment', 'pharmacy', 'physician', 'ehr', 'hipaa', 'veterinary', 'veterinarian', 'animal', 'surgical', 'radiology', 'anesthesia', 'phlebotomy', 'therapy'],
    'Finance': ['accounting', 'financial', 'audit', 'tax', 'banking', 'investment', 'cpa', 'gaap', 'budget', 'reconciliation', 'ledger', 'payroll'],
    'Security': ['cybersecurity', 'security', 'penetration', 'vulnerability', 'firewall', 'siem', 'incident', 'threat', 'compliance', 'cissp'],
    'Marketing': ['marketing', 'seo', 'content', 'social media', 'campaign', 'brand', 'advertising', 'analytics', 'digital marketing'],
    'Sales': ['sales', 'account executive', 'business development', 'pipeline', 'crm', 'quota', 'revenue', 'prospecting', 'closing'],
    'Human Resources': ['hr', 'recruiting', 'talent', 'onboarding', 'benefits', 'compensation', 'employee relations', 'hris', 'performance management'],
    'Education': ['teaching', 'curriculum', 'instruction', 'student', 'classroom', 'academic', 'learning', 'education', 'training'],
    'Legal': ['legal', 'attorney', 'lawyer', 'litigation', 'contract', 'paralegal', 'compliance', 'regulatory'],
    'Manufacturing': ['manufacturing', 'production', 'assembly', 'quality control', 'lean', 'six sigma', 'supply chain', 'logistics'],
    'Construction': ['construction', 'building', 'contractor', 'project management', 'blueprint', 'safety', 'osha'],
    'Hospitality': ['hospitality', 'hotel', 'restaurant', 'customer service', 'guest', 'event planning', 'catering'],
    'Retail': ['retail', 'merchandising', 'inventory', 'point of sale', 'customer', 'store', 'visual merchandising'],
    'Real Estate': ['real estate', 'property', 'broker', 'listing', 'mortgage', 'appraisal', 'escrow'],
    'Transportation': ['transportation', 'logistics', 'shipping', 'fleet', 'cdl', 'freight', 'dispatch'],
    'Agriculture': ['agriculture', 'farming', 'crop', 'livestock', 'irrigation', 'harvest', 'agronomy'],
    'Energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'utilities', 'power'],
    'Government': ['government', 'public sector', 'federal', 'municipal', 'policy', 'administration', 'civil service'],
    'Non-Profit': ['nonprofit', 'fundraising', 'grant', 'volunteer', 'community', 'advocacy', 'outreach'],
    'Media': ['media', 'journalism', 'broadcast', 'publishing', 'content creation', 'video', 'production']
}


@dataclass
class ExtractedSkill:
    """Represents an extracted skill with confidence metrics"""
    skill_name: str
    matched_keyword: Optional[str]  # Matched keyword ID from database
    confidence: float  # 0-1 confidence score
    extraction_method: str  # 'exact', 'fuzzy', 'pattern', 'context'
    context: str  # surrounding text for verification
    position: Tuple[int, int]  # start and end position in text


class SkillExtractor:
    """
    Intelligent skill extractor using Spacy NER and custom patterns.

    This extractor combines:
    - Spacy NER for general skill entity recognition
    - Custom pattern matching against taxonomy
    - Fuzzy matching for typos and variations
    - Context-aware confidence scoring
    """

    def __init__(self, db=None):
        """
        Initialize the skill extractor.

        Args:
            db: SQLAlchemy db instance for loading keywords from database
        """
        self.db = db
        self.nlp = None
        self.keywords_dict = {}  # {keyword_name: keyword_id}
        self.fuzzy_threshold = 85  # Minimum fuzzy match score

        self._initialize_spacy()
        self._load_keywords_from_db()

    def _initialize_spacy(self):
        """Load Spacy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ Spacy model loaded successfully")
        except OSError:
            logger.error("❌ Spacy model not found. Install with: python -m spacy download en_core_web_sm")
            raise

    def _load_keywords_from_db(self):
        """Load keywords from database for matching"""
        if not self.db:
            logger.warning("⚠️  No database provided to SkillExtractor, using empty keyword dict")
            return

        try:
            # Import here to avoid circular imports
            from app import app
            from models import Keyword

            with app.app_context():
                # Load all keywords with their IDs
                keywords = Keyword.query.all()
                for kw in keywords:
                    # Store both exact name and lowercase for matching
                    self.keywords_dict[kw.keyword.lower()] = {
                        'id': kw.id,
                        'name': kw.keyword,
                        'category': kw.category,
                        'priority': kw.priority,
                        'synonyms': kw.synonyms or []
                    }

            logger.info(f"✅ Loaded {len(self.keywords_dict)} keywords from database")
        except Exception as e:
            logger.error(f"❌ Error loading keywords from database: {str(e)}")

    def extract_skills(self, text: str, auto_learn: bool = True) -> List[ExtractedSkill]:
        """
        Extract skills from resume text using multiple intelligent strategies.
        Works for ANY job field by combining:
        - Known keyword matching
        - NLP-based extraction
        - Context pattern matching
        - Auto-learning of new skills

        Args:
            text: Resume or job description text
            auto_learn: Whether to auto-learn new skills (default True)

        Returns:
            List of extracted skills with confidence scores
        """
        if not text or not text.strip():
            return []

        extracted_skills = []
        doc = self.nlp(text)

        # Strategy 1: Pattern-based extraction (exact and fuzzy match against known keywords)
        pattern_skills = self._extract_by_pattern(text, doc)
        extracted_skills.extend(pattern_skills)

        # Strategy 2: Context-aware extraction (uses universal skill patterns)
        context_skills = self._extract_by_context(doc, text)
        extracted_skills.extend(context_skills)

        # Strategy 3: Noun phrase extraction (catches industry-specific terms)
        if auto_learn:
            noun_phrase_skills = self._extract_noun_phrases(doc, text)
            extracted_skills.extend(noun_phrase_skills)

        # Strategy 4: NER-based extraction (organizations, products that might be tools)
        ner_skills = self._extract_by_ner(doc, text)
        extracted_skills.extend(ner_skills)

        # Remove duplicates and keep highest confidence match
        extracted_skills = self._deduplicate_skills(extracted_skills)

        return extracted_skills

    def _extract_by_ner(self, doc, text: str) -> List[ExtractedSkill]:
        """Extract skills using Spacy NER"""
        skills = []

        # Look for PRODUCT entities which often include technologies/frameworks
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG', 'GPE']:
                # Filter for likely skills (short entities, all caps or specific patterns)
                if self._is_likely_skill(ent.text):
                    matched_kw = self._match_keyword(ent.text)

                    skills.append(ExtractedSkill(
                        skill_name=ent.text,
                        matched_keyword=matched_kw['id'] if matched_kw else None,
                        confidence=0.7 if matched_kw else 0.5,
                        extraction_method='ner',
                        context=self._get_context(text, ent.start_char, ent.end_char),
                        position=(ent.start_char, ent.end_char)
                    ))

        return skills

    def _extract_by_pattern(self, text: str, doc) -> List[ExtractedSkill]:
        """Extract skills by matching against known keywords"""
        skills = []
        text_lower = text.lower()

        # Check all keywords in database
        for keyword_lower, kw_info in self.keywords_dict.items():
            # Exact match
            if keyword_lower in text_lower:
                position = text_lower.find(keyword_lower)
                if position >= 0:
                    skills.append(ExtractedSkill(
                        skill_name=kw_info['name'],
                        matched_keyword=kw_info['id'],
                        confidence=1.0,
                        extraction_method='exact',
                        context=self._get_context(text, position, position + len(keyword_lower)),
                        position=(position, position + len(keyword_lower))
                    ))
            else:
                # Fuzzy match for typos/variations
                for word_token in doc:
                    word = word_token.text.lower()
                    fuzzy_score = fuzz.ratio(word, keyword_lower)

                    if fuzzy_score >= self.fuzzy_threshold and word != keyword_lower:
                        skills.append(ExtractedSkill(
                            skill_name=kw_info['name'],
                            matched_keyword=kw_info['id'],
                            confidence=min(1.0, fuzzy_score / 100),
                            extraction_method='fuzzy',
                            context=self._get_context(text, word_token.idx, word_token.idx + len(word)),
                            position=(word_token.idx, word_token.idx + len(word))
                        ))

                # Check synonyms
                for synonym in kw_info['synonyms']:
                    if synonym.lower() in text_lower:
                        position = text_lower.find(synonym.lower())
                        skills.append(ExtractedSkill(
                            skill_name=kw_info['name'],
                            matched_keyword=kw_info['id'],
                            confidence=0.95,
                            extraction_method='synonym',
                            context=self._get_context(text, position, position + len(synonym)),
                            position=(position, position + len(synonym))
                        ))

        return skills

    def _extract_by_context(self, doc, text: str) -> List[ExtractedSkill]:
        """
        Extract skills using context clues - works for ANY job field.
        Uses universal patterns that indicate skills across all industries.
        """
        skills = []

        # Use comprehensive patterns from SKILL_INDICATORS
        for pattern in SKILL_INDICATORS['context_patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill_text = match.group(1).strip() if match.lastindex else match.group(0).strip()

                # Split by common delimiters and process each potential skill
                potential_skills = re.split(r'[,;/\n]|(?:\s+and\s+)|\s+or\s+', skill_text)

                for skill_candidate in potential_skills:
                    skill_candidate = skill_candidate.strip()
                    if len(skill_candidate) < 2 or len(skill_candidate) > 50:
                        continue

                    # Try to match against known keywords first
                    matched_kw = self._match_keyword(skill_candidate)

                    if matched_kw:
                        skills.append(ExtractedSkill(
                            skill_name=matched_kw['name'],
                            matched_keyword=matched_kw['id'],
                            confidence=0.85,
                            extraction_method='context',
                            context=match.group(0)[:100],
                            position=(match.start(), min(match.end(), match.start() + 100))
                        ))
                    elif self._is_valid_skill_candidate(skill_candidate):
                        # NEW: Auto-learn unknown skills
                        new_kw_id = self._auto_learn_skill(skill_candidate, text)
                        skills.append(ExtractedSkill(
                            skill_name=skill_candidate,
                            matched_keyword=new_kw_id,
                            confidence=0.70,  # Lower confidence for auto-learned
                            extraction_method='auto_learned',
                            context=match.group(0)[:100],
                            position=(match.start(), min(match.end(), match.start() + 100))
                        ))

        return skills

    def _extract_noun_phrases(self, doc, text: str) -> List[ExtractedSkill]:
        """
        Extract potential skills from noun phrases - works for ANY job field.
        This catches industry-specific terms that aren't in patterns.
        """
        skills = []

        for chunk in doc.noun_chunks:
            # Filter for likely skill phrases
            chunk_text = chunk.text.strip()

            # Skip common non-skill phrases
            if self._is_common_phrase(chunk_text):
                continue

            # Check if it matches known keywords
            matched_kw = self._match_keyword(chunk_text)

            if matched_kw:
                skills.append(ExtractedSkill(
                    skill_name=matched_kw['name'],
                    matched_keyword=matched_kw['id'],
                    confidence=0.75,
                    extraction_method='noun_phrase',
                    context=self._get_context(text, chunk.start_char, chunk.end_char),
                    position=(chunk.start_char, chunk.end_char)
                ))
            elif self._is_valid_skill_candidate(chunk_text) and len(chunk_text) > 3:
                # Only auto-learn noun phrases that look like skills
                if self._looks_like_skill(chunk_text, doc, chunk):
                    new_kw_id = self._auto_learn_skill(chunk_text, text)
                    if new_kw_id:
                        skills.append(ExtractedSkill(
                            skill_name=chunk_text,
                            matched_keyword=new_kw_id,
                            confidence=0.60,
                            extraction_method='noun_phrase_learned',
                            context=self._get_context(text, chunk.start_char, chunk.end_char),
                            position=(chunk.start_char, chunk.end_char)
                        ))

        return skills

    def _looks_like_skill(self, text: str, doc, chunk) -> bool:
        """
        Determine if a noun phrase looks like a skill based on context.
        """
        text_lower = text.lower()

        # Check for skill-indicator words nearby
        context_start = max(0, chunk.start - 10)
        context_end = min(len(doc), chunk.end + 10)
        context_tokens = [t.text.lower() for t in doc[context_start:context_end]]

        skill_context_words = {'experience', 'skills', 'proficient', 'knowledge',
                               'certified', 'trained', 'expertise', 'ability',
                               'competent', 'required', 'preferred', 'must'}

        if any(word in skill_context_words for word in context_tokens):
            return True

        # Acronyms are often skills (CPA, HIPAA, AWS, etc.)
        if text.isupper() and len(text) >= 2:
            return True

        # Title case proper nouns often are (QuickBooks, Salesforce, etc.)
        if text[0].isupper() and ' ' not in text and len(text) > 2:
            return True

        return False

    def _is_valid_skill_candidate(self, text: str) -> bool:
        """Check if text could be a valid skill name."""
        if not text or len(text) < 2 or len(text) > 50:
            return False

        # Filter out common stop words and articles
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                      'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                      'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                      'will', 'would', 'could', 'should', 'may', 'might', 'must',
                      'shall', 'can', 'need', 'our', 'your', 'their', 'this', 'that',
                      'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}

        if text.lower() in stop_words:
            return False

        # Must contain at least one letter
        if not any(c.isalpha() for c in text):
            return False

        return True

    def _is_common_phrase(self, text: str) -> bool:
        """Check if text is a common non-skill phrase."""
        text_lower = text.lower()

        common_phrases = {
            'the company', 'our team', 'this position', 'the role', 'the job',
            'a team', 'the candidate', 'applicants', 'years', 'experience',
            'responsibilities', 'duties', 'requirements', 'qualifications',
            'benefits', 'salary', 'compensation', 'location', 'office',
            'full time', 'part time', 'remote', 'hybrid', 'on site',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'equal opportunity', 'diversity', 'inclusion'
        }

        return text_lower in common_phrases or len(text) > 40

    def _auto_learn_skill(self, skill_name: str, context: str) -> Optional[int]:
        """
        Auto-learn a new skill by adding it to the database.
        This makes the system intelligent and self-improving.
        """
        if not self.db or not skill_name:
            return None

        try:
            from app import app
            from models import Keyword

            with app.app_context():
                # Check if already exists (case-insensitive)
                existing = Keyword.query.filter(
                    Keyword.keyword.ilike(skill_name)
                ).first()

                if existing:
                    return existing.id

                # Detect industry from context
                detected_industry = self.detect_industry(context)

                # Create new keyword
                new_keyword = Keyword(
                    keyword=skill_name,
                    keyword_type='skill',
                    category=detected_industry or 'General',
                    priority='normal',
                    source='auto_learned',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self.db.session.add(new_keyword)
                self.db.session.commit()

                # Add to local cache
                self.keywords_dict[skill_name.lower()] = {
                    'id': new_keyword.id,
                    'name': skill_name,
                    'category': detected_industry or 'General',
                    'priority': 'normal',
                    'synonyms': []
                }

                logger.info(f"Auto-learned new skill: {skill_name} (industry: {detected_industry})")
                return new_keyword.id

        except Exception as e:
            logger.warning(f"Failed to auto-learn skill '{skill_name}': {str(e)}")
            return None

    def detect_industry(self, text: str) -> Optional[str]:
        """
        Intelligently detect the industry from text content.
        Works for ANY industry by matching against known patterns.
        """
        if not text:
            return None

        text_lower = text.lower()
        industry_scores = Counter()

        for industry, keywords in INDUSTRY_DETECTION.items():
            for keyword in keywords:
                if keyword in text_lower:
                    industry_scores[industry] += 1

        if industry_scores:
            # Return the industry with highest score
            return industry_scores.most_common(1)[0][0]

        return None

    def get_industry_skills(self, industry: str) -> List[Dict]:
        """
        Get skills commonly associated with an industry.
        """
        if not self.db:
            return []

        try:
            from app import app
            from models import Keyword

            with app.app_context():
                skills = Keyword.query.filter(
                    Keyword.category == industry
                ).order_by(Keyword.extraction_count.desc().nullsfirst()).limit(50).all()

                return [{'id': s.id, 'name': s.keyword, 'category': s.category} for s in skills]
        except Exception as e:
            logger.warning(f"Failed to get industry skills: {str(e)}")
            return []

    def _is_likely_skill(self, text: str) -> bool:
        """
        Check if text is likely to be a skill name.
        Works across ALL industries, not just tech.
        """
        # Filter out very long entities (usually not skills)
        if len(text) > 40:
            return False

        # Filter out single letters
        if len(text) <= 1:
            return False

        text_lower = text.lower()

        # Check if it's already a known keyword
        if text_lower in self.keywords_dict:
            return True

        # Acronyms are often certifications/tools (CPA, HIPAA, AWS, etc.)
        if text.isupper() and 2 <= len(text) <= 10:
            return True

        # Check for common skill-indicating patterns
        skill_patterns = [
            r'\d',  # Contains numbers (Python3, .NET 4.0, etc.)
            r'[+#]',  # Contains special chars (C++, C#)
            r'\.',  # Contains dots (.NET, Node.js)
        ]

        for pattern in skill_patterns:
            if re.search(pattern, text):
                return True

        # Title case words are often proper nouns/tools
        if text[0].isupper() and not text.isupper():
            return True

        return False

    def _match_keyword(self, text: str) -> Optional[Dict]:
        """
        Match text against known keywords.

        Returns:
            Matched keyword info or None
        """
        text_lower = text.lower().strip()

        # Exact match
        if text_lower in self.keywords_dict:
            return self.keywords_dict[text_lower]

        # Fuzzy match
        best_match = None
        best_score = 0

        for keyword_lower, kw_info in self.keywords_dict.items():
            score = fuzz.ratio(text_lower, keyword_lower)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = kw_info

        return best_match

    def _get_context(self, text: str, start: int, end: int, context_length: int = 50) -> str:
        """
        Get surrounding context of extracted skill.

        Args:
            text: Full text
            start: Start position
            end: End position
            context_length: Number of characters on each side

        Returns:
            Context string
        """
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        return text[context_start:context_end].strip()

    def _deduplicate_skills(self, skills: List[ExtractedSkill]) -> List[ExtractedSkill]:
        """
        Remove duplicate skill extractions, keeping the highest confidence match.

        Args:
            skills: List of extracted skills

        Returns:
            Deduplicated list
        """
        seen = {}  # {skill_name: highest_confidence_skill}

        for skill in sorted(skills, key=lambda s: s.confidence, reverse=True):
            skill_key = skill.matched_keyword or skill.skill_name.lower()

            if skill_key not in seen:
                seen[skill_key] = skill

        return list(seen.values())

    def get_extraction_confidence(self, skill: ExtractedSkill) -> float:
        """
        Calculate final confidence score for extracted skill.

        Takes into account:
        - Extraction method confidence
        - Keyword priority
        - Context quality

        Args:
            skill: Extracted skill

        Returns:
            Final confidence score (0-1)
        """
        # Base confidence from extraction method
        base_confidence = skill.confidence

        # Boost for exact matches
        if skill.extraction_method == 'exact':
            base_confidence = min(1.0, base_confidence * 1.1)

        # Reduce for fuzzy matches
        elif skill.extraction_method == 'fuzzy':
            base_confidence = base_confidence * 0.9

        # Moderate boost for context-based extraction
        elif skill.extraction_method == 'context':
            base_confidence = min(1.0, base_confidence * 1.05)

        return min(1.0, base_confidence)

    def get_method_accuracy(self, extraction_method: str) -> float:
        """
        Get historical accuracy of a specific extraction method based on user feedback.

        Args:
            extraction_method: Method to evaluate ('exact', 'fuzzy', 'pattern', 'context', 'ner')

        Returns:
            Accuracy score (0-1) based on user confirmations vs rejections
        """
        if not self.db:
            return 0.5  # Default neutral accuracy

        try:
            from app import app
            from models import SkillExtraction

            with app.app_context():
                # Get all extractions with this method
                extractions = SkillExtraction.query.filter_by(
                    extraction_method=extraction_method
                ).all()

                if not extractions:
                    return 0.7  # Default confidence for new methods

                # Calculate accuracy based on feedback
                total = len(extractions)
                confirmed = sum(1 for e in extractions if e.user_confirmed)
                rejected = sum(1 for e in extractions if e.user_rejected)

                if confirmed + rejected == 0:
                    return 0.5  # No feedback yet, neutral

                accuracy = confirmed / (confirmed + rejected)
                return accuracy

        except Exception as e:
            logger.warning(f"Could not calculate method accuracy: {str(e)}")
            return 0.5

    def get_skill_extraction_history(self, skill_name: str) -> Dict:
        """
        Get historical extraction data for a skill to inform future extractions.

        Args:
            skill_name: Skill name to look up

        Returns:
            Dictionary with extraction history and confidence adjustments
        """
        if not self.db:
            return {}

        try:
            from app import app
            from models import SkillExtraction, Keyword

            with app.app_context():
                # Find keyword by name
                keyword = Keyword.query.filter_by(keyword=skill_name.lower()).first()

                if not keyword:
                    return {}

                # Get all extractions that matched this keyword
                extractions = SkillExtraction.query.filter_by(
                    matched_keyword_id=keyword.id
                ).all()

                if not extractions:
                    return {}

                # Analyze extraction history
                total = len(extractions)
                confirmed = sum(1 for e in extractions if e.user_confirmed)
                rejected = sum(1 for e in extractions if e.user_rejected)
                avg_confidence = sum(e.confidence for e in extractions) / total

                return {
                    'total_extractions': total,
                    'confirmed': confirmed,
                    'rejected': rejected,
                    'accuracy': confirmed / (confirmed + rejected) if (confirmed + rejected) > 0 else None,
                    'average_confidence': round(avg_confidence, 3),
                    'methods_used': list(set(e.extraction_method for e in extractions if e.extraction_method))
                }

        except Exception as e:
            logger.warning(f"Could not retrieve extraction history: {str(e)}")
            return {}

    def adjust_confidence_with_feedback(self, skill: ExtractedSkill) -> float:
        """
        Adjust skill extraction confidence based on historical user feedback.

        Uses:
        - Method accuracy based on user confirmations/rejections
        - Skill-specific extraction accuracy
        - Overall extraction quality scores

        Args:
            skill: Extracted skill

        Returns:
            Adjusted confidence score (0-1)
        """
        base_confidence = skill.confidence

        # Adjust based on extraction method accuracy
        method_accuracy = self.get_method_accuracy(skill.extraction_method)
        method_adjustment = (method_accuracy - 0.5) * 0.2  # Max ±10% adjustment

        # Adjust based on skill extraction history
        history = self.get_skill_extraction_history(skill.skill_name)
        if history and history.get('accuracy') is not None:
            history_adjustment = (history['accuracy'] - 0.5) * 0.15  # Max ±7.5% adjustment
        else:
            history_adjustment = 0

        # Calculate final adjusted confidence
        adjusted = base_confidence + method_adjustment + history_adjustment
        return min(1.0, max(0.0, adjusted))


# Global instance (lazy loaded)
_extractor = None


def get_skill_extractor(db=None) -> SkillExtractor:
    """
    Get or create the global skill extractor instance.

    Args:
        db: SQLAlchemy db instance (optional, for initialization)

    Returns:
        SkillExtractor instance
    """
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor(db=db)
    return _extractor


def extract_skills_from_resume(resume_text: str) -> List[ExtractedSkill]:
    """
    Convenience function to extract skills from resume text.

    Args:
        resume_text: Resume or job description text

    Returns:
        List of extracted skills
    """
    extractor = get_skill_extractor()
    return extractor.extract_skills(resume_text)
