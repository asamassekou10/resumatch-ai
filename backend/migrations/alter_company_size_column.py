"""
Migration: Alter company_size column in company_intel table
Reason: AI-generated company sizes can exceed 50 characters
Change: VARCHAR(50) -> VARCHAR(200)
Date: 2025-11-30
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/resume_optimizer')

def run_migration():
    """Alter company_size column to support longer values"""

    print("Starting migration: Alter company_size column...")
    print(f"Database URL: {DATABASE_URL}")

    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Alter company_size column from VARCHAR(50) to VARCHAR(200)
            print("\nAltering company_size column from VARCHAR(50) to VARCHAR(200)...")
            conn.execute(text("""
                ALTER TABLE company_intel
                ALTER COLUMN company_size TYPE VARCHAR(200);
            """))
            conn.commit()
            print("✓ Column altered successfully")

            # Verify the change
            print("\nVerifying column type...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'company_intel'
                AND column_name = 'company_size';
            """))

            for row in result:
                print(f"✓ {row[0]}: {row[1]}({row[2]})")

            print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == '__main__':
    run_migration()
