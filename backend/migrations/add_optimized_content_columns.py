"""
Migration: Add optimized content columns to analyses table
Adds optimized_feedback and cover_letter columns
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Add new columns for optimized content"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Adding optimized_feedback column...")
        try:
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN IF NOT EXISTS optimized_feedback TEXT;
            """))
            conn.commit()
            print("✓ optimized_feedback column added")
        except Exception as e:
            print(f"Error adding optimized_feedback: {e}")

        print("Adding cover_letter column...")
        try:
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN IF NOT EXISTS cover_letter TEXT;
            """))
            conn.commit()
            print("✓ cover_letter column added")
        except Exception as e:
            print(f"Error adding cover_letter: {e}")

    print("\nMigration completed!")

if __name__ == "__main__":
    run_migration()
