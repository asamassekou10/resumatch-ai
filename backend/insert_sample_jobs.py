"""
Insert sample job postings for demo/presentation purposes
Quick solution to populate market intelligence pages
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def insert_sample_jobs():
    """Insert 5 sample tech job postings"""

    print("=" * 60)
    print("INSERTING SAMPLE JOBS FOR DEMO")
    print("=" * 60)
    print()

    # Sample job data - realistic tech jobs
    sample_jobs = [
        {
            'title': 'Senior Software Engineer',
            'company': 'TechCorp Solutions',
            'location': 'San Francisco, CA',
            'industry': 'Technology',
            'salary_min': 130000,
            'salary_max': 180000,
            'requirements': ['Python', 'React', 'AWS', 'Docker', 'Kubernetes', '5+ years experience'],
            'description': 'We are seeking a Senior Software Engineer to join our growing team. You will work on building scalable web applications using modern technologies.',
            'employment_type': 'full-time',
            'experience_level': 'Senior',
            'remote_type': 'hybrid',
            'external_url': 'https://example.com/jobs/senior-software-engineer',
            'source': 'Demo Data'
        },
        {
            'title': 'Full Stack Developer',
            'company': 'InnovateTech Inc',
            'location': 'New York, NY',
            'industry': 'Technology',
            'salary_min': 100000,
            'salary_max': 140000,
            'requirements': ['JavaScript', 'Node.js', 'React', 'PostgreSQL', 'Git', '3+ years experience'],
            'description': 'Join our dynamic team to build cutting-edge web applications. Work with modern JavaScript frameworks and contribute to our microservices architecture.',
            'employment_type': 'full-time',
            'experience_level': 'Mid',
            'remote_type': 'remote',
            'external_url': 'https://example.com/jobs/full-stack-developer',
            'source': 'Demo Data'
        },
        {
            'title': 'Data Scientist',
            'company': 'DataDriven Analytics',
            'location': 'Boston, MA',
            'industry': 'Analytics',
            'salary_min': 115000,
            'salary_max': 160000,
            'requirements': ['Python', 'Machine Learning', 'TensorFlow', 'scikit-learn', 'SQL', 'Statistics'],
            'description': 'Seeking a Data Scientist to develop ML models and drive data-driven decision making. Experience with deep learning and NLP is a plus.',
            'employment_type': 'full-time',
            'experience_level': 'Mid',
            'remote_type': 'hybrid',
            'external_url': 'https://example.com/jobs/data-scientist',
            'source': 'Demo Data'
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudFirst Systems',
            'location': 'Seattle, WA',
            'industry': 'Technology',
            'salary_min': 120000,
            'salary_max': 165000,
            'requirements': ['AWS', 'Terraform', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Python', 'Linux'],
            'description': 'Looking for a DevOps Engineer to manage our cloud infrastructure and implement automation solutions. Strong AWS experience required.',
            'employment_type': 'full-time',
            'experience_level': 'Senior',
            'remote_type': 'remote',
            'external_url': 'https://example.com/jobs/devops-engineer',
            'source': 'Demo Data'
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'AI Innovations Lab',
            'location': 'Austin, TX',
            'industry': 'Artificial Intelligence',
            'salary_min': 125000,
            'salary_max': 175000,
            'requirements': ['Python', 'PyTorch', 'TensorFlow', 'MLOps', 'Docker', 'REST APIs', 'Computer Vision'],
            'description': 'Join our AI team to build and deploy production ML systems. Work on exciting projects in computer vision and NLP.',
            'employment_type': 'full-time',
            'experience_level': 'Senior',
            'remote_type': 'hybrid',
            'external_url': 'https://example.com/jobs/ml-engineer',
            'source': 'Demo Data'
        }
    ]

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found!")
        return False

    try:
        engine = create_engine(database_url)
        conn = engine.connect()

        # Check if jobs already exist
        result = conn.execute(text('SELECT COUNT(*) FROM job_postings'))
        existing_count = result.scalar()

        if existing_count > 0:
            print(f"ℹ️  Found {existing_count} existing jobs")
            print("   Clearing existing jobs for fresh demo data...")
            conn.execute(text('DELETE FROM job_postings'))
            conn.commit()

        # Insert sample jobs
        print()
        print("Inserting 5 sample jobs...")
        print()

        for i, job in enumerate(sample_jobs, 1):
            # Convert requirements list to JSON
            job_data = {
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'industry': job['industry'],
                'salary_min': job['salary_min'],
                'salary_max': job['salary_max'],
                'requirements': json.dumps(job['requirements']),
                'description': job['description'],
                'employment_type': job['employment_type'],
                'experience_level': job['experience_level'],
                'remote_type': job['remote_type'],
                'external_url': job['external_url'],
                'source': job['source']
            }

            conn.execute(text('''
                INSERT INTO job_postings
                (title, company, location, industry, salary_min, salary_max,
                 requirements, description, employment_type, experience_level,
                 remote_type, external_url, source, is_active, created_at, posted_date)
                VALUES
                (:title, :company, :location, :industry, :salary_min, :salary_max,
                 :requirements, :description, :employment_type, :experience_level,
                 :remote_type, :external_url, :source, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            '''), job_data)

            print(f"  ✅ {i}. {job['title']} at {job['company']}")

        conn.commit()

        print()
        print("=" * 60)
        print("✅ SAMPLE JOBS INSERTED SUCCESSFULLY")
        print("=" * 60)
        print()

        # Verify
        result = conn.execute(text('SELECT COUNT(*) FROM job_postings'))
        job_count = result.scalar()
        print(f"📊 Total jobs in database: {job_count}")
        print()

        # Show the jobs
        result = conn.execute(text('''
            SELECT title, company, location, salary_min, salary_max
            FROM job_postings
            ORDER BY created_at DESC
        '''))
        jobs = result.fetchall()

        print("Jobs in database:")
        print("-" * 60)
        for job in jobs:
            title, company, location, sal_min, sal_max = job
            salary = f"${sal_min:,} - ${sal_max:,}" if sal_min and sal_max else "Not specified"
            print(f"  • {title} at {company}")
            print(f"    📍 {location} | 💰 {salary}")

        conn.close()
        print()
        print("=" * 60)
        print("🎉 Market Intelligence pages are now ready for demo!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = insert_sample_jobs()
    sys.exit(0 if success else 1)
