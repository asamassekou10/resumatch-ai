"""
Manually trigger job ingestion from Adzuna API
Populates job_postings table for market intelligence features
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def ingest_jobs():
    """Manually trigger job ingestion"""

    print("=" * 60)
    print("MANUAL JOB INGESTION FROM ADZUNA")
    print("=" * 60)
    print()

    # Check if Adzuna credentials are set
    app_id = os.getenv('ADZUNA_APP_ID')
    app_key = os.getenv('ADZUNA_APP_KEY')

    if not app_id or not app_key:
        print("❌ Adzuna credentials not configured!")
        print()
        print("Required environment variables:")
        print("  - ADZUNA_APP_ID")
        print("  - ADZUNA_APP_KEY")
        print()
        print("Add these to your Render environment variables.")
        return False

    print("✅ Adzuna credentials found")
    print()

    try:
        # Import the ingestion function
        print("Loading ingestion module...")
        from scheduled_ingestion_tasks import ingest_real_job_postings

        print("✅ Module loaded")
        print()

        # Trigger ingestion
        print("Starting job ingestion...")
        print("This will fetch real jobs from Adzuna API")
        print("(This may take 2-5 minutes)")
        print()

        result = ingest_real_job_postings()

        print()
        print("=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print()

        if result:
            print("✅ Jobs successfully ingested")
            print()
            print("Market intelligence pages should now show data:")
            print("  - Market Trends")
            print("  - Salary Analysis")
            print("  - Skills Demand")
            print("  - Top Companies")
            print()
        else:
            print("⚠️  Ingestion completed with warnings")
            print("Check logs above for details")
            print()

        # Verify job count
        from sqlalchemy import create_engine, text
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        conn = engine.connect()

        result = conn.execute(text('SELECT COUNT(*) FROM job_postings'))
        job_count = result.scalar()

        print(f"📊 Total jobs in database: {job_count}")
        print()

        if job_count > 0:
            # Show sample jobs
            result = conn.execute(text('''
                SELECT job_title, company_name, location, salary_min, salary_max
                FROM job_postings
                LIMIT 5
            '''))
            jobs = result.fetchall()

            print("Sample jobs:")
            print("-" * 60)
            for job in jobs:
                title, company, location, sal_min, sal_max = job
                salary = f"${sal_min:,} - ${sal_max:,}" if sal_min and sal_max else "Not specified"
                print(f"  {title} at {company}")
                print(f"    Location: {location}")
                print(f"    Salary: {salary}")
                print()

        conn.close()

        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = ingest_jobs()
    sys.exit(0 if success else 1)
