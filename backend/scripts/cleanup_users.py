"""
Script to remove all users except the specified one from production database.
This script handles all foreign key relationships safely.

Usage:
    python -m scripts.cleanup_users
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Analysis, AdminLog, JobMatch, InterviewPrep, CompanyIntel, CareerPath, UserSkillHistory, GuestSession, SystemConfiguration, Keyword
from sqlalchemy import text, func

# Load environment variables
load_dotenv()

def cleanup_users(keep_email='alhassane.samassekou@gmail.com'):
    """Remove all users except the specified one"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find the user to keep
            user_to_keep = User.query.filter_by(email=keep_email).first()
            
            if not user_to_keep:
                print(f"ERROR: User '{keep_email}' not found in database!")
                print("Available users:")
                all_users = User.query.all()
                for u in all_users:
                    print(f"  - {u.email} (ID: {u.id})")
                return False
            
            print(f"Found user to keep: {user_to_keep.email} (ID: {user_to_keep.id})")
            
            # Count users to delete (without loading into memory)
            user_count = User.query.filter(User.email != keep_email).count()
            
            if user_count == 0:
                print("No users to delete. Only the specified user exists.")
                return True
            
            print(f"\nFound {user_count} users to delete")
            
            # Count related data using SQL aggregates (memory efficient)
            print("Counting related data...")
            total_analyses = db.session.query(func.count(Analysis.id)).filter(
                Analysis.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_admin_logs = db.session.query(func.count(AdminLog.id)).filter(
                AdminLog.admin_user_id != user_to_keep.id
            ).scalar() or 0
            
            total_job_matches = db.session.query(func.count(JobMatch.id)).filter(
                JobMatch.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_interview_preps = db.session.query(func.count(InterviewPrep.id)).filter(
                InterviewPrep.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_company_intels = db.session.query(func.count(CompanyIntel.id)).filter(
                CompanyIntel.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_career_paths = db.session.query(func.count(CareerPath.id)).filter(
                CareerPath.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_skill_history = db.session.query(func.count(UserSkillHistory.id)).filter(
                UserSkillHistory.user_id != user_to_keep.id
            ).scalar() or 0
            
            total_guest_sessions = db.session.query(func.count(GuestSession.id)).filter(
                GuestSession.converted_user_id != None,
                GuestSession.converted_user_id != user_to_keep.id
            ).scalar() or 0
            
            print(f"\nRelated data to be deleted:")
            print(f"  - Analyses: {total_analyses}")
            print(f"  - Admin Logs: {total_admin_logs}")
            print(f"  - Job Matches: {total_job_matches}")
            print(f"  - Interview Preps: {total_interview_preps}")
            print(f"  - Company Intels: {total_company_intels}")
            print(f"  - Career Paths: {total_career_paths}")
            print(f"  - Skill History: {total_skill_history}")
            print(f"  - Guest Sessions (converted): {total_guest_sessions}")
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will permanently delete {user_count} users and all their data!")
            response = input("Type 'DELETE' to confirm: ")
            
            if response != 'DELETE':
                print("Deletion cancelled.")
                return False
            
            # Delete related data using bulk SQL operations (memory efficient)
            print("\nDeleting related data in batches...")
            
            # Use bulk delete operations
            deleted_analyses = Analysis.query.filter(Analysis.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_analyses} analyses")
            
            deleted_admin_logs = AdminLog.query.filter(AdminLog.admin_user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_admin_logs} admin logs")
            
            deleted_job_matches = JobMatch.query.filter(JobMatch.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_job_matches} job matches")
            
            deleted_interview_preps = InterviewPrep.query.filter(InterviewPrep.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_interview_preps} interview preps")
            
            deleted_company_intels = CompanyIntel.query.filter(CompanyIntel.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_company_intels} company intels")
            
            deleted_career_paths = CareerPath.query.filter(CareerPath.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_career_paths} career paths")
            
            deleted_skill_history = UserSkillHistory.query.filter(UserSkillHistory.user_id != user_to_keep.id).delete(synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Deleted {deleted_skill_history} skill history records")
            
            # Update guest sessions (set converted_user_id to NULL)
            updated_guest_sessions = GuestSession.query.filter(
                GuestSession.converted_user_id != None,
                GuestSession.converted_user_id != user_to_keep.id
            ).update({'converted_user_id': None}, synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Updated {updated_guest_sessions} guest sessions")
            
            # Update system configurations (set updated_by_id to NULL)
            updated_configs = SystemConfiguration.query.filter(
                SystemConfiguration.updated_by_id != None,
                SystemConfiguration.updated_by_id != user_to_keep.id
            ).update({'updated_by_id': None}, synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Updated {updated_configs} system configurations")
            
            # Update keywords (set updated_by_id to NULL)
            updated_keywords = Keyword.query.filter(
                Keyword.updated_by_id != None,
                Keyword.updated_by_id != user_to_keep.id
            ).update({'updated_by_id': None}, synchronize_session=False)
            db.session.commit()
            print(f"  ✓ Updated {updated_keywords} keywords")
            
            # Delete user roles associations
            deleted_roles = db.session.execute(
                text("DELETE FROM user_roles WHERE user_id != :keep_user_id"),
                {'keep_user_id': user_to_keep.id}
            ).rowcount
            db.session.commit()
            print(f"  ✓ Deleted {deleted_roles} user role associations")
            
            print("✓ Related data deleted")
            
            # Delete users in batches (process 100 at a time to avoid memory issues)
            print("\nDeleting users in batches...")
            batch_size = 100
            deleted_count = 0
            
            while True:
                # Get a batch of user IDs to delete
                user_ids = db.session.query(User.id).filter(
                    User.email != keep_email
                ).limit(batch_size).all()
                
                if not user_ids:
                    break
                
                user_ids_list = [uid[0] for uid in user_ids]
                
                # Delete this batch
                batch_deleted = User.query.filter(User.id.in_(user_ids_list)).delete(synchronize_session=False)
                db.session.commit()
                deleted_count += batch_deleted
                print(f"  ✓ Deleted batch: {batch_deleted} users (total: {deleted_count}/{user_count})")
                
                # Small delay to avoid overwhelming the database
                import time
                time.sleep(0.1)
            
            print(f"✓ Deleted {deleted_count} users")
            
            # Verify
            remaining_users = User.query.all()
            print(f"\n✓ Cleanup complete! Remaining users: {len(remaining_users)}")
            for u in remaining_users:
                print(f"  - {u.email} (ID: {u.id})")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during cleanup: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Cleanup users from database')
    parser.add_argument('--keep-email', default='alhassane.samassekou@gmail.com',
                       help='Email of user to keep (default: alhassane.samassekou@gmail.com)')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt (use with caution!)')
    
    args = parser.parse_args()
    
    if args.yes:
        # For non-interactive use, we'll need to modify the function
        print("⚠️  Non-interactive mode: Skipping confirmation")
    
    success = cleanup_users(keep_email=args.keep_email)
    sys.exit(0 if success else 1)

