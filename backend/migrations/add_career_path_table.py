"""
Database migration: Add career_path table for AI-powered career roadmaps
Creates table for storing personalized career progression strategies
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/resume_optimizer')

def run_migration():
    """Run the migration to add career_path table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Creating career_path table...")

        # Create career_path table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS career_path (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

                -- Career positions
                current_role VARCHAR(200) NOT NULL,
                target_role VARCHAR(200) NOT NULL,
                industry VARCHAR(100),
                years_of_experience INTEGER,

                -- Path overview
                path_summary TEXT,
                estimated_duration VARCHAR(100),
                difficulty_level VARCHAR(50),

                -- Career steps (JSON)
                career_steps JSON,

                -- Skills analysis
                current_skills JSON,
                skills_gap JSON,
                transferable_skills JSON,

                -- Learning resources and certifications (JSON)
                learning_resources JSON,
                certifications JSON,

                -- Salary and alternatives
                salary_expectations JSON,
                alternative_paths JSON,

                -- Networking and mentorship
                networking_tips TEXT,
                mentor_guidance TEXT,
                industry_connections JSON,

                -- Success metrics
                key_milestones JSON,
                success_stories JSON,

                -- AI insights
                ai_recommendations TEXT,
                risk_factors JSON,
                success_factors JSON,

                -- Market insights
                job_market_outlook TEXT,
                demand_trend VARCHAR(50),

                -- User interaction
                is_saved BOOLEAN DEFAULT FALSE,
                notes TEXT,
                progress_tracking JSON DEFAULT '{}',

                -- Timestamps and caching
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cached_until TIMESTAMP
            );
        """))

        print("Creating indexes for career_path...")

        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_career_path_user ON career_path(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_current_role ON career_path(current_role);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_target_role ON career_path(target_role);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_industry ON career_path(industry);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_user_roles ON career_path(user_id, current_role, target_role);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_saved ON career_path(is_saved);",
            "CREATE INDEX IF NOT EXISTS idx_career_path_created ON career_path(created_at);",
        ]

        for index_sql in indexes:
            conn.execute(text(index_sql))
            print(f"  ✓ Created index")

        conn.commit()
        print("✓ Career path table created successfully!")

def rollback_migration():
    """Rollback the migration (drop career_path table)"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Dropping career_path table...")
        conn.execute(text("DROP TABLE IF EXISTS career_path CASCADE;"))
        conn.commit()
        print("✓ Career path table dropped successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    else:
        run_migration()
