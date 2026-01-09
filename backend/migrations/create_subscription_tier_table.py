# -*- coding: utf-8 -*-
"""
Create subscription_tier table
This table stores the different pricing tiers and their configurations
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def create_subscription_tier_table():
    """Create subscription_tier table with all necessary fields"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("CREATING SUBSCRIPTION_TIER TABLE")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("[OK] Connected to database")
        print()

        # Create subscription_tier table
        print("1. Creating subscription_tier table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subscription_tier (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(100) NOT NULL,
                monthly_credits INTEGER NOT NULL DEFAULT 0,
                price_cents INTEGER NOT NULL DEFAULT 0,
                stripe_price_id VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                max_subscribers INTEGER,
                description TEXT,
                features JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        print("   [OK] subscription_tier table created")

        # Create indexes
        print("2. Creating indexes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_subscription_tier_name
            ON subscription_tier(name)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_subscription_tier_active
            ON subscription_tier(is_active)
        """))
        conn.commit()
        print("   [OK] Indexes created")

        print()
        print("=" * 60)
        print("[SUCCESS] SUBSCRIPTION_TIER TABLE CREATED!")
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
    success = create_subscription_tier_table()
    sys.exit(0 if success else 1)
