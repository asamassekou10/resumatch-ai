"""
Nuclear option: Force reset database by dropping ALL objects
Uses raw SQL to bypass SQLAlchemy issues with phantom indexes
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def force_reset_database():
    """Force drop everything and recreate from scratch"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        return False

    print("=" * 60)
    print("FORCE DATABASE RESET")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DROP ALL database objects!")
    print()

    try:
        # Create database engine
        print("1. Connecting to database...")
        engine = create_engine(database_url)
        connection = engine.connect()
        print("   ✅ Connected successfully")
        print()

        # Force drop ALL objects in public schema
        print("2. Force dropping ALL database objects...")

        # Drop all tables with CASCADE to remove dependencies
        print("   - Dropping all tables...")
        result = connection.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        connection.commit()
        print("   ✅ All tables dropped")

        # Drop all indexes
        print("   - Dropping all indexes...")
        result = connection.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT indexname FROM pg_indexes WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.indexname) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        connection.commit()
        print("   ✅ All indexes dropped")

        # Drop all sequences
        print("   - Dropping all sequences...")
        result = connection.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
                    EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        connection.commit()
        print("   ✅ All sequences dropped")

        # Drop all views
        print("   - Dropping all views...")
        result = connection.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = 'public') LOOP
                    EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        connection.commit()
        print("   ✅ All views dropped")

        print()
        print("   ✅ Database completely cleaned!")
        print()

        # Verify clean state
        print("3. Verifying database is empty...")
        result = connection.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        table_count = result.scalar()

        result = connection.execute(text("""
            SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'
        """))
        index_count = result.scalar()

        print(f"   Tables: {table_count}")
        print(f"   Indexes: {index_count}")

        if table_count == 0 and index_count == 0:
            print("   ✅ Database is completely empty")
        else:
            print("   ⚠️  Some objects still remain")
        print()

        # Now create fresh tables
        print("4. Loading database models...")
        from models import db
        from models import (
            User, Analysis, GuestSession, GuestAnalysis,
            JobPosting, JobMatch, InterviewPrep, CompanyIntel,
            CareerPath, SystemConfiguration, Keyword,
            SubscriptionTier, RateLimitConfig, ScoringThreshold,
            ValidationRule
        )
        print("   ✅ Models loaded")
        print()

        # Set the database engine
        db.metadata.bind = engine

        # Create all tables
        print("5. Creating fresh database tables...")
        db.metadata.create_all(engine)
        print("   ✅ Tables created successfully!")
        print()

        # Verify tables were created
        print("6. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print("   ❌ No tables found after creation!")
            return False

        print(f"   ✅ Verified {len(tables)} tables created")
        print()

        # List all tables with row counts
        print("7. Created tables:")
        print("   " + "-" * 56)
        for table in sorted(tables):
            try:
                result = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                count = result.scalar()
                print(f"   ✅ {table:<35} ({count} rows)")
            except:
                print(f"   ✅ {table}")
        print("   " + "-" * 56)
        print()

        # Initialize default configurations
        print("8. Initializing default configurations...")
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # System configurations
            print("   - Creating system configurations...")
            configs = [
                ('max_file_size_mb', '16', 'int', 'file', 'Maximum file size in MB'),
                ('password_min_length', '8', 'int', 'validation', 'Minimum password length'),
                ('gemini_model', 'models/gemini-2.5-flash', 'string', 'ai', 'Gemini AI model'),
                ('jwt_token_expires_days', '7', 'int', 'security', 'JWT token expiration in days'),
            ]

            for config_key, config_value, data_type, category, description in configs:
                session.execute(text(
                    'INSERT INTO system_configuration '
                    '(config_key, config_value, data_type, category, description) '
                    'VALUES (:key, :value, :type, :cat, :desc)'
                ), {
                    'key': config_key,
                    'value': config_value,
                    'type': data_type,
                    'cat': category,
                    'desc': description
                })
            print("   ✅ System configurations created")

            # Subscription tiers
            print("   - Creating subscription tiers...")
            tiers = [
                ('free', 'Free Plan', 0, 0, 5, 5, 1, True),
                ('pro', 'Pro Plan', 20, 1999, 100, 16, 2, True),
            ]

            for name, display_name, monthly_credits, price_cents, max_analyses, max_file_size, position, is_active in tiers:
                session.execute(text(
                    'INSERT INTO subscription_tier '
                    '(name, display_name, monthly_credits, price_cents, max_analyses_per_month, '
                    'max_file_size_mb, position, is_active) '
                    'VALUES (:name, :display, :credits, :price, :analyses, :filesize, :pos, :active)'
                ), {
                    'name': name,
                    'display': display_name,
                    'credits': monthly_credits,
                    'price': price_cents,
                    'analyses': max_analyses,
                    'filesize': max_file_size,
                    'pos': position,
                    'active': is_active
                })
            print("   ✅ Subscription tiers created")

            session.commit()
            print("   ✅ Default configurations initialized")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️  Warning: Could not initialize configs: {str(e)}")
        finally:
            session.close()

        print()

        # Final summary
        print("=" * 60)
        print("✅ DATABASE RESET COMPLETE!")
        print("=" * 60)
        print()
        print(f"📊 Total tables created: {len(tables)}")
        print()
        print("✅ Your database is now ready to use!")
        print("✅ All authentication and features should work now.")
        print()
        print("⚠️  Note: All old data has been wiped.")
        print("   You'll need to register new accounts.")
        print()
        print("=" * 60)

        connection.close()
        return True

    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = force_reset_database()
    sys.exit(0 if success else 1)
