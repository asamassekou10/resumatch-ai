"""
Insert sample job postings for demo/presentation purposes
Quick solution to populate market intelligence pages
"""

import os
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
            'job_title': 'Senior Software Engineer',
            'company_name': 'TechCorp Solutions',
            'location': 'San Francisco, CA',
            'salary_min': 130000,
            'salary_max': 180000,
            'requirements': 'Python, React, AWS, Docker, Kubernetes, 5+ years experience, Bachelor\'s degree in Computer Science',
            'job_description': 'We are seeking a Senior Software Engineer to join our growing team. You will work on building scalable web applications using modern technologies.',
            'posted_date': datetime.utcnow(),
            'application_url': 'https://example.com/jobs/senior-software-engineer'
        },
        {
            'job_title': 'Full Stack Developer',
            'company_name': 'InnovateTech Inc',
            'location': 'New York, NY',
            'salary_min': 100000,
            'salary_max': 140000,
            'requirements': 'JavaScript, Node.js, React, PostgreSQL, Git, 3+ years experience',
            'job_description': 'Join our dynamic team to build cutting-edge web applications. Work with modern JavaScript frameworks and contribute to our microservices architecture.',
            'posted_date': datetime.utcnow(),
            'application_url': 'https://example.com/jobs/full-stack-developer'
        },
        {
            'job_title': 'Data Scientist',
            'company_name': 'DataDriven Analytics',
            'location': 'Boston, MA',
            'salary_min': 115000,
            'salary_max': 160000,
            'requirements': 'Python, Machine Learning, TensorFlow, scikit-learn, SQL, Statistics, PhD or Master\'s degree preferred',
            'job_description': 'Seeking a Data Scientist to develop ML models and drive data-driven decision making. Experience with deep learning and NLP is a plus.',
            'posted_date': datetime.utcnow(),
            'application_url': 'https://example.com/jobs/data-scientist'
        },
        {
            'job_title': 'DevOps Engineer',
            'company_name': 'CloudFirst Systems',
            'location': 'Seattle, WA',
            'salary_min': 120000,
            'salary_max': 165000,
            'requirements': 'AWS, Terraform, Docker, Kubernetes, CI/CD, Jenkins, Python, Linux',
            'job_description': 'Looking for a DevOps Engineer to manage our cloud infrastructure and implement automation solutions. Strong AWS experience required.',
            'posted_date': datetime.utcnow(),
            'application_url': 'https://example.com/jobs/devops-engineer'
        },
        {
            'job_title': 'Machine Learning Engineer',
            'company_name': 'AI Innovations Lab',
            'location': 'Austin, TX',
            'salary_min': 125000,
            'salary_max': 175000,
            'requirements': 'Python, PyTorch, TensorFlow, MLOps, Docker, REST APIs, Computer Vision, 4+ years experience',
            'job_description': 'Join our AI team to build and deploy production ML systems. Work on exciting projects in computer vision and NLP.',
            'posted_date': datetime.utcnow(),
            'application_url': 'https://example.com/jobs/ml-engineer'
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
            conn.execute(text('''
                INSERT INTO job_postings
                (job_title, company_name, location, salary_min, salary_max,
                 requirements, job_description, posted_date, application_url, created_at)
                VALUES
                (:job_title, :company_name, :location, :salary_min, :salary_max,
                 :requirements, :job_description, :posted_date, :application_url, CURRENT_TIMESTAMP)
            '''), job)

            print(f"  ✅ {i}. {job['job_title']} at {job['company_name']}")

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
            SELECT job_title, company_name, location, salary_min, salary_max
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
