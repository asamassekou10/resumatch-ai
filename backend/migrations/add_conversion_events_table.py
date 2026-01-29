"""
Migration: Add conversion_events table
Run this script to create the conversion_events table for tracking conversion funnel events
"""

from app import app, db
from models import ConversionEvent

def create_conversion_events_table():
    """Create the conversion_events table"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ Conversion events table created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating conversion events table: {str(e)}")
            return False

if __name__ == '__main__':
    create_conversion_events_table()
