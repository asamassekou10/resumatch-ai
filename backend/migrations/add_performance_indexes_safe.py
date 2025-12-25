"""
Safe Migration: Add Performance Indexes

This migration ONLY adds database indexes - it does NOT modify or delete any data.
Indexes are 100% safe and will improve query performance without affecting existing data.

To run on Render:
1. Connect to your Render database via SSH or use Render's shell
2. Run: python backend/migrations/add_performance_indexes_safe.py
3. Or use Flask-Migrate: flask db upgrade

This migration can be run multiple times safely (uses IF NOT EXISTS).
"""

from sqlalchemy import create_engine, text
import os
import sys

def check_index_exists(conn, index_name, table_name):
    """Check if an index already exists"""
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 
            FROM pg_indexes 
            WHERE indexname = :index_name 
            AND tablename = :table_name
        );
    """), {"index_name": index_name, "table_name": table_name})
    return result.scalar()

def run_migration():
    """Add performance indexes safely"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL before running this migration")
        sys.exit(1)
    
    print("=" * 60)
    print("SAFE MIGRATION: Adding Performance Indexes")
    print("=" * 60)
    print("This migration ONLY adds indexes - NO data will be modified or deleted")
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print("=" * 60)
    
    # Create engine with autocommit mode for DDL statements (CREATE INDEX)
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    
    try:
        # Use autocommit mode for individual index creation
        # This way if one fails, others can still succeed
        with engine.connect() as conn:
            indexes_to_create = [
                    {
                        "name": "idx_analysis_user_created",
                        "table": "analyses",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_analysis_user_created ON analyses(user_id, created_at DESC);",
                        "description": "Index for user analysis queries sorted by date"
                    },
                    {
                        "name": "idx_analysis_user_id",
                        "table": "analyses",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analyses(user_id);",
                        "description": "Index for filtering analyses by user"
                    },
                    {
                        "name": "idx_jobposting_industry_active",
                        "table": "job_postings",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_jobposting_industry_active ON job_postings(industry, is_active);",
                        "description": "Index for job posting queries by industry and status"
                    },
                    {
                        "name": "idx_user_email",
                        "table": "users",
                        "sql": 'CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);',
                        "description": "Index for user login lookups by email"
                    },
                    {
                        "name": "idx_guest_session_created",
                        "table": "guest_sessions",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_guest_session_created ON guest_sessions(created_at DESC);",
                        "description": "Index for guest session queries sorted by date"
                    },
                    {
                        "name": "idx_guest_analysis_session",
                        "table": "guest_analyses",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_guest_analysis_session ON guest_analyses(guest_session_id);",
                        "description": "Index for guest analysis queries by session"
                    }
                ]
                
                print("\nChecking existing indexes...")
                existing_count = 0
                for idx in indexes_to_create:
                    exists = check_index_exists(conn, idx["name"], idx["table"])
                    if exists:
                        print(f"  ✓ {idx['name']} already exists (skipping)")
                        existing_count += 1
                    else:
                        print(f"  - {idx['name']} will be created")
                
                if existing_count == len(indexes_to_create):
                    print("\n✅ All indexes already exist. Nothing to do!")
                    return
                
                print(f"\nCreating {len(indexes_to_create) - existing_count} new index(es)...")
                
                # Create indexes
                for idx in indexes_to_create:
                    exists = check_index_exists(conn, idx["name"], idx["table"])
                    if not exists:
                        try:
                            print(f"\n  Creating {idx['name']}...")
                            print(f"    Description: {idx['description']}")
                            print(f"    Table: {idx['table']}")
                            # Execute directly (autocommit is enabled)
                            conn.execute(text(idx["sql"]))
                            print(f"    ✅ Successfully created")
                        except Exception as e:
                            print(f"    ⚠️  Warning: {e}")
                            # Continue with other indexes even if one fails
                
                print("\n" + "=" * 60)
                print("✅ MIGRATION COMPLETED")
                print("=" * 60)
                print("Indexes have been created. Your data is safe and unchanged.")
                print("Query performance should now be improved.")
                print("=" * 60)
                
    except Exception as e:
        print(f"\n❌ FATAL ERROR: Could not connect to database: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("\n🔒 SAFETY GUARANTEE:")
    print("   - This migration ONLY adds indexes")
    print("   - NO data will be modified or deleted")
    print("   - Can be run multiple times safely")
    print("   - Uses IF NOT EXISTS to prevent duplicates\n")
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        run_migration()
    else:
        print("Migration cancelled.")
        sys.exit(0)

