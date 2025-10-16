import re
from functools import wraps
from flask import request, jsonify
from bleach import clean

# File upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 50000  # Max characters for text inputs

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