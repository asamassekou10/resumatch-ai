"""Script to create an admin account"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, User, bcrypt
from datetime import datetime

def create_admin_user(email, password, name="Admin"):
    """Create an admin user account"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False

        # Create new admin user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        admin_user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            auth_provider='email',
            is_admin=True,
            is_active=True,
            email_verified=True,
            subscription_tier='pro',
            credits=999999,  # Effectively unlimited credits
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )

        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"✓ Admin user created successfully!")
            print(f"  Email: {email}")
            print(f"  Name: {name}")
            print(f"  ID: {admin_user.id}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating admin user: {str(e)}")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [name]")
        print("Example: python create_admin.py admin@example.com password123 'Admin User'")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "Admin"

    create_admin_user(email, password, name)
