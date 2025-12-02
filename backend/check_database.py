"""
Lightweight database verification script
Connects directly to PostgreSQL without loading Flask app or AI models
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv()

def check_database():
    """Check database connection and tables without loading Flask app"""

    # Get database URL
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        return False

    print("=" * 60)
    print("LIGHTWEIGHT DATABASE CHECK")
    print("=" * 60)
    print()

    try:
        # Create direct database connection
        print("1. Connecting to database...")
        engine = create_engine(database_url)
        connection = engine.connect()
        print("   ✅ Database connection: SUCCESS")
        print()

        # Test simple query
        print("2. Testing database query...")
        result = connection.execute(text('SELECT 1'))
        print("   ✅ Query execution: SUCCESS")
        print()

        # Get all tables
        print("3. Listing tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print("   ❌ NO TABLES FOUND!")
            print()
            print("   ACTION REQUIRED:")
            print("   Run: python backend/init_database.py")
            print()
            connection.close()
            return False

        print(f"   ✅ Found {len(tables)} tables")
        print()

        # Expected tables
        expected_tables = [
            'users', 'analyses', 'guest_session', 'guest_analyses',
            'job_postings', 'job_matches', 'interview_prep',
            'company_intel', 'career_paths', 'system_configuration',
            'keywords'
        ]

        print("4. Checking expected tables:")
        print("   " + "-" * 56)
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (MISSING)")
        print("   " + "-" * 56)
        print()

        # Count rows in key tables
        print("5. Row counts:")
        print("   " + "-" * 56)
        for table in ['users', 'analyses', 'guest_session', 'job_postings']:
            if table in tables:
                try:
                    result = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.scalar()
                    print(f"   {table:<30} {count:>10} rows")
                except Exception as e:
                    print(f"   {table:<30} ERROR: {str(e)[:30]}")
        print("   " + "-" * 56)
        print()

        # Check for users
        if 'users' in tables:
            print("6. Checking users:")
            try:
                result = connection.execute(text('SELECT COUNT(*) FROM users'))
                user_count = result.scalar()
                print(f"   Total users: {user_count}")

                if user_count > 0:
                    result = connection.execute(text(
                        'SELECT email, auth_provider, is_admin, email_verified '
                        'FROM users LIMIT 5'
                    ))
                    users = result.fetchall()
                    print("   First 5 users:")
                    for user in users:
                        email, provider, is_admin, verified = user
                        admin_badge = " [ADMIN]" if is_admin else ""
                        verified_badge = " ✅" if verified else " ⚠️"
                        print(f"      - {email} ({provider}){admin_badge}{verified_badge}")
                else:
                    print("   ⚠️  No users found")
                    print("   This is normal for a fresh installation")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        print()

        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)

        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print(f"⚠️  Missing {len(missing)} tables: {', '.join(missing)}")
            print()
            print("ACTION REQUIRED:")
            print("Run: python backend/init_database.py")
        else:
            print("✅ All expected tables present")
            print(f"✅ Database has {len(tables)} tables")
            print("✅ Database is ready!")

        print("=" * 60)
        print()

        connection.close()
        return len(missing) == 0

    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_database()
    sys.exit(0 if success else 1)
