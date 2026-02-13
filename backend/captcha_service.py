"""
CAPTCHA Verification Service
Uses Cloudflare Turnstile (free, unlimited) to prevent bot abuse
"""
import requests
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Cloudflare Turnstile configuration
TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY')
TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
TURNSTILE_ENABLED = os.getenv('TURNSTILE_ENABLED', 'true').lower() == 'true'


def verify_turnstile(token: str, ip_address: str = None) -> Tuple[bool, str]:
    """
    Verify Cloudflare Turnstile CAPTCHA token.

    Args:
        token: The Turnstile response token from the frontend
        ip_address: Optional IP address of the user (for additional verification)

    Returns:
        (success: bool, error_message: str) - (True, "") if verified, (False, reason) if failed
    """
    # Skip CAPTCHA in development if not configured
    if not TURNSTILE_ENABLED:
        logger.info("CAPTCHA verification disabled (TURNSTILE_ENABLED=false)")
        return True, ""

    if not TURNSTILE_SECRET_KEY:
        logger.warning("TURNSTILE_SECRET_KEY not configured - skipping CAPTCHA verification (development mode)")
        # Fail open in development to avoid blocking
        if os.getenv('FLASK_ENV') == 'development':
            return True, ""
        else:
            # Fail closed in production if not configured
            return False, "CAPTCHA system not configured"

    if not token:
        logger.warning("No CAPTCHA token provided")
        return False, "CAPTCHA verification required"

    try:
        # Prepare verification request
        payload = {
            'secret': TURNSTILE_SECRET_KEY,
            'response': token
        }

        # Include IP address if provided (optional but recommended)
        if ip_address:
            payload['remoteip'] = ip_address

        # Make verification request to Cloudflare
        response = requests.post(
            TURNSTILE_VERIFY_URL,
            json=payload,
            timeout=5
        )

        # Check HTTP status
        if response.status_code != 200:
            logger.error(f"CAPTCHA verification HTTP error: {response.status_code}")
            return False, "CAPTCHA verification service error"

        # Parse response
        result = response.json()
        success = result.get('success', False)

        if success:
            logger.info(f"CAPTCHA verified successfully for IP: {ip_address}")
            return True, ""
        else:
            # Log error codes for debugging
            error_codes = result.get('error-codes', [])
            logger.warning(f"CAPTCHA verification failed: {error_codes} (IP: {ip_address})")

            # Provide user-friendly error messages
            if 'timeout-or-duplicate' in error_codes:
                return False, "CAPTCHA expired. Please refresh and try again."
            elif 'invalid-input-response' in error_codes:
                return False, "Invalid CAPTCHA response. Please try again."
            elif 'bad-request' in error_codes:
                return False, "CAPTCHA verification failed. Please try again."
            else:
                return False, "CAPTCHA verification failed. Please try again."

    except requests.Timeout:
        logger.error("CAPTCHA verification timeout")
        # Fail open on timeout to avoid blocking legitimate users
        return True, ""

    except requests.RequestException as e:
        logger.error(f"CAPTCHA verification network error: {e}")
        # Fail open on network error
        return True, ""

    except Exception as e:
        logger.error(f"CAPTCHA verification unexpected error: {e}", exc_info=True)
        # Fail open on unexpected errors
        return True, ""


def is_captcha_required() -> bool:
    """
    Check if CAPTCHA verification is currently required.

    Returns:
        True if CAPTCHA is enabled and configured, False otherwise
    """
    return TURNSTILE_ENABLED and bool(TURNSTILE_SECRET_KEY)


def get_captcha_config() -> dict:
    """
    Get CAPTCHA configuration info for frontend.

    Returns:
        Dictionary with CAPTCHA configuration (safe for frontend)
    """
    return {
        'enabled': is_captcha_required(),
        'site_key': os.getenv('TURNSTILE_SITE_KEY', ''),
        'provider': 'cloudflare-turnstile'
    }
