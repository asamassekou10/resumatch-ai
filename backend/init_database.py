"""
Initialize database tables for production deployment
Run this script once after deploying to create all required tables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up app context
from app import app, db

def init_database():
    """Create all database tables"""
    with app.app_context():
        try:
            print("Creating database tables...")

            # Import all models to register them
            from models import (
                User, Analysis, GuestSession, GuestAnalysis,
                JobPosting, JobMatch, InterviewPrep, CompanyIntel,
                CareerPath, SystemConfiguration, Keyword
            )

            # Create all tables
            db.create_all()

            print("✅ Database tables created successfully!")

            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print(f"\n📊 Created {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   - {table}")

            return True

        except Exception as e:
            print(f"❌ Error creating database tables: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
