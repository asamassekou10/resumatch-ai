"""
Intelligent Resume Analysis Engine - Using Google Gemini AI
Industry-agnostic, AI-driven resume scoring and ATS optimization
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
import google.generativeai as genai

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


def retry_on_error(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Decorator to retry Gemini API calls on failure
    Handles rate limits, timeouts, and transient errors
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

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_job_requirements(self, prompt: str) -> str:
        """Protected method to call Gemini API with retry logic"""
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        return response.text.strip()

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_resume_parsing(self, prompt: str) -> str:
        """Protected method to call Gemini API for resume parsing"""
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        return response.text.strip()

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_matching(self, prompt: str) -> str:
        """Protected method to call Gemini API for matching analysis"""
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        return response.text.strip()

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_ats_optimization(self, prompt: str) -> str:
        """Protected method to call Gemini API for ATS optimization"""
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        return response.text.strip()

    @retry_on_error(max_retries=MAX_RETRIES)
    def _call_gemini_for_recommendations(self, prompt: str) -> str:
        """Protected method to call Gemini API for recommendations"""
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            request_options=self.request_options
        )
        return response.text.strip()

    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Use Gemini to intelligently extract job requirements
        Works for ANY industry - no hardcoding needed
        """
        logger.info("Extracting job requirements with Gemini...")

        prompt = f"""Analyze this job description and extract structured requirements in JSON format.

Job Description:
{job_description}

Return ONLY valid JSON (no markdown, no code blocks) with this structure:
{{
    "core_skills": ["list of essential technical/professional skills"],
    "soft_skills": ["communication", "leadership", "teamwork", etc.],
    "experience_required": "X years in Y field",
    "experience_level": "entry/mid/senior",
    "industry": "detected industry",
    "key_responsibilities": ["main duties"],
    "nice_to_have": ["optional/bonus skills"],
    "keywords": ["important domain-specific terms"],
    "tools_technologies": ["software, frameworks, platforms mentioned"],
    "salary_range": "extracted range if mentioned",
    "location_requirements": "location preference if mentioned"
}}

Be precise and extract exactly what the job posting requires."""

        try:
            response_text = self._call_gemini_for_job_requirements(prompt)

            # Clean up markdown if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            logger.info(f"Successfully extracted job requirements for {result.get('industry', 'unknown')} role")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse job requirements JSON: {e}")
            return self._get_default_job_analysis()
        except Exception as e:
            logger.error(f"Error extracting job requirements: {e}")
            return self._get_default_job_analysis()

    def extract_resume_content(self, resume_text: str) -> Dict[str, Any]:
        """
        Use Gemini to intelligently parse resume
        Understands professional context, soft skills, achievements
        """
        logger.info("Parsing resume content with Gemini...")

        prompt = f"""Analyze this resume and extract structured information in JSON format.
Only include relevant information, ignore contact details for privacy.

Resume:
{resume_text[:5000]}

Return ONLY valid JSON (no markdown, no code blocks) with this structure:
{{
    "summary": "1-sentence professional summary extracted",
    "technical_skills": ["list of technical skills"],
    "soft_skills": ["communication", "leadership", "project_management", etc.],
    "years_experience_total": 5,
    "years_in_primary_field": 3,
    "experience_level": "entry/mid/senior/expert",
    "industries_worked_in": ["list of industries"],
    "key_accomplishments": ["quantifiable achievement 1", "achievement 2"],
    "education": {{
        "degree": "Bachelor of Science",
        "field": "Computer Science"
    }},
    "certifications": ["list of professional certifications"],
    "languages": ["English", "Spanish"],
    "ats_readability": {{
        "structure_clarity": 85,
        "formatting_issues": ["identified issue 1", "issue 2"],
        "missing_sections": ["optional section"]
    }}
}}

Be accurate - this is for professional evaluation."""

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

        prompt = f"""You are an expert HR recruiter and ATS specialist.
Analyze this resume against this job to provide detailed matching analysis.

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

RESUME CONTENT:
{json.dumps(resume_content, indent=2)}

Provide analysis in JSON format:
{{
    "overall_match_score": 75,
    "match_breakdown": {{
        "skill_alignment": 80,
        "experience_level_fit": 70,
        "industry_relevance": 85,
        "requirement_coverage": 75
    }},
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
            "keyword": "required skill",
            "importance": "critical/important/optional",
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
    "ats_pass_likelihood": 75,
    "interview_likelihood": 70,
    "hiring_recommendation": "strong_candidate/competitive/needs_improvement"
}}

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
            logger.info(f"Match analysis complete - Score: {result.get('overall_match_score', 'N/A')}%")
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

    def comprehensive_resume_analysis(
        self, resume_text: str, job_description: str, language: str = None
    ) -> Dict[str, Any]:
        """
        Complete intelligent resume analysis pipeline with multilingual support.

        Args:
            resume_text: The resume content
            job_description: The target job description
            language: ISO 639-1 language code. If None, auto-detects from resume.

        Returns:
            Complete analysis results including detected language
        """
        logger.info("Starting comprehensive resume analysis...")

        try:
            # Step 0: Detect language from resume if not specified
            if language is None:
                language = self.detect_language(resume_text)
            logger.info(f"Analysis language: {language}")

            # Step 1: Extract job requirements (AI-driven)
            job_analysis = self.extract_job_requirements(job_description)

            # Step 2: Parse resume with semantic understanding
            resume_parsed = self.extract_resume_content(resume_text)

            # Step 3: Semantic matching
            match_analysis = self.intelligent_match_analysis(
                job_analysis, resume_parsed, job_description, resume_text
            )

            # Step 4: Calibrate score
            score_data = self._calibrate_match_score(match_analysis)

            # Step 5: ATS optimization (with language support)
            ats_optimization = self.generate_ats_optimization_recommendations(
                job_description, resume_parsed, match_analysis, language
            )

            # Step 6: Generate recommendations (with language support)
            recommendations = self.generate_intelligent_recommendations(
                job_description, resume_parsed, match_analysis,
                job_analysis.get("industry", "unknown"), language
            )

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
            }

            logger.info(f"Analysis complete - Score: {result['overall_score']}%, Language: {language}")
            return result

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise

    @staticmethod
    def _calibrate_match_score(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert analysis components to realistic match score"""
        components = analysis.get("match_breakdown", {})

        weighted_score = (
            components.get("skill_alignment", 50) * 0.35
            + components.get("requirement_coverage", 50) * 0.35
            + components.get("experience_level_fit", 50) * 0.20
            + components.get("industry_relevance", 50) * 0.10
        )

        if weighted_score >= 80:
            interpretation = "Excellent match - strong candidate for interview"
        elif weighted_score >= 65:
            interpretation = "Good match - competitive candidate"
        elif weighted_score >= 50:
            interpretation = "Moderate match - needs improvements"
        elif weighted_score >= 30:
            interpretation = "Weak match - significant gaps"
        else:
            interpretation = "Poor match - consider different roles"

        return {
            "final_score": round(weighted_score, 1),
            "interpretation": interpretation,
        }

    @staticmethod
    def _get_default_job_analysis() -> Dict[str, Any]:
        """Default job analysis structure"""
        return {
            "core_skills": [],
            "soft_skills": [],
            "experience_required": "Unknown",
            "experience_level": "mid",
            "industry": "Unknown",
            "key_responsibilities": [],
            "nice_to_have": [],
            "keywords": [],
            "tools_technologies": [],
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
