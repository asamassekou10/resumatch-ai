"""
Lightweight database initialization - creates tables without loading Flask app
Bypasses AI model loading for faster execution in production environments
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

def init_database_direct():
    """Create all database tables without loading Flask app"""

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        return False

    print("=" * 60)
    print("LIGHTWEIGHT DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    print("⚡ Bypassing Flask app and AI models for fast initialization")
    print()

    try:
        # Create database engine
        print("1. Connecting to database...")
        engine = create_engine(database_url)
        connection = engine.connect()
        print("   ✅ Connected successfully")
        print()

        # Import models (this defines the table schemas)
        print("2. Loading database models...")
        # Import db and all models - this registers the table definitions
        from models import db

        # Import all model classes to ensure they're registered
        from models import (
            User, Analysis, GuestSession, GuestAnalysis,
            JobPosting, JobMatch, InterviewPrep, CompanyIntel,
            CareerPath, SystemConfiguration, Keyword,
            SubscriptionTier, RateLimitConfig, ScoringThreshold,
            ValidationRule
        )
        print("   ✅ Models loaded")
        print()

        # Set the database engine for the models
        db.metadata.bind = engine

        # Create all tables
        print("3. Creating database tables...")
        db.metadata.create_all(engine)
        print("   ✅ Tables created successfully!")
        print()

        # Verify tables were created
        print("4. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print("   ❌ No tables found after creation!")
            return False

        print(f"   ✅ Verified {len(tables)} tables created")
        print()

        # List all tables
        print("5. Created tables:")
        print("   " + "-" * 56)
        for table in sorted(tables):
            print(f"   ✅ {table}")
        print("   " + "-" * 56)
        print()

        # Initialize default configurations
        print("6. Initializing default configurations...")
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
        print("Your database is now ready to use!")
        print("All authentication and features should work now.")
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
    success = init_database_direct()
    sys.exit(0 if success else 1)
