from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from models import db, User, user_schema
from validators import TextValidator, RequestValidator
from errors import ValidationError, AuthenticationError, AuthorizationError
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_success_response(message: str, data: dict = None, status_code: int = 200):
    """Create standardized success response"""
    response = {
        'status': 'success',
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data:
        response['data'] = data
    return jsonify(response), status_code

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user"""
    try:
        # Validate request
        data = RequestValidator.validate_json_request(['email', 'password'])
        
        # Validate and clean input
        email = TextValidator.validate_email(data['email'])
        password = TextValidator.validate_password(data['password'])
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValidationError("Email already registered")
        
        # Create new user
        password_hash = generate_password_hash(password).decode('utf-8')
        user = User(
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"New user registered: {email}")
        
        return create_success_response(
            "User created successfully",
            {
                'access_token': access_token,
                'user': user.to_dict()
            },
            201
        )
        
    except ValidationError as e:
        logger.warning(f"Registration validation error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        raise

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return access token"""
    try:
        # Validate request
        data = RequestValidator.validate_json_request(['email', 'password'])
        
        # Validate and clean input
        email = TextValidator.validate_email(data['email'])
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User logged in: {email}")
        
        return create_success_response(
            "Login successful",
            {
                'access_token': access_token,
                'user': user.to_dict()
            }
        )
        
    except ValidationError as e:
        logger.warning(f"Login validation error: {e.message}")
        raise
    except AuthenticationError as e:
        logger.warning(f"Login authentication error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        return create_success_response(
            "User information retrieved",
            {'user': user.to_dict()}
        )
        
    except AuthenticationError as e:
        logger.warning(f"Get user error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token will be invalidated client-side)"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"User logged out: {user_id}")
        
        return create_success_response("Logout successful")
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Validate request
        data = RequestValidator.validate_json_request(['current_password', 'new_password'])
        
        # Verify current password
        if not check_password_hash(user.password_hash, data['current_password']):
            raise AuthenticationError("Current password is incorrect")
        
        # Validate new password
        new_password = TextValidator.validate_password(data['new_password'])
        
        # Update password
        user.password_hash = generate_password_hash(new_password).decode('utf-8')
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return create_success_response("Password changed successfully")
        
    except ValidationError as e:
        logger.warning(f"Change password validation error: {e.message}")
        raise
    except AuthenticationError as e:
        logger.warning(f"Change password authentication error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        db.session.rollback()
        raise
