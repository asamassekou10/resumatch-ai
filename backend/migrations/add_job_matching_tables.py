"""
Migration: Add job matching tables (job_postings and job_matches)
Creates tables for AI-powered job matching feature
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Create job_postings and job_matches tables with proper indexes"""

    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Creating job matching tables...")

        # Create job_postings table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS job_postings (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    company VARCHAR(200) NOT NULL,
                    location VARCHAR(200),
                    remote_type VARCHAR(50),
                    industry VARCHAR(100),
                    description TEXT,
                    requirements JSON,
                    responsibilities JSON,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency VARCHAR(10) DEFAULT 'USD',
                    employment_type VARCHAR(50),
                    experience_level VARCHAR(50),
                    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_date TIMESTAMP,
                    source VARCHAR(100),
                    external_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print("✓ job_postings table created")
        except Exception as e:
            print(f"Note: job_postings table: {e}")

        # Create indexes for job_postings
        print("\nCreating indexes for job_postings...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_job_title ON job_postings(title);",
            "CREATE INDEX IF NOT EXISTS idx_job_company ON job_postings(company);",
            "CREATE INDEX IF NOT EXISTS idx_job_industry ON job_postings(industry);",
            "CREATE INDEX IF NOT EXISTS idx_job_posted_date ON job_postings(posted_date);",
            "CREATE INDEX IF NOT EXISTS idx_job_is_active ON job_postings(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_job_industry_active ON job_postings(industry, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_job_posted_active ON job_postings(posted_date, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_job_location ON job_postings(location);"
        ]

        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"Note: Index creation: {e}")

        print("✓ job_postings indexes created")

        # Create job_matches table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS job_matches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
                    match_score FLOAT NOT NULL,
                    ai_explanation TEXT,
                    matching_skills JSON,
                    missing_skills JSON,
                    skill_match_percentage FLOAT,
                    is_saved BOOLEAN DEFAULT FALSE,
                    is_applied BOOLEAN DEFAULT FALSE,
                    is_dismissed BOOLEAN DEFAULT FALSE,
                    viewed_at TIMESTAMP,
                    saved_at TIMESTAMP,
                    applied_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, job_posting_id)
                );
            """))
            conn.commit()
            print("✓ job_matches table created")
        except Exception as e:
            print(f"Note: job_matches table: {e}")

        # Create indexes for job_matches
        print("\nCreating indexes for job_matches...")
        match_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_match_user_id ON job_matches(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_match_job_id ON job_matches(job_posting_id);",
            "CREATE INDEX IF NOT EXISTS idx_match_score ON job_matches(match_score);",
            "CREATE INDEX IF NOT EXISTS idx_match_is_saved ON job_matches(is_saved);",
            "CREATE INDEX IF NOT EXISTS idx_match_created_at ON job_matches(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_match_user_score ON job_matches(user_id, match_score);",
            "CREATE INDEX IF NOT EXISTS idx_match_user_saved ON job_matches(user_id, is_saved);"
        ]

        for index_sql in match_indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"Note: Index creation: {e}")

        print("✓ job_matches indexes created")

        print("\n✅ Job matching tables migration completed!")
        print("\nTables created:")
        print("  • job_postings - Stores job listings")
        print("  • job_matches - Stores AI-generated matches with scores")
        print("\nNext steps:")
        print("  1. Seed sample job postings")
        print("  2. Test AI matching service")
        print("  3. Generate matches for users")

if __name__ == "__main__":
    run_migration()
