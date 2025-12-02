"""
Migration: Add industry personalization fields to users table
Ensures industry preference fields exist for market intelligence personalization
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Add industry personalization fields to users table"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Adding industry personalization fields to users table...")

        # Add preferred_industry column
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferred_industry VARCHAR(100);
            """))
            conn.commit()
            print("✓ preferred_industry column added/verified")
        except Exception as e:
            print(f"Note: preferred_industry column: {e}")

        # Add preferred_job_titles column (JSON array)
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferred_job_titles JSON DEFAULT '[]';
            """))
            conn.commit()
            print("✓ preferred_job_titles column added/verified")
        except Exception as e:
            print(f"Note: preferred_job_titles column: {e}")

        # Add preferred_location column
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferred_location VARCHAR(200);
            """))
            conn.commit()
            print("✓ preferred_location column added/verified")
        except Exception as e:
            print(f"Note: preferred_location column: {e}")

        # Add experience_level column
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50);
            """))
            conn.commit()
            print("✓ experience_level column added/verified")
        except Exception as e:
            print(f"Note: experience_level column: {e}")

        # Add preferences_completed column
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferences_completed BOOLEAN DEFAULT FALSE;
            """))
            conn.commit()
            print("✓ preferences_completed column added/verified")
        except Exception as e:
            print(f"Note: preferences_completed column: {e}")

        # Add detected_industries column (JSON array)
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS detected_industries JSON DEFAULT '[]';
            """))
            conn.commit()
            print("✓ detected_industries column added/verified")
        except Exception as e:
            print(f"Note: detected_industries column: {e}")

        # Add indexes for better query performance
        print("\nAdding indexes for performance...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_preferred_industry ON users(preferred_industry);
            """))
            conn.commit()
            print("✓ Index on preferred_industry created")
        except Exception as e:
            print(f"Note: Index creation: {e}")

        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_experience_level ON users(experience_level);
            """))
            conn.commit()
            print("✓ Index on experience_level created")
        except Exception as e:
            print(f"Note: Index creation: {e}")

        print("\n✅ Industry personalization migration completed!")
        print("\nNext steps:")
        print("1. Users can now set their preferred industry")
        print("2. Market intelligence will filter by user's industry")
        print("3. AI features will use industry context for personalization")

if __name__ == "__main__":
    run_migration()
