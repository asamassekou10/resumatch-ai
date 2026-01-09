# -*- coding: utf-8 -*-
"""
Add missing subscription-related fields to User model
- subscription_start_date: Track when subscription started for billing anniversary
- last_credit_reset: Track last time credits were reset
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def add_subscription_fields():
    """Add subscription tracking fields to users table"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("ADDING SUBSCRIPTION FIELDS TO USERS")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("[OK] Connected to database")
        print()

        # Add subscription_start_date field
        print("1. Adding subscription_start_date field...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMP
            """))
            conn.commit()
            print("   [OK] subscription_start_date added")
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise
            print("   [WARN] subscription_start_date already exists")

        # Add last_credit_reset field
        print("2. Adding last_credit_reset field...")
        try:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS last_credit_reset TIMESTAMP
            """))
            conn.commit()
            print("   [OK] last_credit_reset added")
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise
            print("   [WARN] last_credit_reset already exists")

        # Create index for efficient querying
        print("3. Creating indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_subscription_start_date
                ON users(subscription_start_date)
            """))
            conn.commit()
            print("   [OK] Indexes created")
        except Exception as e:
            print("   [WARN] Index warning: " + str(e)[:60])

        print()
        print("=" * 60)
        print("[SUCCESS] SUBSCRIPTION FIELDS ADDED!")
        print("=" * 60)
        print()

        conn.close()
        return True

    except Exception as e:
        print("[ERROR] Failed: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_subscription_fields()
    sys.exit(0 if success else 1)
