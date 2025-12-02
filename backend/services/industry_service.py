"""
Industry Service - Helper functions for industry-based personalization and data filtering
"""

from typing import Optional, List, Dict, Any
from models import User

# Standard industry categories
INDUSTRIES = [
    'Technology',
    'Healthcare',
    'Finance',
    'Marketing',
    'Sales',
    'Education',
    'Engineering',
    'Design',
    'Product Management',
    'Data Science',
    'Cybersecurity',
    'Cloud & DevOps',
    'Retail',
    'Manufacturing',
    'Legal',
    'Consulting',
    'General'
]

# Industry-specific skills mapping
INDUSTRY_SKILLS = {
    'Technology': {
        'high_demand': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes', 'TypeScript', 'SQL', 'Git'],
        'emerging': ['Rust', 'Go', 'WebAssembly', 'GraphQL', 'Terraform', 'Next.js', 'Svelte', 'Edge Computing'],
        'categories': ['Programming', 'Cloud', 'DevOps', 'Frontend', 'Backend', 'Database', 'Mobile']
    },
    'Data Science': {
        'high_demand': ['Python', 'R', 'SQL', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'Statistics'],
        'emerging': ['MLOps', 'LLMs', 'Deep Learning', 'Computer Vision', 'NLP', 'AutoML', 'Feature Engineering'],
        'categories': ['ML/AI', 'Statistics', 'Data Engineering', 'Visualization', 'Big Data']
    },
    'Cybersecurity': {
        'high_demand': ['Security Analysis', 'Penetration Testing', 'SIEM', 'Firewall', 'IDS/IPS', 'Network Security', 'Threat Intelligence', 'IAM'],
        'emerging': ['Cloud Security', 'Zero Trust', 'DevSecOps', 'Container Security', 'AI Security', 'Blockchain Security'],
        'categories': ['Network Security', 'Application Security', 'Cloud Security', 'Compliance', 'Incident Response']
    },
    'Healthcare': {
        'high_demand': ['HIPAA Compliance', 'EMR/EHR Systems', 'Patient Care', 'Medical Terminology', 'Clinical Research', 'Healthcare IT'],
        'emerging': ['Telemedicine', 'Health Analytics', 'Medical AI', 'Digital Health', 'Genomics'],
        'categories': ['Clinical', 'Healthcare IT', 'Research', 'Compliance', 'Administration']
    },
    'Finance': {
        'high_demand': ['Financial Analysis', 'Risk Management', 'Bloomberg Terminal', 'Excel', 'SQL', 'Python', 'Accounting', 'GAAP'],
        'emerging': ['FinTech', 'Blockchain', 'Algorithmic Trading', 'RegTech', 'Cryptocurrency', 'Robo-Advisory'],
        'categories': ['Analysis', 'Trading', 'Risk', 'Compliance', 'Technology']
    },
    'Cloud & DevOps': {
        'high_demand': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'Jenkins', 'Git', 'Linux'],
        'emerging': ['GitOps', 'Service Mesh', 'Serverless', 'Infrastructure as Code', 'Platform Engineering', 'SRE'],
        'categories': ['Cloud Platforms', 'Containers', 'CI/CD', 'Monitoring', 'Automation']
    },
    'Marketing': {
        'high_demand': ['Digital Marketing', 'SEO', 'SEM', 'Google Analytics', 'Social Media', 'Content Marketing', 'Email Marketing'],
        'emerging': ['Marketing Automation', 'AI Marketing', 'Influencer Marketing', 'Growth Hacking', 'Marketing Analytics'],
        'categories': ['Digital', 'Content', 'Analytics', 'Social Media', 'Strategy']
    },
    'Design': {
        'high_demand': ['Figma', 'Adobe XD', 'Sketch', 'UI/UX Design', 'Wireframing', 'Prototyping', 'User Research', 'Design Systems'],
        'emerging': ['Design Tokens', 'AI-Assisted Design', 'Motion Design', '3D Design', 'AR/VR Design', 'Inclusive Design'],
        'categories': ['UI Design', 'UX Research', 'Product Design', 'Visual Design', 'Interaction Design']
    },
    'Product Management': {
        'high_demand': ['Product Strategy', 'Roadmapping', 'User Stories', 'Agile', 'Scrum', 'Stakeholder Management', 'Analytics', 'A/B Testing'],
        'emerging': ['AI Product Management', 'Data-Driven PM', 'Growth PM', 'Platform PM', 'API Product Management'],
        'categories': ['Strategy', 'Analytics', 'User Research', 'Agile', 'Technical PM']
    },
    'Engineering': {
        'high_demand': ['CAD', 'AutoCAD', 'SolidWorks', 'MATLAB', 'Project Management', 'Technical Documentation', 'Quality Control'],
        'emerging': ['Digital Twin', 'Additive Manufacturing', 'IoT Engineering', 'Sustainable Engineering', 'Smart Manufacturing'],
        'categories': ['Mechanical', 'Electrical', 'Civil', 'Software', 'Systems']
    },
    'General': {
        'high_demand': ['Communication', 'Leadership', 'Project Management', 'Problem Solving', 'Teamwork', 'Time Management'],
        'emerging': ['Remote Collaboration', 'Change Management', 'Emotional Intelligence', 'Digital Literacy'],
        'categories': ['Soft Skills', 'Management', 'Communication', 'Technical']
    }
}

def get_user_industry(user: User) -> str:
    """
    Get user's primary industry from their profile or detected industries

    Priority order:
    1. preferred_industry (explicitly set by user)
    2. detected_industries[0] (from latest resume analysis)
    3. "General" (fallback)

    Args:
        user: User object

    Returns:
        str: Industry name (e.g., "Technology", "Healthcare")
    """
    # First check if user has explicitly set their preferred industry
    if user.preferred_industry:
        return user.preferred_industry

    # Next check if we've detected industries from their resumes
    if user.detected_industries and len(user.detected_industries) > 0:
        return user.detected_industries[0]

    # Default to General if no industry information available
    return "General"


def get_all_industries() -> List[str]:
    """
    Get list of all available industries

    Returns:
        List[str]: List of industry names
    """
    return INDUSTRIES


def get_industry_skills(industry: str, category: str = 'high_demand') -> List[str]:
    """
    Get relevant skills for a specific industry

    Args:
        industry: Industry name (e.g., "Technology")
        category: 'high_demand', 'emerging', or 'all'

    Returns:
        List[str]: List of relevant skills
    """
    if industry not in INDUSTRY_SKILLS:
        industry = 'General'

    skills_data = INDUSTRY_SKILLS[industry]

    if category == 'all':
        return skills_data.get('high_demand', []) + skills_data.get('emerging', [])
    else:
        return skills_data.get(category, [])


def get_industry_categories(industry: str) -> List[str]:
    """
    Get skill categories for a specific industry

    Args:
        industry: Industry name

    Returns:
        List[str]: List of skill categories
    """
    if industry not in INDUSTRY_SKILLS:
        industry = 'General'

    return INDUSTRY_SKILLS[industry].get('categories', [])


def filter_market_data_by_industry(data: List[Dict], industry: str, industry_field: str = 'industry') -> List[Dict]:
    """
    Filter market data (jobs, skills, companies) by industry

    Args:
        data: List of data items (dicts)
        industry: Industry to filter by
        industry_field: Field name containing industry in data items

    Returns:
        List[Dict]: Filtered data matching the industry
    """
    if industry == 'General' or not industry:
        return data

    return [item for item in data if item.get(industry_field) == industry]


def detect_industry_from_text(text: str, use_ai: bool = False) -> str:
    """
    Detect industry from resume text or job description

    Uses keyword matching for now. Can be enhanced with AI later.

    Args:
        text: Resume or job description text
        use_ai: Whether to use AI for detection (future enhancement)

    Returns:
        str: Detected industry name
    """
    text_lower = text.lower()

    # Industry keywords for detection
    industry_keywords = {
        'Technology': ['software', 'developer', 'programming', 'javascript', 'python', 'react', 'node.js', 'api', 'database', 'cloud', 'aws', 'docker'],
        'Data Science': ['data scientist', 'machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'data analysis', 'statistics', 'pandas', 'numpy'],
        'Cybersecurity': ['security', 'cybersecurity', 'penetration testing', 'siem', 'firewall', 'threat', 'vulnerability', 'security analyst'],
        'Cloud & DevOps': ['devops', 'kubernetes', 'docker', 'ci/cd', 'terraform', 'jenkins', 'infrastructure', 'sre', 'cloud engineer'],
        'Healthcare': ['healthcare', 'medical', 'clinical', 'patient', 'hipaa', 'emr', 'ehr', 'hospital', 'nursing', 'physician'],
        'Finance': ['finance', 'financial', 'accounting', 'banking', 'investment', 'trading', 'risk management', 'portfolio'],
        'Marketing': ['marketing', 'seo', 'sem', 'social media', 'content marketing', 'digital marketing', 'brand', 'campaign'],
        'Design': ['designer', 'ui/ux', 'figma', 'adobe', 'sketch', 'wireframe', 'prototype', 'visual design', 'user experience'],
        'Product Management': ['product manager', 'product owner', 'roadmap', 'agile', 'scrum', 'user stories', 'backlog'],
        'Engineering': ['engineer', 'mechanical', 'electrical', 'civil', 'cad', 'autocad', 'solidworks', 'manufacturing'],
    }

    # Count keyword matches for each industry
    industry_scores = {}
    for industry, keywords in industry_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            industry_scores[industry] = score

    # Return industry with highest score
    if industry_scores:
        return max(industry_scores, key=industry_scores.get)

    return 'General'


def get_industry_job_titles(industry: str) -> List[str]:
    """
    Get common job titles for an industry

    Args:
        industry: Industry name

    Returns:
        List[str]: Common job titles in that industry
    """
    job_titles = {
        'Technology': ['Software Engineer', 'Full Stack Developer', 'Frontend Developer', 'Backend Developer', 'DevOps Engineer', 'Technical Lead', 'Software Architect'],
        'Data Science': ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst', 'AI Research Scientist', 'Data Engineer', 'ML Ops Engineer'],
        'Cybersecurity': ['Security Analyst', 'Penetration Tester', 'Security Engineer', 'CISO', 'SOC Analyst', 'Security Architect'],
        'Cloud & DevOps': ['DevOps Engineer', 'Cloud Engineer', 'SRE', 'Platform Engineer', 'Cloud Architect', 'Infrastructure Engineer'],
        'Healthcare': ['Healthcare IT Specialist', 'Clinical Informatics Specialist', 'Medical Data Analyst', 'Healthcare Software Engineer'],
        'Finance': ['Financial Analyst', 'Investment Analyst', 'Risk Analyst', 'Quantitative Analyst', 'FinTech Developer'],
        'Marketing': ['Digital Marketing Manager', 'SEO Specialist', 'Content Marketing Manager', 'Growth Marketing Manager', 'Marketing Analyst'],
        'Design': ['UI/UX Designer', 'Product Designer', 'Visual Designer', 'Interaction Designer', 'Design System Lead'],
        'Product Management': ['Product Manager', 'Senior Product Manager', 'Technical Product Manager', 'Product Owner', 'Group Product Manager'],
        'Engineering': ['Mechanical Engineer', 'Electrical Engineer', 'Civil Engineer', 'Systems Engineer', 'Manufacturing Engineer'],
        'General': ['Project Manager', 'Business Analyst', 'Operations Manager', 'Consultant', 'Team Lead']
    }

    return job_titles.get(industry, job_titles['General'])


def get_industry_salary_range(industry: str, experience_level: str = 'Mid') -> Dict[str, int]:
    """
    Get typical salary ranges for an industry and experience level

    Args:
        industry: Industry name
        experience_level: 'Entry', 'Mid', 'Senior', 'Lead', 'Executive'

    Returns:
        Dict with 'min' and 'max' salary in USD
    """
    # Simplified salary ranges (can be enhanced with real market data later)
    base_ranges = {
        'Technology': {'Entry': (70000, 100000), 'Mid': (100000, 150000), 'Senior': (150000, 220000), 'Lead': (180000, 280000), 'Executive': (250000, 400000)},
        'Data Science': {'Entry': (80000, 110000), 'Mid': (110000, 160000), 'Senior': (160000, 230000), 'Lead': (200000, 300000), 'Executive': (270000, 450000)},
        'Cybersecurity': {'Entry': (75000, 105000), 'Mid': (105000, 155000), 'Senior': (155000, 225000), 'Lead': (190000, 290000), 'Executive': (260000, 420000)},
        'Cloud & DevOps': {'Entry': (75000, 105000), 'Mid': (105000, 155000), 'Senior': (155000, 225000), 'Lead': (190000, 290000), 'Executive': (260000, 420000)},
        'Healthcare': {'Entry': (55000, 80000), 'Mid': (80000, 120000), 'Senior': (120000, 180000), 'Lead': (150000, 230000), 'Executive': (200000, 350000)},
        'Finance': {'Entry': (65000, 95000), 'Mid': (95000, 140000), 'Senior': (140000, 210000), 'Lead': (180000, 280000), 'Executive': (250000, 450000)},
        'Marketing': {'Entry': (50000, 75000), 'Mid': (75000, 110000), 'Senior': (110000, 160000), 'Lead': (140000, 210000), 'Executive': (180000, 300000)},
        'Design': {'Entry': (55000, 80000), 'Mid': (80000, 120000), 'Senior': (120000, 175000), 'Lead': (150000, 220000), 'Executive': (180000, 300000)},
        'Product Management': {'Entry': (75000, 110000), 'Mid': (110000, 160000), 'Senior': (160000, 230000), 'Lead': (200000, 300000), 'Executive': (250000, 450000)},
        'Engineering': {'Entry': (60000, 85000), 'Mid': (85000, 125000), 'Senior': (125000, 180000), 'Lead': (150000, 230000), 'Executive': (200000, 350000)},
        'General': {'Entry': (45000, 65000), 'Mid': (65000, 95000), 'Senior': (95000, 140000), 'Lead': (120000, 180000), 'Executive': (150000, 250000)}
    }

    ranges = base_ranges.get(industry, base_ranges['General'])
    salary_tuple = ranges.get(experience_level, ranges['Mid'])

    return {
        'min': salary_tuple[0],
        'max': salary_tuple[1],
        'currency': 'USD'
    }


def is_valid_industry(industry: str) -> bool:
    """
    Check if an industry name is valid

    Args:
        industry: Industry name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return industry in INDUSTRIES


def get_industry_description(industry: str) -> str:
    """
    Get a description of an industry

    Args:
        industry: Industry name

    Returns:
        str: Industry description
    """
    descriptions = {
        'Technology': 'Software development, web development, mobile apps, and technology solutions',
        'Data Science': 'Machine learning, data analysis, AI, and statistical modeling',
        'Cybersecurity': 'Information security, network security, and threat protection',
        'Cloud & DevOps': 'Cloud infrastructure, containerization, CI/CD, and site reliability',
        'Healthcare': 'Medical technology, patient care systems, and healthcare IT',
        'Finance': 'Financial services, banking, investment, and fintech',
        'Marketing': 'Digital marketing, brand management, and customer acquisition',
        'Design': 'UI/UX design, product design, and visual communication',
        'Product Management': 'Product strategy, roadmapping, and product development',
        'Engineering': 'Mechanical, electrical, civil, and systems engineering',
        'General': 'Cross-industry roles and general professional skills'
    }

    return descriptions.get(industry, 'Professional industry')
