"""
Template configuration for resume and cover letter templates.
"""

RESUME_TEMPLATES = {
    "modern": {
        "id": "modern",
        "name": "Modern Professional",
        "description": "Clean, contemporary design with blue accent colors and clear section headers",
        "ats_score": 95,
        "features": ["Centered header", "Color accents", "Clean typography", "ATS-friendly"],
        "recommended_for": ["Tech", "Creative", "Marketing", "Startups"],
        "file": "resume_modern.html"
    },
    "classic": {
        "id": "classic",
        "name": "Classic Traditional",
        "description": "Traditional single-column format with maximum ATS compatibility",
        "ats_score": 100,
        "features": ["Single column", "Traditional layout", "Maximum ATS compatibility", "Conservative"],
        "recommended_for": ["Finance", "Legal", "Government", "Healthcare", "Academia"],
        "file": "resume_classic.html"
    }
}

COVER_LETTER_TEMPLATES = {
    "professional": {
        "id": "professional",
        "name": "Professional Standard",
        "description": "Clean, professional format suitable for any industry",
        "features": ["Business letter format", "Clean margins", "Professional typography"],
        "recommended_for": ["All industries"],
        "file": "cover_letter_professional.html"
    },
    "simple": {
        "id": "simple",
        "name": "Simple Clean",
        "description": "Minimalist design focusing purely on content",
        "features": ["Minimal styling", "Maximum readability", "Clean layout"],
        "recommended_for": ["Tech", "Startups", "Modern companies"],
        "file": "cover_letter_simple.html"
    }
}

def get_template_list(template_type="resume"):
    """Get list of templates for API response"""
    templates = RESUME_TEMPLATES if template_type == "resume" else COVER_LETTER_TEMPLATES
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "ats_score": t.get("ats_score"),
            "features": t["features"],
            "recommended_for": t["recommended_for"]
        }
        for t in templates.values()
    ]
