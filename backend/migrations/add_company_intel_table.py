"""
Database migration: Add company_intel table for AI-powered company research
Creates table for storing comprehensive company intelligence and insights
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/resume_optimizer')

def run_migration():
    """Run the migration to add company_intel table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Creating company_intel table...")

        # Create company_intel table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS company_intel (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                company VARCHAR(200) NOT NULL,
                industry VARCHAR(100),

                -- Company overview
                overview TEXT,
                founded_year INTEGER,
                headquarters VARCHAR(200),
                company_size VARCHAR(50),
                website VARCHAR(500),

                -- Business information (JSON)
                products_services JSON,
                target_markets JSON,
                competitors JSON,

                -- Culture and values
                company_culture TEXT,
                core_values JSON,
                work_environment TEXT,

                -- News and updates (JSON)
                recent_news JSON,
                major_developments JSON,

                -- Leadership team (JSON)
                leadership JSON,

                -- Financial and growth (JSON)
                financial_health JSON,
                growth_metrics JSON,

                -- Career insights
                interview_insights TEXT,
                employee_sentiment TEXT,
                pros_cons JSON,

                -- Technology stack (JSON)
                tech_stack JSON,

                -- AI-generated insights
                ai_summary TEXT,
                key_insights JSON,
                recommendations JSON,

                -- User interaction
                is_saved BOOLEAN DEFAULT FALSE,
                notes TEXT,

                -- Timestamps and caching
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                cached_until TIMESTAMP
            );
        """))

        print("✓ company_intel table created")

        # Create indexes
        print("Creating indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_company_intel_user ON company_intel(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_intel_company ON company_intel(company);",
            "CREATE INDEX IF NOT EXISTS idx_company_intel_industry ON company_intel(industry);",
            "CREATE INDEX IF NOT EXISTS idx_company_intel_user_company ON company_intel(user_id, company);",
            "CREATE INDEX IF NOT EXISTS idx_company_intel_saved ON company_intel(is_saved);",
            "CREATE INDEX IF NOT EXISTS idx_company_intel_created ON company_intel(created_at);",
        ]

        for idx_sql in indexes:
            conn.execute(text(idx_sql))
            print(f"✓ {idx_sql.split('idx_')[1].split(' ')[0]} index created")

        conn.commit()

        print("\n✅ Migration completed successfully!")
        print("Company intel table created with 6 indexes")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)
