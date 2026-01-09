# -*- coding: utf-8 -*-
"""
Drop subscription_tier table to recreate with correct schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def drop_subscription_tier_table():
    """Drop subscription_tier table if it exists"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("DROPPING SUBSCRIPTION_TIER TABLE")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("[OK] Connected to database")
        print()

        # Drop subscription_tier table
        print("1. Dropping subscription_tier table...")
        conn.execute(text("DROP TABLE IF EXISTS subscription_tier CASCADE"))
        conn.commit()
        print("   [OK] subscription_tier table dropped")

        print()
        print("=" * 60)
        print("[SUCCESS] TABLE DROPPED!")
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
    success = drop_subscription_tier_table()
    sys.exit(0 if success else 1)
