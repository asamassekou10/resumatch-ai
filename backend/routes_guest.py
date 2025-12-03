"""
Guest mode routes - allow users to try the app with 5 free credits without login.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import uuid
import secrets
import json
from models import db, GuestSession, GuestAnalysis
from ai_processor import process_resume_analysis
from security_config import sanitize_text_input, validate_file_upload
import logging

guest_bp = Blueprint('guest', __name__, url_prefix='/api/guest')
logger = logging.getLogger(__name__)

# ============== HELPER FUNCTIONS ==============

def generate_guest_token():
    """Generate a unique guest token"""
    return 'guest_' + secrets.token_urlsafe(32)

def get_guest_session_from_token(token):
    """Retrieve and validate guest session from token"""
    if not token or not token.startswith('guest_'):
        return None

    session = GuestSession.query.filter_by(session_token=token).first()
    if not session:
        return None

    if session.is_expired():
        session.status = 'expired'
        db.session.commit()
        return None

    return session

# ============== MIDDLEWARE ==============

def guest_token_required(f):
    """Decorator to require guest token in Authorization header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        try:
            token = auth_header.split(' ')[1]
            guest_session = get_guest_session_from_token(token)

            if not guest_session:
                return jsonify({
                    'error': 'Invalid or expired guest session',
                    'error_type': 'UNAUTHORIZED'
                }), 401

            g.guest_session = guest_session
            g.is_guest = True
            return f(*args, **kwargs)
        except (IndexError, AttributeError):
            return jsonify({
                'error': 'Missing or invalid Authorization header',
                'error_type': 'UNAUTHORIZED'
            }), 401

    return decorated_function

# ============== GUEST ENDPOINTS ==============

@guest_bp.route('/session', methods=['POST'])
def create_guest_session():
    """
    Create a new guest session with abuse prevention

    Returns:
        - guest_token: Unique token for this session
        - credits: Number of free credits (2 analyses)
        - expires_at: When the session expires
        - session_id: UUID of the session
    """
    try:
        # Get client IP address
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()

        # Get user agent and device fingerprint
        user_agent = request.headers.get('User-Agent', '')
        request_data = request.get_json(silent=True) or {}
        device_fingerprint = request_data.get('device_fingerprint')

        # SECURITY: Check for abuse - limit guest sessions per IP
        # Count active sessions from this IP in the last 24 hours
        recent_sessions_count = GuestSession.query.filter(
            GuestSession.ip_address == ip_address,
            GuestSession.created_at >= datetime.utcnow() - timedelta(hours=24),
            GuestSession.status == 'active'
        ).count()

        # Allow max 3 active sessions per IP per day to prevent abuse
        if recent_sessions_count >= 3:
            logger.warning(f"Rate limit exceeded for IP {ip_address}: {recent_sessions_count} sessions in 24h")
            return jsonify({
                'error': 'Too many guest sessions from this IP. Please try again later or create an account.',
                'error_type': 'RATE_LIMIT_EXCEEDED',
                'retry_after': '24 hours'
            }), 429

        # SECURITY: Check if this IP has already used guest credits recently
        # This prevents users from creating multiple sessions to bypass the 2-analysis limit
        total_analyses_from_ip = db.session.query(GuestAnalysis).join(GuestSession).filter(
            GuestSession.ip_address == ip_address,
            GuestSession.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()

        if total_analyses_from_ip >= 10:  # Max 10 total analyses per IP per day across all sessions
            logger.warning(f"Analysis limit exceeded for IP {ip_address}: {total_analyses_from_ip} analyses in 24h")
            return jsonify({
                'error': 'Daily guest analysis limit reached. Create an account for unlimited access.',
                'error_type': 'DAILY_LIMIT_EXCEEDED',
                'analyses_used': total_analyses_from_ip
            }), 429

        # Generate session
        session_id = str(uuid.uuid4())
        session_token = generate_guest_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)

        guest_session = GuestSession(
            id=session_id,
            session_token=session_token,
            credits_remaining=10,  # CHANGED: Increased to 10 analyses for presentation
            credits_used=0,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            expires_at=expires_at,
            status='active'
        )

        db.session.add(guest_session)
        db.session.commit()

        logger.info(f"Created guest session {session_id} from {ip_address} (2 credits)")

        return jsonify({
            'guest_token': session_token,
            'credits': 2,  # CHANGED: Show 2 credits instead of 5
            'expires_at': expires_at.isoformat(),
            'session_id': session_id,
            'message': 'Guest session created - 2 free analyses available'
        }), 201

    except Exception as e:
        logger.error(f"Error creating guest session: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create guest session',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500

@guest_bp.route('/analyze', methods=['POST'])
@guest_token_required
def analyze_resume_guest():
    """
    Analyze resume as guest (uses 1 credit, max 2 analyses per session)

    Request body (multipart/form-data):
        - resume: Resume file (PDF, DOCX, or TXT)
        - job_description: Job description text (required)
        - job_title: Target job title (optional)
        - company_name: Target company name (optional)

    Returns:
        - analysis_id: ID of the analysis
        - results: Analysis results
        - credits_remaining: Credits left after analysis
    """
    guest_session = g.guest_session

    try:
        # SECURITY: Check if guest has credits
        if not guest_session.has_credits():
            return jsonify({
                'error': 'No guest credits remaining. Create an account for unlimited analyses.',
                'error_type': 'INSUFFICIENT_CREDITS',
                'credits_remaining': 0,
                'upgrade_message': 'Sign up now to unlock unlimited resume analyses and advanced features!'
            }), 402

        # SECURITY: Double-check IP hasn't exceeded daily limit (defense in depth)
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()

        total_analyses_from_ip = db.session.query(GuestAnalysis).join(GuestSession).filter(
            GuestSession.ip_address == ip_address,
            GuestSession.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()

        if total_analyses_from_ip >= 5:
            logger.warning(f"Analysis attempt from IP {ip_address} that exceeded daily limit")
            return jsonify({
                'error': 'Daily guest analysis limit reached for your network.',
                'error_type': 'DAILY_LIMIT_EXCEEDED',
                'upgrade_message': 'Create an account for unlimited access!'
            }), 429

        # Validate file upload
        if 'resume' not in request.files:
            return jsonify({
                'error': 'Resume file required',
                'error_type': 'INVALID_REQUEST'
            }), 400

        resume_file = request.files['resume']

        # Validate file
        is_valid, error_message = validate_file_upload(resume_file)
        if not is_valid:
            return jsonify({
                'error': error_message,
                'error_type': 'INVALID_REQUEST'
            }), 400

        # Sanitize text inputs
        job_description = sanitize_text_input(request.form.get('job_description', ''), max_length=10000)
        job_title = sanitize_text_input(request.form.get('job_title', ''), max_length=200)
        company_name = sanitize_text_input(request.form.get('company_name', ''), max_length=200)

        if not job_description:
            return jsonify({
                'error': 'Job description required',
                'error_type': 'INVALID_REQUEST'
            }), 400

        # Run analysis with intelligent analyzer
        try:
            # Extract resume text from file
            from ai_processor import extract_text_from_file
            resume_text = extract_text_from_file(resume_file)

            # Use intelligent analyzer for better results
            from intelligent_resume_analyzer import get_analyzer
            analyzer = get_analyzer()

            logger.info(f"Starting intelligent analysis for guest session {guest_session.id}")
            analysis_result = analyzer.comprehensive_resume_analysis(resume_text, job_description)

            if not analysis_result:
                return jsonify({
                    'error': 'Analysis failed',
                    'error_type': 'ANALYSIS_ERROR',
                    'details': 'No result returned from analysis'
                }), 500

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return jsonify({
                'error': 'Analysis failed',
                'error_type': 'ANALYSIS_ERROR',
                'details': str(e)
            }), 500

        # Create guest analysis record
        analysis_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Extract data from intelligent analysis result
        match_analysis = analysis_result.get('match_analysis', {})
        keywords_found = match_analysis.get('keywords_present', [])
        keywords_missing = [k['keyword'] if isinstance(k, dict) else k for k in match_analysis.get('keywords_missing', [])]

        guest_analysis = GuestAnalysis(
            id=analysis_id,
            guest_session_id=guest_session.id,
            resume_text=resume_text[:50000],  # Limit stored text
            job_description=job_description,
            job_title=job_title,
            company_name=company_name,
            match_score=analysis_result.get('overall_score', 0),
            keywords_found=keywords_found[:20],  # Limit to 20
            keywords_missing=keywords_missing[:20],  # Limit to 20
            suggestions=analysis_result.get('interpretation', ''),
            ai_feedback=json.dumps(analysis_result.get('recommendations', {})),  # Store full recommendations
            detected_industry=analysis_result.get('job_industry', 'Unknown'),
            expires_at=expires_at
        )

        db.session.add(guest_analysis)

        # Deduct credits from guest session
        guest_session.deduct_credits(1)
        guest_session.last_activity = datetime.utcnow()

        db.session.commit()

        logger.info(f"Guest analysis created: {analysis_id} for session {guest_session.id}")

        return jsonify({
            'analysis_id': analysis_id,
            'overall_score': analysis_result.get('overall_score'),
            'interpretation': analysis_result.get('interpretation'),
            'match_analysis': analysis_result.get('match_analysis'),
            'ats_optimization': analysis_result.get('ats_optimization'),
            'recommendations': analysis_result.get('recommendations'),
            'job_industry': analysis_result.get('job_industry'),
            'job_level': analysis_result.get('job_level'),
            'resume_level': analysis_result.get('resume_level'),
            'expected_ats_pass_rate': analysis_result.get('expected_ats_pass_rate'),
            'credits_remaining': guest_session.credits_remaining,
            'expires_at': expires_at.isoformat(),
            'message': 'Analysis complete - create account to save results'
        }), 200

    except Exception as e:
        logger.error(f"Error in guest analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'error_type': 'INTERNAL_SERVER_ERROR',
            'details': str(e)
        }), 500

@guest_bp.route('/analysis/<analysis_id>', methods=['GET'])
@guest_token_required
def get_guest_analysis(analysis_id):
    """
    Retrieve guest analysis results

    Returns:
        - analysis: Guest analysis results (without resume/job_description content for safety)
    """
    guest_session = g.guest_session

    try:
        analysis = GuestAnalysis.query.filter_by(
            id=analysis_id,
            guest_session_id=guest_session.id
        ).first()

        if not analysis:
            return jsonify({
                'error': 'Analysis not found',
                'error_type': 'NOT_FOUND'
            }), 404

        if analysis.is_expired():
            return jsonify({
                'error': 'Analysis has expired (24-hour limit for guest sessions)',
                'error_type': 'EXPIRED'
            }), 410

        return jsonify({
            'analysis': analysis.to_dict(include_content=False)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving guest analysis: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve analysis',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500

@guest_bp.route('/session/info', methods=['GET'])
@guest_token_required
def get_guest_session_info():
    """Get current guest session information"""
    guest_session = g.guest_session

    return jsonify({
        'session': guest_session.to_dict(),
        'analyses_count': len(guest_session.analyses),
        'time_remaining_minutes': max(0, int((guest_session.expires_at - datetime.utcnow()).total_seconds() / 60))
    }), 200

# ============== CLEANUP ==============

@guest_bp.route('/cleanup', methods=['POST'])
def cleanup_expired_sessions():
    """
    Cleanup expired guest sessions (should be called periodically by cron)
    Admin/internal endpoint
    """
    try:
        # Delete analyses from expired sessions
        expired_analyses = GuestAnalysis.query.filter(
            GuestAnalysis.expires_at < datetime.utcnow()
        ).delete()

        # Mark sessions as expired
        expired_sessions = GuestSession.query.filter(
            GuestSession.expires_at < datetime.utcnow(),
            GuestSession.status == 'active'
        ).update({'status': 'expired'})

        db.session.commit()

        logger.info(f"Cleanup: Deleted {expired_analyses} analyses, marked {expired_sessions} sessions as expired")

        return jsonify({
            'message': 'Cleanup completed',
            'deleted_analyses': expired_analyses,
            'expired_sessions': expired_sessions
        }), 200

    except Exception as e:
        logger.error(f"Error during guest session cleanup: {str(e)}")
        return jsonify({
            'error': 'Cleanup failed',
            'error_type': 'INTERNAL_SERVER_ERROR'
        }), 500
