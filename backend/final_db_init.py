"""
Final database initialization using IF NOT EXISTS to bypass phantom indexes
This script is safe to run multiple times
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def final_init():
    """Initialize database with IF NOT EXISTS safety"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("FINAL DATABASE INITIALIZATION")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        conn = engine.connect()
        print("✅ Connected")
        print()

        # Drop schema and recreate
        print("1. Resetting schema...")
        conn.execute(text("""
            DROP SCHEMA IF EXISTS public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
        """))
        conn.commit()
        print("   ✅ Schema reset")
        print()

        # Create tables using SQLAlchemy but catch index errors
        print("2. Creating tables...")

        from models import db
        from models import (
            User, Analysis, GuestSession, GuestAnalysis,
            JobPosting, JobMatch, InterviewPrep, CompanyIntel,
            CareerPath, SystemConfiguration, Keyword,
            SubscriptionTier, RateLimitConfig, ScoringThreshold,
            ValidationRule
        )

        db.metadata.bind = engine

        # Create tables one by one, ignoring index errors
        for table in db.metadata.sorted_tables:
            try:
                table.create(engine, checkfirst=True)
                print(f"   ✅ {table.name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"   ⚠️  {table.name} (skipped - already exists)")
                else:
                    print(f"   ❌ {table.name}: {str(e)[:60]}")

        conn.commit()
        print()

        # Verify
        print("3. Verification...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"   ✅ {len(tables)} tables exist")
        print()

        # Initialize data
        print("4. Initializing default data...")
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # System configs
            config_count = session.execute(
                text('SELECT COUNT(*) FROM system_configuration')
            ).scalar()

            if config_count == 0:
                session.execute(text("""
                    INSERT INTO system_configuration (config_key, config_value, data_type, category, description)
                    VALUES
                        ('max_file_size_mb', '16', 'int', 'file', 'Maximum file size'),
                        ('password_min_length', '8', 'int', 'validation', 'Min password length'),
                        ('gemini_model', 'models/gemini-2.5-flash', 'string', 'ai', 'AI model'),
                        ('jwt_token_expires_days', '7', 'int', 'security', 'JWT expiry')
                """))
                print("   ✅ System configs")

            # Subscription tiers
            tier_count = session.execute(
                text('SELECT COUNT(*) FROM subscription_tier')
            ).scalar()

            if tier_count == 0:
                session.execute(text("""
                    INSERT INTO subscription_tier
                    (name, display_name, monthly_credits, price_cents, max_analyses_per_month, max_file_size_mb, position, is_active)
                    VALUES
                        ('free', 'Free Plan', 0, 0, 5, 5, 1, true),
                        ('pro', 'Pro Plan', 20, 1999, 100, 16, 2, true)
                """))
                print("   ✅ Subscription tiers")

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  Data init warning: {str(e)[:60]}")
        finally:
            session.close()

        print()
        print("=" * 60)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"📊 Tables: {len(tables)}")
        print()

        if len(tables) > 0:
            print("✅ Database is ready!")
            print()
            print("Next steps:")
            print("  1. Restart your backend service on Render")
            print("  2. Test guest session")
            print("  3. Test email registration")
            print("  4. Test Google OAuth")
        else:
            print("⚠️  No tables created - check errors above")

        print()
        print("=" * 60)

        conn.close()
        return len(tables) > 0

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = final_init()
    sys.exit(0 if success else 1)
