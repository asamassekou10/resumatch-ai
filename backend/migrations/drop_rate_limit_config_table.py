# -*- coding: utf-8 -*-
"""
Drop rate_limit_config table to recreate with correct schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def drop_rate_limit_config_table():
    """Drop rate_limit_config table if it exists"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("DROPPING RATE_LIMIT_CONFIG TABLE")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("[OK] Connected to database")
        print()

        # Drop rate_limit_config table
        print("1. Dropping rate_limit_config table...")
        conn.execute(text("DROP TABLE IF EXISTS rate_limit_config CASCADE"))
        conn.commit()
        print("   [OK] rate_limit_config table dropped")

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
    success = drop_rate_limit_config_table()
    sys.exit(0 if success else 1)
