"""
Update admin passwords with bcrypt hashing
The login endpoint uses bcrypt, so passwords must be hashed with bcrypt
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt

load_dotenv()

def update_admin_passwords():
    """Update admin passwords with bcrypt hashing"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set!")
        return False

    # Fix postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print("=" * 60)
    print("UPDATING ADMIN PASSWORDS WITH BCRYPT")
    print("=" * 60)
    print()

    try:
        # Initialize bcrypt
        bcrypt = Bcrypt()

        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Admin 1: Project Owner
        admin1_email = "alhassane.samassekou@gmail.com"
        admin1_password = "AdminResuMatch2024!"

        # Admin 2: Professor
        admin2_email = "sitaram.ayyagari@project.review"
        admin2_password = "ProfessorReview2024!"

        # Hash passwords with bcrypt
        print("Hashing passwords with bcrypt...")
        admin1_hash = bcrypt.generate_password_hash(admin1_password).decode('utf-8')
        admin2_hash = bcrypt.generate_password_hash(admin2_password).decode('utf-8')

        print(f"✅ Admin 1 password hashed")
        print(f"✅ Admin 2 password hashed")
        print()

        # Update passwords
        print("Updating passwords in database...")

        result1 = session.execute(
            text('''
                UPDATE users
                SET password_hash = :password_hash,
                    auth_provider = 'email',
                    is_admin = true,
                    email_verified = true,
                    is_active = true,
                    subscription_tier = 'pro',
                    subscription_status = 'active',
                    credits = 1000
                WHERE email = :email
            '''),
            {
                'email': admin1_email,
                'password_hash': admin1_hash
            }
        )

        result2 = session.execute(
            text('''
                UPDATE users
                SET password_hash = :password_hash,
                    auth_provider = 'email',
                    is_admin = true,
                    email_verified = true,
                    is_active = true,
                    subscription_tier = 'pro',
                    subscription_status = 'active',
                    credits = 1000
                WHERE email = :email
            '''),
            {
                'email': admin2_email,
                'password_hash': admin2_hash
            }
        )

        session.commit()

        print(f"✅ Updated password for: {admin1_email}")
        print(f"✅ Updated password for: {admin2_email}")
        print()

        # Verify
        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print()

        result = session.execute(
            text('''
                SELECT email, name, is_admin, email_verified, auth_provider,
                       subscription_tier, credits, password_hash IS NOT NULL as has_password
                FROM users
                WHERE email IN (:email1, :email2)
                ORDER BY email
            '''),
            {'email1': admin1_email, 'email2': admin2_email}
        )

        print("Admin accounts:")
        print("-" * 60)
        for row in result:
            email, name, is_admin, verified, auth_provider, tier, credits, has_password = row
            admin_badge = "✅ ADMIN" if is_admin else "❌ NOT ADMIN"
            verified_badge = "✅ VERIFIED" if verified else "❌ NOT VERIFIED"
            password_badge = "✅ HAS PASSWORD" if has_password else "❌ NO PASSWORD"
            print(f"{email}")
            print(f"  Name: {name}")
            print(f"  Status: {admin_badge} | {verified_badge} | {password_badge}")
            print(f"  Auth Provider: {auth_provider}")
            print(f"  Tier: {tier} | Credits: {credits}")
            print()

        print("=" * 60)
        print("ADMIN CREDENTIALS")
        print("=" * 60)
        print()
        print("🔐 Account 1 - Project Owner:")
        print(f"   Email: {admin1_email}")
        print(f"   Password: {admin1_password}")
        print()
        print("🔐 Account 2 - Professor:")
        print(f"   Email: {admin2_email}")
        print(f"   Password: {admin2_password}")
        print()
        print("=" * 60)
        print()
        print("✅ Passwords updated with bcrypt hashing!")
        print("   You can now login at: https://resumeanalyzerai.com")
        print()
        print("=" * 60)

        session.close()
        return True

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_admin_passwords()
    sys.exit(0 if success else 1)
