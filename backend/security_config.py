import re
import logging
import time
from functools import wraps
from flask import request, jsonify, g
from bleach import clean

logger = logging.getLogger(__name__)

# File upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 50000  # Max characters for text inputs

# Request validation settings
MAX_JSON_SIZE = 1 * 1024 * 1024  # 1MB max JSON payload
MAX_URL_LENGTH = 2048  # Max URL length
BLOCKED_USER_AGENTS = ['sqlmap', 'nikto', 'nmap', 'masscan']  # Known scanning tools

def validate_email(email):
    """Validate email format"""
    if not email or len(email) > 254:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    Returns: (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password is too long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_text_input(text, max_length=MAX_TEXT_LENGTH):
    """Sanitize and validate text input"""
    if not text:
        return ""
    # Remove HTML tags and dangerous content
    sanitized = clean(text, tags=[], strip=True)
    # Limit length
    return sanitized[:max_length]

def validate_file_upload(file):
    """
    Validate uploaded file
    Returns: (is_valid: bool, error_message: str)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "Invalid filename"
    
    # Check extension
    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
    
    if file_size == 0:
        return False, "File is empty"

    return True, ""


def validate_json_request(f):
    """
    Decorator to validate JSON request payload size and content type
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check content length for JSON requests
        if request.content_type and 'application/json' in request.content_type:
            content_length = request.content_length or 0
            if content_length > MAX_JSON_SIZE:
                logger.warning(f"Request rejected - JSON payload too large: {content_length} bytes")
                return jsonify({'error': 'Request payload too large'}), 413
        return f(*args, **kwargs)
    return decorated_function


def block_suspicious_requests(f):
    """
    Decorator to block requests from known scanning tools
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_agent = request.headers.get('User-Agent', '').lower()

        # Block known scanning tools
        for blocked in BLOCKED_USER_AGENTS:
            if blocked in user_agent:
                logger.warning(f"Blocked suspicious request from User-Agent: {user_agent}")
                return jsonify({'error': 'Request blocked'}), 403

        # Block excessively long URLs (potential attack)
        if len(request.url) > MAX_URL_LENGTH:
            logger.warning(f"Blocked request with URL length: {len(request.url)}")
            return jsonify({'error': 'Invalid request'}), 400

        return f(*args, **kwargs)
    return decorated_function


class RequestLogger:
    """
    Middleware for logging requests and performance metrics
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """Record request start time"""
        g.request_start_time = time.time()

    def after_request(self, response):
        """Log request completion with timing"""
        # Skip logging for health checks and static files
        if request.path in ['/api/health', '/health', '/favicon.ico']:
            return response

        # Calculate request duration
        duration = time.time() - getattr(g, 'request_start_time', time.time())
        duration_ms = round(duration * 1000, 2)

        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} - "
                f"{response.status_code} - {duration_ms}ms"
            )

        # Log all non-2xx responses
        if response.status_code >= 400:
            logger.info(
                f"REQUEST: {request.method} {request.path} - "
                f"{response.status_code} - {duration_ms}ms - "
                f"IP: {request.remote_addr}"
            )

        # Add timing header for debugging
        response.headers['X-Response-Time'] = f"{duration_ms}ms"

        return response


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal and other attacks
    """
    if not filename:
        return None

    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Only allow alphanumeric, dots, dashes, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Prevent hidden files
    if sanitized.startswith('.'):
        sanitized = '_' + sanitized[1:]

    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:250] + ('.' + ext if ext else '')

    return sanitized


def validate_pagination_params(page, per_page, max_per_page=100):
    """
    Validate and sanitize pagination parameters
    Returns: (page, per_page) with safe values
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = min(max(1, int(per_page)), max_per_page)
    except (TypeError, ValueError):
        per_page = 20

    return page, per_page


def rate_limit_key_func():
    """
    Generate rate limit key based on user identity or IP
    Prioritizes authenticated user ID over IP for more accurate limiting
    """
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            return f"user:{identity}"
    except Exception:
        pass

    # Fall back to IP address
    return f"ip:{request.remote_addr}"