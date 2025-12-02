"""
Migration: Add subscription_status column to users table
Adds subscription_status field to track subscription state (inactive, active, cancelled, expired, past_due)
"""

from sqlalchemy import create_engine, text
import os

def run_migration():
    """Add subscription_status column to users table"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://resumatch_user:resumatch_password@localhost:5432/resumatch_db')

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("Adding subscription_status column to users table...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'inactive' NOT NULL;
            """))
            conn.commit()
            print("✓ subscription_status column added")
        except Exception as e:
            print(f"Error adding subscription_status column: {e}")

        # Update existing users with paid subscriptions to have active status
        print("\nUpdating existing subscribed users to 'active' status...")
        try:
            conn.execute(text("""
                UPDATE users
                SET subscription_status = 'active'
                WHERE subscription_tier != 'free'
                AND subscription_id IS NOT NULL;
            """))
            conn.commit()
            print("✓ Existing subscribed users updated")
        except Exception as e:
            print(f"Error updating existing users: {e}")

    print("\nMigration completed!")

if __name__ == "__main__":
    run_migration()
