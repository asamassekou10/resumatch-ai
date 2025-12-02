"""
Migration: Add interview_prep table for AI-powered interview preparation
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Create interview_prep table with indexes"""

    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Creating interview_prep table...")

        # Create interview_prep table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS interview_prep (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    company VARCHAR(200) NOT NULL,
                    job_title VARCHAR(200),
                    industry VARCHAR(100),
                    questions JSON,
                    company_culture TEXT,
                    interview_process JSON,
                    interview_tips JSON,
                    common_topics JSON,
                    is_saved BOOLEAN DEFAULT FALSE,
                    practiced_questions JSON DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cached_until TIMESTAMP
                );
            """))
            conn.commit()
            print("✓ interview_prep table created")
        except Exception as e:
            print(f"Note: interview_prep table: {e}")

        # Create indexes for interview_prep
        print("\nCreating indexes for interview_prep...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_prep_user_id ON interview_prep(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_prep_company ON interview_prep(company);",
            "CREATE INDEX IF NOT EXISTS idx_prep_industry ON interview_prep(industry);",
            "CREATE INDEX IF NOT EXISTS idx_prep_is_saved ON interview_prep(is_saved);",
            "CREATE INDEX IF NOT EXISTS idx_prep_created_at ON interview_prep(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_prep_user_company ON interview_prep(user_id, company);"
        ]

        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
            except Exception as e:
                print(f"Note: Index creation: {e}")

        print("✓ interview_prep indexes created")

        print("\n✅ Interview prep table migration completed!")
        print("\nTable created:")
        print("  • interview_prep - Stores AI-generated interview preparation")
        print("\nNext steps:")
        print("  1. Test interview prep generation with Gemini")
        print("  2. Generate prep for sample companies")
        print("  3. Test question practice tracking")

if __name__ == "__main__":
    run_migration()
