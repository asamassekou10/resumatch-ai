"""
Migration: Add template system columns to analyses table
Adds structured_resume, selected_resume_template, and selected_cover_letter_template columns
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Add new columns for template system"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Adding structured_resume column (JSON for parsed resume data)...")
        try:
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN IF NOT EXISTS structured_resume JSONB;
            """))
            conn.commit()
            print("✓ structured_resume column added")
        except Exception as e:
            print(f"Error adding structured_resume: {e}")

        print("Adding selected_resume_template column...")
        try:
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN IF NOT EXISTS selected_resume_template VARCHAR(50) DEFAULT 'modern';
            """))
            conn.commit()
            print("✓ selected_resume_template column added")
        except Exception as e:
            print(f"Error adding selected_resume_template: {e}")

        print("Adding selected_cover_letter_template column...")
        try:
            conn.execute(text("""
                ALTER TABLE analyses
                ADD COLUMN IF NOT EXISTS selected_cover_letter_template VARCHAR(50) DEFAULT 'professional';
            """))
            conn.commit()
            print("✓ selected_cover_letter_template column added")
        except Exception as e:
            print(f"Error adding selected_cover_letter_template: {e}")

    print("\nTemplate system migration completed!")

if __name__ == "__main__":
    run_migration()
