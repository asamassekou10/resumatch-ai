"""
Intelligent Resume Analysis Engine - Using Google Gemini AI
Industry-agnostic, AI-driven resume scoring and ATS optimization
"""

import os
import json
import logging
import time
import re
import hashlib
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
import google.api_core.exceptions
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception_message,
    before_sleep_log
)

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini Pro (faster, cheaper for text analysis)
MODEL_NAME = "gemini-2.0-flash"

# Timeout and retry configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds


# Global semaphore to limit concurrent Gemini API calls
# Prevents hitting rate limits: max 10 concurrent calls across all users
GEMINI_SEMAPHORE = Semaphore(10)

def retry_on_error(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Legacy retry decorator - kept for backward compatibility.
    New code should use _call_gemini_with_rate_limit which includes tenacity retry.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()

                    # Check if it's a retryable error
                    is_retryable = any(keyword in error_msg for keyword in [
                        'timeout', 'rate limit', 'quota', 'unavailable',
                        'connection', 'deadline', 'resource exhausted'
                    ])

                    if attempt < max_retries and is_retryable:
                        wait_time = delay * (attempt + 1)  # Exponential backoff
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        if attempt == max_retries:
                            logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        break

            raise last_exception
        return wrapper
    return decorator


class IntelligentResumeAnalyzer:
    """
    Industry-agnostic resume analyzer using Google Gemini AI
    Provides semantic matching, ATS optimization, and intelligent recommendations
    With timeout handling, retry logic, and multilingual support
    """

    # Language instruction templates for multilingual AI responses
    LANGUAGE_INSTRUCTIONS = {
        'en': 'Respond entirely in English.',
        'fr': 'Répondez entièrement en français. Utilisez un ton professionnel.',
        'de': 'Antworten Sie vollständig auf Deutsch. Verwenden Sie einen professionellen Ton.',
        'es': 'Responda completamente en español. Use un tono profesional.',
        'nl': 'Antwoord volledig in het Nederlands. Gebruik een professionele toon.',
        'pt': 'Responda inteiramente em português. Use um tom profissional.',
        'it': 'Rispondi interamente in italiano. Usa un tono professionale.',
        'pl': 'Odpowiedz w całości po polsku. Użyj profesjonalnego tonu.',
        'ru': 'Отвечайте полностью на русском языке. Используйте профессиональный тон.',
        'zh': '请完全用中文回复。使用专业的语气。',
        'ja': '日本語で完全に回答してください。プロフェッショナルなトーンを使用してください。',
        'ko': '한국어로 완전히 응답하세요. 전문적인 어조를 사용하세요.',
        'ar': 'أجب بالكامل باللغة العربية. استخدم نبرة مهنية.',
        'hi': 'कृपया पूरी तरह से हिंदी में उत्तर दें। पेशेवर लहजे का प्रयोग करें।',
    }

    SUPPORTED_LANGUAGES = list(LANGUAGE_INSTRUCTIONS.keys())

    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.2,  # Lower temperature for more consistent/deterministic results
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        self.request_options = {
            'timeout': DEFAULT_TIMEOUT
        }
        self._language_cache = {}  # Cache for detected languages

    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of the given text.
        Returns ISO 639-1 two-letter language code.
        """
        if not text or len(text.strip()) < 50:
            return 'en'

        # Check cache first
        cache_key = hash(text[:200])
        if cache_key in self._language_cache:
            return self._language_cache[cache_key]

        text_sample = text[:1000]
        prompt = f"""Analyze this text and determine its primary language.
Return ONLY the ISO 639-1 two-letter language code (lowercase).
Supported codes: en, fr, de, es, nl, pt, it, pl, ru, zh, ja, ko, ar, hi
If unsure, return 'en'.

Text: {text_sample}

Response (just the code):"""

        try:
            response = self.model.generate_content(
                prompt,
                request_options={'timeout': 10}
            )
            if response and response.text:
                detected = response.text.strip().lower()[:2]
                if detected in self.SUPPORTED_LANGUAGES:
                    logger.info(f"Detected language: {detected}")
                    self._language_cache[cache_key] = detected
                    return detected
            return 'en'
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'

    def _get_language_instruction(self, language: str) -> str:
        """Get the language instruction for prompts"""
        return self.LANGUAGE_INSTRUCTIONS.get(language, self.LANGUAGE_INSTRUCTIONS['en'])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((
            google.api_core.exceptions.ResourceExhausted,
            google.api_core.exceptions.ServiceUnavailable,
            google.api_core.exceptions.DeadlineExceeded
        )) | retry_if_exception_message(match=r"(?i)(rate limit|quota|429|resource exhausted|deadline exceeded)"),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _call_gemini_safe(self, prompt: str, operation_name: str) -> str:
        """
        Call Gemini API with tenacity-based retry logic.
        Handles rate limits, timeouts, and transient errors with exponential backoff.
        """
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        if response and response.text:
            return response.text.strip()
        else:
            raise ValueError(f"Empty response from Gemini API for {operation_name}")

    def _call_gemini_with_rate_limit(self, prompt: str, operation_name: str) -> str:
        """
        Call Gemini API with semaphore-based rate limiting + tenacity retry.
        Semaphore ensures max 10 concurrent calls globally to prevent 429 errors.
        """
        # Acquire semaphore (blocks if 10 calls already in progress)
        logger.debug(f"Acquiring semaphore for {operation_name} (available: {GEMINI_SEMAPHORE._value})")
        with GEMINI_SEMAPHORE:
            logger.debug(f"Semaphore acquired for {operation_name}")
            try:
                return self._call_gemini_safe(prompt, operation_name)
            finally:
                logger.debug(f"Semaphore released for {operation_name}")

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_job_requirements(self, prompt: str) -> str:
        """Protected method to call Gemini API with retry logic"""
        return self._call_gemini_with_rate_limit(prompt, "job_requirements")

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_resume_parsing(self, prompt: str) -> str:
        """Protected method to call Gemini API for resume parsing"""
        return self._call_gemini_with_rate_limit(prompt, "resume_parsing")

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_matching(self, prompt: str) -> str:
        """Protected method to call Gemini API for matching analysis"""
        return self._call_gemini_with_rate_limit(prompt, "matching_analysis")

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_ats_optimization(self, prompt: str) -> str:
        """Protected method to call Gemini API for ATS optimization"""
        return self._call_gemini_with_rate_limit(prompt, "ats_optimization")

    @retry_on_error(max_retries=MAX_RETRIES)
    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_recommendations(self, prompt: str) -> str:
        """Protected method to call Gemini API for recommendations"""
        return self._call_gemini_with_rate_limit(prompt, "recommendations")

    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Use Gemini to intelligently extract job requirements
        Distinguishes required vs preferred skills and identifies knockout criteria
        Works for ANY industry - no hardcoding needed
        """
        logger.info("Extracting job requirements with Gemini...")

        prompt = f"""Extract job requirements as JSON. Distinguish required_skills (must-have) vs preferred_skills (nice-to-have). Hard_requirements = knockout criteria.

Job: {job_description[:1500]}

JSON structure:
{{
    "required_skills": ["must-have"],
    "preferred_skills": ["nice-to-have"],
    "hard_requirements": ["knockouts like '5+ years'"],
    "core_skills": ["essential"],
    "soft_skills": ["communication", "leadership"],
    "experience_required": {{"minimum_years": 5, "field": "field", "description": "X+ years"}},
    "experience_level": "entry/mid/senior",
    "industry": "industry",
    "key_responsibilities": ["duties"],
    "nice_to_have": ["optional"],
    "keywords": ["terms"],
    "tools_technologies": ["tech"],
    "salary_range": "range",
    "location_requirements": "location",
    "education_requirements": {{"required": "degree", "preferred": "higher"}}
}}"""

        try:
            response_text = self._call_gemini_for_job_requirements(prompt)

            # Clean up markdown if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            
            # Normalize structure: ensure required/preferred fields exist, handle backward compatibility
            result = self._normalize_job_requirements(result)
            
            logger.info(f"Successfully extracted job requirements for {result.get('industry', 'unknown')} role")
            logger.info(f"Required skills: {len(result.get('required_skills', []))}, Preferred: {len(result.get('preferred_skills', []))}, Hard requirements: {len(result.get('hard_requirements', []))}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse job requirements JSON: {e}")
            return self._get_default_job_analysis()
        except Exception as e:
            logger.error(f"Error extracting job requirements: {e}")
            return self._get_default_job_analysis()

    def _normalize_job_requirements(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job requirements structure to ensure required/preferred fields exist.
        Handles backward compatibility with old format.
        """
        default = self._get_default_job_analysis()
        
        # Ensure required_skills exists
        if "required_skills" not in result or not result.get("required_skills"):
            # Try to infer from core_skills if required_skills missing
            if "core_skills" in result and result["core_skills"]:
                result["required_skills"] = result["core_skills"]
            else:
                result["required_skills"] = []
        
        # Ensure preferred_skills exists
        if "preferred_skills" not in result:
            # Use nice_to_have if preferred_skills missing
            if "nice_to_have" in result and result["nice_to_have"]:
                result["preferred_skills"] = result["nice_to_have"]
            else:
                result["preferred_skills"] = []
        
        # Ensure hard_requirements exists
        if "hard_requirements" not in result:
            result["hard_requirements"] = []
        
        # Normalize experience_required structure
        if "experience_required" in result:
            if isinstance(result["experience_required"], str):
                # Old format - try to parse
                exp_str = result["experience_required"]
                result["experience_required"] = {
                    "minimum_years": 0,
                    "field": "Unknown",
                    "preferred_years": 0,
                    "description": exp_str
                }
            elif not isinstance(result["experience_required"], dict):
                result["experience_required"] = default["experience_required"]
        else:
            result["experience_required"] = default["experience_required"]
        
        # Normalize education_requirements
        if "education_requirements" not in result:
            result["education_requirements"] = default["education_requirements"]
        
        return result

    def _normalize_match_analysis(self, result: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize match_analysis structure to ensure new format exists.
        Handles backward compatibility with old format.
        """
        # Ensure match_breakdown exists
        if "match_breakdown" not in result:
            result["match_breakdown"] = {}
        
        breakdown = result["match_breakdown"]
        
        # Normalize skill_alignment
        if "skill_alignment" not in breakdown:
            # Try to create from old format or defaults
            breakdown["skill_alignment"] = {
                "matched_required_skills": [],
                "missing_required_skills": job_requirements.get("required_skills", []),
                "matched_preferred_skills": [],
                "total_required": len(job_requirements.get("required_skills", [])),
                "total_preferred": len(job_requirements.get("preferred_skills", [])),
                "score": 50
            }
        elif isinstance(breakdown["skill_alignment"], (int, float)):
            # Old format: just a number
            old_score = breakdown["skill_alignment"]
            breakdown["skill_alignment"] = {
                "matched_required_skills": [],
                "missing_required_skills": [],
                "matched_preferred_skills": [],
                "total_required": len(job_requirements.get("required_skills", [])),
                "total_preferred": len(job_requirements.get("preferred_skills", [])),
                "score": old_score
            }
        
        # Normalize experience_fit
        if "experience_fit" not in breakdown:
            exp_req = job_requirements.get("experience_required", {})
            if isinstance(exp_req, dict):
                min_years = exp_req.get("minimum_years", 0)
            else:
                min_years = 0
            
            breakdown["experience_fit"] = {
                "required_years": min_years,
                "resume_years": 0,
                "gap": min_years,
                "level_match": "unknown",
                "education_match": False,
                "score": 50
            }
        elif isinstance(breakdown["experience_fit"], (int, float)):
            old_score = breakdown["experience_fit"]
            exp_req = job_requirements.get("experience_required", {})
            if isinstance(exp_req, dict):
                min_years = exp_req.get("minimum_years", 0)
            else:
                min_years = 0
            
            breakdown["experience_fit"] = {
                "required_years": min_years,
                "resume_years": 0,
                "gap": min_years,
                "level_match": "unknown",
                "education_match": False,
                "score": old_score
            }
        
        # Normalize content_quality
        if "content_quality" not in breakdown:
            breakdown["content_quality"] = {
                "quantifiable_achievements_count": 0,
                "action_verbs_count": 0,
                "summary_quality": "unknown",
                "achievements_vs_duties_ratio": 0.0,
                "score": 50
            }
        elif isinstance(breakdown["content_quality"], (int, float)):
            breakdown["content_quality"] = {
                "quantifiable_achievements_count": 0,
                "action_verbs_count": 0,
                "summary_quality": "unknown",
                "achievements_vs_duties_ratio": 0.0,
                "score": breakdown["content_quality"]
            }
        
        # Normalize job_specific_match
        if "job_specific_match" not in breakdown:
            breakdown["job_specific_match"] = {
                "industry_relevance": breakdown.get("industry_relevance", 50),
                "role_title_alignment": 50,
                "tools_technologies_match": 50,
                "score": 50
            }
        elif isinstance(breakdown["job_specific_match"], (int, float)):
            breakdown["job_specific_match"] = {
                "industry_relevance": breakdown.get("industry_relevance", 50),
                "role_title_alignment": 50,
                "tools_technologies_match": 50,
                "score": breakdown["job_specific_match"]
            }
        
        # Normalize ats_readability (will be merged with heuristics later)
        if "ats_readability" not in breakdown:
            breakdown["ats_readability"] = {
                "chronological_order_valid": True,
                "section_structure_clear": True,
                "parse_ability_assessment": "unknown",
                "score": 50
            }
        elif isinstance(breakdown["ats_readability"], (int, float)):
            breakdown["ats_readability"] = {
                "chronological_order_valid": True,
                "section_structure_clear": True,
                "parse_ability_assessment": "unknown",
                "score": breakdown["ats_readability"]
            }
        
        # Ensure hard_filter_violations exists
        if "hard_filter_violations" not in result:
            result["hard_filter_violations"] = []
        
        # Ensure keywords_missing has proper structure
        if "keywords_missing" in result:
            for kw in result["keywords_missing"]:
                if isinstance(kw, str):
                    # Convert string to dict
                    idx = result["keywords_missing"].index(kw)
                    result["keywords_missing"][idx] = {
                        "keyword": kw,
                        "importance": "unknown",
                        "penalty": 5,
                        "why_matters": ""
                    }
                elif isinstance(kw, dict):
                    # Ensure required fields exist
                    if "importance" not in kw:
                        kw["importance"] = "unknown"
                    if "penalty" not in kw:
                        kw["penalty"] = 10 if kw.get("importance") == "required" else 2
        
        # Ensure bonuses exists
        if "bonuses" not in result:
            result["bonuses"] = []
        
        return result

    def extract_resume_content(self, resume_text: str) -> Dict[str, Any]:
        """
        Use Gemini to intelligently parse resume
        Understands professional context, soft skills, achievements
        """
        logger.info("Parsing resume content with Gemini...")

        prompt = f"""Extract resume info as JSON. Ignore contact details.

Resume: {resume_text[:3000]}

JSON:
{{
    "summary": "1-sentence summary",
    "technical_skills": ["skills"],
    "soft_skills": ["communication", "leadership"],
    "years_experience_total": 5,
    "years_in_primary_field": 3,
    "experience_level": "entry/mid/senior/expert",
    "industries_worked_in": ["industries"],
    "key_accomplishments": ["achievements"],
    "education": {{"degree": "degree", "field": "field"}},
    "certifications": ["certs"],
    "languages": ["langs"],
    "ats_readability": {{"structure_clarity": 85, "formatting_issues": [], "missing_sections": []}}
}}"""

        try:
            response_text = self._call_gemini_for_resume_parsing(prompt)

            # Clean up markdown if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            logger.info(f"Successfully parsed resume ({result.get('experience_level', 'unknown')} level)")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resume JSON: {e}")
            return self._get_default_resume_analysis()
        except Exception as e:
            logger.error(f"Error extracting resume content: {e}")
            return self._get_default_resume_analysis()

    def intelligent_match_analysis(
        self,
        job_requirements: Dict[str, Any],
        resume_content: Dict[str, Any],
        job_description: str,
        resume_text: str,
    ) -> Dict[str, Any]:
        """
        Use Gemini to intelligently match resume to job
        Understands semantic relationships, transferable skills, context
        """
        logger.info("Performing semantic matching analysis...")

        prompt = f"""Analyze resume vs job match. Provide RAW DATA only - Python calculates final score.

Job: {json.dumps(job_requirements, indent=1)[:800]}
Resume: {json.dumps(resume_content, indent=1)[:800]}

Return ONLY valid JSON (no markdown, no code blocks) with this structure:
{{
    "match_breakdown": {{
        "skill_alignment": {{
            "matched_required_skills": ["Python", "AWS"],
            "missing_required_skills": ["Docker"],
            "matched_preferred_skills": ["Kubernetes"],
            "total_required": 5,
            "total_preferred": 3,
            "score": 75
        }},
        "experience_fit": {{
            "required_years": 5,
            "resume_years": 4,
            "gap": 1,
            "level_match": "mid",
            "education_match": true,
            "score": 85
        }},
        "content_quality": {{
            "quantifiable_achievements_count": 5,
            "action_verbs_count": 12,
            "summary_quality": "good",
            "achievements_vs_duties_ratio": 0.7,
            "score": 80
        }},
        "job_specific_match": {{
        "industry_relevance": 85,
            "role_title_alignment": 75,
            "tools_technologies_match": 80,
            "score": 80
        }},
        "ats_readability": {{
            "chronological_order_valid": true,
            "section_structure_clear": true,
            "parse_ability_assessment": "good",
            "score": 85
        }}
    }},
    "hard_filter_violations": [
        {{
            "type": "missing_critical_keyword",
            "keyword": "Python",
            "severity": "critical"
        }}
    ],
    "strengths": [
        {{
            "category": "skill",
            "strength": "description",
            "relevance": "why it matters for this role"
        }}
    ],
    "gaps": [
        {{
            "category": "skill",
            "gap": "what's missing",
            "severity": "critical/important/nice_to_have",
            "how_to_improve": "specific recommendation"
        }}
    ],
    "keywords_present": ["top 10 keywords from job that appear in resume"],
    "keywords_missing": [
        {{
            "keyword": "Docker",
            "importance": "required",
            "penalty": 10,
            "why_matters": "context"
        }},
        {{
            "keyword": "Kubernetes",
            "importance": "preferred",
            "penalty": 2,
            "why_matters": "context"
        }}
    ],
    "transferable_skills": [
        {{
            "resume_skill": "what's in resume",
            "matches_job_need": "what job needs",
            "explanation": "why it transfers"
        }}
    ],
    "bonuses": [
        {{
            "reason": "Exceptional quantifiable achievements",
            "points": 5,
            "category": "content_quality"
        }}
    ],
    "ats_pass_likelihood": 75,
    "interview_likelihood": 70,
    "hiring_recommendation": "strong_candidate/competitive/needs_improvement"
}}

IMPORTANT RULES:
1. For each factor in match_breakdown, provide a score (0-100) based on the raw data
2. Distinguish required_skills from preferred_skills when matching
3. Identify hard_filter_violations (missing critical requirements)
4. Assign penalties to missing keywords (required=higher penalty, preferred=lower)
5. Identify bonuses for exceptional items
6. Do NOT calculate a final overall score - Python will do that

Be honest and realistic in your assessment. This is for professional development."""

        try:
            response_text = self._call_gemini_for_matching(prompt)

            # Clean up markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            
            # Normalize match_analysis structure for backward compatibility
            result = self._normalize_match_analysis(result, job_requirements)
            
            logger.info(f"Match analysis complete - Raw component scores extracted")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse match analysis JSON: {e}")
            return self._get_default_match_analysis()
        except Exception as e:
            logger.error(f"Error in match analysis: {e}")
            return self._get_default_match_analysis()

    def generate_ats_optimization_recommendations(
        self, job_description: str, resume_content: Dict[str, Any], match_analysis: Dict[str, Any],
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Generate specific, natural ways to add keywords for ATS optimization.
        Supports multilingual responses based on the detected resume language.
        """
        logger.info(f"Generating ATS optimization recommendations in {language}...")

        lang_instruction = self._get_language_instruction(language)
        missing_keywords = match_analysis.get("keywords_missing", [])[:10]

        prompt = f"""You are an ATS optimization expert specializing in resume formatting.

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}

Missing Keywords for ATS:
{json.dumps(missing_keywords, indent=2)}

Resume Current Content:
{json.dumps(resume_content, indent=2)}

Generate optimization recommendations in JSON format.
IMPORTANT: All text values in the JSON must be in the same language as specified above.

{{
    "keyword_optimization": [
        {{
            "missing_keyword": "keyword",
            "section": "Skills/Experience/Summary",
            "suggested_addition": "exact phrasing to add",
            "example": "how it appears in context",
            "ats_boost": 5
        }}
    ],
    "natural_integration_tips": [
        "tips to avoid keyword stuffing",
        "how to sound natural while optimizing"
    ],
    "priority_keywords_to_add": [
        "top 5 keywords by impact"
    ],
    "formatting_improvements": [
        "structure/clarity improvements",
        "ATS readability fixes"
    ]
}}

Focus on natural, professional language - not keyword stuffing.
Remember: {lang_instruction}"""

        try:
            response_text = self._call_gemini_for_ats_optimization(prompt)

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            logger.info("ATS optimization recommendations generated")
            return result
        except Exception as e:
            logger.error(f"Error generating ATS recommendations: {e}")
            return {"keyword_optimization": [], "natural_integration_tips": []}

    def generate_intelligent_recommendations(
        self, job_description: str, resume_content: Dict[str, Any], match_analysis: Dict[str, Any],
        industry: str, language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Generate industry-specific, actionable recommendations.
        Supports multilingual responses based on the detected resume language.
        """
        logger.info(f"Generating {industry}-specific recommendations in {language}...")

        lang_instruction = self._get_language_instruction(language)
        gaps = match_analysis.get("gaps", [])[:5]

        prompt = f"""You are a career coach for {industry} professionals.

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}

Resume gaps identified:
{json.dumps(gaps, indent=2)}

Generate industry-specific recommendations in JSON format.
IMPORTANT: All text values in the JSON must be in the same language as specified above.

{{
    "priority_improvements": [
        {{
            "rank": 1,
            "area": "gap category",
            "action": "specific thing to do",
            "why_matters": "industry context",
            "example": "exact phrasing",
            "estimated_impact": 10
        }}
    ],
    "quick_wins": [
        "improvements taking <5 minutes",
        "high impact, low effort"
    ],
    "deep_work": [
        "improvements requiring more effort"
    ],
    "industry_best_practices": [
        "what top {industry} candidates do"
    ],
    "career_path_advice": "guidance for advancement",
    "skill_development_priorities": [
        "skills to develop next"
    ]
}}

Provide concrete, actionable advice specific to {industry}.
Remember: {lang_instruction}"""

        try:
            response_text = self._call_gemini_for_recommendations(prompt)

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            logger.info("Intelligent recommendations generated")
            return result
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {"priority_improvements": [], "quick_wins": []}

    def _check_ats_readability_heuristics(self, resume_text: str) -> Dict[str, Any]:
        """
        Python-based heuristic checks for ATS compatibility.
        LLM cannot see PDF formatting, so we check in Python.
        
        Returns:
            Dict with heuristic scores and issues detected
        """
        checks = {
            "text_extraction_quality": 100,  # Default good
            "parse_errors": [],
            "column_structure_issues": False,
            "non_standard_chars": 0,
            "suspicious_low_length": False,
            "issues": [],
            "score": 100
        }
        
        # Check 1: Text length (image-based PDFs extract poorly)
        text_length = len(resume_text.strip())
        if text_length < 500:
            checks["suspicious_low_length"] = True
            checks["text_extraction_quality"] -= 30
            checks["issues"].append("Resume text is suspiciously short - may be image-based PDF that ATS cannot parse")
        elif text_length < 1000:
            checks["text_extraction_quality"] -= 15
            checks["issues"].append("Resume text is shorter than expected - may have formatting issues")
        
        # Check 2: Non-standard characters (formatting artifacts)
        # Count characters outside normal ASCII printable range (excluding common whitespace)
        non_std_count = 0
        for char in resume_text:
            code = ord(char)
            # Allow: ASCII printable (32-126), newline (10), tab (9), carriage return (13)
            if code > 127 and code not in [8232, 8233]:  # Allow paragraph separators
                non_std_count += 1
        
        checks["non_standard_chars"] = non_std_count
        if non_std_count > 100:
            checks["text_extraction_quality"] -= 20
            checks["issues"].append(f"High number of non-standard characters ({non_std_count}) - may indicate formatting issues")
        elif non_std_count > 50:
            checks["text_extraction_quality"] -= 10
            checks["issues"].append(f"Some non-standard characters detected ({non_std_count})")
        
        # Check 3: Parse error patterns
        # Check for malformed dates (common ATS parsing issue)
        # Look for date patterns that might be broken
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Standard dates
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # Month Year
        ]
        found_dates = 0
        for pattern in date_patterns:
            found_dates += len(re.findall(pattern, resume_text, re.IGNORECASE))
        
        # If no dates found but resume is long, might indicate parsing issues
        if text_length > 2000 and found_dates < 2:
            checks["parse_errors"].append("Few or no dates detected - may indicate parsing issues")
            checks["text_extraction_quality"] -= 10
        
        # Check 4: Column structure detection
        # Look for text that might indicate broken column parsing
        # Common issue: dates/companies on left, descriptions on right get mixed
        lines = resume_text.split('\n')
        suspicious_lines = 0
        for line in lines:
            # Very short lines followed by very long lines might indicate column issues
            stripped = line.strip()
            if len(stripped) > 0 and len(stripped) < 5:
                suspicious_lines += 1
        
        if suspicious_lines > len(lines) * 0.3:  # More than 30% of lines are suspiciously short
            checks["column_structure_issues"] = True
            checks["text_extraction_quality"] -= 15
            checks["issues"].append("Possible column structure issues detected - text may be misaligned")
        
        # Check 5: Section headers detection
        # ATS-friendly resumes should have clear section headers
        section_keywords = ['experience', 'education', 'skills', 'summary', 'objective', 'work', 'employment']
        found_sections = sum(1 for keyword in section_keywords if keyword.lower() in resume_text.lower())
        
        if found_sections < 2:
            checks["text_extraction_quality"] -= 10
            checks["issues"].append("Few standard section headers detected - may affect ATS parsing")
        
        # Calculate final score (0-100)
        checks["score"] = max(0, min(100, checks["text_extraction_quality"]))
        
        return checks

    def _get_analysis_cache_key(self, resume_text: str, job_description: str) -> str:
        """
        Generate cache key for analysis results.
        Uses MD5 hash of resume and job description for cache lookup.
        """
        resume_hash = hashlib.md5(resume_text.encode()).hexdigest()[:16]
        job_hash = hashlib.md5(job_description.encode()).hexdigest()[:16]
        return f"analysis:{resume_hash}:{job_hash}"

    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis result.
        Tries Redis first, falls back to in-memory cache.
        """
        try:
            # Try Redis if available
            try:
                import redis
                redis_url = os.getenv('REDIS_URL')
                if redis_url:
                    redis_client = redis.from_url(redis_url, decode_responses=False)
                    cached_data = redis_client.get(cache_key)
                    if cached_data:
                        logger.info(f"Cache hit from Redis: {cache_key}")
                        return json.loads(cached_data.decode('utf-8'))
            except (ImportError, AttributeError, Exception) as e:
                # Redis not available or error, fall back to in-memory
                pass
            
            # Fallback: In-memory cache (not persisted across restarts)
            if not hasattr(self, '_memory_cache'):
                self._memory_cache = {}
                self._memory_cache_timestamps = {}
            
            if cache_key in self._memory_cache:
                # Check if cache entry is still valid (24 hours)
                cache_time = self._memory_cache_timestamps.get(cache_key, 0)
                if time.time() - cache_time < 86400:
                    logger.info(f"Cache hit from memory: {cache_key}")
                    return self._memory_cache[cache_key]
                else:
                    # Expired, remove it
                    del self._memory_cache[cache_key]
                    del self._memory_cache_timestamps[cache_key]
            
            return None
        except Exception as e:
            logger.warning(f"Error retrieving cache: {e}")
            return None

    def _cache_analysis_result(self, cache_key: str, result: Dict[str, Any], ttl_seconds: int = 86400):
        """
        Cache analysis result.
        Tries Redis first, falls back to in-memory cache.
        """
        try:
            # Try Redis if available
            try:
                import redis
                redis_url = os.getenv('REDIS_URL')
                if redis_url:
                    redis_client = redis.from_url(redis_url, decode_responses=False)
                    redis_client.setex(cache_key, ttl_seconds, json.dumps(result).encode('utf-8'))
                    logger.info(f"Cached analysis result in Redis: {cache_key}")
                    return
            except (ImportError, AttributeError, Exception) as e:
                # Redis not available or error, fall back to in-memory
                pass
            
            # Fallback: In-memory cache
            if not hasattr(self, '_memory_cache'):
                self._memory_cache = {}
                self._memory_cache_timestamps = {}
            
            self._memory_cache[cache_key] = result
            self._memory_cache_timestamps[cache_key] = time.time()
            
            # Limit memory cache size (keep only last 100 entries)
            if len(self._memory_cache) > 100:
                # Remove oldest entry
                oldest_key = min(self._memory_cache_timestamps.items(), key=lambda x: x[1])[0]
                del self._memory_cache[oldest_key]
                del self._memory_cache_timestamps[oldest_key]
            
            logger.info(f"Cached analysis result in memory: {cache_key}")
        except Exception as e:
            logger.warning(f"Error caching result: {e}")

    def comprehensive_resume_analysis(
        self, resume_text: str, job_description: str, language: str = None
    ) -> Dict[str, Any]:
        """
        Complete intelligent resume analysis pipeline with multilingual support.
        Uses parallelization to reduce analysis time from 30s to 8-10s.

        Args:
            resume_text: The resume content
            job_description: The target job description
            language: ISO 639-1 language code. If None, auto-detects from resume.

        Returns:
            Complete analysis results including detected language
        """
        logger.info("Starting comprehensive resume analysis...")
        start_time = time.time()

        try:
            # Step 0: Detect language from resume if not specified
            if language is None:
                language = self.detect_language(resume_text)
            logger.info(f"Analysis language: {language}")

            # Step 0.5: Check cache
            cache_key = self._get_analysis_cache_key(resume_text, job_description)
            cached_result = self._get_cached_analysis(cache_key)
            if cached_result:
                logger.info(f"Returning cached analysis result (key: {cache_key})")
                return cached_result

            # PARALLEL BATCH 1: Extract job requirements and resume content simultaneously
            logger.info("Batch 1: Parallel extraction of job requirements and resume content...")
            batch1_start = time.time()
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                job_future = executor.submit(self.extract_job_requirements, job_description)
                resume_future = executor.submit(self.extract_resume_content, resume_text)
                
                # Wait for both to complete
                job_analysis = job_future.result()
                resume_parsed = resume_future.result()
            
            batch1_time = time.time() - batch1_start
            logger.info(f"Batch 1 completed in {batch1_time:.2f}s")

            # Step 2.5: ATS Readability Heuristics (Python-based, instant)
            ats_heuristics = self._check_ats_readability_heuristics(resume_text)
            logger.info(f"ATS readability heuristics: {ats_heuristics['score']}/100")

            # BATCH 2a: Match analysis (must complete before batch 2b)
            logger.info("Batch 2a: Generating match analysis...")
            batch2a_start = time.time()
            match_analysis = self.intelligent_match_analysis(
                job_analysis, resume_parsed, job_description, resume_text
            )
            batch2a_time = time.time() - batch2a_start
            logger.info(f"Batch 2a completed in {batch2a_time:.2f}s")
            
            # Inject ATS heuristics into match_analysis
            if "match_breakdown" not in match_analysis:
                match_analysis["match_breakdown"] = {}
            match_analysis["ats_readability_heuristics"] = ats_heuristics

            # Step 4: Calibrate score (Python calculates, not LLM)
            score_data = self._calibrate_match_score(match_analysis, job_analysis)
            
            # Step 4.5: Generate score breakdown for transparency
            score_breakdown = self._generate_score_breakdown(match_analysis, score_data, job_analysis)

            # PARALLEL BATCH 2b: ATS optimization and recommendations (can run in parallel)
            logger.info("Batch 2b: Parallel generation of ATS optimization and recommendations...")
            batch2b_start = time.time()
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                ats_future = executor.submit(
                    self.generate_ats_optimization_recommendations,
                job_description, resume_parsed, match_analysis, language
            )

                rec_future = executor.submit(
                    self.generate_intelligent_recommendations,
                job_description, resume_parsed, match_analysis,
                job_analysis.get("industry", "unknown"), language
            )
                
                # Wait for both to complete
                ats_optimization = ats_future.result()
                recommendations = rec_future.result()
            
            batch2b_time = time.time() - batch2b_start
            logger.info(f"Batch 2b completed in {batch2b_time:.2f}s")

            result = {
                "overall_score": score_data["final_score"],
                "interpretation": score_data["interpretation"],
                "match_analysis": match_analysis,
                "ats_optimization": ats_optimization,
                "recommendations": recommendations,
                "job_industry": job_analysis.get("industry", "Unknown"),
                "job_level": job_analysis.get("experience_level", "Unknown"),
                "resume_level": resume_parsed.get("experience_level", "Unknown"),
                "expected_ats_pass_rate": f"{match_analysis.get('ats_pass_likelihood', 50)}%",
                "detected_language": language,  # Include detected language in result
                "score_breakdown": score_breakdown,  # Transparent score calculation
            }

            total_time = time.time() - start_time
            logger.info(f"Analysis complete in {total_time:.2f}s - Score: {result['overall_score']}%, Language: {language}")
            
            # Cache result (24 hour TTL)
            self._cache_analysis_result(cache_key, result, ttl_seconds=86400)
            
            return result

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise

    @staticmethod
    def _calibrate_match_score(analysis: Dict[str, Any], job_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate final score in Python (NOT LLM).
        LLM provides raw data, Python does the math.
        This fixes the 76.8% clustering problem by decoupling scoring from LLM.
        """
        components = analysis.get("match_breakdown", {})

        # Extract raw scores from LLM analysis (structured format)
        skill_alignment_data = components.get("skill_alignment", {})
        if isinstance(skill_alignment_data, dict):
            keyword_score = skill_alignment_data.get("score", 50)
        else:
            keyword_score = skill_alignment_data if isinstance(skill_alignment_data, (int, float)) else 50
        
        experience_data = components.get("experience_fit", {})
        if isinstance(experience_data, dict):
            experience_score = experience_data.get("score", 50)
            experience_gap = experience_data.get("gap", 0)
        else:
            experience_score = experience_data if isinstance(experience_data, (int, float)) else 50
            experience_gap = 0
        
        content_quality_data = components.get("content_quality", {})
        if isinstance(content_quality_data, dict):
            content_quality_score = content_quality_data.get("score", 50)
        else:
            content_quality_score = content_quality_data if isinstance(content_quality_data, (int, float)) else 50
        
        job_match_data = components.get("job_specific_match", {})
        if isinstance(job_match_data, dict):
            job_match_score = job_match_data.get("score", 50)
        else:
            job_match_score = job_match_data if isinstance(job_match_data, (int, float)) else 50
        
        # ATS Readability: Combine LLM assessment with Python heuristics
        ats_llm_data = components.get("ats_readability", {})
        if isinstance(ats_llm_data, dict):
            ats_llm_score = ats_llm_data.get("score", 50)
        else:
            ats_llm_score = ats_llm_data if isinstance(ats_llm_data, (int, float)) else 50
        
        # Get Python heuristics score (if available)
        ats_heuristics = analysis.get("ats_readability_heuristics", {})
        ats_heuristic_score = ats_heuristics.get("score", 100) if ats_heuristics else 100
        
        # Combine LLM and heuristic scores (weighted: 60% LLM, 40% heuristics)
        ats_readability_score = (ats_llm_score * 0.6) + (ats_heuristic_score * 0.4)
        
        # Calculate weighted base score
        weighted_score = (
            keyword_score * 0.25 +          # Keyword Matching (25%)
            experience_score * 0.20 +      # Experience & Qualifications (20%)
            ats_readability_score * 0.15 +  # ATS Readability (15%)
            content_quality_score * 0.20 +  # Content Quality (20%)
            job_match_score * 0.15          # Job-Specific Match (15%)
        )
        
        # Apply hard filter multipliers (knockout questions)
        hard_filters = analysis.get("hard_filter_violations", [])
        critical_violations = [v for v in hard_filters if v.get("severity") == "critical"]
        
        hard_filter_multiplier = 1.0
        hard_filter_applied = False
        
        # Hard Filter 1: Missing >3 critical keywords
        if len(critical_violations) > 3:
            hard_filter_multiplier = 0.6
            hard_filter_applied = True
            logger.info(f"Hard filter applied: {len(critical_violations)} critical violations")
        
        # Hard Filter 2: Experience gap >2 years
        if experience_gap > 2:
            hard_filter_multiplier = min(hard_filter_multiplier, 0.6)
            hard_filter_applied = True
            logger.info(f"Hard filter applied: Experience gap of {experience_gap} years")
        
        # Check missing required skills
        skill_alignment_data = components.get("skill_alignment", {})
        if isinstance(skill_alignment_data, dict):
            missing_required = skill_alignment_data.get("missing_required_skills", [])
            total_required = skill_alignment_data.get("total_required", 0)
            
            if total_required > 0 and len(missing_required) > total_required * 0.5:  # Missing >50% of required
                hard_filter_multiplier = min(hard_filter_multiplier, 0.6)
                hard_filter_applied = True
                logger.info(f"Hard filter applied: Missing {len(missing_required)}/{total_required} required skills")
        
        weighted_score *= hard_filter_multiplier
        
        # Apply keyword penalties
        missing_keywords = analysis.get("keywords_missing", [])
        for keyword in missing_keywords:
            if isinstance(keyword, dict):
                importance = keyword.get("importance", "unknown")
                penalty = keyword.get("penalty", 0)
                
                if importance == "required":
                    weighted_score -= penalty
                elif importance == "preferred":
                    weighted_score -= penalty * 0.2  # Lighter penalty for preferred
            elif isinstance(keyword, str):
                # Default penalty for string keywords
                weighted_score -= 5
        
        # Apply bonuses
        bonuses = analysis.get("bonuses", [])
        for bonus in bonuses:
            if isinstance(bonus, dict):
                points = bonus.get("points", 0)
                weighted_score += points
            elif isinstance(bonus, (int, float)):
                weighted_score += bonus
        
        # Cap and normalize final score
        final_score = max(0, min(100, round(weighted_score, 1)))
        
        # Generate interpretation with better tiers
        if final_score >= 90:
            interpretation = "Excellent - Top-tier candidate, strong interview likelihood"
        elif final_score >= 75:
            interpretation = "Good - Competitive candidate, good interview chances"
        elif final_score >= 60:
            interpretation = "Average - Room for improvement to be competitive"
        elif final_score >= 40:
            interpretation = "Below Average - Significant gaps, needs major improvements"
        else:
            interpretation = "Poor Match - Consider different roles or major resume overhaul"

        return {
            "final_score": final_score,
            "interpretation": interpretation,
            "hard_filter_applied": hard_filter_applied,
            "hard_filter_multiplier": hard_filter_multiplier,
            "raw_components": {
                "keyword": keyword_score,
                "experience": experience_score,
                "ats_readability": ats_readability_score,
                "content_quality": content_quality_score,
                "job_match": job_match_score
            },
            "weighted_base_score": round(weighted_score / hard_filter_multiplier if hard_filter_multiplier > 0 else weighted_score, 1),
            "penalties_applied": len(missing_keywords),
            "bonuses_applied": len(bonuses)
        }

    def _generate_score_breakdown(
        self, 
        analysis: Dict[str, Any], 
        score_calculation: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate transparent breakdown of how score was calculated.
        Provides detailed explanations for each factor.
        """
        components = analysis.get("match_breakdown", {})
        
        # Keyword Matching breakdown
        skill_data = components.get("skill_alignment", {})
        if isinstance(skill_data, dict):
            matched_required = skill_data.get("matched_required_skills", [])
            missing_required = skill_data.get("missing_required_skills", [])
            matched_preferred = skill_data.get("matched_preferred_skills", [])
            total_required = skill_data.get("total_required", 0)
            total_preferred = skill_data.get("total_preferred", 0)
        else:
            matched_required = []
            missing_required = []
            matched_preferred = []
            total_required = 0
            total_preferred = 0
        
        keyword_explanation = f"Matched {len(matched_required)} of {total_required} required skills"
        if missing_required:
            keyword_explanation += f". Missing: {', '.join(missing_required[:3])}"
            if len(missing_required) > 3:
                keyword_explanation += f" and {len(missing_required) - 3} more"
        
        # Experience breakdown
        exp_data = components.get("experience_fit", {})
        if isinstance(exp_data, dict):
            required_years = exp_data.get("required_years", 0)
            resume_years = exp_data.get("resume_years", 0)
            gap = exp_data.get("gap", 0)
            level_match = exp_data.get("level_match", "unknown")
        else:
            required_years = 0
            resume_years = 0
            gap = 0
            level_match = "unknown"
        
        experience_explanation = f"Required: {required_years} years, Resume: {resume_years} years"
        if gap > 0:
            experience_explanation += f" (Gap: {gap} years)"
        experience_explanation += f". Level: {level_match}"
        
        # Content Quality breakdown
        content_data = components.get("content_quality", {})
        if isinstance(content_data, dict):
            achievements_count = content_data.get("quantifiable_achievements_count", 0)
            action_verbs = content_data.get("action_verbs_count", 0)
            summary_quality = content_data.get("summary_quality", "unknown")
        else:
            achievements_count = 0
            action_verbs = 0
            summary_quality = "unknown"
        
        content_explanation = f"{achievements_count} quantifiable achievements, {action_verbs} action verbs"
        if summary_quality != "unknown":
            content_explanation += f", Summary: {summary_quality}"
        
        # Job Match breakdown
        job_data = components.get("job_specific_match", {})
        if isinstance(job_data, dict):
            industry_relevance = job_data.get("industry_relevance", 50)
            role_alignment = job_data.get("role_title_alignment", 50)
            tools_match = job_data.get("tools_technologies_match", 50)
        else:
            industry_relevance = 50
            role_alignment = 50
            tools_match = 50
        
        job_explanation = f"Industry: {industry_relevance}%, Role: {role_alignment}%, Tools: {tools_match}%"
        
        # ATS Readability breakdown
        ats_heuristics = analysis.get("ats_readability_heuristics", {})
        ats_issues = ats_heuristics.get("issues", [])
        ats_explanation = "Formatting is ATS-compatible"
        if ats_issues:
            ats_explanation = f"Issues detected: {', '.join(ats_issues[:2])}"
            if len(ats_issues) > 2:
                ats_explanation += f" and {len(ats_issues) - 2} more"
        
        # Build matches and gaps lists
        matches = []
        for skill in matched_required[:5]:
            matches.append({
                "item": skill,
                "status": "found",
                "location": "resume",
                "severity": "required"
            })
        
        gaps = []
        for keyword in analysis.get("keywords_missing", [])[:10]:
            if isinstance(keyword, dict):
                gaps.append({
                    "item": keyword.get("keyword", ""),
                    "status": "missing",
                    "severity": keyword.get("importance", "unknown"),
                    "penalty": keyword.get("penalty", 0),
                    "why_matters": keyword.get("why_matters", "")
                })
            elif isinstance(keyword, str):
                gaps.append({
                    "item": keyword,
                    "status": "missing",
                    "severity": "unknown",
                    "penalty": 5,
                    "why_matters": ""
                })
        
        # Hard filter details
        hard_filter_details = []
        if score_calculation.get("hard_filter_applied", False):
            hard_filters = analysis.get("hard_filter_violations", [])
            critical_violations = [v for v in hard_filters if v.get("severity") == "critical"]
            
            if len(critical_violations) > 3:
                hard_filter_details.append({
                    "type": "missing_critical_keywords",
                    "count": len(critical_violations),
                    "multiplier": score_calculation.get("hard_filter_multiplier", 1.0),
                    "explanation": f"Missing {len(critical_violations)} critical requirements"
                })
            
            exp_data = components.get("experience_fit", {})
            if isinstance(exp_data, dict) and exp_data.get("gap", 0) > 2:
                hard_filter_details.append({
                    "type": "experience_gap",
                    "gap": exp_data.get("gap", 0),
                    "multiplier": score_calculation.get("hard_filter_multiplier", 1.0),
                    "explanation": f"Experience gap of {exp_data.get('gap', 0)} years exceeds threshold"
                })
        
        # Penalties and bonuses
        penalties_list = []
        for keyword in analysis.get("keywords_missing", [])[:5]:
            if isinstance(keyword, dict) and keyword.get("importance") == "required":
                penalties_list.append({
                    "reason": f"Missing required skill: {keyword.get('keyword', '')}",
                    "points": -keyword.get("penalty", 10),
                    "category": "keyword"
                })
        
        bonuses_list = []
        for bonus in analysis.get("bonuses", []):
            if isinstance(bonus, dict):
                bonuses_list.append({
                    "reason": bonus.get("reason", "Bonus"),
                    "points": bonus.get("points", 0),
                    "category": bonus.get("category", "general")
                })
        
        # Calculate formula string
        raw_components = score_calculation.get("raw_components", {})
        base_score = score_calculation.get("weighted_base_score", 0)
        multiplier = score_calculation.get("hard_filter_multiplier", 1.0)
        final_score = score_calculation.get("final_score", 0)
        
        formula_parts = [
            f"Base weighted score: {base_score:.1f}%",
        ]
        if multiplier < 1.0:
            formula_parts.append(f"Hard filter: {multiplier:.1f}x")
        if penalties_list:
            total_penalties = sum(p.get("points", 0) for p in penalties_list)
            formula_parts.append(f"Penalties: {total_penalties:.1f}")
        if bonuses_list:
            total_bonuses = sum(b.get("points", 0) for b in bonuses_list)
            formula_parts.append(f"Bonuses: +{total_bonuses:.1f}")
        formula_parts.append(f"Final: {final_score:.1f}%")
        
        formula_string = " | ".join(formula_parts)
        
        return {
            "score_calculation": {
                "keyword_matching": {
                    "score": raw_components.get("keyword", 50),
                    "weight": 0.25,
                    "weighted_contribution": round(raw_components.get("keyword", 50) * 0.25, 2),
                    "details": {
                        "matched_required": len(matched_required),
                        "total_required": total_required,
                        "missing_required": len(missing_required),
                        "matched_preferred": len(matched_preferred),
                        "total_preferred": total_preferred
                    },
                    "explanation": keyword_explanation,
                    "matches": matches,
                    "gaps": [g for g in gaps if g.get("severity") in ["required", "critical"]][:5]
                },
                "experience_qualifications": {
                    "score": raw_components.get("experience", 50),
                    "weight": 0.20,
                    "weighted_contribution": round(raw_components.get("experience", 50) * 0.20, 2),
                    "details": {
                        "required_years": required_years,
                        "resume_years": resume_years,
                        "gap": gap,
                        "level_match": level_match
                    },
                    "explanation": experience_explanation
                },
                "ats_readability": {
                    "score": raw_components.get("ats_readability", 50),
                    "weight": 0.15,
                    "weighted_contribution": round(raw_components.get("ats_readability", 50) * 0.15, 2),
                    "details": {
                        "heuristic_score": ats_heuristics.get("score", 100),
                        "issues": ats_issues
                    },
                    "explanation": ats_explanation
                },
                "content_quality": {
                    "score": raw_components.get("content_quality", 50),
                    "weight": 0.20,
                    "weighted_contribution": round(raw_components.get("content_quality", 50) * 0.20, 2),
                    "details": {
                        "quantifiable_achievements": achievements_count,
                        "action_verbs": action_verbs,
                        "summary_quality": summary_quality
                    },
                    "explanation": content_explanation
                },
                "job_specific_match": {
                    "score": raw_components.get("job_match", 50),
                    "weight": 0.15,
                    "weighted_contribution": round(raw_components.get("job_match", 50) * 0.15, 2),
                    "details": {
                        "industry_relevance": industry_relevance,
                        "role_title_alignment": role_alignment,
                        "tools_technologies_match": tools_match
                    },
                    "explanation": job_explanation
                },
                "hard_filters": {
                    "applied": score_calculation.get("hard_filter_applied", False),
                    "multiplier": score_calculation.get("hard_filter_multiplier", 1.0),
                    "reasons": hard_filter_details
                },
                "penalties": penalties_list,
                "bonuses": bonuses_list,
                "final_formula": formula_string
            }
        }

    @staticmethod
    def _get_default_job_analysis() -> Dict[str, Any]:
        """Default job analysis structure with required vs preferred distinction"""
        return {
            "required_skills": [],
            "preferred_skills": [],
            "hard_requirements": [],
            "core_skills": [],
            "soft_skills": [],
            "experience_required": {
                "minimum_years": 0,
                "field": "Unknown",
                "preferred_years": 0,
                "description": "Unknown"
            },
            "experience_level": "mid",
            "industry": "Unknown",
            "key_responsibilities": [],
            "nice_to_have": [],
            "keywords": [],
            "tools_technologies": [],
            "education_requirements": {
                "required": "",
                "preferred": ""
            }
        }

    @staticmethod
    def _get_default_resume_analysis() -> Dict[str, Any]:
        """Default resume analysis structure"""
        return {
            "summary": "",
            "technical_skills": [],
            "soft_skills": [],
            "years_experience_total": 0,
            "years_in_primary_field": 0,
            "experience_level": "entry",
            "industries_worked_in": [],
            "key_accomplishments": [],
            "education": {"degree": "", "field": ""},
            "certifications": [],
            "languages": [],
        }

    @staticmethod
    def _get_default_match_analysis() -> Dict[str, Any]:
        """Default match analysis structure"""
        return {
            "overall_match_score": 50,
            "match_breakdown": {
                "skill_alignment": 50,
                "experience_level_fit": 50,
                "industry_relevance": 50,
                "requirement_coverage": 50,
            },
            "strengths": [],
            "gaps": [],
            "keywords_present": [],
            "keywords_missing": [],
            "transferable_skills": [],
        }


# Singleton instance
_analyzer_instance = None


def get_analyzer() -> IntelligentResumeAnalyzer:
    """Get or create analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = IntelligentResumeAnalyzer()
    return _analyzer_instance
