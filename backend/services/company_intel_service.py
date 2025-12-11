"""
Company Intel Service - AI-powered company research and intelligence using Google Gemini
"""

import os
import json
import re
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import google.generativeai as genai
from models import User, CompanyIntel, db

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set - company intel will use fallback data")


class CompanyIntelService:
    """AI-powered company intelligence service using Gemini"""

    def __init__(self):
        """Initialize the company intel service"""
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.ai_enabled = True
        else:
            self.model = None
            self.ai_enabled = False
            logger.info("Company intel running in fallback mode (no AI)")

    def generate_company_intel(
        self,
        user_id: int,
        company: str,
        industry: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Generate AI-powered company intelligence

        Args:
            user_id: User ID
            company: Company name
            industry: Industry (optional)
            force_refresh: Force regeneration ignoring cache

        Returns:
            Dict with company intelligence data
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Check for existing cached intel (14-day cache)
            if not force_refresh:
                existing_intel = CompanyIntel.query.filter_by(
                    user_id=user_id,
                    company=company
                ).first()

                if existing_intel and existing_intel.is_cached():
                    logger.info(f"Using cached company intel for {company}")
                    return existing_intel.to_dict()

            # Generate intel content with AI
            if self.ai_enabled:
                intel_data = self._generate_intel_with_ai(company, industry)
            else:
                intel_data = self._generate_intel_fallback(company, industry)

            # Save or update in database
            if existing_intel:
                # Update existing
                self._update_intel_object(existing_intel, intel_data)
                existing_intel.updated_at = datetime.utcnow()
                existing_intel.cached_until = datetime.utcnow() + timedelta(days=90)  # Increased from 14 to 90 days
                intel_obj = existing_intel
            else:
                # Create new
                intel_obj = self._create_intel_object(user_id, company, industry, intel_data)
                db.session.add(intel_obj)

            db.session.commit()
            logger.info(f"Generated company intel for {company}")

            return intel_obj.to_dict()

        except Exception as e:
            logger.error(f"Error generating company intel: {str(e)}")
            raise

    def _generate_intel_with_ai(self, company: str, industry: Optional[str]) -> Dict:
        """Generate company intelligence using Gemini AI"""
        try:
            prompt = f"""
Generate comprehensive company intelligence for **{company}** in the {industry or 'Technology'} industry.

Provide detailed, factual information (as of 2024) about this company in the following JSON structure:

```json
{{
  "overview": "2-3 paragraph company description including founding story, mission, and current position",
  "founded_year": 2000,
  "headquarters": "City, State/Country",
  "company_size": "1,000-5,000 employees",
  "website": "https://company.com",

  "products_services": [
    {{"name": "Product/Service Name", "description": "What it does and who it serves"}}
  ],

  "target_markets": ["Market 1", "Market 2", "Market 3"],

  "competitors": [
    {{"name": "Competitor 1", "comparison": "Brief comparison"}}
  ],

  "company_culture": "2-3 paragraphs about work culture, values in action, and employee experience",

  "core_values": ["Value 1", "Value 2", "Value 3"],

  "work_environment": "Description of typical work environment (remote, hybrid, office, work-life balance)",

  "recent_news": [
    {{"title": "News headline", "summary": "Brief summary", "date": "2024-XX-XX", "source": "Source"}}
  ],

  "major_developments": ["Recent major achievement or change", "Another development"],

  "leadership": [
    {{"name": "CEO Name", "title": "Chief Executive Officer", "bio": "Brief background"}}
  ],

  "financial_health": {{
    "revenue": "Approximate revenue or range",
    "funding": "Funding status (bootstrapped, Series A-D, IPO, etc.)",
    "profitability": "Profitable/Not profitable/Unknown",
    "valuation": "Estimated valuation if known"
  }},

  "growth_metrics": {{
    "employee_growth": "Growing/Stable/Declining",
    "revenue_growth": "Growth rate or trend",
    "market_share": "Market position"
  }},

  "interview_insights": "2-3 paragraphs about typical interview process, difficulty, and what they look for",

  "employee_sentiment": "Analysis of employee satisfaction based on common feedback (Glassdoor-style)",

  "pros_cons": {{
    "pros": ["Advantage 1", "Advantage 2", "Advantage 3"],
    "cons": ["Challenge 1", "Challenge 2", "Challenge 3"]
  }},

  "tech_stack": {{
    "languages": ["Python", "JavaScript", etc.],
    "frameworks": ["React", "Django", etc.],
    "tools": ["AWS", "Docker", etc.]
  }},

  "ai_summary": "Executive summary (2-3 sentences) highlighting key points for job seekers",

  "key_insights": [
    "Important insight 1",
    "Important insight 2",
    "Important insight 3"
  ],

  "recommendations": [
    "Recommendation for job seekers interested in this company",
    "Another actionable recommendation"
  ]
}}
```

**IMPORTANT:**
- Provide ONLY the JSON, no other text
- Be specific to {company}
- Base on 2024 knowledge
- If uncertain about specific data (like exact revenue), provide reasonable estimates or ranges
- Focus on information valuable for job seekers
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
                    logger.warning(f"Gemini API timeout for {company}, using fallback")
                    return self._generate_intel_fallback(company, industry)
                raise

            # Parse AI response
            intel_data = self._parse_ai_response(result_text)

            # Validate
            if not intel_data.get('overview'):
                raise ValueError("No overview generated")

            return intel_data

        except Exception as e:
            logger.error(f"AI intel generation failed, using fallback: {str(e)}")
            return self._generate_intel_fallback(company, industry)

    def _generate_intel_fallback(self, company: str, industry: Optional[str]) -> Dict:
        """Fallback company intelligence generation (no AI required)"""

        return {
            "overview": f"{company} is a company in the {industry or 'Technology'} industry. This company has established itself as a player in its market segment. Further detailed research is recommended for comprehensive insights.",
            "founded_year": None,
            "headquarters": "Information not available",
            "company_size": "Information not available",
            "website": f"https://{company.lower().replace(' ', '')}.com",

            "products_services": [
                {
                    "name": "Primary Product/Service",
                    "description": f"{company} offers products and services in the {industry or 'Technology'} sector."
                }
            ],

            "target_markets": [
                industry or "Technology",
                "Enterprise",
                "Consumer"
            ],

            "competitors": [
                {
                    "name": "Industry competitors",
                    "comparison": "Competitive analysis requires further research"
                }
            ],

            "company_culture": f"Company culture information for {company} is not available in fallback mode. We recommend researching employee reviews on platforms like Glassdoor, LinkedIn, and Indeed for authentic insights into the work environment, values, and employee experiences.",

            "core_values": [
                "Innovation",
                "Customer Focus",
                "Integrity",
                "Collaboration"
            ],

            "work_environment": "Work environment details require research. Check company careers page and employee reviews.",

            "recent_news": [],

            "major_developments": [
                "Recent developments require current news research"
            ],

            "leadership": [],

            "financial_health": {
                "revenue": "Not available",
                "funding": "Not available",
                "profitability": "Unknown",
                "valuation": "Not available"
            },

            "growth_metrics": {
                "employee_growth": "Research required",
                "revenue_growth": "Research required",
                "market_share": "Research required"
            },

            "interview_insights": f"Interview process for {company} typically includes multiple rounds. We recommend researching on Glassdoor and preparing for both technical and behavioral questions. Practice common interview scenarios and prepare thoughtful questions about the role and company.",

            "employee_sentiment": "Employee reviews and sentiment analysis require research on platforms like Glassdoor, Indeed, and LinkedIn.",

            "pros_cons": {
                "pros": [
                    "Research employee reviews for authentic insights",
                    "Check Glassdoor and Indeed for detailed feedback",
                    "Connect with current employees on LinkedIn"
                ],
                "cons": [
                    "Limited information in fallback mode",
                    "Requires manual research for comprehensive insights"
                ]
            },

            "tech_stack": {
                "languages": [],
                "frameworks": [],
                "tools": []
            },

            "ai_summary": f"Comprehensive intelligence for {company} requires AI analysis. Please ensure GEMINI_API_KEY is configured for detailed insights.",

            "key_insights": [
                "AI-powered insights require Gemini API key",
                f"Research {company} on LinkedIn, Glassdoor, and company website",
                "Connect with current employees for authentic insights"
            ],

            "recommendations": [
                "Research the company thoroughly before applying",
                "Read recent employee reviews on Glassdoor",
                "Visit the company's careers page and blog",
                "Connect with employees on LinkedIn"
            ]
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
                if not data.get('overview'):
                    raise ValueError("No overview in response")

                return data
            else:
                raise ValueError("No JSON found in AI response")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            raise

    def _create_intel_object(self, user_id: int, company: str, industry: Optional[str], data: Dict) -> CompanyIntel:
        """Create new CompanyIntel object"""
        return CompanyIntel(
            user_id=user_id,
            company=company,
            industry=industry or data.get('industry'),
            overview=data.get('overview'),
            founded_year=data.get('founded_year'),
            headquarters=data.get('headquarters'),
            company_size=data.get('company_size'),
            website=data.get('website'),
            products_services=data.get('products_services'),
            target_markets=data.get('target_markets'),
            competitors=data.get('competitors'),
            company_culture=data.get('company_culture'),
            core_values=data.get('core_values'),
            work_environment=data.get('work_environment'),
            recent_news=data.get('recent_news'),
            major_developments=data.get('major_developments'),
            leadership=data.get('leadership'),
            financial_health=data.get('financial_health'),
            growth_metrics=data.get('growth_metrics'),
            interview_insights=data.get('interview_insights'),
            employee_sentiment=data.get('employee_sentiment'),
            pros_cons=data.get('pros_cons'),
            tech_stack=data.get('tech_stack'),
            ai_summary=data.get('ai_summary'),
            key_insights=data.get('key_insights'),
            recommendations=data.get('recommendations'),
            cached_until=datetime.utcnow() + timedelta(days=90)  # Increased from 14 to 90 days
        )

    def _update_intel_object(self, intel_obj: CompanyIntel, data: Dict):
        """Update existing CompanyIntel object"""
        intel_obj.industry = intel_obj.industry or data.get('industry')
        intel_obj.overview = data.get('overview')
        intel_obj.founded_year = data.get('founded_year')
        intel_obj.headquarters = data.get('headquarters')
        intel_obj.company_size = data.get('company_size')
        intel_obj.website = data.get('website')
        intel_obj.products_services = data.get('products_services')
        intel_obj.target_markets = data.get('target_markets')
        intel_obj.competitors = data.get('competitors')
        intel_obj.company_culture = data.get('company_culture')
        intel_obj.core_values = data.get('core_values')
        intel_obj.work_environment = data.get('work_environment')
        intel_obj.recent_news = data.get('recent_news')
        intel_obj.major_developments = data.get('major_developments')
        intel_obj.leadership = data.get('leadership')
        intel_obj.financial_health = data.get('financial_health')
        intel_obj.growth_metrics = data.get('growth_metrics')
        intel_obj.interview_insights = data.get('interview_insights')
        intel_obj.employee_sentiment = data.get('employee_sentiment')
        intel_obj.pros_cons = data.get('pros_cons')
        intel_obj.tech_stack = data.get('tech_stack')
        intel_obj.ai_summary = data.get('ai_summary')
        intel_obj.key_insights = data.get('key_insights')
        intel_obj.recommendations = data.get('recommendations')


# Singleton instance
_company_intel_instance = None

def get_company_intel_service() -> CompanyIntelService:
    """Get singleton instance of CompanyIntelService"""
    global _company_intel_instance
    if _company_intel_instance is None:
        _company_intel_instance = CompanyIntelService()
    return _company_intel_instance
