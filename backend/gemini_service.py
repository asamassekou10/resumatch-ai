import google.generativeai as genai
import os
import traceback
import time
import html
import re
from typing import Optional, List, Dict, Any
from errors import AIProcessingError
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class GeminiService:
    """Enhanced Gemini service with retry logic, error handling, and multilingual support"""

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

    # Supported language codes
    SUPPORTED_LANGUAGES = list(LANGUAGE_INSTRUCTIONS.keys())

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL_NAME', 'models/gemini-2.5-flash')
        self.model = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self._language_cache = {}  # Cache detected languages
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model with error handling"""
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini model {self.model_name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def _is_model_available(self) -> bool:
        """Check if model is available"""
        return self.model is not None

    def _sanitize_response(self, text: str) -> str:
        """Clean up HTML entities and formatting issues from AI responses"""
        if not text:
            return text

        # Decode HTML entities like &nbsp; &amp; etc.
        text = html.unescape(text)

        # Replace multiple consecutive spaces with single space
        text = re.sub(r' {2,}', ' ', text)

        # Replace multiple consecutive newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove any remaining HTML-like nbsp patterns
        text = text.replace('\xa0', ' ')  # Non-breaking space character

        return text.strip()

    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of the given text (resume or job description).
        Uses a quick Gemini call to identify the language.
        Returns ISO 639-1 two-letter language code (e.g., 'en', 'fr', 'de').
        """
        if not text or len(text.strip()) < 50:
            return 'en'  # Default to English for very short text

        # Check cache first (use first 200 chars as key)
        cache_key = hash(text[:200])
        if cache_key in self._language_cache:
            return self._language_cache[cache_key]

        if not self._is_model_available():
            return 'en'

        # Use a sample of the text to detect language (faster)
        text_sample = text[:1000]

        prompt = f"""Analyze this text and determine its primary language.
Return ONLY the ISO 639-1 two-letter language code (lowercase).

Supported codes: en, fr, de, es, nl, pt, it, pl, ru, zh, ja, ko, ar, hi

If the text is in multiple languages, return the dominant one.
If unsure, return 'en'.

Text sample:
{text_sample}

Response (just the two-letter code, nothing else):"""

        try:
            response = self.model.generate_content(
                prompt,
                request_options={'timeout': 10}  # Quick timeout for language detection
            )
            if response and response.text:
                detected = response.text.strip().lower()[:2]
                # Validate it's a supported language
                if detected in self.SUPPORTED_LANGUAGES:
                    logger.info(f"Detected language: {detected}")
                    self._language_cache[cache_key] = detected
                    return detected
            return 'en'
        except Exception as e:
            logger.warning(f"Language detection failed, defaulting to English: {e}")
            return 'en'

    def _get_language_instruction(self, language: str) -> str:
        """Get the language instruction for prompts"""
        return self.LANGUAGE_INSTRUCTIONS.get(language, self.LANGUAGE_INSTRUCTIONS['en'])

    def _call_gemini_with_retry(self, prompt: str, operation_name: str) -> Optional[str]:
        """Call Gemini API with retry logic"""
        if not self._is_model_available():
            raise AIProcessingError("Gemini AI service is not available")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Gemini API for {operation_name} (attempt {attempt + 1})")
                response = self.model.generate_content(
                    prompt,
                    request_options={'timeout': 30}
                )

                if response and response.text:
                    logger.info(f"Gemini API {operation_name} completed successfully")
                    return self._sanitize_response(response.text)
                else:
                    logger.warning(f"Empty response from Gemini API for {operation_name}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise AIProcessingError(f"Empty response from Gemini API for {operation_name}")
                        
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Gemini API {operation_name} attempt {attempt + 1} failed: {error_msg}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise AIProcessingError(f"Gemini API {operation_name} failed after {self.max_retries} attempts: {error_msg}")
        
        return None
    
    def generate_personalized_feedback(self, resume_text: str, job_description: str,
                                    match_score: float, keywords_found: list,
                                    keywords_missing: list, language: str = None) -> str:
        """
        Generate detailed, personalized feedback using Gemini AI.

        Args:
            resume_text: The resume content
            job_description: The job description
            match_score: The calculated match score
            keywords_found: List of matching keywords
            keywords_missing: List of missing keywords
            language: ISO 639-1 language code (e.g., 'fr', 'de'). If None, auto-detects from resume.

        Returns:
            Personalized feedback in the detected/specified language
        """
        if not self._is_model_available():
            return self._generate_fallback_feedback(match_score, keywords_missing)

        # Auto-detect language from resume if not specified
        if language is None:
            language = self.detect_language(resume_text)

        lang_instruction = self._get_language_instruction(language)

        # Limit text lengths to avoid token limits
        resume_excerpt = resume_text[:2000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""

        prompt = f"""You are an expert career coach and resume writer.

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}

Analyze this resume against the job description and provide specific, actionable feedback.

RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{job_excerpt}

CURRENT ANALYSIS:
- Match Score: {match_score}%
- Keywords Found: {', '.join(keywords_found[:10]) if keywords_found else 'None'}
- Keywords Missing: {', '.join(keywords_missing[:10]) if keywords_missing else 'None'}

FORMAT REQUIREMENTS - Structure your feedback as follows:

📊 OVERALL ASSESSMENT
[2-3 sentences about the current match quality and overall impression]

✅ KEY STRENGTHS
1. [Specific strength with example from resume]
2. [Specific strength with example from resume]
3. [Specific strength with example from resume]

⚠️ CRITICAL GAPS
1. [Important missing element with specific impact]
2. [Important missing element with specific impact]
3. [Important missing element with specific impact]

🎯 PRIORITY ACTION ITEMS
1. [Specific action] - [Example of how to implement]
2. [Specific action] - [Example of how to implement]
3. [Specific action] - [Example of how to implement]
4. [Specific action] - [Example of how to implement]
5. [Specific action] - [Example of how to implement]

🔑 KEYWORD INTEGRATION STRATEGY
[Paragraph explaining how to naturally integrate the missing keywords into existing experience. Provide specific examples of before/after bullet points.]

💡 QUICK WINS
• [Immediate change that will improve the resume]
• [Immediate change that will improve the resume]
• [Immediate change that will improve the resume]

IMPORTANT:
- {lang_instruction}
- Be specific and actionable, not vague
- Focus on what the candidate CAN control
- Provide concrete examples and rewording suggestions
- Be encouraging while being honest
- Keep the total response under 800 words
- Use bullet points and clear formatting
- Include specific metrics and quantifiable improvements where possible"""

        try:
            return self._call_gemini_with_retry(prompt, "personalized_feedback")
        except AIProcessingError as e:
            logger.error(f"Failed to generate personalized feedback: {e}")
            return self._generate_fallback_feedback(match_score, keywords_missing)
    
    def generate_optimized_resume(self,
                                resume_text: str,
                                job_description: str,
                                keywords_missing: list,
                                language: str = None) -> Optional[str]:
        """
        Generate an optimized version of the resume tailored to the job.

        Args:
            resume_text: The original resume content
            job_description: The target job description
            keywords_missing: List of keywords to integrate
            language: ISO 639-1 language code. If None, auto-detects from resume.

        Returns:
            Optimized resume in the same language as the original
        """
        # 1. Check model availability
        if not self._is_model_available():
            return None

        # Auto-detect language from resume if not specified
        if language is None:
            language = self.detect_language(resume_text)

        lang_instruction = self._get_language_instruction(language)

        # 2. Limit text lengths to avoid token limits (Safety check)
        resume_excerpt = resume_text[:3000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""

        # Handle the keywords list safely
        formatted_keywords = ', '.join(keywords_missing[:15]) if keywords_missing else 'None'

        # 3. Construct the Prompt
        prompt = f"""You are an expert resume writer.

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}
Write the optimized resume in the SAME LANGUAGE as the original resume.

Rewrite this resume to better match the job description while maintaining the candidate's authentic experience and achievements.

    ORIGINAL RESUME:
    {resume_excerpt}

    TARGET JOB DESCRIPTION:
    {job_excerpt}

    MISSING KEYWORDS TO INTEGRATE:
    {formatted_keywords}

    INSTRUCTIONS:
    1. {lang_instruction}
    2. Keep all real experiences and achievements - DO NOT fabricate
    3. Rephrase bullets to include relevant keywords naturally
    4. Emphasize experiences that match the job requirements
    5. Add a professional summary tailored to this role
    6. Reorganize sections to highlight most relevant experience first
    7. Use action verbs and quantify achievements where possible
    8. Integrate missing keywords ONLY where they genuinely apply

    FORMAT REQUIREMENTS - Follow this exact professional resume structure:

    [CANDIDATE NAME]
    [Contact Information: Email | Phone | LinkedIn | Location]

    PROFESSIONAL SUMMARY
    [3-4 lines highlighting key qualifications and value proposition tailored to the target role]

    CORE COMPETENCIES
    • [Skill 1] • [Skill 2] • [Skill 3] • [Skill 4]
    • [Skill 5] • [Skill 6] • [Skill 7] • [Skill 8]

    PROFESSIONAL EXPERIENCE

    [Job Title] | [Company Name] | [Location]
    [Start Date] - [End Date]
    • [Achievement-focused bullet with metrics and impact]
    • [Achievement-focused bullet with metrics and impact]
    • [Achievement-focused bullet with metrics and impact]

    [Repeat for each position]

    EDUCATION
    [Degree] in [Major] | [University Name] | [Graduation Year]

    CERTIFICATIONS (if applicable)
    • [Certification Name] | [Issuing Organization] | [Year]

    TECHNICAL SKILLS (if applicable)
    [List relevant technical skills]

    IMPORTANT:
    - {lang_instruction}
    - Use proper formatting with clear section headers
    - Start each bullet with strong action verbs
    - Include quantifiable achievements wherever possible
    - Be honest - only include keywords where the candidate actually has that experience
    - Make it ATS-friendly with standard section names
    - Keep formatting clean and professional"""

        # 4. API Call with Error Handling
        try:
            return self._call_gemini_with_retry(prompt, "optimized_resume")
        except Exception as e:
            logger.error(f"Failed to generate optimized resume: {e}")
            return None

    def generate_cover_letter(self, resume_text: str, job_description: str,
                            company_name: str, job_title: str,
                            language: str = None) -> Optional[str]:
        """
        Generate a tailored cover letter.

        Args:
            resume_text: The candidate's resume
            job_description: The target job description
            company_name: Name of the company
            job_title: Title of the position
            language: ISO 639-1 language code. If None, auto-detects from resume.

        Returns:
            Cover letter in the detected/specified language
        """
        if not self._is_model_available():
            return None

        # Auto-detect language from resume if not specified
        if language is None:
            language = self.detect_language(resume_text)

        lang_instruction = self._get_language_instruction(language)

        # Limit text lengths to avoid token limits
        resume_excerpt = resume_text[:2000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""

        prompt = f"""Write a compelling cover letter for this candidate applying to {company_name} for the {job_title} position.

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}
Write the cover letter in the SAME LANGUAGE as the resume.

CANDIDATE'S RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{job_excerpt}

REQUIREMENTS:
1. {lang_instruction}
2. Professional yet personable tone
3. 3-4 paragraphs (250-350 words)
4. Highlight 2-3 most relevant experiences
5. Show genuine interest in the company/role
6. Include a strong closing call-to-action
7. Use specific examples from their resume

FORMAT REQUIREMENTS - Follow this exact professional cover letter structure:

[Your Name]
[Your Address]
[City, State ZIP Code]
[Your Email]
[Your Phone]
[Date]

[Hiring Manager's Name] (if known, otherwise "Hiring Manager")
{company_name}
[Company Address]
[City, State ZIP Code]

Dear [Hiring Manager's Name/Hiring Manager],

[OPENING PARAGRAPH - Express enthusiasm for the role and company. Mention how you learned about the position. Include a strong hook that demonstrates your understanding of the company/role.]

[BODY PARAGRAPH 1 - Highlight 2-3 key achievements from your experience that directly relate to the job requirements. Use specific examples with quantifiable results. Show how your skills match what they're looking for.]

[BODY PARAGRAPH 2 - Demonstrate knowledge of the company and explain why you're particularly interested in this role. Connect your career goals with the company's mission/values. Show cultural fit.]

[CLOSING PARAGRAPH - Reiterate your enthusiasm. Include a clear call-to-action expressing desire for an interview. Thank them for their consideration. End professionally.]

Sincerely,

[Your Name]

IMPORTANT:
- {lang_instruction}
- Make it unique and authentic, not generic
- Use the candidate's actual experiences and achievements
- Maintain a confident yet humble tone
- Avoid clichés and overused phrases
- Be specific and concrete, not vague
- Keep it focused and concise"""

        try:
            return self._call_gemini_with_retry(prompt, "cover_letter")
        except AIProcessingError as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return None
    
    def suggest_missing_experience(self, keywords_missing: list, resume_text: str,
                                   language: str = None) -> Optional[str]:
        """
        Suggest how to gain or highlight missing skills.

        Args:
            keywords_missing: List of missing skills/keywords
            resume_text: The candidate's resume
            language: ISO 639-1 language code. If None, auto-detects from resume.

        Returns:
            Skill suggestions in the detected/specified language
        """
        if not self._is_model_available():
            return None

        # Auto-detect language from resume if not specified
        if language is None:
            language = self.detect_language(resume_text)

        lang_instruction = self._get_language_instruction(language)

        resume_excerpt = resume_text[:1500] if resume_text else ""
        missing_skills = ', '.join(keywords_missing[:10]) if keywords_missing else 'None'

        prompt = f"""The candidate is missing these skills for their target role: {missing_skills}

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}

Based on their resume background:
{resume_excerpt}

Provide 5 specific, actionable suggestions for how they could:
1. Gain these skills (online courses, projects, certifications)
2. Highlight existing transferable experience
3. Reframe their experience to show these skills

IMPORTANT:
- {lang_instruction}
- Be specific with course names, project ideas, and phrasing examples
- Keep response under 500 words"""

        try:
            return self._call_gemini_with_retry(prompt, "skill_suggestions")
        except AIProcessingError as e:
            logger.error(f"Failed to generate skill suggestions: {e}")
            return None
    
    def _generate_fallback_feedback(self, match_score: float, keywords_missing: list) -> str:
        """Generate fallback feedback when AI is unavailable"""
        feedback_parts = [
            f"Your resume has a {match_score}% match with the job description.",
        ]
        
        if match_score < 50:
            feedback_parts.append("Consider significant revisions to better align with the job requirements.")
        elif match_score < 70:
            feedback_parts.append("Good alignment with room for improvement.")
        else:
            feedback_parts.append("Strong alignment! Your resume matches well with the job.")
        
        if keywords_missing:
            feedback_parts.append(f"Focus on adding these skills: {', '.join(keywords_missing[:5])}.")
        
        feedback_parts.extend([
            "Use action verbs and quantify your achievements.",
            "Tailor your professional summary to match the job requirements.",
            "Ensure your experience section highlights relevant projects."
        ])
        
        return " ".join(feedback_parts)

# Create global instance
gemini_service = GeminiService()

# Backward compatibility functions (now with optional language parameter)
def generate_personalized_feedback(resume_text: str, job_description: str,
                                 match_score: float, keywords_found: list,
                                 keywords_missing: list, language: str = None) -> str:
    """Backward compatibility function - language auto-detected if not provided"""
    return gemini_service.generate_personalized_feedback(
        resume_text, job_description, match_score, keywords_found, keywords_missing, language
    )

def generate_optimized_resume(resume_text: str, job_description: str,
                            keywords_missing: list, language: str = None) -> Optional[str]:
    """Backward compatibility function - language auto-detected if not provided"""
    return gemini_service.generate_optimized_resume(resume_text, job_description, keywords_missing, language)

def generate_cover_letter(resume_text: str, job_description: str,
                        company_name: str, job_title: str, language: str = None) -> Optional[str]:
    """Backward compatibility function - language auto-detected if not provided"""
    return gemini_service.generate_cover_letter(resume_text, job_description, company_name, job_title, language)

def suggest_missing_experience(keywords_missing: list, resume_text: str, language: str = None) -> Optional[str]:
    """Backward compatibility function - language auto-detected if not provided"""
    return gemini_service.suggest_missing_experience(keywords_missing, resume_text, language)

def detect_language(text: str) -> str:
    """Detect language of text - returns ISO 639-1 code"""
    return gemini_service.detect_language(text)
