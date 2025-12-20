#!/usr/bin/env python3
"""
Set Admin Status for User
This script marks a user as admin and gives them premium subscription.
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import User

def set_admin(email):
    """Set a user as admin with premium subscription"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"❌ User not found: {email}")
            return False

        print(f"📧 Found user: {user.email}")
        print(f"   Current status:")
        print(f"   - ID: {user.id}")
        print(f"   - Name: {user.name}")
        print(f"   - Is Admin: {user.is_admin}")
        print(f"   - Subscription Tier: {user.subscription_tier}")
        print(f"   - Subscription Status: {user.subscription_status}")
        print(f"   - Credits: {user.credits}")
        print()

        # Update user to admin with premium subscription
        user.is_admin = True
        user.subscription_tier = 'premium'
        user.subscription_status = 'active'
        user.credits = 10000  # Give plenty of credits
        user.is_active = True
        user.email_verified = True

        db.session.commit()

        print("✅ User updated successfully!")
        print(f"   New status:")
        print(f"   - Is Admin: {user.is_admin}")
        print(f"   - Subscription Tier: {user.subscription_tier}")
        print(f"   - Subscription Status: {user.subscription_status}")
        print(f"   - Credits: {user.credits}")

        return True

def list_all_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.all()

        if not users:
            print("❌ No users found in database")
            return

        print(f"\n📋 Total users: {len(users)}\n")
        print(f"{'ID':<5} {'Email':<35} {'Admin':<7} {'Tier':<10} {'Status':<10} {'Credits':<8}")
        print("="*90)

        for user in users:
            print(f"{user.id:<5} {user.email:<35} {'Yes' if user.is_admin else 'No':<7} {user.subscription_tier:<10} {user.subscription_status:<10} {user.credits:<8}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python set_admin.py <email>          - Set user as admin")
        print("  python set_admin.py --list           - List all users")
        print()
        print("Example:")
        print("  python set_admin.py alhassane.samassekou@gmail.com")
        sys.exit(1)

    if sys.argv[1] == '--list':
        list_all_users()
    else:
        email = sys.argv[1]
        set_admin(email)
