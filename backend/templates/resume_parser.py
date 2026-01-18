"""
Resume Parser - Uses Gemini AI to parse optimized resume text into structured JSON.
"""

import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse plain text resume into structured format for template rendering."""

    def __init__(self, gemini_service=None):
        """
        Initialize parser with optional Gemini service.
        If not provided, will import on first use.
        """
        self._gemini_service = gemini_service

    @property
    def gemini_service(self):
        """Lazy load Gemini service to avoid circular imports."""
        if self._gemini_service is None:
            from gemini_service import gemini_service
            self._gemini_service = gemini_service
        return self._gemini_service

    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text into structured JSON format.

        Args:
            resume_text: Plain text resume content (typically from optimized_resume)

        Returns:
            Structured dictionary with contact, summary, experience, education, skills
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is required for parsing")

        logger.info("Parsing resume text into structured format...")

        prompt = self._build_parsing_prompt(resume_text)

        try:
            response = self.gemini_service._call_gemini_with_retry(
                prompt,
                "resume_parsing_for_template"
            )

            structured_data = self._parse_json_response(response)
            validated_data = self._validate_and_normalize(structured_data)

            logger.info("Resume parsing completed successfully")
            return validated_data

        except Exception as e:
            logger.warning(f"AI parsing failed: {e}. Falling back to regex parsing.")
            return self._fallback_parse(resume_text)

    def _build_parsing_prompt(self, resume_text: str) -> str:
        """Build the prompt for Gemini to parse the resume."""
        return f"""Parse this resume into a structured JSON format. Extract all information accurately.

RESUME TEXT:
{resume_text[:8000]}

Return a JSON object with EXACTLY this structure (no additional text, just JSON):
{{
    "contact": {{
        "name": "Full Name (required)",
        "email": "email@example.com (if found)",
        "phone": "phone number (if found)",
        "linkedin": "LinkedIn URL or username (if found)",
        "location": "City, State/Country (if found)",
        "website": "personal website (if found)"
    }},
    "summary": "Professional summary or objective (1-3 sentences, if found)",
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, State (if found)",
            "start_date": "Start date (format: YYYY-MM or Month YYYY)",
            "end_date": "End date or 'Present'",
            "achievements": [
                "Bullet point achievement 1",
                "Bullet point achievement 2"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name (e.g., Bachelor of Science)",
            "field": "Field of Study (e.g., Computer Science)",
            "institution": "University/School Name",
            "graduation_date": "Graduation year or date",
            "gpa": "GPA if mentioned (optional)",
            "honors": "Honors, awards, or distinctions (optional)"
        }}
    ],
    "skills": {{
        "technical": ["List of technical skills, tools, technologies"],
        "soft": ["List of soft skills if mentioned"],
        "languages": ["Programming or spoken languages if mentioned"],
        "certifications": ["Certifications if mentioned separately from skills"]
    }},
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "Date obtained",
            "expiry": "Expiry date if applicable"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["Technologies used"],
            "url": "Project URL if mentioned"
        }}
    ],
    "awards": [
        {{
            "name": "Award Name",
            "issuer": "Issuing Organization",
            "date": "Date received"
        }}
    ],
    "publications": [
        {{
            "title": "Publication Title",
            "venue": "Journal/Conference",
            "date": "Publication date"
        }}
    ]
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown code blocks, no explanations
- If a section is not found in the resume, use empty array [] or null
- For contact.name, extract the person's full name (usually at the top of the resume)
- For experience, list jobs in reverse chronological order (most recent first)
- For achievements, include quantifiable results where available
- Preserve the original wording where possible"""

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response, handling common formatting issues."""
        if not response:
            raise ValueError("Empty response from AI")

        # Clean up the response
        cleaned = response.strip()

        # Remove markdown code blocks if present
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        # Try to find JSON object in the response
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            cleaned = json_match.group(0)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response was: {cleaned[:500]}...")
            raise ValueError(f"Invalid JSON response: {e}")

    def _validate_and_normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the parsed data structure."""
        # Ensure all required keys exist with defaults
        normalized = {
            "contact": {
                "name": "",
                "email": "",
                "phone": "",
                "linkedin": "",
                "location": "",
                "website": ""
            },
            "summary": "",
            "experience": [],
            "education": [],
            "skills": {
                "technical": [],
                "soft": [],
                "languages": [],
                "certifications": []
            },
            "certifications": [],
            "projects": [],
            "awards": [],
            "publications": []
        }

        # Merge parsed data
        if "contact" in data and isinstance(data["contact"], dict):
            for key in normalized["contact"]:
                if key in data["contact"] and data["contact"][key]:
                    normalized["contact"][key] = str(data["contact"][key]).strip()

        if "summary" in data and data["summary"]:
            normalized["summary"] = str(data["summary"]).strip()

        if "experience" in data and isinstance(data["experience"], list):
            normalized["experience"] = self._normalize_experience(data["experience"])

        if "education" in data and isinstance(data["education"], list):
            normalized["education"] = self._normalize_education(data["education"])

        if "skills" in data and isinstance(data["skills"], dict):
            for key in normalized["skills"]:
                if key in data["skills"] and isinstance(data["skills"][key], list):
                    normalized["skills"][key] = [
                        str(s).strip() for s in data["skills"][key] if s
                    ]

        for section in ["certifications", "projects", "awards", "publications"]:
            if section in data and isinstance(data[section], list):
                normalized[section] = data[section]

        return normalized

    def _normalize_experience(self, experience: list) -> list:
        """Normalize experience entries."""
        normalized = []
        for exp in experience:
            if not isinstance(exp, dict):
                continue

            entry = {
                "title": str(exp.get("title", "")).strip(),
                "company": str(exp.get("company", "")).strip(),
                "location": str(exp.get("location", "")).strip(),
                "start_date": str(exp.get("start_date", "")).strip(),
                "end_date": str(exp.get("end_date", "")).strip(),
                "achievements": []
            }

            # Handle achievements
            achievements = exp.get("achievements", [])
            if isinstance(achievements, list):
                entry["achievements"] = [
                    str(a).strip() for a in achievements if a
                ]
            elif isinstance(achievements, str):
                entry["achievements"] = [achievements.strip()]

            # Only add if we have at least title and company
            if entry["title"] or entry["company"]:
                normalized.append(entry)

        return normalized

    def _normalize_education(self, education: list) -> list:
        """Normalize education entries."""
        normalized = []
        for edu in education:
            if not isinstance(edu, dict):
                continue

            entry = {
                "degree": str(edu.get("degree", "")).strip(),
                "field": str(edu.get("field", "")).strip(),
                "institution": str(edu.get("institution", "")).strip(),
                "graduation_date": str(edu.get("graduation_date", "")).strip(),
                "gpa": str(edu.get("gpa", "")).strip() if edu.get("gpa") else "",
                "honors": str(edu.get("honors", "")).strip() if edu.get("honors") else ""
            }

            # Only add if we have at least institution
            if entry["institution"] or entry["degree"]:
                normalized.append(entry)

        return normalized

    def _fallback_parse(self, resume_text: str) -> Dict[str, Any]:
        """
        Fallback parsing using regex patterns when AI parsing fails.
        This provides a basic structure that the user can edit.
        """
        logger.info("Using fallback regex parsing")

        lines = resume_text.strip().split('\n')

        result = {
            "contact": {
                "name": self._extract_name(lines),
                "email": self._extract_email(resume_text),
                "phone": self._extract_phone(resume_text),
                "linkedin": self._extract_linkedin(resume_text),
                "location": "",
                "website": ""
            },
            "summary": "",
            "experience": [],
            "education": [],
            "skills": {
                "technical": self._extract_skills(resume_text),
                "soft": [],
                "languages": [],
                "certifications": []
            },
            "certifications": [],
            "projects": [],
            "awards": [],
            "publications": []
        }

        return result

    def _extract_name(self, lines: list) -> str:
        """Extract name from first non-empty line."""
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not '@' in line and not line.startswith('http'):
                # Check if it looks like a name (2-4 words, mostly letters)
                words = line.split()
                if 1 <= len(words) <= 5 and all(
                    re.match(r'^[A-Za-z\-\'\.]+$', w) for w in words
                ):
                    return line
        return ""

    def _extract_email(self, text: str) -> str:
        """Extract email address."""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number."""
        patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+?[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL."""
        match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        return match.group(0) if match else ""

    def _extract_skills(self, text: str) -> list:
        """Extract technical skills using common patterns."""
        # Look for Skills section
        skills_section = re.search(
            r'(?:Technical\s+)?Skills[:\s]*(.*?)(?=\n\n|\nExperience|\nEducation|\nWork|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if skills_section:
            skills_text = skills_section.group(1)
            # Split by common delimiters
            skills = re.split(r'[,;•|\n]', skills_text)
            return [s.strip() for s in skills if s.strip() and len(s.strip()) < 50]

        return []


# Singleton instance
resume_parser = ResumeParser()
