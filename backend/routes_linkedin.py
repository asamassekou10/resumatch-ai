"""
LinkedIn OAuth and Profile Routes

Provides endpoints for:
- LinkedIn OAuth login flow
- LinkedIn profile data retrieval
- LinkedIn integration status
"""

from flask import Blueprint, request, jsonify, redirect, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import secrets
import logging
import os

from linkedin_integration import get_linkedin_client, linkedin_login_required

logger = logging.getLogger(__name__)

# Create blueprint
linkedin_bp = Blueprint('linkedin', __name__, url_prefix='/api/auth/linkedin')


def get_frontend_url(request_host: str = None) -> str:
    """Get the appropriate frontend URL based on request host."""
    if request_host and ('localhost' in request_host or '127.0.0.1' in request_host):
        return os.getenv('FRONTEND_URL_LOCAL', 'http://localhost:3000')
    return os.getenv('FRONTEND_URL', 'http://localhost:3000')


@linkedin_bp.route('/status', methods=['GET'])
def linkedin_status():
    """
    Check LinkedIn integration status.

    Returns whether LinkedIn OAuth is configured and available.
    """
    client = get_linkedin_client()
    return jsonify({
        "configured": client.is_configured(),
        "message": "LinkedIn integration is available" if client.is_configured()
                   else "LinkedIn credentials not configured"
    }), 200


@linkedin_bp.route('/login', methods=['GET'])
@linkedin_login_required
def linkedin_login():
    """
    Initiate LinkedIn OAuth login flow.

    Redirects user to LinkedIn authorization page.
    """
    client = get_linkedin_client()

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['linkedin_oauth_state'] = state

    # Store the request host for callback to use the same redirect URI
    session['linkedin_request_host'] = request.host

    auth_url = client.get_authorization_url(state=state, request_host=request.host)

    logger.info(f"Redirecting user to LinkedIn for authorization (host: {request.host})")
    return redirect(auth_url)


@linkedin_bp.route('/callback', methods=['GET'])
@linkedin_login_required
def linkedin_callback():
    """
    Handle LinkedIn OAuth callback.

    Exchanges authorization code for token and creates/updates user.
    """
    from models import User, db

    # Get authorization code and state
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    # Check for errors
    if error:
        logger.error(f"LinkedIn OAuth error: {error} - {error_description}")
        frontend_url = get_frontend_url(request.host)
        return redirect(f"{frontend_url}/auth/error?message=linkedin_auth_failed")

    # Validate state (CSRF protection)
    stored_state = session.pop('linkedin_oauth_state', None)
    stored_host = session.pop('linkedin_request_host', request.host)
    if not state or state != stored_state:
        logger.warning("LinkedIn OAuth state mismatch - possible CSRF attempt")
        frontend_url = get_frontend_url(stored_host)
        return redirect(f"{frontend_url}/auth/error?message=oauth_state_mismatch")

    try:
        client = get_linkedin_client()

        # Exchange code for token using the same host as the login request
        token_data = client.exchange_code_for_token(code, request_host=stored_host)
        access_token = token_data.get('access_token')

        if not access_token:
            raise ValueError("No access token received from LinkedIn")

        # Get user profile
        profile = client.get_user_profile(access_token)

        # Find or create user
        linkedin_id = profile.get('linkedin_id')
        email = profile.get('email')

        if not email:
            raise ValueError("Email not available from LinkedIn profile")

        # Check if user exists
        user = User.query.filter(
            (User.email == email) |
            (User.google_id == linkedin_id)  # Reuse google_id field for LinkedIn
        ).first()

        if user:
            # Update existing user with LinkedIn info
            user.google_id = linkedin_id  # Store LinkedIn ID
            user.auth_provider = 'linkedin'
            user.last_login = datetime.utcnow()
            if profile.get('name'):
                user.name = profile.get('name')
            if profile.get('picture'):
                user.profile_picture = profile.get('picture')
            user.email_verified = profile.get('email_verified', True)
            logger.info(f"Existing user logged in via LinkedIn: {email}")
        else:
            # Create new user
            user = User(
                email=email,
                name=profile.get('name') or email.split('@')[0],
                google_id=linkedin_id,
                profile_picture=profile.get('picture'),
                auth_provider='linkedin',
                email_verified=profile.get('email_verified', True),
                last_login=datetime.utcnow()
            )
            db.session.add(user)
            logger.info(f"New user created via LinkedIn: {email}")

        db.session.commit()

        # Create JWT token
        jwt_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7)
        )

        # Redirect to frontend with token
        frontend_url = get_frontend_url(stored_host)
        return redirect(f"{frontend_url}/auth/callback?token={jwt_token}&provider=linkedin")

    except Exception as e:
        logger.error(f"LinkedIn OAuth callback error: {str(e)}")
        frontend_url = get_frontend_url(stored_host)
        return redirect(f"{frontend_url}/auth/error?message=linkedin_auth_failed")


@linkedin_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_linkedin_profile():
    """
    Get current user's LinkedIn profile data (if linked).

    Returns profile information stored from LinkedIn OAuth.
    """
    from models import User

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.auth_provider != 'linkedin':
        return jsonify({
            "linked": False,
            "message": "Account not linked to LinkedIn"
        }), 200

    return jsonify({
        "linked": True,
        "profile": {
            "name": user.name,
            "email": user.email,
            "picture": user.profile_picture,
            "linkedin_id": user.google_id,
            "auth_provider": user.auth_provider
        }
    }), 200


@linkedin_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect_linkedin():
    """
    Disconnect LinkedIn from user account.

    Removes LinkedIn-specific data but keeps the account.
    """
    from models import User, db

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.auth_provider != 'linkedin':
        return jsonify({"error": "Account not linked to LinkedIn"}), 400

    # Can only disconnect if user has a password set
    if not user.password_hash:
        return jsonify({
            "error": "Cannot disconnect LinkedIn - no password set",
            "message": "Please set a password before disconnecting LinkedIn"
        }), 400

    # Remove LinkedIn-specific data
    user.google_id = None
    user.auth_provider = 'email'
    db.session.commit()

    logger.info(f"User {user.email} disconnected LinkedIn")

    return jsonify({
        "success": True,
        "message": "LinkedIn disconnected successfully"
    }), 200
