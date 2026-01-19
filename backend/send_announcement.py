"""
Script to send feature announcement email to all users.
Run this script from the backend directory with your admin credentials.

Usage:
    python send_announcement.py --mode [test|production]
    python send_announcement.py --mode test --token YOUR_JWT_TOKEN

    test mode: Sends to your admin email only
    production mode: Sends to all active, verified users

For Google OAuth users: Use --token flag with your JWT token from browser DevTools
"""

import sys
import os
import requests
import argparse
from getpass import getpass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_api_url():
    """Get API URL from environment or use default"""
    return os.getenv('BACKEND_URL', 'http://localhost:5000')

def login(api_url, email, password):
    """Login and get JWT token"""
    response = requests.post(
        f"{api_url}/api/v1/auth/login",
        json={"email": email, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def get_user_info(api_url, token):
    """Get user info from token to extract email"""
    response = requests.get(
        f"{api_url}/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('email')
    return None

def send_announcement(api_url, token, test_email=None, send_to_all=False):
    """Send feature announcement email"""
    payload = {}

    if test_email:
        payload['test_email'] = test_email
        print(f"\n📧 Sending test email to: {test_email}")
    elif send_to_all:
        payload['send_to_all'] = True
        print(f"\n📧 Sending to ALL active users...")
    else:
        print("❌ Error: Must specify either test_email or send_to_all")
        return False

    response = requests.post(
        f"{api_url}/api/admin/send-feature-announcement",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"   Sent: {data.get('data', {}).get('sent', 0)}")
        print(f"   Failed: {data.get('data', {}).get('failed', 0)}")

        errors = data.get('data', {}).get('errors', [])
        if errors:
            print(f"\n⚠️  Errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more")

        return True
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(response.text)
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Send feature announcement email to users'
    )
    parser.add_argument(
        '--mode',
        choices=['test', 'production'],
        required=True,
        help='Send mode: test (your email only) or production (all users)'
    )
    parser.add_argument(
        '--api-url',
        help='API URL (default: from BACKEND_URL env or http://localhost:5000)'
    )
    parser.add_argument(
        '--token',
        help='JWT token (for Google OAuth users, get from browser DevTools)'
    )
    parser.add_argument(
        '--email',
        help='Email address for test mode (required if using --token)'
    )

    args = parser.parse_args()

    # Get API URL
    api_url = args.api_url or get_api_url()
    print(f"🌐 API URL: {api_url}")

    # Get authentication
    if args.token:
        # Use provided token (for Google OAuth users)
        token = args.token
        print("\n✅ Using provided JWT token")

        # Get email from token or user input
        if args.email:
            email = args.email
        else:
            # Try to get email from API
            email = get_user_info(api_url, token)
            if not email and args.mode == 'test':
                email = input("Enter your email address for test mode: ")
    else:
        # Traditional email/password login
        print("\n🔐 Admin Login")
        print("(For Google OAuth users, use --token flag instead)")
        email = input("Admin email: ")
        password = getpass("Admin password: ")

        # Login
        print("\n🔄 Logging in...")
        token = login(api_url, email, password)

        if not token:
            print("❌ Authentication failed. Exiting.")
            print("\n💡 Tip: If you login with Google, use --token flag:")
            print("   1. Open your app in browser and login")
            print("   2. Press F12 → Console tab")
            print("   3. Type: localStorage.getItem('access_token')")
            print("   4. Copy the token and run:")
            print(f"      python send_announcement.py --mode test --token YOUR_TOKEN --api-url {api_url}")
            return 1

        print("✅ Logged in successfully")

    # Confirm production send
    if args.mode == 'production':
        print("\n" + "="*60)
        print("⚠️  WARNING: PRODUCTION MODE")
        print("="*60)
        print("This will send emails to ALL active, verified users.")
        print("Make sure you've tested the email first!")
        confirm = input("\nType 'SEND' to confirm: ")

        if confirm != 'SEND':
            print("❌ Cancelled.")
            return 0

        # Send to all users
        success = send_announcement(api_url, token, send_to_all=True)
    else:
        # Test mode - send to admin email
        success = send_announcement(api_url, token, test_email=email)

    return 0 if success else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
