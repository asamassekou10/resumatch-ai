# -*- coding: utf-8 -*-
"""
Create rate_limit_config table
This table stores credit costs per operation per tier
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def create_rate_limit_config_table():
    """Create rate_limit_config table with all necessary fields"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("CREATING RATE_LIMIT_CONFIG TABLE")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("[OK] Connected to database")
        print()

        # Create rate_limit_config table
        print("1. Creating rate_limit_config table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rate_limit_config (
                id SERIAL PRIMARY KEY,
                operation VARCHAR(50) NOT NULL,
                subscription_tier VARCHAR(50) NOT NULL,
                cost_in_credits INTEGER NOT NULL DEFAULT 1,
                daily_limit INTEGER,
                monthly_limit INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(operation, subscription_tier)
            )
        """))
        conn.commit()
        print("   [OK] rate_limit_config table created")

        # Create indexes
        print("2. Creating indexes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_rate_limit_operation
            ON rate_limit_config(operation)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_rate_limit_tier
            ON rate_limit_config(subscription_tier)
        """))
        conn.commit()
        print("   [OK] Indexes created")

        print()
        print("=" * 60)
        print("[SUCCESS] RATE_LIMIT_CONFIG TABLE CREATED!")
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
    success = create_rate_limit_config_table()
    sys.exit(0 if success else 1)
