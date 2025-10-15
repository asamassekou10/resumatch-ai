import logging
import traceback
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import structlog
from datetime import datetime

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

class ValidationError(APIError):
    """Raised when input validation fails"""
    def __init__(self, message="Validation failed", payload=None):
        super().__init__(message, 400, payload)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication failed", payload=None):
        super().__init__(message, 401, payload)

class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message="Access denied", payload=None):
        super().__init__(message, 403, payload)

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, 404, payload)

class AIProcessingError(APIError):
    """Raised when AI processing fails"""
    def __init__(self, message="AI processing failed", payload=None):
        super().__init__(message, 500, payload)

class FileProcessingError(APIError):
    """Raised when file processing fails"""
    def __init__(self, message="File processing failed", payload=None):
        super().__init__(message, 400, payload)

def create_error_response(message, status_code, payload=None, error_type=None):
    """Create standardized error response"""
    response = {
        'status': 'error',
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'path': request.path if request else None
    }
    
    if payload:
        response['details'] = payload
    
    if error_type:
        response['error_type'] = error_type
    
    return jsonify(response), status_code

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        logger.error("API Error", 
                    error_message=error.message,
                    status_code=error.status_code,
                    payload=error.payload,
                    path=request.path,
                    method=request.method)
        return create_error_response(error.message, error.status_code, error.payload)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning("Validation Error",
                      error_message=error.message,
                      payload=error.payload,
                      path=request.path)
        return create_error_response(error.message, 400, error.payload, 'validation_error')
    
    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        logger.warning("Authentication Error",
                      error_message=error.message,
                      path=request.path,
                      ip=request.remote_addr)
        return create_error_response(error.message, 401, error.payload, 'authentication_error')
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        logger.warning("Authorization Error",
                      error_message=error.message,
                      path=request.path,
                      ip=request.remote_addr)
        return create_error_response(error.message, 403, error.payload, 'authorization_error')
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        logger.info("Not Found Error",
                   error_message=error.message,
                   path=request.path)
        return create_error_response(error.message, 404, error.payload, 'not_found_error')
    
    @app.errorhandler(AIProcessingError)
    def handle_ai_error(error):
        logger.error("AI Processing Error",
                    error_message=error.message,
                    payload=error.payload,
                    path=request.path)
        return create_error_response(error.message, 500, error.payload, 'ai_processing_error')
    
    @app.errorhandler(FileProcessingError)
    def handle_file_error(error):
        logger.warning("File Processing Error",
                      error_message=error.message,
                      payload=error.payload,
                      path=request.path)
        return create_error_response(error.message, 400, error.payload, 'file_processing_error')
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        logger.warning("HTTP Exception",
                      error_code=error.code,
                      error_description=error.description,
                      path=request.path)
        return create_error_response(error.description, error.code, error_type='http_exception')
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        logger.error("Unhandled Exception",
                    error_type=type(error).__name__,
                    error_message=str(error),
                    traceback=traceback.format_exc(),
                    path=request.path,
                    method=request.method)
        
        # Don't expose internal errors in production
        if app.config.get('DEBUG', False):
            message = f"Internal server error: {str(error)}"
            payload = {'traceback': traceback.format_exc()}
        else:
            message = "An unexpected error occurred. Please try again later."
            payload = None
        
        return create_error_response(message, 500, payload, 'internal_server_error')
    
    @app.errorhandler(413)
    def handle_file_too_large(error):
        logger.warning("File too large",
                      path=request.path,
                      content_length=request.content_length)
        return create_error_response(
            "File too large. Maximum file size is 16MB.",
            413,
            error_type='file_too_large'
        )
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        logger.warning("Rate limit exceeded",
                      path=request.path,
                      ip=request.remote_addr)
        return create_error_response(
            "Rate limit exceeded. Please try again later.",
            429,
            error_type='rate_limit_exceeded'
        )

def log_request_info():
    """Log request information for debugging"""
    logger.info("Request received",
               method=request.method,
               path=request.path,
               ip=request.remote_addr,
               user_agent=request.headers.get('User-Agent'),
               content_type=request.content_type,
               content_length=request.content_length)

def log_response_info(response):
    """Log response information for debugging"""
    logger.info("Response sent",
               status_code=response.status_code,
               path=request.path,
               content_type=response.content_type,
               content_length=response.content_length)
    return response
