"""
Create admin accounts for project owner and professor
Run this once to create verified admin accounts
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

load_dotenv()

def create_admin_accounts():
    """Create two admin accounts"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set!")
        return False

    print("=" * 60)
    print("CREATING ADMIN ACCOUNTS")
    print("=" * 60)
    print()

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Admin 1: Project Owner (Alhassane Samassekou)
        admin1_email = "alhassane.samassekou@gmail.com"
        admin1_password = "AdminResuMatch2024!"
        admin1_name = "Alhassane Samassekou"

        # Admin 2: Professor (Sitaram Ayyagari)
        admin2_email = "sitaram.ayyagari@project.review"
        admin2_password = "ProfessorReview2024!"
        admin2_name = "Professor Sitaram Ayyagari"

        print("Creating admin accounts...")
        print()

        # Check if accounts already exist
        existing1 = session.execute(
            text('SELECT id FROM users WHERE email = :email'),
            {'email': admin1_email}
        ).fetchone()

        existing2 = session.execute(
            text('SELECT id FROM users WHERE email = :email'),
            {'email': admin2_email}
        ).fetchone()

        created_count = 0

        # Create Admin 1 if doesn't exist
        if existing1:
            print(f"✅ {admin1_email} already exists (ID: {existing1[0]})")
            # Update to ensure admin status
            session.execute(
                text('''
                    UPDATE users
                    SET is_admin = true,
                        email_verified = true,
                        is_active = true,
                        subscription_tier = 'pro',
                        subscription_status = 'active',
                        credits = 1000
                    WHERE email = :email
                '''),
                {'email': admin1_email}
            )
            print(f"   ✅ Updated admin privileges")
        else:
            password_hash = generate_password_hash(admin1_password)
            session.execute(
                text('''
                    INSERT INTO users
                    (email, password_hash, name, auth_provider, is_admin,
                     email_verified, is_active, subscription_tier, subscription_status, credits,
                     created_at, updated_at)
                    VALUES
                    (:email, :password_hash, :name, 'email', true, true, true, 'pro', 'active', 1000,
                     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                '''),
                {
                    'email': admin1_email,
                    'password_hash': password_hash,
                    'name': admin1_name
                }
            )
            created_count += 1
            print(f"✅ Created: {admin1_email}")
            print(f"   Name: {admin1_name}")
            print(f"   Password: {admin1_password}")

        print()

        # Create Admin 2 if doesn't exist
        if existing2:
            print(f"✅ {admin2_email} already exists (ID: {existing2[0]})")
            # Update to ensure admin status
            session.execute(
                text('''
                    UPDATE users
                    SET is_admin = true,
                        email_verified = true,
                        is_active = true,
                        subscription_tier = 'pro',
                        subscription_status = 'active',
                        credits = 1000
                    WHERE email = :email
                '''),
                {'email': admin2_email}
            )
            print(f"   ✅ Updated admin privileges")
        else:
            password_hash = generate_password_hash(admin2_password)
            session.execute(
                text('''
                    INSERT INTO users
                    (email, password_hash, name, auth_provider, is_admin,
                     email_verified, is_active, subscription_tier, subscription_status, credits,
                     created_at, updated_at)
                    VALUES
                    (:email, :password_hash, :name, 'email', true, true, true, 'pro', 'active', 1000,
                     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                '''),
                {
                    'email': admin2_email,
                    'password_hash': password_hash,
                    'name': admin2_name
                }
            )
            created_count += 1
            print(f"✅ Created: {admin2_email}")
            print(f"   Name: {admin2_name}")
            print(f"   Password: {admin2_password}")

        session.commit()
        print()

        # Verify creation
        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print()

        result = session.execute(
            text('''
                SELECT email, name, is_admin, email_verified, subscription_tier, credits
                FROM users
                WHERE email IN (:email1, :email2)
                ORDER BY email
            '''),
            {'email1': admin1_email, 'email2': admin2_email}
        )

        print("Admin accounts:")
        print("-" * 60)
        for row in result:
            email, name, is_admin, verified, tier, credits = row
            admin_badge = "✅ ADMIN" if is_admin else "❌ NOT ADMIN"
            verified_badge = "✅ VERIFIED" if verified else "❌ NOT VERIFIED"
            print(f"{email}")
            print(f"  Name: {name}")
            print(f"  Status: {admin_badge} | {verified_badge}")
            print(f"  Tier: {tier} | Credits: {credits}")
            print()

        print("=" * 60)
        print("ADMIN CREDENTIALS")
        print("=" * 60)
        print()
        print("🔐 Account 1 - Project Owner:")
        print(f"   Email: {admin1_email}")
        print(f"   Password: {admin1_password}")
        print(f"   Name: {admin1_name}")
        print()
        print("🔐 Account 2 - Professor:")
        print(f"   Email: {admin2_email}")
        print(f"   Password: {admin2_password}")
        print(f"   Name: {admin2_name}")
        print()
        print("=" * 60)
        print()
        print("✅ Both accounts have:")
        print("   - Admin access (can access /admin dashboard)")
        print("   - Email verified (no verification needed)")
        print("   - Pro subscription tier")
        print("   - 1000 credits")
        print("   - Full access to all features")
        print()
        print("🔗 Login at: https://resumeanalyzerai.com")
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
    success = create_admin_accounts()
    sys.exit(0 if success else 1)
