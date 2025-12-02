#!/usr/bin/env python
"""
Initialize guest tables for guest mode feature.
This script creates the necessary tables for guest sessions and guest analyses.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Flask app and models
from app import app, db
from models import GuestSession, GuestAnalysis

def create_guest_tables():
    """Create guest session and analysis tables"""
    with app.app_context():
        try:
            print("Creating guest_sessions table...")
            GuestSession.__table__.create(db.engine, checkfirst=True)
            print("✓ guest_sessions table created successfully")

            print("Creating guest_analyses table...")
            GuestAnalysis.__table__.create(db.engine, checkfirst=True)
            print("✓ guest_analyses table created successfully")

            print("\n✅ All guest tables initialized successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error creating guest tables: {e}")
            return False

if __name__ == '__main__':
    success = create_guest_tables()
    sys.exit(0 if success else 1)
