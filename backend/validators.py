import re
import bleach
from flask import request
from werkzeug.utils import secure_filename
from errors import ValidationError, FileProcessingError

# Try to import magic, but handle gracefully if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. File type validation will be limited.")

class FileValidator:
    """File validation utilities"""
    
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain'
    }
    
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def validate_file_upload(file, field_name='file'):
        """Validate uploaded file"""
        if not file:
            raise ValidationError(f"{field_name} is required")
        
        if not file.filename:
            raise ValidationError(f"{field_name} must have a filename")
        
        # Check file extension
        filename = secure_filename(file.filename)
        if not filename or not FileValidator._allowed_file(filename):
            raise ValidationError(
                f"Invalid file type. Allowed types: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > FileValidator.MAX_FILE_SIZE:
            raise ValidationError(f"File too large. Maximum size: {FileValidator.MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Check MIME type (if magic is available)
        if MAGIC_AVAILABLE:
            file_content = file.read(1024)
            file.seek(0)  # Reset to beginning
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                if mime_type not in FileValidator.ALLOWED_MIME_TYPES:
                    raise ValidationError("Invalid file content. Please upload a valid PDF, DOCX, or TXT file")
            except Exception:
                # If magic fails, fall back to extension-based validation
                print("Warning: MIME type detection failed, using extension validation")
        else:
            # If magic is not available, skip MIME type check
            print("Warning: MIME type validation skipped (libmagic not available)")
        
        return True
    
    @staticmethod
    def _allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileValidator.ALLOWED_EXTENSIONS

class TextValidator:
    """Text validation utilities"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            raise ValidationError("Email is required")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        if len(email) > 120:
            raise ValidationError("Email must be less than 120 characters")
        
        return email.lower().strip()
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        if len(password) > 128:
            raise ValidationError("Password must be less than 128 characters")
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
        if password.lower() in weak_passwords:
            raise ValidationError("Password is too common. Please choose a stronger password")
        
        return password
    
    @staticmethod
    def validate_job_description(job_description):
        """Validate job description"""
        if not job_description:
            raise ValidationError("Job description is required")
        
        if len(job_description.strip()) < 50:
            raise ValidationError("Job description must be at least 50 characters long")
        
        if len(job_description) > 10000:
            raise ValidationError("Job description must be less than 10,000 characters")
        
        # Sanitize HTML and script tags
        sanitized = bleach.clean(job_description, strip=True)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_job_title(job_title):
        """Validate job title"""
        if job_title and len(job_title) > 200:
            raise ValidationError("Job title must be less than 200 characters")
        
        if job_title:
            # Sanitize input
            sanitized = bleach.clean(job_title, strip=True)
            return sanitized.strip()
        
        return None
    
    @staticmethod
    def validate_company_name(company_name):
        """Validate company name"""
        if company_name and len(company_name) > 200:
            raise ValidationError("Company name must be less than 200 characters")
        
        if company_name:
            # Sanitize input
            sanitized = bleach.clean(company_name, strip=True)
            return sanitized.strip()
        
        return None
    
    @staticmethod
    def sanitize_text(text, max_length=None):
        """Sanitize and validate general text input"""
        if not text:
            return None
        
        # Remove HTML tags and scripts
        sanitized = bleach.clean(text, strip=True)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Check length if specified
        if max_length and len(sanitized) > max_length:
            raise ValidationError(f"Text must be less than {max_length} characters")
        
        return sanitized

class RequestValidator:
    """Request validation utilities"""
    
    @staticmethod
    def validate_json_request(required_fields=None, optional_fields=None):
        """Validate JSON request data"""
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # Check required fields
        if required_fields:
            for field in required_fields:
                if field not in data:
                    raise ValidationError(f"Missing required field: {field}")
        
        # Filter out unexpected fields
        if optional_fields:
            allowed_fields = set(required_fields or []) | set(optional_fields)
            unexpected_fields = set(data.keys()) - allowed_fields
            if unexpected_fields:
                raise ValidationError(f"Unexpected fields: {', '.join(unexpected_fields)}")
        
        return data
    
    @staticmethod
    def validate_form_request(required_fields=None, optional_fields=None):
        """Validate form request data"""
        data = request.form.to_dict()
        
        # Check required fields
        if required_fields:
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Missing required field: {field}")
        
        # Filter out unexpected fields
        if optional_fields:
            allowed_fields = set(required_fields or []) | set(optional_fields)
            unexpected_fields = set(data.keys()) - allowed_fields
            if unexpected_fields:
                raise ValidationError(f"Unexpected fields: {', '.join(unexpected_fields)}")
        
        return data

class RateLimitValidator:
    """Rate limiting validation"""
    
    @staticmethod
    def validate_analysis_rate_limit(user_id, analyses_count, max_analyses_per_day=50):
        """Validate user hasn't exceeded analysis rate limit"""
        if analyses_count >= max_analyses_per_day:
            raise ValidationError(
                f"Rate limit exceeded. Maximum {max_analyses_per_day} analyses per day allowed."
            )
        return True

class SecurityValidator:
    """Security-related validation"""
    
    @staticmethod
    def validate_jwt_token_format(token):
        """Validate JWT token format"""
        if not token:
            raise ValidationError("Token is required")
        
        # Basic JWT format validation (3 parts separated by dots)
        parts = token.split('.')
        if len(parts) != 3:
            raise ValidationError("Invalid token format")
        
        return True
    
    @staticmethod
    def validate_request_origin(allowed_origins):
        """Validate request origin"""
        origin = request.headers.get('Origin')
        if origin and origin not in allowed_origins:
            raise ValidationError("Request origin not allowed")
        
        return True
