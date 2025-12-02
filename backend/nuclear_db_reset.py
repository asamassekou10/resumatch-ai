"""
Ultimate nuclear option: Create tables using raw SQL to bypass phantom index issues
Works around race conditions with running Flask app
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def nuclear_reset():
    """Drop everything and recreate using raw SQL"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        return False

    print("=" * 60)
    print("NUCLEAR DATABASE RESET - RAW SQL METHOD")
    print("=" * 60)
    print()
    print("⚠️  Using raw SQL to bypass phantom index issues")
    print()

    try:
        engine = create_engine(database_url)
        connection = engine.connect()
        print("✅ Connected to database")
        print()

        # Step 1: Drop ALL objects
        print("1. Nuking ALL database objects...")
        connection.execute(text("""
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
        """))
        connection.commit()
        print("   ✅ Database wiped clean")
        print()

        # Step 2: Verify clean slate
        result = connection.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        table_count = result.scalar()
        print(f"2. Verification: {table_count} tables exist")
        print()

        # Step 3: Create tables using checkfirst to ignore existing indexes
        print("3. Creating tables (bypassing index conflicts)...")

        from models import db
        from models import (
            User, Analysis, GuestSession, GuestAnalysis,
            JobPosting, JobMatch, InterviewPrep, CompanyIntel,
            CareerPath, SystemConfiguration, Keyword,
            SubscriptionTier, RateLimitConfig, ScoringThreshold,
            ValidationRule
        )

        db.metadata.bind = engine

        # Try to create all
        try:
            db.metadata.create_all(engine, checkfirst=True)
            print("   ✅ Tables created")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ⚠️  Ignoring duplicate error: {str(e)[:100]}")
                print("   Continuing anyway...")
            else:
                raise
        print()

        # Step 4: Verify tables exist
        print("4. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"   ✅ Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"      - {table}")
        print()

        # Step 5: Initialize configurations
        print("5. Initializing default data...")
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Check if data exists
            config_exists = session.execute(
                text('SELECT COUNT(*) FROM system_configuration')
            ).scalar()

            if config_exists == 0:
                # System configurations
                session.execute(text("""
                    INSERT INTO system_configuration (config_key, config_value, data_type, category, description)
                    VALUES
                        ('max_file_size_mb', '16', 'int', 'file', 'Maximum file size in MB'),
                        ('password_min_length', '8', 'int', 'validation', 'Minimum password length'),
                        ('gemini_model', 'models/gemini-2.5-flash', 'string', 'ai', 'Gemini AI model'),
                        ('jwt_token_expires_days', '7', 'int', 'security', 'JWT token expiration in days')
                """))
                print("   ✅ System configurations created")
            else:
                print(f"   ✅ System configurations exist ({config_exists})")

            tier_exists = session.execute(
                text('SELECT COUNT(*) FROM subscription_tier')
            ).scalar()

            if tier_exists == 0:
                # Subscription tiers
                session.execute(text("""
                    INSERT INTO subscription_tier
                    (name, display_name, monthly_credits, price_cents, max_analyses_per_month, max_file_size_mb, position, is_active)
                    VALUES
                        ('free', 'Free Plan', 0, 0, 5, 5, 1, true),
                        ('pro', 'Pro Plan', 20, 1999, 100, 16, 2, true)
                """))
                print("   ✅ Subscription tiers created")
            else:
                print(f"   ✅ Subscription tiers exist ({tier_exists})")

            session.commit()
            print("   ✅ Default data initialized")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  Warning: {str(e)[:100]}")
        finally:
            session.close()

        print()
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETE!")
        print("=" * 60)
        print()
        print(f"📊 Tables created: {len(tables)}")
        print()
        print("Your database is ready! Test your app now:")
        print("  1. Guest session")
        print("  2. Email registration")
        print("  3. Google OAuth")
        print()
        print("=" * 60)

        connection.close()
        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = nuclear_reset()
    sys.exit(0 if success else 1)
