"""
Interview Prep Service - AI-powered interview preparation using Google Gemini
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import google.generativeai as genai
from models import User, InterviewPrep, Analysis, db

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set - interview prep will use fallback data")


class InterviewPrepService:
    """AI-powered interview preparation service using Gemini"""

    def __init__(self):
        """Initialize the interview prep service"""
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.ai_enabled = True
        else:
            self.model = None
            self.ai_enabled = False
            logger.info("Interview prep running in fallback mode (no AI)")

    def generate_interview_prep(
        self,
        user_id: int,
        company: str,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Generate AI-powered interview preparation for a specific company/role

        Args:
            user_id: User ID
            company: Company name
            job_title: Job title (optional)
            industry: Industry (optional)
            force_refresh: Force regeneration ignoring cache

        Returns:
            Dict with interview prep data
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Check for existing cached prep (1 week cache)
            if not force_refresh:
                existing_prep = InterviewPrep.query.filter_by(
                    user_id=user_id,
                    company=company
                ).first()

                if existing_prep and existing_prep.is_cached():
                    logger.info(f"Using cached interview prep for {company}")
                    return existing_prep.to_dict()

            # Get user's background from resume
            user_skills, user_experience = self._get_user_background(user_id)

            # Generate prep content with AI
            if self.ai_enabled:
                prep_data = self._generate_prep_with_ai(
                    company, job_title, industry, user_skills, user_experience
                )
            else:
                prep_data = self._generate_prep_fallback(
                    company, job_title, industry
                )

            # Save or update in database
            if existing_prep:
                # Update existing
                existing_prep.job_title = job_title
                existing_prep.industry = industry
                existing_prep.questions = prep_data['questions']
                existing_prep.company_culture = prep_data['company_culture']
                existing_prep.interview_process = prep_data['interview_process']
                existing_prep.interview_tips = prep_data['interview_tips']
                existing_prep.common_topics = prep_data['common_topics']
                existing_prep.updated_at = datetime.utcnow()
                existing_prep.cached_until = datetime.utcnow() + timedelta(days=90)  # Increased from 7 to 90 days
                prep_obj = existing_prep
            else:
                # Create new
                prep_obj = InterviewPrep(
                    user_id=user_id,
                    company=company,
                    job_title=job_title,
                    industry=industry,
                    questions=prep_data['questions'],
                    company_culture=prep_data['company_culture'],
                    interview_process=prep_data['interview_process'],
                    interview_tips=prep_data['interview_tips'],
                    common_topics=prep_data['common_topics'],
                    cached_until=datetime.utcnow() + timedelta(days=90)  # Increased from 7 to 90 days
                )
                db.session.add(prep_obj)

            db.session.commit()
            logger.info(f"Generated interview prep for {company}")

            return prep_obj.to_dict()

        except Exception as e:
            logger.error(f"Error generating interview prep: {str(e)}")
            raise

    def _get_user_background(self, user_id: int) -> tuple:
        """Get user's skills and experience from resume analyses"""
        latest_analysis = Analysis.query.filter_by(
            user_id=user_id
        ).order_by(Analysis.created_at.desc()).first()

        skills = []
        experience_level = 'Mid'

        if latest_analysis:
            if latest_analysis.keywords_found:
                skills = latest_analysis.keywords_found[:10]  # Top 10 skills

        user = User.query.get(user_id)
        if user and user.experience_level:
            experience_level = user.experience_level

        return skills, experience_level

    def _generate_prep_with_ai(
        self,
        company: str,
        job_title: Optional[str],
        industry: Optional[str],
        user_skills: List[str],
        user_experience: str
    ) -> Dict:
        """Generate interview prep using Gemini AI"""
        try:
            prompt = f"""
Generate comprehensive interview preparation for this company and role:

**Company:** {company}
**Role:** {job_title or 'General position'}
**Industry:** {industry or 'Technology'}

**Candidate Background:**
- Skills: {', '.join(user_skills) if user_skills else 'General technical skills'}
- Experience Level: {user_experience}

**Generate the following:**

1. **10 Interview Questions** covering:
   - Technical questions (3-4)
   - Behavioral questions (3-4)
   - Company-specific questions (2-3)

2. **Company Culture Analysis** (2-3 paragraphs about {company}'s culture, values, and work environment)

3. **Interview Process** (typical rounds, stages, and timeline for {company})

4. **5 Interview Tips** specific to {company}

5. **Common Topics** (5-6 topics frequently discussed in {company} interviews)

**Output Format (JSON only):**
```json
{{
    "questions": [
        {{
            "question": "Question text here",
            "type": "technical",
            "answer_framework": "STAR framework: Situation - Task - Action - Result. Focus on...",
            "tips": "Tip for answering this question"
        }}
    ],
    "company_culture": "Company culture description...",
    "interview_process": {{
        "rounds": 3,
        "stages": ["Phone Screen", "Technical Interview", "Final Round"],
        "duration": "2-3 weeks"
    }},
    "interview_tips": [
        "Tip 1",
        "Tip 2",
        "Tip 3",
        "Tip 4",
        "Tip 5"
    ],
    "common_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]
}}
```

Provide ONLY the JSON, no other text. Make it specific to {company}.
"""

            # Call Gemini API with timeout
            import asyncio
            from concurrent.futures import TimeoutError as FutureTimeoutError

            try:
                # Set 30-second timeout for API call
                response = self.model.generate_content(
                    prompt,
                    request_options={'timeout': 30}
                )
                result_text = response.text.strip()
            except (TimeoutError, FutureTimeoutError, Exception) as e:
                if 'timeout' in str(e).lower():
                    logger.warning(f"Gemini API timeout for {company} interview prep, using fallback")
                    return self._generate_prep_fallback(company, job_title, industry)
                raise

            # Parse AI response
            prep_data = self._parse_ai_response(result_text)

            # Validate and sanitize
            if not prep_data.get('questions'):
                raise ValueError("No questions generated")

            return prep_data

        except Exception as e:
            logger.error(f"AI prep generation failed, using fallback: {str(e)}")
            return self._generate_prep_fallback(company, job_title, industry)

    def _generate_prep_fallback(
        self,
        company: str,
        job_title: Optional[str],
        industry: Optional[str]
    ) -> Dict:
        """Fallback interview prep generation (no AI required)"""

        # Generic interview questions
        questions = [
            {
                "question": f"Tell me about yourself and why you want to work at {company}?",
                "type": "behavioral",
                "answer_framework": "Use the present-past-future framework. Present: Current role/skills. Past: Relevant experience. Future: Why this company aligns with your goals.",
                "tips": f"Research {company}'s mission and values. Connect your experience to what they're looking for."
            },
            {
                "question": f"What do you know about {company} and our products/services?",
                "type": "behavioral",
                "answer_framework": "Demonstrate research: mention recent news, products, company values, and why they interest you.",
                "tips": "Visit company website, read recent press releases, and understand their market position."
            },
            {
                "question": "Describe a challenging project you worked on. How did you overcome obstacles?",
                "type": "behavioral",
                "answer_framework": "STAR method: Situation (context), Task (your responsibility), Action (steps you took), Result (outcome and learning).",
                "tips": "Choose a project relevant to this role. Quantify results when possible."
            },
            {
                "question": "How do you handle tight deadlines and conflicting priorities?",
                "type": "behavioral",
                "answer_framework": "Describe your prioritization process, communication with stakeholders, and time management techniques.",
                "tips": "Give specific examples. Show how you stay calm under pressure."
            },
            {
                "question": f"What technical skills do you bring that would benefit {company}?",
                "type": "technical",
                "answer_framework": "Highlight 3-4 key technical skills. For each, provide a brief example of how you've used it effectively.",
                "tips": "Align your skills with the job description. Be ready to discuss in depth."
            },
            {
                "question": "Walk me through your approach to solving a complex technical problem.",
                "type": "technical",
                "answer_framework": "Problem understanding → Research → Design → Implementation → Testing → Learning. Use a specific example.",
                "tips": "Show your thought process, not just the solution. Mention collaboration."
            },
            {
                "question": "How do you stay updated with industry trends and new technologies?",
                "type": "technical",
                "answer_framework": "Mention specific resources: blogs, courses, communities, conferences. Show continuous learning mindset.",
                "tips": "Demonstrate genuine interest in growth, not just checkbox learning."
            },
            {
                "question": "Describe a time you had to work with a difficult team member.",
                "type": "behavioral",
                "answer_framework": "STAR method focusing on empathy, communication, and finding common ground to achieve team goals.",
                "tips": "Focus on positive resolution. Show emotional intelligence."
            },
            {
                "question": f"Where do you see yourself in 3-5 years, ideally at {company}?",
                "type": "behavioral",
                "answer_framework": "Show ambition aligned with company growth. Mention skill development and potential leadership.",
                "tips": "Research career paths at the company. Be realistic but ambitious."
            },
            {
                "question": "Do you have any questions for us?",
                "type": "behavioral",
                "answer_framework": "Always have 3-5 thoughtful questions about company culture, team dynamics, growth opportunities, or recent company news.",
                "tips": "This shows genuine interest. Avoid questions about salary/benefits in first interview."
            }
        ]

        # Generic company culture description
        company_culture = f"{company} is known for fostering innovation and collaboration. The company values include integrity, customer focus, and continuous improvement. Employees often describe the work environment as fast-paced but supportive, with opportunities for professional growth. The company encourages work-life balance and offers various employee development programs."

        # Generic interview process
        interview_process = {
            "rounds": 3,
            "stages": ["Phone/Video Screen", "Technical/Skills Assessment", "Final Interview with Hiring Manager"],
            "duration": "2-4 weeks"
        }

        # Generic interview tips
        interview_tips = [
            f"Research {company}'s recent news, products, and company values before the interview",
            "Prepare specific examples using the STAR method for behavioral questions",
            "Practice technical skills relevant to the role and be ready for hands-on assessments",
            "Dress professionally and test your technology setup if it's a video interview",
            "Follow up with a thank-you email within 24 hours, referencing specific discussion points"
        ]

        # Common topics
        common_topics = [
            "Technical skills and experience",
            "Problem-solving approach",
            "Team collaboration",
            "Company culture fit",
            "Career goals and motivations"
        ]

        return {
            "questions": questions,
            "company_culture": company_culture,
            "interview_process": interview_process,
            "interview_tips": interview_tips,
            "common_topics": common_topics
        }

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response and extract JSON"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                # Remove markdown code blocks if present
                json_str = re.sub(r'```json\s*|\s*```', '', json_str)
                data = json.loads(json_str)

                # Validate required fields
                if not data.get('questions'):
                    raise ValueError("No questions in response")

                return data
            else:
                raise ValueError("No JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            raise


# Singleton instance
_interview_prep_instance = None

def get_interview_prep_service() -> InterviewPrepService:
    """Get singleton instance of InterviewPrepService"""
    global _interview_prep_instance
    if _interview_prep_instance is None:
        _interview_prep_instance = InterviewPrepService()
    return _interview_prep_instance
