from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import re
import json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

jobs_bp = Blueprint('jobs_v1', __name__, url_prefix='/api/v1/jobs')

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
    """Fetch job description from LinkedIn with multiple extraction strategies"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        description = None

        # Strategy 1: Try to extract from JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'description' in data:
                        desc = data['description']
                        if isinstance(desc, str) and len(desc) > 100:
                            description = desc
                            logger.info("Extracted from JSON-LD structured data")
                            break
            except (json.JSONDecodeError, AttributeError):
                continue

        # Strategy 2: Try modern LinkedIn class selectors (2024-2025)
        if not description:
            selectors = [
                {'class': 'show-more-less-html__markup'},
                {'class': 'description__text'},
                {'class': 'jobs-description__content'},
                {'class': 'jobs-description-content__text'},
                {'class': 'jobs-box__html-content'},
                {'class': 'jobs-description-content'},
                {'data-testid': 'job-description'},
                {'id': 'job-details'},
                {'class': 'jobs-description__text'},
            ]
            
            for selector in selectors:
                desc_div = soup.find('div', selector)
                if desc_div:
                    text = desc_div.get_text(strip=True, separator='\n')
                    if len(text) > 100:
                        description = text
                        logger.info(f"Extracted using selector: {selector}")
                        break

        # Strategy 3: Try to find in script tags with job data
        if not description:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('description' in script.string.lower() or 'jobDescription' in script.string):
                    try:
                        text = script.string
                        json_start = text.find('{')
                        if json_start != -1:
                            json_end = text.rfind('}') + 1
                            if json_end > json_start:
                                json_str = text[json_start:json_end]
                                data = json.loads(json_str)
                                def find_description(obj):
                                    if isinstance(obj, dict):
                                        for key, value in obj.items():
                                            if 'description' in key.lower() and isinstance(value, str) and len(value) > 100:
                                                return value
                                            if isinstance(value, (dict, list)):
                                                result = find_description(value)
                                                if result:
                                                    return result
                                    elif isinstance(obj, list):
                                        for item in obj:
                                            result = find_description(item)
                                            if result:
                                                return result
                                    return None
                                
                                desc = find_description(data)
                                if desc:
                                    description = desc
                                    logger.info("Extracted from script JSON")
                                    break
                    except (json.JSONDecodeError, ValueError):
                        continue

        # Strategy 4: Fallback - find divs with substantial text content
        if not description:
            all_divs = soup.find_all('div')
            candidates = []
            for div in all_divs:
                text = div.get_text(strip=True)
                keywords = ['responsibilities', 'qualifications', 'requirements', 'experience', 'skills', 'education']
                if len(text) > 300 and any(keyword in text.lower() for keyword in keywords):
                    parent_classes = ' '.join(div.get('class', []))
                    if 'nav' not in parent_classes.lower() and 'footer' not in parent_classes.lower():
                        candidates.append((len(text), text))
            
            if candidates:
                candidates.sort(reverse=True, key=lambda x: x[0])
                description = candidates[0][1]
                logger.info("Extracted using fallback text search")

        if description:
            description = description.strip()
            description = re.sub(r'\n{3,}', '\n\n', description)
            return description

        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching LinkedIn job: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching LinkedIn job: {e}")
        return None

def fetch_indeed_job(url):
    """Fetch job description from Indeed with multiple extraction strategies"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        description = None

        # Strategy 1: Try ID-based selectors (most reliable for Indeed)
        id_selectors = [
            'jobDescriptionText',
            'job-description',
            'jobDescription',
            'jobDescriptionContainer'
        ]
        for selector_id in id_selectors:
            desc_div = soup.find('div', {'id': selector_id})
            if desc_div:
                text = desc_div.get_text(strip=True, separator='\n')
                if len(text) > 100:
                    description = text
                    logger.info(f"Extracted using ID selector: {selector_id}")
                    break

        # Strategy 2: Try class-based selectors
        if not description:
            class_selectors = [
                'jobsearch-jobDescriptionText',
                'job-description',
                'jobsearch-JobComponent-description',
                'jobsearch-jobDescription',
                'jobDescription',
                'jobDescriptionContent',
                'jobsearch-jobDescriptionText-container'
            ]
            for class_name in class_selectors:
                desc_div = soup.find('div', {'class': class_name})
                if desc_div:
                    text = desc_div.get_text(strip=True, separator='\n')
                    if len(text) > 100:
                        description = text
                        logger.info(f"Extracted using class selector: {class_name}")
                        break

        # Strategy 3: Try data-testid selectors
        if not description:
            testid_selectors = [
                'job-description',
                'jobDescriptionText',
                'jobDescription',
                'job-description-container'
            ]
            for testid in testid_selectors:
                desc_div = soup.find('div', {'data-testid': testid})
                if desc_div:
                    text = desc_div.get_text(strip=True, separator='\n')
                    if len(text) > 100:
                        description = text
                        logger.info(f"Extracted using data-testid: {testid}")
                        break

        # Strategy 4: Try to extract from JSON-LD structured data
        if not description:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'description' in data:
                            desc = data['description']
                            if isinstance(desc, str) and len(desc) > 100:
                                description = desc
                                logger.info("Extracted from JSON-LD structured data")
                                break
                except (json.JSONDecodeError, AttributeError):
                    continue

        # Strategy 5: Try to find in script tags with job data
        if not description:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'jobDescriptionText' in script.string:
                    try:
                        text = script.string
                        # Look for window.mosaic data or similar
                        if 'mosaic' in text or 'jobDescription' in text:
                            # Try to extract JSON
                            json_start = text.find('{')
                            if json_start != -1:
                                json_end = text.rfind('}') + 1
                                if json_end > json_start:
                                    json_str = text[json_start:json_end]
                                    data = json.loads(json_str)
                                    # Recursively search for description
                                    def find_description(obj):
                                        if isinstance(obj, dict):
                                            for key, value in obj.items():
                                                if 'description' in key.lower() and isinstance(value, str) and len(value) > 100:
                                                    return value
                                                if isinstance(value, (dict, list)):
                                                    result = find_description(value)
                                                    if result:
                                                        return result
                                        elif isinstance(obj, list):
                                            for item in obj:
                                                result = find_description(item)
                                                if result:
                                                    return result
                                        return None
                                    
                                    desc = find_description(data)
                                    if desc:
                                        description = desc
                                        logger.info("Extracted from script JSON")
                                        break
                    except (json.JSONDecodeError, ValueError):
                        continue

        # Strategy 6: Fallback - find divs with substantial text and job keywords
        if not description:
            all_divs = soup.find_all('div')
            candidates = []
            keywords = ['responsibilities', 'qualifications', 'requirements', 'experience', 'skills', 'education', 'benefits']
            
            for div in all_divs:
                text = div.get_text(strip=True)
                # Check if div has substantial text and job-related keywords
                if len(text) > 200:
                    text_lower = text.lower()
                    keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
                    if keyword_count >= 2:  # At least 2 keywords found
                        # Exclude navigation, footer, header elements
                        parent_id = div.get('id', '')
                        parent_class = ' '.join(div.get('class', []))
                        if 'nav' not in parent_class.lower() and 'footer' not in parent_class.lower() and 'header' not in parent_class.lower():
                            candidates.append((len(text), keyword_count, text))
            
            if candidates:
                # Sort by keyword count first, then by length
                candidates.sort(reverse=True, key=lambda x: (x[1], x[0]))
                description = candidates[0][2]
                logger.info("Extracted using fallback text search")

        if description:
            # Clean up the description
            description = description.strip()
            # Remove excessive whitespace
            description = re.sub(r'\n{3,}', '\n\n', description)
            return description

        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching Indeed job: {e}")
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
