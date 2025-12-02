"""
Seed script for job postings - Creates sample job listings across all industries
"""

from datetime import datetime, timedelta
import random
from models import JobPosting, db
from app import app

# Sample job postings data across all industries
SAMPLE_JOBS = [
    # Technology
    {
        'title': 'Senior Full Stack Engineer',
        'company': 'TechCorp Inc',
        'location': 'San Francisco, CA',
        'remote_type': 'hybrid',
        'industry': 'Technology',
        'description': 'Join our team building next-generation cloud applications. Work with modern tech stack including React, Node.js, and AWS.',
        'requirements': ['JavaScript', 'React', 'Node.js', 'AWS', 'Docker', '5+ years experience'],
        'responsibilities': ['Build scalable APIs', 'Lead technical initiatives', 'Mentor junior engineers'],
        'salary_min': 140000,
        'salary_max': 190000,
        'employment_type': 'full-time',
        'experience_level': 'Senior',
        'external_url': 'https://example.com/jobs/1'
    },
    {
        'title': 'Frontend Developer',
        'company': 'StartupXYZ',
        'location': 'Austin, TX',
        'remote_type': 'remote',
        'industry': 'Technology',
        'description': 'Build beautiful user interfaces with React and TypeScript. Join a fast-growing startup.',
        'requirements': ['React', 'TypeScript', 'CSS', 'HTML', '3+ years experience'],
        'responsibilities': ['Build responsive UIs', 'Collaborate with designers', 'Write clean code'],
        'salary_min': 100000,
        'salary_max': 140000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/2'
    },
    # Data Science
    {
        'title': 'Data Scientist - Machine Learning',
        'company': 'DataFlow Analytics',
        'location': 'New York, NY',
        'remote_type': 'hybrid',
        'industry': 'Data Science',
        'description': 'Build ML models to solve complex business problems. Work with large-scale datasets and modern ML frameworks.',
        'requirements': ['Python', 'TensorFlow', 'PyTorch', 'SQL', 'Statistics', 'ML algorithms'],
        'responsibilities': ['Develop ML models', 'Analyze data patterns', 'Deploy models to production'],
        'salary_min': 130000,
        'salary_max': 180000,
        'employment_type': 'full-time',
        'experience_level': 'Senior',
        'external_url': 'https://example.com/jobs/3'
    },
    {
        'title': 'Junior Data Analyst',
        'company': 'Growth Metrics Co',
        'location': 'Remote',
        'remote_type': 'remote',
        'industry': 'Data Science',
        'description': 'Analyze business metrics and create insightful dashboards. Great opportunity to learn from senior data scientists.',
        'requirements': ['Python', 'SQL', 'Excel', 'Data visualization', 'Statistics basics'],
        'responsibilities': ['Create dashboards', 'Analyze trends', 'Generate reports'],
        'salary_min': 75000,
        'salary_max': 95000,
        'employment_type': 'full-time',
        'experience_level': 'Entry',
        'external_url': 'https://example.com/jobs/4'
    },
    # Cybersecurity
    {
        'title': 'Security Engineer',
        'company': 'SecureNet Systems',
        'location': 'Washington, DC',
        'remote_type': 'onsite',
        'industry': 'Cybersecurity',
        'description': 'Protect enterprise systems from security threats. Implement security best practices and monitor for vulnerabilities.',
        'requirements': ['Security analysis', 'SIEM', 'Firewall', 'IDS/IPS', 'Python', 'Penetration testing'],
        'responsibilities': ['Monitor security events', 'Conduct security audits', 'Respond to incidents'],
        'salary_min': 120000,
        'salary_max': 160000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/5'
    },
    # Cloud & DevOps
    {
        'title': 'DevOps Engineer',
        'company': 'CloudFirst Technologies',
        'location': 'Seattle, WA',
        'remote_type': 'remote',
        'industry': 'Cloud & DevOps',
        'description': 'Build and maintain CI/CD pipelines. Automate infrastructure with Terraform and manage Kubernetes clusters.',
        'requirements': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'CI/CD', 'Linux'],
        'responsibilities': ['Manage cloud infrastructure', 'Build deployment pipelines', 'Ensure system reliability'],
        'salary_min': 125000,
        'salary_max': 170000,
        'employment_type': 'full-time',
        'experience_level': 'Senior',
        'external_url': 'https://example.com/jobs/6'
    },
    # Product Management
    {
        'title': 'Product Manager',
        'company': 'Innovation Labs',
        'location': 'San Francisco, CA',
        'remote_type': 'hybrid',
        'industry': 'Product Management',
        'description': 'Define product roadmap and work with cross-functional teams to deliver customer value.',
        'requirements': ['Product strategy', 'Agile', 'User research', 'Analytics', 'Stakeholder management'],
        'responsibilities': ['Define product vision', 'Prioritize features', 'Collaborate with engineering'],
        'salary_min': 135000,
        'salary_max': 185000,
        'employment_type': 'full-time',
        'experience_level': 'Senior',
        'external_url': 'https://example.com/jobs/7'
    },
    # Design
    {
        'title': 'UI/UX Designer',
        'company': 'DesignStudio Pro',
        'location': 'Los Angeles, CA',
        'remote_type': 'remote',
        'industry': 'Design',
        'description': 'Create beautiful, user-friendly interfaces. Collaborate with product and engineering to deliver exceptional experiences.',
        'requirements': ['Figma', 'UI/UX design', 'Prototyping', 'User research', 'Design systems'],
        'responsibilities': ['Design interfaces', 'Create prototypes', 'Conduct user testing'],
        'salary_min': 95000,
        'salary_max': 135000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/8'
    },
    # Marketing
    {
        'title': 'Digital Marketing Manager',
        'company': 'GrowthHackers Inc',
        'location': 'Chicago, IL',
        'remote_type': 'hybrid',
        'industry': 'Marketing',
        'description': 'Drive growth through digital marketing channels. Manage SEO, SEM, and social media campaigns.',
        'requirements': ['Digital marketing', 'SEO', 'Google Analytics', 'Social media', 'Content marketing'],
        'responsibilities': ['Plan campaigns', 'Analyze performance', 'Optimize conversions'],
        'salary_min': 85000,
        'salary_max': 120000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/9'
    },
    # Healthcare
    {
        'title': 'Healthcare IT Specialist',
        'company': 'MedTech Solutions',
        'location': 'Boston, MA',
        'remote_type': 'onsite',
        'industry': 'Healthcare',
        'description': 'Manage healthcare IT systems and ensure HIPAA compliance. Work with EMR/EHR systems.',
        'requirements': ['EMR/EHR systems', 'HIPAA compliance', 'Healthcare IT', 'System administration'],
        'responsibilities': ['Maintain IT systems', 'Ensure compliance', 'Support clinical staff'],
        'salary_min': 80000,
        'salary_max': 110000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/10'
    },
    # Finance
    {
        'title': 'Financial Analyst',
        'company': 'InvestCorp',
        'location': 'New York, NY',
        'remote_type': 'hybrid',
        'industry': 'Finance',
        'description': 'Analyze financial data and create investment recommendations. Work with Bloomberg Terminal and financial models.',
        'requirements': ['Financial analysis', 'Excel', 'Bloomberg Terminal', 'Financial modeling', 'SQL'],
        'responsibilities': ['Create financial models', 'Analyze market trends', 'Generate reports'],
        'salary_min': 95000,
        'salary_max': 130000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/11'
    },
    # Engineering
    {
        'title': 'Mechanical Engineer',
        'company': 'Manufacturing Dynamics',
        'location': 'Detroit, MI',
        'remote_type': 'onsite',
        'industry': 'Engineering',
        'description': 'Design and optimize manufacturing processes. Work with CAD software and production systems.',
        'requirements': ['CAD', 'SolidWorks', 'Manufacturing', 'Process optimization', 'Engineering degree'],
        'responsibilities': ['Design components', 'Optimize processes', 'Quality control'],
        'salary_min': 85000,
        'salary_max': 115000,
        'employment_type': 'full-time',
        'experience_level': 'Mid',
        'external_url': 'https://example.com/jobs/12'
    },
    # Additional Technology roles
    {
        'title': 'Backend Engineer - Python',
        'company': 'APIFlow Inc',
        'location': 'Remote',
        'remote_type': 'remote',
        'industry': 'Technology',
        'description': 'Build scalable backend services with Python. Design REST APIs and work with microservices architecture.',
        'requirements': ['Python', 'Django', 'PostgreSQL', 'REST APIs', 'Microservices'],
        'responsibilities': ['Build APIs', 'Optimize performance', 'Write tests'],
        'salary_min': 120000,
        'salary_max': 160000,
        'employment_type': 'full-time',
        'experience_level': 'Senior',
        'external_url': 'https://example.com/jobs/13'
    },
    {
        'title': 'Software Engineer - Entry Level',
        'company': 'CodeAcademy Tech',
        'location': 'Portland, OR',
        'remote_type': 'hybrid',
        'industry': 'Technology',
        'description': 'Start your career in software engineering. Learn from experienced mentors and work on real products.',
        'requirements': ['JavaScript', 'Python', 'Git', 'HTML/CSS', 'Computer Science degree'],
        'responsibilities': ['Write code', 'Participate in code reviews', 'Learn best practices'],
        'salary_min': 75000,
        'salary_max': 95000,
        'employment_type': 'full-time',
        'experience_level': 'Entry',
        'external_url': 'https://example.com/jobs/14'
    },
    {
        'title': 'Lead Software Architect',
        'company': 'Enterprise Solutions Corp',
        'location': 'New York, NY',
        'remote_type': 'hybrid',
        'industry': 'Technology',
        'description': 'Lead architecture decisions for enterprise software. Mentor teams and drive technical excellence.',
        'requirements': ['System architecture', 'Java', 'Microservices', 'Cloud', '10+ years experience', 'Leadership'],
        'responsibilities': ['Design architecture', 'Lead technical teams', 'Set standards'],
        'salary_min': 180000,
        'salary_max': 250000,
        'employment_type': 'full-time',
        'experience_level': 'Lead',
        'external_url': 'https://example.com/jobs/15'
    }
]


def seed_job_postings():
    """Seed database with sample job postings"""

    with app.app_context():
        print("Seeding job postings...")

        # Check if jobs already exist
        existing_count = JobPosting.query.count()
        if existing_count > 0:
            print(f"Found {existing_count} existing job postings")
            response = input("Do you want to clear existing jobs and reseed? (yes/no): ")
            if response.lower() == 'yes':
                print("Clearing existing job postings...")
                JobPosting.query.delete()
                db.session.commit()
                print("✓ Cleared existing jobs")
            else:
                print("Keeping existing jobs and adding new ones...")

        # Create jobs with varied posting dates
        created_count = 0
        for i, job_data in enumerate(SAMPLE_JOBS):
            # Vary posting dates (0-30 days ago)
            days_ago = random.randint(0, 30)
            posted_date = datetime.utcnow() - timedelta(days=days_ago)

            job = JobPosting(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                remote_type=job_data['remote_type'],
                industry=job_data['industry'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                responsibilities=job_data.get('responsibilities', []),
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                employment_type=job_data['employment_type'],
                experience_level=job_data['experience_level'],
                posted_date=posted_date,
                source='Manual Seed',
                external_url=job_data['external_url'],
                is_active=True
            )

            db.session.add(job)
            created_count += 1

        db.session.commit()

        print(f"\n✅ Successfully seeded {created_count} job postings!")

        # Show summary by industry
        print("\nJobs by industry:")
        industries = {}
        for job in SAMPLE_JOBS:
            industry = job['industry']
            industries[industry] = industries.get(industry, 0) + 1

        for industry, count in sorted(industries.items()):
            print(f"  • {industry}: {count} jobs")

        print("\nJobs by experience level:")
        levels = {}
        for job in SAMPLE_JOBS:
            level = job['experience_level']
            levels[level] = levels.get(level, 0) + 1

        for level, count in sorted(levels.items()):
            print(f"  • {level}: {count} jobs")

        print("\nNext steps:")
        print("  1. Test job matching API: GET /api/job-matches/")
        print("  2. Matches will be generated using AI (Gemini) or fallback algorithm")
        print("  3. Check match scores and explanations")


if __name__ == "__main__":
    seed_job_postings()
