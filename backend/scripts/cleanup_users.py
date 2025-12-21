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
from models import db, User, Analysis, AdminLog, JobMatch, InterviewPrep, CompanyIntel, CareerPath, UserSkillHistory, GuestAnalysis, SystemConfiguration, Keyword
from sqlalchemy import text

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
            
            # Get all other users
            users_to_delete = User.query.filter(User.email != keep_email).all()
            
            if not users_to_delete:
                print("No users to delete. Only the specified user exists.")
                return True
            
            print(f"\nFound {len(users_to_delete)} users to delete:")
            for u in users_to_delete:
                print(f"  - {u.email} (ID: {u.id})")
            
            # Count related data
            total_analyses = 0
            total_admin_logs = 0
            total_job_matches = 0
            total_interview_preps = 0
            total_company_intels = 0
            total_career_paths = 0
            total_skill_history = 0
            total_guest_analyses = 0
            
            for user in users_to_delete:
                total_analyses += Analysis.query.filter_by(user_id=user.id).count()
                total_admin_logs += AdminLog.query.filter_by(admin_user_id=user.id).count()
                total_job_matches += JobMatch.query.filter_by(user_id=user.id).count()
                total_interview_preps += InterviewPrep.query.filter_by(user_id=user.id).count()
                total_company_intels += CompanyIntel.query.filter_by(user_id=user.id).count()
                total_career_paths += CareerPath.query.filter_by(user_id=user.id).count()
                total_skill_history += UserSkillHistory.query.filter_by(user_id=user.id).count()
                total_guest_analyses += GuestAnalysis.query.filter_by(converted_user_id=user.id).count()
            
            print(f"\nRelated data to be deleted:")
            print(f"  - Analyses: {total_analyses}")
            print(f"  - Admin Logs: {total_admin_logs}")
            print(f"  - Job Matches: {total_job_matches}")
            print(f"  - Interview Preps: {total_interview_preps}")
            print(f"  - Company Intels: {total_company_intels}")
            print(f"  - Career Paths: {total_career_paths}")
            print(f"  - Skill History: {total_skill_history}")
            print(f"  - Guest Analyses (converted): {total_guest_analyses}")
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will permanently delete {len(users_to_delete)} users and all their data!")
            response = input("Type 'DELETE' to confirm: ")
            
            if response != 'DELETE':
                print("Deletion cancelled.")
                return False
            
            # Delete related data first (some may cascade, but being explicit)
            print("\nDeleting related data...")
            
            for user in users_to_delete:
                # Delete analyses (should cascade, but being explicit)
                Analysis.query.filter_by(user_id=user.id).delete()
                
                # Delete admin logs
                AdminLog.query.filter_by(admin_user_id=user.id).delete()
                
                # Delete job matches
                JobMatch.query.filter_by(user_id=user.id).delete()
                
                # Delete interview preps
                InterviewPrep.query.filter_by(user_id=user.id).delete()
                
                # Delete company intels
                CompanyIntel.query.filter_by(user_id=user.id).delete()
                
                # Delete career paths
                CareerPath.query.filter_by(user_id=user.id).delete()
                
                # Delete skill history
                UserSkillHistory.query.filter_by(user_id=user.id).delete()
                
                # Update guest analyses (set converted_user_id to NULL)
                GuestAnalysis.query.filter_by(converted_user_id=user.id).update({'converted_user_id': None})
                
                # Update system configurations (set updated_by_id to NULL)
                SystemConfiguration.query.filter_by(updated_by_id=user.id).update({'updated_by_id': None})
                
                # Update keywords (set updated_by_id to NULL)
                Keyword.query.filter_by(updated_by_id=user.id).update({'updated_by_id': None})
                
                # Delete user roles associations
                db.session.execute(
                    text("DELETE FROM user_roles WHERE user_id = :user_id"),
                    {'user_id': user.id}
                )
            
            # Commit related data deletions
            db.session.commit()
            print("✓ Related data deleted")
            
            # Delete users
            print("\nDeleting users...")
            for user in users_to_delete:
                db.session.delete(user)
            
            db.session.commit()
            print(f"✓ Deleted {len(users_to_delete)} users")
            
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

