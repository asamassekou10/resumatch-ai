"""
Populate market intelligence data for testing and demo

This script populates the JobPostingKeyword table with sample job postings
to enable Top Skills and market statistics features.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, JobPostingKeyword, Keyword
from sample_job_postings import load_sample_postings
from app import app

def populate_market_data():
    """
    Populate JobPostingKeyword table with sample data
    """
    print("Starting market data population...")

    with app.app_context():
        # Load sample postings
        sample_postings = load_sample_postings()
        print(f"Loaded {len(sample_postings)} sample job postings")

        # Get all keywords from database for mapping
        all_keywords = Keyword.query.all()
        keyword_map = {kw.name.lower(): kw for kw in all_keywords}
        print(f"Found {len(keyword_map)} keywords in database")

        # Track statistics
        inserted_count = 0
        skipped_count = 0
        missing_skills = set()

        # Insert job posting keywords
        for posting in sample_postings:
            job_title = posting['job_title']
            company = posting['company_name']
            skills = posting.get('skills', [])

            for skill_name in skills:
                # Find matching keyword (case-insensitive)
                keyword = keyword_map.get(skill_name.lower())

                if not keyword:
                    # Try to create keyword if it doesn't exist
                    try:
                        keyword = Keyword(
                            name=skill_name,
                            category='technical',
                            frequency=1
                        )
                        db.session.add(keyword)
                        db.session.flush()  # Get ID without committing
                        keyword_map[skill_name.lower()] = keyword
                        print(f"  Created new keyword: {skill_name}")
                    except Exception as e:
                        missing_skills.add(skill_name)
                        skipped_count += 1
                        continue

                # Check if this exact record already exists
                existing = JobPostingKeyword.query.filter_by(
                    job_posting_url=posting['job_posting_url'],
                    keyword_id=keyword.id
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                # Create job posting keyword record
                job_keyword = JobPostingKeyword(
                    job_posting_url=posting['job_posting_url'],
                    job_title=job_title,
                    company_name=company,
                    keyword_id=keyword.id,
                    frequency=1,
                    salary_min=posting.get('salary_min'),
                    salary_max=posting.get('salary_max'),
                    salary_currency='USD',
                    location=posting.get('location'),
                    industry=posting.get('industry'),
                    source='sample_data',
                    extracted_at=datetime.utcnow() - timedelta(days=5)  # Make it look slightly old
                )

                db.session.add(job_keyword)
                inserted_count += 1

        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully inserted {inserted_count} job-skill records")
            print(f"⏭️  Skipped {skipped_count} duplicate records")

            if missing_skills:
                print(f"\n⚠️  Missing skills (couldn't find or create): {', '.join(missing_skills)}")

            # Verify data
            total_records = JobPostingKeyword.query.count()
            print(f"\n📊 Total JobPostingKeyword records in database: {total_records}")

            # Show breakdown by industry
            print("\n📈 Records by industry:")
            industries = db.session.query(
                JobPostingKeyword.industry,
                db.func.count(JobPostingKeyword.id)
            ).group_by(JobPostingKeyword.industry).all()

            for industry, count in industries:
                print(f"  {industry or 'Unknown'}: {count} records")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing data: {e}")
            raise

if __name__ == '__main__':
    try:
        populate_market_data()
        print("\n✨ Market data population complete!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
