"""
Create job_applications table for application tracking feature
Run this with: python backend/migrations/create_job_applications_table.py
"""

import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, JobApplication
from app import app

def create_job_applications_table():
    """Create the job_applications table if it doesn't exist"""
    with app.app_context():
        # Check if table exists
        inspector = db.inspect(db.engine)
        if 'job_applications' in inspector.get_table_names():
            print("✓ job_applications table already exists")
            return

        print("Creating job_applications table...")

        # Create the table
        JobApplication.__table__.create(db.engine)

        print("✓ job_applications table created successfully")
        print("\nTable includes:")
        print("  - Job details (company, title, URL, description)")
        print("  - Status tracking (saved, applied, interview, etc.)")
        print("  - Important dates (applied, interview, follow-up)")
        print("  - Notes and tracking info")
        print("  - Star and archive functionality")

if __name__ == '__main__':
    try:
        create_job_applications_table()
        print("\n✓ Migration completed successfully")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
