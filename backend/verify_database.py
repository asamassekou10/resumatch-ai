"""
Verify database status and tables
Run this script to check if database initialization succeeded
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up app context
from app import app, db

def verify_database():
    """Verify database connection and list all tables with row counts"""
    with app.app_context():
        try:
            print("=" * 60)
            print("DATABASE VERIFICATION REPORT")
            print("=" * 60)
            print()

            # Test database connection
            from sqlalchemy import text, inspect
            print("1. Testing database connection...")
            try:
                db.session.execute(text('SELECT 1'))
                print("   ✅ Database connection: SUCCESS")
            except Exception as e:
                print(f"   ❌ Database connection: FAILED - {str(e)}")
                return False

            print()

            # Get all tables
            print("2. Checking database tables...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if not tables:
                print("   ❌ No tables found in database!")
                print()
                print("   ACTION REQUIRED: Run init_database.py to create tables")
                return False

            print(f"   ✅ Found {len(tables)} tables")
            print()

            # Expected tables
            expected_tables = [
                'users',
                'analyses',
                'guest_session',
                'guest_analyses',
                'job_postings',
                'job_matches',
                'interview_prep',
                'company_intel',
                'career_paths',
                'system_configuration',
                'keywords'
            ]

            missing_tables = [t for t in expected_tables if t not in tables]
            if missing_tables:
                print("   ⚠️  Missing tables:")
                for table in missing_tables:
                    print(f"      - {table}")
                print()

            # Get row counts for each table
            print("3. Table status and row counts:")
            print("   " + "-" * 56)
            print(f"   {'Table Name':<30} {'Row Count':>10} {'Status':<15}")
            print("   " + "-" * 56)

            table_data = []
            for table in sorted(tables):
                try:
                    result = db.session.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.scalar()
                    status = "✅ OK" if count >= 0 else "❌ ERROR"
                    table_data.append((table, count, status))
                    print(f"   {table:<30} {count:>10} {status:<15}")
                except Exception as e:
                    print(f"   {table:<30} {'ERROR':>10} ❌ {str(e)[:20]}")
                    table_data.append((table, 'ERROR', f"❌ {str(e)[:20]}"))

            print("   " + "-" * 56)
            print()

            # Check for admin users
            print("4. Checking for users...")
            try:
                result = db.session.execute(text('SELECT COUNT(*) FROM users'))
                user_count = result.scalar()
                print(f"   Total users: {user_count}")

                if user_count > 0:
                    result = db.session.execute(text('SELECT COUNT(*) FROM users WHERE is_admin = TRUE'))
                    admin_count = result.scalar()
                    print(f"   Admin users: {admin_count}")

                    result = db.session.execute(text('SELECT email, auth_provider, is_admin, email_verified FROM users LIMIT 5'))
                    users = result.fetchall()
                    print()
                    print("   Recent users:")
                    for user in users:
                        email, provider, is_admin, verified = user
                        admin_badge = " [ADMIN]" if is_admin else ""
                        verified_badge = " ✅" if verified else " ⚠️ unverified"
                        print(f"      - {email} ({provider}){admin_badge}{verified_badge}")
                else:
                    print("   ⚠️  No users found in database")
                    print("   This is normal for a fresh installation")
            except Exception as e:
                print(f"   ❌ Error checking users: {str(e)}")

            print()

            # Summary
            print("=" * 60)
            print("SUMMARY")
            print("=" * 60)

            if len(tables) == len(expected_tables) and not missing_tables:
                print("✅ All expected tables are present")
            else:
                print(f"⚠️  {len(missing_tables)} missing tables out of {len(expected_tables)} expected")

            print(f"✅ Database has {len(tables)} tables")
            total_rows = sum(t[1] for t in table_data if isinstance(t[1], int))
            print(f"✅ Database contains {total_rows} total rows")

            print()
            print("=" * 60)
            print()

            return True

        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = verify_database()
    sys.exit(0 if success else 1)
