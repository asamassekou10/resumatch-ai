from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

jobs_bp = Blueprint('jobs_v1', __name__, url_prefix='/api/v1/jobs')

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day", "20 per hour"]
)

def create_success_response(message: str, data: dict = None, status_code: int = 200):
    """Create standardized success response"""
    response = {
        'status': 'success',
        'message': message
    }
    if data:
        response['data'] = data
    return jsonify(response), status_code

def create_error_response(message: str, status_code: int = 400):
    """Create standardized error response"""
    return jsonify({
        'status': 'error',
        'error': message
    }), status_code

def fetch_linkedin_job(url):
    """Fetch job description from LinkedIn"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find job description
        description_div = soup.find('div', {'class': 'description__text'})
        if not description_div:
            description_div = soup.find('div', {'class': 'show-more-less-html__markup'})

        if description_div:
            return description_div.get_text(strip=True, separator='\n')

        return None
    except Exception as e:
        logger.error(f"Error fetching LinkedIn job: {e}")
        return None

def fetch_indeed_job(url):
    """Fetch job description from Indeed"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try multiple selectors (Indeed changes their HTML frequently)
        description_div = None

        # Try ID-based selectors
        if not description_div:
            description_div = soup.find('div', {'id': 'jobDescriptionText'})

        # Try class-based selectors
        if not description_div:
            description_div = soup.find('div', {'class': 'jobsearch-jobDescriptionText'})
        if not description_div:
            description_div = soup.find('div', {'class': 'job-description'})
        if not description_div:
            description_div = soup.find('div', {'class': 'jobsearch-JobComponent-description'})

        # Try data attribute selectors
        if not description_div:
            description_div = soup.find('div', {'data-testid': 'job-description'})
        if not description_div:
            description_div = soup.find('div', {'data-testid': 'jobDescriptionText'})

        # Try finding any div with job description text
        if not description_div:
            # Look for divs with lots of text that might be the description
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text(strip=True)
                # If div has substantial text (likely a description)
                if len(text) > 200 and 'responsibilities' in text.lower() or 'qualifications' in text.lower() or 'requirements' in text.lower():
                    description_div = div
                    break

        if description_div:
            return description_div.get_text(strip=True, separator='\n')

        return None
    except Exception as e:
        logger.error(f"Error fetching Indeed job: {e}")
        return None

def fetch_glassdoor_job(url):
    """Fetch job description from Glassdoor"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find job description
        description_div = soup.find('div', {'class': 'jobDescriptionContent'})
        if not description_div:
            description_div = soup.find('div', {'class': 'desc'})

        if description_div:
            return description_div.get_text(strip=True, separator='\n')

        return None
    except Exception as e:
        logger.error(f"Error fetching Glassdoor job: {e}")
        return None

def detect_job_board(url):
    """Detect which job board the URL is from"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if 'linkedin.com' in domain:
        return 'linkedin'
    elif 'indeed.com' in domain:
        return 'indeed'
    elif 'glassdoor.com' in domain:
        return 'glassdoor'
    elif 'monster.com' in domain:
        return 'monster'
    elif 'ziprecruiter.com' in domain:
        return 'ziprecruiter'
    else:
        return 'unknown'

@jobs_bp.route('/fetch', methods=['POST'])
@limiter.limit("10 per minute")
def fetch_job_description():
    """
    Fetch job description from a job posting URL

    Supports: LinkedIn, Indeed, Glassdoor

    Request body:
    {
        "url": "https://www.linkedin.com/jobs/view/..."
    }

    Response:
    {
        "status": "success",
        "message": "Job description fetched successfully",
        "data": {
            "description": "Full job description text...",
            "source": "linkedin",
            "url": "original_url"
        }
    }
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            return create_error_response("Job posting URL is required", 400)

        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return create_error_response("Invalid URL format", 400)
        except Exception:
            return create_error_response("Invalid URL format", 400)

        # Detect job board
        job_board = detect_job_board(url)
        logger.info(f"Fetching job from {job_board}: {url}")

        # Fetch description based on job board
        description = None

        if job_board == 'linkedin':
            description = fetch_linkedin_job(url)
        elif job_board == 'indeed':
            description = fetch_indeed_job(url)
        elif job_board == 'glassdoor':
            description = fetch_glassdoor_job(url)
        else:
            return create_error_response(
                f"Unsupported job board. We currently support: LinkedIn, Indeed, and Glassdoor. "
                f"Please copy and paste the job description manually.",
                400
            )

        if not description:
            return create_error_response(
                "Unable to extract job description from this URL. "
                "The page structure may have changed or the URL may be invalid. "
                "Please try copying and pasting the job description manually.",
                400
            )

        logger.info(f"Successfully fetched job description from {job_board}")

        return create_success_response(
            "Job description fetched successfully",
            {
                'description': description,
                'source': job_board,
                'url': url
            }
        )

    except Exception as e:
        logger.error(f"Error fetching job description: {e}")
        return create_error_response(
            "Failed to fetch job description. Please try again or paste the description manually.",
            500
        )
