"""
Career Path Service - AI-powered career roadmap generation using Google Gemini
Provides personalized career progression strategies and actionable plans
"""

import os
import json
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import google.generativeai as genai
from models import User, CareerPath, db

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set - career path will use fallback data")


class CareerPathService:
    """AI-powered career path generation service using Gemini"""

    def __init__(self):
        """Initialize the career path service"""
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.ai_enabled = True
        else:
            self.model = None
            self.ai_enabled = False
            logger.info("Career path running in fallback mode (no AI)")

    def generate_career_path(
        self,
        user_id: int,
        current_role: str,
        target_role: str,
        industry: Optional[str] = None,
        years_of_experience: Optional[int] = None,
        current_skills: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Generate AI-powered career path roadmap

        Args:
            user_id: User ID
            current_role: Current position
            target_role: Desired target position
            industry: Industry (optional)
            years_of_experience: Years of experience (optional)
            current_skills: List of current skills (optional)
            force_refresh: Force regeneration ignoring cache

        Returns:
            Dict with career path data
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Check for existing cached path (30-day cache)
            if not force_refresh:
                existing_path = CareerPath.query.filter_by(
                    user_id=user_id,
                    current_role=current_role,
                    target_role=target_role
                ).first()

                if existing_path and existing_path.is_cached():
                    logger.info(f"Using cached career path: {current_role} → {target_role}")
                    return existing_path.to_dict()

            # Generate path content with AI
            if self.ai_enabled:
                path_data = self._generate_path_with_ai(
                    current_role,
                    target_role,
                    industry,
                    years_of_experience,
                    current_skills
                )
            else:
                path_data = self._generate_path_fallback(
                    current_role,
                    target_role,
                    industry
                )

            # Save or update in database
            if existing_path:
                # Update existing
                self._update_path_object(existing_path, path_data)
                existing_path.updated_at = datetime.utcnow()
                existing_path.cached_until = datetime.utcnow() + timedelta(days=90)  # Increased from 30 to 90 days
                path_obj = existing_path
            else:
                # Create new
                path_obj = self._create_path_object(
                    user_id, current_role, target_role, industry,
                    years_of_experience, current_skills, path_data
                )
                db.session.add(path_obj)

            db.session.commit()
            logger.info(f"Generated career path: {current_role} → {target_role}")

            return path_obj.to_dict()

        except Exception as e:
            logger.error(f"Error generating career path: {str(e)}")
            raise

    def _generate_path_with_ai(
        self,
        current_role: str,
        target_role: str,
        industry: Optional[str],
        years_of_experience: Optional[int],
        current_skills: Optional[List[str]]
    ) -> Dict:
        """Generate career path using Gemini AI"""
        try:
            # Build context
            skills_context = ""
            if current_skills and len(current_skills) > 0:
                skills_context = f"\nCurrent Skills: {', '.join(current_skills)}"

            experience_context = ""
            if years_of_experience is not None:
                experience_context = f"\nYears of Experience: {years_of_experience}"

            prompt = f"""
Generate a comprehensive, actionable career roadmap for transitioning from **{current_role}** to **{target_role}** in the {industry or 'Technology'} industry.{experience_context}{skills_context}

Provide a detailed, realistic career progression plan in the following JSON structure:

```json
{{
  "path_summary": "2-3 paragraph executive summary of the career path, key challenges, and what makes this transition achievable",
  "estimated_duration": "2-3 years" (or realistic timeframe),
  "difficulty_level": "Moderate" (Beginner-friendly/Moderate/Challenging),

  "career_steps": [
    {{
      "step_number": 1,
      "title": "Step title (e.g., 'Master Core Technical Skills')",
      "description": "Detailed description of what this step involves",
      "duration": "3-6 months",
      "skills_to_acquire": ["Skill 1", "Skill 2", "Skill 3"],
      "key_actions": [
        "Specific action item 1",
        "Specific action item 2"
      ],
      "certifications": ["Optional certification relevant to this step"],
      "success_metrics": "How to know you've completed this step"
    }},
    {{
      "step_number": 2,
      "title": "Next step title",
      "description": "...",
      "duration": "6-12 months",
      "skills_to_acquire": ["..."],
      "key_actions": ["..."],
      "certifications": ["..."],
      "success_metrics": "..."
    }}
    // Include 4-6 progressive steps
  ],

  "current_skills": ["Skill from current role", "Another transferable skill"],
  "skills_gap": [
    {{
      "skill": "Skill name",
      "importance": "Critical/Important/Nice-to-have",
      "how_to_acquire": "Specific learning path"
    }}
  ],
  "transferable_skills": ["Skill that transfers well", "Another one"],

  "learning_resources": [
    {{
      "type": "Online Course/Book/Bootcamp/Tutorial",
      "title": "Resource name",
      "provider": "Provider name",
      "url": "https://...",
      "description": "Why this resource is valuable",
      "cost": "$0 - $500 or Free",
      "priority": "High/Medium/Low"
    }}
  ],

  "certifications": [
    {{
      "name": "Certification name",
      "provider": "Provider",
      "cost": "$200",
      "duration": "3 months",
      "priority": "High/Medium/Low",
      "relevance": "Why this certification matters"
    }}
  ],

  "salary_expectations": [
    {{
      "role": "Entry-level position in path",
      "min_salary": 60000,
      "max_salary": 80000,
      "median_salary": 70000
    }},
    {{
      "role": "{target_role}",
      "min_salary": 100000,
      "max_salary": 150000,
      "median_salary": 125000
    }}
  ],

  "alternative_paths": [
    {{
      "path_name": "Alternative approach name",
      "description": "Brief description of alternative path",
      "duration": "Different timeline",
      "steps_summary": "High-level overview of steps"
    }}
  ],

  "networking_tips": "2-3 paragraphs about networking strategy for this transition, which events to attend, who to connect with",

  "mentor_guidance": "Advice on finding mentors for this transition, what to look for, how to approach them",

  "industry_connections": [
    {{
      "platform": "LinkedIn/Meetup/Conference",
      "group_or_event": "Specific group or event name",
      "why_join": "How this helps the transition"
    }}
  ],

  "key_milestones": [
    {{
      "milestone": "Milestone description",
      "timeframe": "Month 3-6",
      "success_criteria": "How to measure success",
      "importance": "High/Medium/Low"
    }}
  ],

  "success_stories": [
    {{
      "profile": "Brief anonymized profile (e.g., 'Software Engineer with 5 years experience')",
      "transition_time": "18 months",
      "key_factors": "What made them successful",
      "advice": "Their advice for others making this transition"
    }}
  ],

  "ai_recommendations": "2-3 paragraphs of strategic advice specifically for this career transition",

  "risk_factors": [
    {{
      "factor": "Potential challenge or risk",
      "impact": "High/Medium/Low",
      "mitigation": "How to address or minimize this risk"
    }}
  ],

  "success_factors": [
    {{
      "factor": "What increases likelihood of success",
      "impact": "High/Medium/Low",
      "how_to_leverage": "Practical advice to leverage this factor"
    }}
  ],

  "job_market_outlook": "2-3 paragraphs about current market conditions for {target_role}, hiring trends, demand",

  "demand_trend": "Growing/Stable/Declining"
}}
```

**IMPORTANT:**
- Provide ONLY the JSON, no other text
- Be specific and actionable - avoid generic advice
- Base on realistic 2024 market conditions
- Tailor to the specific transition from {current_role} to {target_role}
- Include 4-6 progressive career steps
- Provide concrete resources with real URLs where possible
- Make success metrics measurable
- Salary ranges should be realistic for the industry and roles
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
                    logger.warning(f"Gemini API timeout for career path {current_role} -> {target_role}, using fallback")
                    return self._generate_path_fallback(current_role, target_role, industry)
                raise

            # Parse AI response
            path_data = self._parse_ai_response(result_text)

            # Validate
            if not path_data.get('path_summary'):
                raise ValueError("No path summary generated")

            if not path_data.get('career_steps') or len(path_data.get('career_steps', [])) < 3:
                raise ValueError("Insufficient career steps generated")

            return path_data

        except Exception as e:
            logger.error(f"AI path generation failed, using fallback: {str(e)}")
            return self._generate_path_fallback(current_role, target_role, industry)

    def _generate_path_fallback(
        self,
        current_role: str,
        target_role: str,
        industry: Optional[str]
    ) -> Dict:
        """Fallback career path generation (no AI required)"""

        return {
            "path_summary": f"A career transition from {current_role} to {target_role} in the {industry or 'Technology'} industry requires strategic planning and skill development. This roadmap is a starting point - please configure GEMINI_API_KEY for personalized, AI-powered guidance tailored to your specific situation.",

            "estimated_duration": "1-3 years (varies by individual)",
            "difficulty_level": "Moderate",

            "career_steps": [
                {
                    "step_number": 1,
                    "title": "Assess Current Position and Set Goals",
                    "description": "Evaluate your current skills, identify gaps, and set clear career objectives.",
                    "duration": "1-2 months",
                    "skills_to_acquire": ["Self-assessment", "Goal setting", "Career planning"],
                    "key_actions": [
                        "Document current skills and experiences",
                        "Research target role requirements",
                        "Create a detailed transition plan"
                    ],
                    "certifications": [],
                    "success_metrics": "Completed skills assessment and documented career plan"
                },
                {
                    "step_number": 2,
                    "title": "Acquire Essential Skills",
                    "description": "Focus on learning the core skills required for the target role.",
                    "duration": "6-12 months",
                    "skills_to_acquire": ["Industry-specific technical skills", "Relevant tools and technologies"],
                    "key_actions": [
                        "Enroll in relevant courses or bootcamps",
                        "Build portfolio projects",
                        "Practice consistently"
                    ],
                    "certifications": ["Industry-relevant certifications"],
                    "success_metrics": "Completed 2-3 portfolio projects demonstrating new skills"
                },
                {
                    "step_number": 3,
                    "title": "Gain Practical Experience",
                    "description": "Apply new skills through projects, freelancing, or internal opportunities.",
                    "duration": "6-12 months",
                    "skills_to_acquire": ["Practical application", "Project management"],
                    "key_actions": [
                        "Take on relevant projects at current job",
                        "Build a strong portfolio",
                        "Seek feedback from experienced professionals"
                    ],
                    "certifications": [],
                    "success_metrics": "3+ completed projects in target domain"
                },
                {
                    "step_number": 4,
                    "title": "Network and Transition",
                    "description": "Build connections in the target field and secure the new role.",
                    "duration": "3-6 months",
                    "skills_to_acquire": ["Networking", "Interview skills", "Personal branding"],
                    "key_actions": [
                        "Attend industry events and meetups",
                        "Connect with professionals on LinkedIn",
                        "Apply for target positions",
                        "Prepare for interviews"
                    ],
                    "certifications": [],
                    "success_metrics": "Secured interviews and received job offers"
                }
            ],

            "current_skills": ["Skills from current role require AI analysis"],
            "skills_gap": [
                {
                    "skill": "Detailed skills gap analysis requires AI configuration",
                    "importance": "Critical",
                    "how_to_acquire": "Configure GEMINI_API_KEY for personalized recommendations"
                }
            ],
            "transferable_skills": ["Leadership", "Communication", "Problem-solving"],

            "learning_resources": [
                {
                    "type": "Online Course",
                    "title": "Industry-specific courses on Coursera, Udemy, or LinkedIn Learning",
                    "provider": "Various",
                    "url": "https://www.coursera.org",
                    "description": "AI-powered recommendations will provide specific courses for your path",
                    "cost": "$0 - $500",
                    "priority": "High"
                }
            ],

            "certifications": [
                {
                    "name": "Industry-relevant certifications",
                    "provider": "Configure AI for specific recommendations",
                    "cost": "Varies",
                    "duration": "Varies",
                    "priority": "High",
                    "relevance": "AI will identify most valuable certifications for your transition"
                }
            ],

            "salary_expectations": [],

            "alternative_paths": [
                {
                    "path_name": "Gradual Internal Transition",
                    "description": "Transition within your current company if possible",
                    "duration": "1-2 years",
                    "steps_summary": "Express interest, take on cross-functional projects, gradually shift responsibilities"
                },
                {
                    "path_name": "Bootcamp + Direct Switch",
                    "description": "Intensive training followed by career change",
                    "duration": "6-12 months",
                    "steps_summary": "Complete intensive bootcamp, build portfolio, apply for entry-level target roles"
                }
            ],

            "networking_tips": "Networking is crucial for career transitions. Attend industry meetups and conferences, join professional associations, connect with people in your target role on LinkedIn, participate in online communities, and don't be afraid to ask for informational interviews. Configure GEMINI_API_KEY for role-specific networking strategies.",

            "mentor_guidance": "Finding a mentor who has made a similar transition can be invaluable. Look for mentors on platforms like LinkedIn, professional associations, or mentorship programs. When approaching potential mentors, be respectful of their time, come prepared with specific questions, and offer value in return where possible.",

            "industry_connections": [
                {
                    "platform": "LinkedIn",
                    "group_or_event": "Industry-specific groups",
                    "why_join": "Connect with professionals in target role"
                },
                {
                    "platform": "Meetup",
                    "group_or_event": "Local industry meetups",
                    "why_join": "Build local professional network"
                }
            ],

            "key_milestones": [
                {
                    "milestone": "Skills assessment completed",
                    "timeframe": "Month 1",
                    "success_criteria": "Documented current skills and target requirements",
                    "importance": "High"
                },
                {
                    "milestone": "First portfolio project completed",
                    "timeframe": "Month 3-6",
                    "success_criteria": "Working project demonstrating target skills",
                    "importance": "High"
                },
                {
                    "milestone": "First interview in target role",
                    "timeframe": "Month 12-18",
                    "success_criteria": "Scheduled and completed professional interview",
                    "importance": "High"
                }
            ],

            "success_stories": [
                {
                    "profile": "Professional making similar transition",
                    "transition_time": "Varies by individual",
                    "key_factors": "AI analysis will provide relevant success stories",
                    "advice": "Configure GEMINI_API_KEY for personalized success stories"
                }
            ],

            "ai_recommendations": f"Transitioning from {current_role} to {target_role} is achievable with proper planning and dedication. Focus on building relevant skills, creating a strong portfolio, and networking in your target industry. For personalized, detailed guidance based on your specific situation, please configure the GEMINI_API_KEY environment variable to enable AI-powered career path generation.",

            "risk_factors": [
                {
                    "factor": "Skills gap may be larger than anticipated",
                    "impact": "High",
                    "mitigation": "Regular self-assessment and seeking feedback from target industry professionals"
                },
                {
                    "factor": "Market conditions may change",
                    "impact": "Medium",
                    "mitigation": "Stay informed about industry trends and maintain flexibility in approach"
                }
            ],

            "success_factors": [
                {
                    "factor": "Consistent learning and practice",
                    "impact": "High",
                    "how_to_leverage": "Dedicate regular time to skill development and portfolio building"
                },
                {
                    "factor": "Strong professional network",
                    "impact": "High",
                    "how_to_leverage": "Actively network and build relationships in target industry"
                }
            ],

            "job_market_outlook": f"Job market analysis for {target_role} requires current data. Please configure GEMINI_API_KEY for AI-powered market insights based on latest 2024 trends. In general, research the role on job boards, industry reports, and professional networks to understand current demand.",

            "demand_trend": "Unknown (requires AI analysis)"
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
                if not data.get('path_summary'):
                    raise ValueError("No path summary in response")

                if not data.get('career_steps') or len(data.get('career_steps', [])) < 3:
                    raise ValueError("Insufficient career steps in response")

                return data
            else:
                raise ValueError("No JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            raise

    def _create_path_object(
        self,
        user_id: int,
        current_role: str,
        target_role: str,
        industry: Optional[str],
        years_of_experience: Optional[int],
        current_skills: Optional[List[str]],
        data: Dict
    ) -> CareerPath:
        """Create new CareerPath object"""
        return CareerPath(
            user_id=user_id,
            current_role=current_role,
            target_role=target_role,
            industry=industry or data.get('industry'),
            years_of_experience=years_of_experience,

            path_summary=data.get('path_summary'),
            estimated_duration=data.get('estimated_duration'),
            difficulty_level=data.get('difficulty_level'),

            career_steps=data.get('career_steps'),

            current_skills=current_skills or data.get('current_skills'),
            skills_gap=data.get('skills_gap'),
            transferable_skills=data.get('transferable_skills'),

            learning_resources=data.get('learning_resources'),
            certifications=data.get('certifications'),

            salary_expectations=data.get('salary_expectations'),
            alternative_paths=data.get('alternative_paths'),

            networking_tips=data.get('networking_tips'),
            mentor_guidance=data.get('mentor_guidance'),
            industry_connections=data.get('industry_connections'),

            key_milestones=data.get('key_milestones'),
            success_stories=data.get('success_stories'),

            ai_recommendations=data.get('ai_recommendations'),
            risk_factors=data.get('risk_factors'),
            success_factors=data.get('success_factors'),

            job_market_outlook=data.get('job_market_outlook'),
            demand_trend=data.get('demand_trend'),

            cached_until=datetime.utcnow() + timedelta(days=90)  # Increased from 30 to 90 days
        )

    def _update_path_object(self, path_obj: CareerPath, data: Dict):
        """Update existing CareerPath object"""
        path_obj.path_summary = data.get('path_summary')
        path_obj.estimated_duration = data.get('estimated_duration')
        path_obj.difficulty_level = data.get('difficulty_level')

        path_obj.career_steps = data.get('career_steps')

        path_obj.current_skills = path_obj.current_skills or data.get('current_skills')
        path_obj.skills_gap = data.get('skills_gap')
        path_obj.transferable_skills = data.get('transferable_skills')

        path_obj.learning_resources = data.get('learning_resources')
        path_obj.certifications = data.get('certifications')

        path_obj.salary_expectations = data.get('salary_expectations')
        path_obj.alternative_paths = data.get('alternative_paths')

        path_obj.networking_tips = data.get('networking_tips')
        path_obj.mentor_guidance = data.get('mentor_guidance')
        path_obj.industry_connections = data.get('industry_connections')

        path_obj.key_milestones = data.get('key_milestones')
        path_obj.success_stories = data.get('success_stories')

        path_obj.ai_recommendations = data.get('ai_recommendations')
        path_obj.risk_factors = data.get('risk_factors')
        path_obj.success_factors = data.get('success_factors')

        path_obj.job_market_outlook = data.get('job_market_outlook')
        path_obj.demand_trend = data.get('demand_trend')


# Singleton instance
_career_path_instance = None

def get_career_path_service() -> CareerPathService:
    """Get singleton instance of CareerPathService"""
    global _career_path_instance
    if _career_path_instance is None:
        _career_path_instance = CareerPathService()
    return _career_path_instance
