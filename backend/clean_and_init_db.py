"""
Clean up orphaned database objects and initialize database from scratch
Handles cases where indexes/constraints exist but tables don't
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

def clean_and_init_database():
    """Clean up orphaned objects and create all tables"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        return False

    print("=" * 60)
    print("DATABASE CLEANUP AND INITIALIZATION")
    print("=" * 60)
    print()

    try:
        # Create database engine
        print("1. Connecting to database...")
        engine = create_engine(database_url)
        connection = engine.connect()
        print("   ✅ Connected successfully")
        print()

        # Check for orphaned objects
        print("2. Checking for orphaned database objects...")
        result = connection.execute(text("""
            SELECT COUNT(*) FROM pg_indexes
            WHERE schemaname = 'public'
        """))
        index_count = result.scalar()

        result = connection.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        table_count = result.scalar()

        print(f"   Tables found: {table_count}")
        print(f"   Indexes found: {index_count}")

        if index_count > 0 and table_count == 0:
            print("   ⚠️  Found orphaned indexes without tables")
            print()

            # Drop all orphaned indexes
            print("3. Cleaning up orphaned indexes...")
            result = connection.execute(text("""
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'public'
            """))
            indexes = result.fetchall()

            for (index_name,) in indexes:
                try:
                    connection.execute(text(f'DROP INDEX IF EXISTS "{index_name}" CASCADE'))
                    print(f"   ✅ Dropped index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  Could not drop {index_name}: {str(e)[:50]}")

            connection.commit()
            print("   ✅ Cleanup complete")
        else:
            print("   ✅ No orphaned objects found")
        print()

        # Import models
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
        print("5. Creating database tables...")
        try:
            db.metadata.create_all(engine, checkfirst=True)
            print("   ✅ Tables created successfully!")
        except Exception as e:
            print(f"   ❌ Error creating tables: {str(e)}")
            # If there's still an error, try dropping everything and recreating
            print()
            print("   Attempting full database reset...")

            # Drop all tables if they exist
            db.metadata.drop_all(engine)
            print("   ✅ Dropped existing objects")

            # Recreate
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

        # List all tables
        print("7. Created tables:")
        print("   " + "-" * 56)
        for table in sorted(tables):
            # Get row count
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
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Check if configurations already exist
            config_count = session.execute(
                text('SELECT COUNT(*) FROM system_configuration')
            ).scalar()

            tier_count = session.execute(
                text('SELECT COUNT(*) FROM subscription_tier')
            ).scalar()

            if config_count == 0:
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
            else:
                print(f"   ✅ System configurations already exist ({config_count} configs)")

            if tier_count == 0:
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
            else:
                print(f"   ✅ Subscription tiers already exist ({tier_count} tiers)")

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
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"📊 Total tables created: {len(tables)}")
        print()
        print("✅ Your database is now ready to use!")
        print("✅ All authentication and features should work now.")
        print()
        print("Next steps:")
        print("1. Test guest session")
        print("2. Test email registration")
        print("3. Test Google OAuth")
        print()
        print("=" * 60)

        connection.close()
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = clean_and_init_database()
    sys.exit(0 if success else 1)
