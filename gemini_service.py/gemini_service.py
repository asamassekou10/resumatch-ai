import google.generativeai as genai
import os
import traceback
import time
from typing import Optional, Dict, Any
from errors import AIProcessingError
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class GeminiService:
    """Enhanced Gemini service with retry logic and error handling"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL_NAME', 'models/gemini-2.5-flash')
        self.model = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds
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
    
    def _call_gemini_with_retry(self, prompt: str, operation_name: str) -> Optional[str]:
        """Call Gemini API with retry logic"""
        if not self._is_model_available():
            raise AIProcessingError("Gemini AI service is not available")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Gemini API for {operation_name} (attempt {attempt + 1})")
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    logger.info(f"Gemini API {operation_name} completed successfully")
                    return response.text
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
                                    keywords_missing: list) -> str:
        """Generate detailed, personalized feedback using Gemini AI"""
        if not self._is_model_available():
            return self._generate_fallback_feedback(match_score, keywords_missing)
        
        # Limit text lengths to avoid token limits
        resume_excerpt = resume_text[:2000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""
        
        prompt = f"""You are an expert career coach and resume writer. Analyze this resume against the job description and provide specific, actionable feedback.

RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{job_excerpt}

CURRENT ANALYSIS:
- Match Score: {match_score}%
- Keywords Found: {', '.join(keywords_found[:10]) if keywords_found else 'None'}
- Keywords Missing: {', '.join(keywords_missing[:10]) if keywords_missing else 'None'}

Please provide:
1. **Overall Assessment** (2-3 sentences about the current match)
2. **Specific Strengths** (3 things this resume does well for this job)
3. **Critical Gaps** (3 most important things missing)
4. **Action Items** (5 specific changes to make, with examples)
5. **Keyword Integration Tips** (How to naturally add missing keywords)

Be specific, encouraging, and actionable. Focus on what the candidate CAN control. Keep the response under 800 words."""

        try:
            return self._call_gemini_with_retry(prompt, "personalized_feedback")
        except AIProcessingError as e:
            logger.error(f"Failed to generate personalized feedback: {e}")
            return self._generate_fallback_feedback(match_score, keywords_missing)
    
    def generate_optimized_resume(self, resume_text: str, job_description: str, 
                                keywords_missing: list) -> Optional[str]:
        """Generate an optimized version of the resume tailored to the job"""
        if not self._is_model_available():
            return None
        
        # Limit text lengths to avoid token limits
        resume_excerpt = resume_text[:3000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""
        
        prompt = f"""You are an expert resume writer. Rewrite this resume to better match the job description while maintaining the candidate's authentic experience and achievements.

ORIGINAL RESUME:
{resume_excerpt}

TARGET JOB DESCRIPTION:
{job_excerpt}

MISSING KEYWORDS TO INTEGRATE:
{', '.join(keywords_missing[:15]) if keywords_missing else 'None'}

INSTRUCTIONS:
1. Keep all real experiences and achievements - DO NOT fabricate
2. Rephrase bullets to include relevant keywords naturally
3. Emphasize experiences that match the job requirements
4. Add a professional summary tailored to this role
5. Reorganize sections to highlight most relevant experience first
6. Use action verbs and quantify achievements where possible
7. Integrate missing keywords ONLY where they genuinely apply

FORMAT: Return the complete optimized resume in a clean, professional format.

IMPORTANT: Be honest - only include keywords where the candidate actually has that experience."""

        try:
            return self._call_gemini_with_retry(prompt, "optimized_resume")
        except AIProcessingError as e:
            logger.error(f"Failed to generate optimized resume: {e}")
            return None
    
    def generate_cover_letter(self, resume_text: str, job_description: str, 
                            company_name: str, job_title: str) -> Optional[str]:
        """Generate a tailored cover letter"""
        if not self._is_model_available():
            return None
        
        # Limit text lengths to avoid token limits
        resume_excerpt = resume_text[:2000] if resume_text else ""
        job_excerpt = job_description[:1500] if job_description else ""
        
        prompt = f"""Write a compelling cover letter for this candidate applying to {company_name} for the {job_title} position.

CANDIDATE'S RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{job_excerpt}

REQUIREMENTS:
1. Professional yet personable tone
2. 3-4 paragraphs (250-300 words)
3. Highlight 2-3 most relevant experiences
4. Show genuine interest in the company/role
5. Include a strong closing call-to-action
6. Use specific examples from their resume

Make it unique and authentic, not generic."""

        try:
            return self._call_gemini_with_retry(prompt, "cover_letter")
        except AIProcessingError as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return None
    
    def suggest_missing_experience(self, keywords_missing: list, resume_text: str) -> Optional[str]:
        """Suggest how to gain or highlight missing skills"""
        if not self._is_model_available():
            return None
        
        resume_excerpt = resume_text[:1500] if resume_text else ""
        missing_skills = ', '.join(keywords_missing[:10]) if keywords_missing else 'None'
        
        prompt = f"""The candidate is missing these skills for their target role: {missing_skills}

Based on their resume background:
{resume_excerpt}

Provide 5 specific, actionable suggestions for how they could:
1. Gain these skills (online courses, projects, certifications)
2. Highlight existing transferable experience
3. Reframe their experience to show these skills

Be specific with course names, project ideas, and phrasing examples. Keep response under 500 words."""

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

# Backward compatibility functions
def generate_personalized_feedback(resume_text: str, job_description: str, 
                                 match_score: float, keywords_found: list, 
                                 keywords_missing: list) -> str:
    """Backward compatibility function"""
    return gemini_service.generate_personalized_feedback(
        resume_text, job_description, match_score, keywords_found, keywords_missing
    )

def generate_optimized_resume(resume_text: str, job_description: str, 
                            keywords_missing: list) -> Optional[str]:
    """Backward compatibility function"""
    return gemini_service.generate_optimized_resume(resume_text, job_description, keywords_missing)

def generate_cover_letter(resume_text: str, job_description: str, 
                        company_name: str, job_title: str) -> Optional[str]:
    """Backward compatibility function"""
    return gemini_service.generate_cover_letter(resume_text, job_description, company_name, job_title)

def suggest_missing_experience(keywords_missing: list, resume_text: str) -> Optional[str]:
    """Backward compatibility function"""
    return gemini_service.suggest_missing_experience(keywords_missing, resume_text)
