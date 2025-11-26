"""
LinkedIn Integration Module

Provides LinkedIn API integration for:
1. OAuth 2.0 Authentication (Login with LinkedIn)
2. Profile Data Extraction (for resume enhancement)
3. Job Recommendations (based on profile)

LinkedIn API Documentation: https://learn.microsoft.com/en-us/linkedin/

Note: LinkedIn's Jobs API requires enterprise partnership. This module uses
the publicly available OAuth and Profile APIs to enhance the resume analyzer.
"""

import os
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class LinkedInClient:
    """
    LinkedIn API Client for OAuth and Profile operations.

    Securely handles LinkedIn API authentication and data retrieval
    using credentials stored in environment variables.
    """

    # LinkedIn API endpoints
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    PROFILE_URL = "https://api.linkedin.com/v2/userinfo"

    # Required OAuth scopes
    SCOPES = [
        "openid",           # Required for OIDC
        "profile",          # Basic profile info
        "email",            # Email address
    ]

    def __init__(self):
        """Initialize LinkedIn client with credentials from environment."""
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        # Support both local and production redirect URIs
        self.redirect_uri_local = os.getenv('LINKEDIN_REDIRECT_URI_LOCAL',
                                            'http://localhost:5000/api/auth/linkedin/callback')
        self.redirect_uri_prod = os.getenv('LINKEDIN_REDIRECT_URI_PROD',
                                           'https://resumatch-backend-7qdb.onrender.com/api/auth/linkedin/callback')
        # Default redirect_uri for backward compatibility
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', self.redirect_uri_local)

        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn credentials not configured - integration disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("LinkedIn integration initialized successfully")

    def get_redirect_uri(self, request_host: str = None) -> str:
        """Get the appropriate redirect URI based on the request host."""
        if request_host:
            if 'localhost' in request_host or '127.0.0.1' in request_host:
                return self.redirect_uri_local
            else:
                return self.redirect_uri_prod
        return self.redirect_uri

    def is_configured(self) -> bool:
        """Check if LinkedIn integration is properly configured."""
        return self.enabled

    def get_authorization_url(self, state: str = None, request_host: str = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection
            request_host: The host from the request to determine redirect URI

        Returns:
            Full authorization URL to redirect user to LinkedIn
        """
        if not self.enabled:
            raise ValueError("LinkedIn integration not configured")

        redirect_uri = self.get_redirect_uri(request_host)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
        }

        if state:
            params["state"] = state

        logger.info(f"Using redirect URI: {redirect_uri}")
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, authorization_code: str, request_host: str = None) -> Dict:
        """
        Exchange authorization code for access token.

        Args:
            authorization_code: Code received from LinkedIn callback
            request_host: The host from the request to determine redirect URI

        Returns:
            Token response containing access_token and expires_in
        """
        if not self.enabled:
            raise ValueError("LinkedIn integration not configured")

        redirect_uri = self.get_redirect_uri(request_host)
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        logger.info(f"Exchanging code with redirect URI: {redirect_uri}")

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            logger.info("Successfully exchanged LinkedIn authorization code for token")
            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange LinkedIn code: {str(e)}")
            raise

    def get_user_profile(self, access_token: str) -> Dict:
        """
        Fetch user profile from LinkedIn.

        Args:
            access_token: Valid LinkedIn access token

        Returns:
            User profile data including name, email, picture
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(
                self.PROFILE_URL,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            profile = response.json()
            logger.info(f"Retrieved LinkedIn profile for user: {profile.get('email', 'unknown')}")

            return {
                "linkedin_id": profile.get("sub"),
                "email": profile.get("email"),
                "name": profile.get("name"),
                "given_name": profile.get("given_name"),
                "family_name": profile.get("family_name"),
                "picture": profile.get("picture"),
                "email_verified": profile.get("email_verified", False),
                "locale": profile.get("locale"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch LinkedIn profile: {str(e)}")
            raise

    def extract_profile_skills(self, profile_data: Dict) -> List[str]:
        """
        Extract skills from LinkedIn profile data.

        Note: Full skills data requires additional API permissions.
        This extracts what's available from basic profile.

        Args:
            profile_data: Profile data from get_user_profile()

        Returns:
            List of extracted skills/keywords
        """
        skills = []

        # Extract from headline if available
        headline = profile_data.get("headline", "")
        if headline:
            # Common skill keywords from headlines
            common_skills = [
                "python", "javascript", "java", "react", "node", "aws",
                "docker", "kubernetes", "sql", "data", "machine learning",
                "devops", "frontend", "backend", "fullstack", "engineer",
                "developer", "architect", "manager", "lead", "senior"
            ]
            headline_lower = headline.lower()
            for skill in common_skills:
                if skill in headline_lower:
                    skills.append(skill)

        return list(set(skills))


def get_linkedin_client() -> LinkedInClient:
    """Get or create LinkedIn client singleton."""
    if not hasattr(get_linkedin_client, '_client'):
        get_linkedin_client._client = LinkedInClient()
    return get_linkedin_client._client


def linkedin_login_required(func):
    """Decorator to check if LinkedIn integration is configured."""
    def wrapper(*args, **kwargs):
        client = get_linkedin_client()
        if not client.is_configured():
            from flask import jsonify
            return jsonify({
                "error": "LinkedIn integration not configured",
                "message": "Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables"
            }), 503
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
