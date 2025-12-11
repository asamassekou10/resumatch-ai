"""
Sample job postings data for market intelligence testing and demo
"""

def load_sample_postings():
    """
    Load sample job postings with extracted skills for market intelligence

    Returns:
        list: List of job posting dictionaries with skills
    """
    return [
        # Technology Jobs
        {
            'job_title': 'Senior Software Engineer',
            'company_name': 'TechCorp Inc',
            'job_posting_url': 'https://example.com/job/1',
            'industry': 'Technology',
            'location': 'San Francisco, CA',
            'salary_min': 120000,
            'salary_max': 180000,
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS', 'Docker', 'Kubernetes']
        },
        {
            'job_title': 'Full Stack Developer',
            'company_name': 'StartupXYZ',
            'job_posting_url': 'https://example.com/job/2',
            'industry': 'Technology',
            'location': 'Austin, TX',
            'salary_min': 100000,
            'salary_max': 150000,
            'skills': ['JavaScript', 'TypeScript', 'React', 'Node.js', 'MongoDB', 'REST API', 'Git']
        },
        {
            'job_title': 'DevOps Engineer',
            'company_name': 'CloudSystems',
            'job_posting_url': 'https://example.com/job/3',
            'industry': 'Technology',
            'location': 'Seattle, WA',
            'salary_min': 110000,
            'salary_max': 160000,
            'skills': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Python', 'Jenkins', 'CI/CD']
        },
        {
            'job_title': 'Data Engineer',
            'company_name': 'DataCo',
            'job_posting_url': 'https://example.com/job/4',
            'industry': 'Technology',
            'location': 'New York, NY',
            'salary_min': 115000,
            'salary_max': 170000,
            'skills': ['Python', 'SQL', 'Spark', 'Airflow', 'AWS', 'ETL', 'Data Warehousing']
        },
        {
            'job_title': 'Machine Learning Engineer',
            'company_name': 'AI Innovations',
            'job_posting_url': 'https://example.com/job/5',
            'industry': 'Technology',
            'location': 'Boston, MA',
            'salary_min': 130000,
            'salary_max': 190000,
            'skills': ['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'SQL', 'AWS']
        },
        {
            'job_title': 'Frontend Developer',
            'company_name': 'WebDesign Pro',
            'job_posting_url': 'https://example.com/job/6',
            'industry': 'Technology',
            'location': 'Los Angeles, CA',
            'salary_min': 95000,
            'salary_max': 140000,
            'skills': ['JavaScript', 'React', 'Vue.js', 'CSS', 'HTML', 'TypeScript', 'Webpack']
        },
        {
            'job_title': 'Backend Developer',
            'company_name': 'API Solutions',
            'job_posting_url': 'https://example.com/job/7',
            'industry': 'Technology',
            'location': 'Denver, CO',
            'salary_min': 105000,
            'salary_max': 155000,
            'skills': ['Python', 'Django', 'PostgreSQL', 'REST API', 'Redis', 'Docker', 'API Design']
        },
        {
            'job_title': 'Cloud Architect',
            'company_name': 'Enterprise Solutions',
            'job_posting_url': 'https://example.com/job/8',
            'industry': 'Technology',
            'location': 'Chicago, IL',
            'salary_min': 140000,
            'salary_max': 200000,
            'skills': ['AWS', 'Azure', 'Cloud Architecture', 'Kubernetes', 'Terraform', 'Security', 'Microservices']
        },
        {
            'job_title': 'Mobile App Developer',
            'company_name': 'MobileTech',
            'job_posting_url': 'https://example.com/job/9',
            'industry': 'Technology',
            'location': 'San Diego, CA',
            'salary_min': 105000,
            'salary_max': 145000,
            'skills': ['React Native', 'JavaScript', 'iOS', 'Android', 'Mobile Development', 'API Integration']
        },
        {
            'job_title': 'Security Engineer',
            'company_name': 'SecureNet',
            'job_posting_url': 'https://example.com/job/10',
            'industry': 'Technology',
            'location': 'Washington, DC',
            'salary_min': 125000,
            'salary_max': 175000,
            'skills': ['Security', 'Penetration Testing', 'Python', 'Networking', 'Encryption', 'SIEM']
        },

        # Finance Jobs
        {
            'job_title': 'Financial Analyst',
            'company_name': 'Global Finance Corp',
            'job_posting_url': 'https://example.com/job/11',
            'industry': 'Finance',
            'location': 'New York, NY',
            'salary_min': 80000,
            'salary_max': 120000,
            'skills': ['Excel', 'Financial Modeling', 'SQL', 'Python', 'Data Analysis', 'Bloomberg Terminal']
        },
        {
            'job_title': 'Data Analyst',
            'company_name': 'Investment Bank',
            'job_posting_url': 'https://example.com/job/12',
            'industry': 'Finance',
            'location': 'New York, NY',
            'salary_min': 85000,
            'salary_max': 125000,
            'skills': ['SQL', 'Python', 'Tableau', 'Data Visualization', 'Excel', 'Financial Analysis']
        },
        {
            'job_title': 'Quantitative Analyst',
            'company_name': 'Hedge Fund LLC',
            'job_posting_url': 'https://example.com/job/13',
            'industry': 'Finance',
            'location': 'Chicago, IL',
            'salary_min': 120000,
            'salary_max': 180000,
            'skills': ['Python', 'R', 'Statistics', 'Machine Learning', 'Financial Modeling', 'SQL']
        },
        {
            'job_title': 'Risk Analyst',
            'company_name': 'Banking Solutions',
            'job_posting_url': 'https://example.com/job/14',
            'industry': 'Finance',
            'location': 'Boston, MA',
            'salary_min': 90000,
            'salary_max': 130000,
            'skills': ['Risk Management', 'Excel', 'SQL', 'Financial Analysis', 'Regulation', 'Reporting']
        },
        {
            'job_title': 'Portfolio Manager',
            'company_name': 'Asset Management Co',
            'job_posting_url': 'https://example.com/job/15',
            'industry': 'Finance',
            'location': 'San Francisco, CA',
            'salary_min': 110000,
            'salary_max': 160000,
            'skills': ['Portfolio Management', 'Financial Analysis', 'Excel', 'Bloomberg Terminal', 'Investment Strategy']
        },

        # Healthcare Jobs
        {
            'job_title': 'Healthcare Data Analyst',
            'company_name': 'MedTech Solutions',
            'job_posting_url': 'https://example.com/job/16',
            'industry': 'Healthcare',
            'location': 'Philadelphia, PA',
            'salary_min': 75000,
            'salary_max': 110000,
            'skills': ['SQL', 'Python', 'Healthcare Analytics', 'Data Analysis', 'Excel', 'HIPAA']
        },
        {
            'job_title': 'Clinical Research Coordinator',
            'company_name': 'Pharma Research Inc',
            'job_posting_url': 'https://example.com/job/17',
            'industry': 'Healthcare',
            'location': 'Baltimore, MD',
            'salary_min': 65000,
            'salary_max': 95000,
            'skills': ['Clinical Research', 'GCP', 'Data Collection', 'Regulatory Compliance', 'Medical Terminology']
        },
        {
            'job_title': 'Health Informatics Specialist',
            'company_name': 'Hospital Network',
            'job_posting_url': 'https://example.com/job/18',
            'industry': 'Healthcare',
            'location': 'Houston, TX',
            'salary_min': 80000,
            'salary_max': 115000,
            'skills': ['Health Informatics', 'SQL', 'EHR Systems', 'Data Analysis', 'HIPAA', 'HL7']
        },
        {
            'job_title': 'Medical Software Developer',
            'company_name': 'HealthTech Inc',
            'job_posting_url': 'https://example.com/job/19',
            'industry': 'Healthcare',
            'location': 'Seattle, WA',
            'salary_min': 100000,
            'salary_max': 145000,
            'skills': ['Python', 'JavaScript', 'SQL', 'Healthcare IT', 'HIPAA', 'API Development']
        },
        {
            'job_title': 'Biostatistician',
            'company_name': 'Clinical Trials Co',
            'job_posting_url': 'https://example.com/job/20',
            'industry': 'Healthcare',
            'location': 'San Diego, CA',
            'salary_min': 90000,
            'salary_max': 135000,
            'skills': ['Statistics', 'R', 'SAS', 'Clinical Trials', 'Data Analysis', 'Biostatistics']
        },

        # Marketing Jobs
        {
            'job_title': 'Digital Marketing Manager',
            'company_name': 'Ad Agency Pro',
            'job_posting_url': 'https://example.com/job/21',
            'industry': 'Marketing',
            'location': 'New York, NY',
            'salary_min': 85000,
            'salary_max': 125000,
            'skills': ['Digital Marketing', 'SEO', 'Google Analytics', 'Social Media', 'Content Marketing', 'PPC']
        },
        {
            'job_title': 'Marketing Data Analyst',
            'company_name': 'MarketInsights',
            'job_posting_url': 'https://example.com/job/22',
            'industry': 'Marketing',
            'location': 'Austin, TX',
            'salary_min': 70000,
            'salary_max': 105000,
            'skills': ['SQL', 'Python', 'Google Analytics', 'Data Visualization', 'A/B Testing', 'Excel']
        },
        {
            'job_title': 'Content Marketing Manager',
            'company_name': 'Content Creators LLC',
            'job_posting_url': 'https://example.com/job/23',
            'industry': 'Marketing',
            'location': 'Los Angeles, CA',
            'salary_min': 75000,
            'salary_max': 110000,
            'skills': ['Content Marketing', 'SEO', 'Copywriting', 'Social Media', 'Content Strategy', 'Analytics']
        },
        {
            'job_title': 'Social Media Manager',
            'company_name': 'Brand Agency',
            'job_posting_url': 'https://example.com/job/24',
            'industry': 'Marketing',
            'location': 'Miami, FL',
            'salary_min': 65000,
            'salary_max': 95000,
            'skills': ['Social Media', 'Content Creation', 'Community Management', 'Analytics', 'Copywriting']
        },
        {
            'job_title': 'Marketing Automation Specialist',
            'company_name': 'AutoMarketing Co',
            'job_posting_url': 'https://example.com/job/25',
            'industry': 'Marketing',
            'location': 'San Francisco, CA',
            'salary_min': 80000,
            'salary_max': 120000,
            'skills': ['Marketing Automation', 'Salesforce', 'HubSpot', 'Email Marketing', 'SQL', 'Analytics']
        },
    ]
