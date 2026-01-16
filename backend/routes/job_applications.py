"""
Job Applications API Routes
Handles CRUD operations for job application tracking
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, JobApplication, User
import logging

job_applications_bp = Blueprint('job_applications', __name__, url_prefix='/api/job-applications')

# Valid status values
VALID_STATUSES = ['saved', 'applied', 'phone_screen', 'interview', 'offer', 'rejected', 'withdrawn', 'accepted']
VALID_WORK_TYPES = ['remote', 'hybrid', 'onsite', None]


def get_current_user():
    """Get current authenticated user"""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


@job_applications_bp.route('', methods=['GET'])
@jwt_required()
def get_applications():
    """
    Get all job applications for the current user

    Query params:
    - status: Filter by status (comma-separated for multiple)
    - starred: Filter starred only (true/false)
    - archived: Include archived (default false)
    - search: Search company/title
    - sort: Sort field (created_at, date_applied, company_name, status)
    - order: Sort order (asc/desc)
    - limit: Pagination limit
    - offset: Pagination offset
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Start query
        query = JobApplication.query.filter_by(user_id=user.id)

        # Filter by status
        status_filter = request.args.get('status')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',')]
            query = query.filter(JobApplication.status.in_(statuses))

        # Filter by starred
        starred = request.args.get('starred')
        if starred == 'true':
            query = query.filter_by(is_starred=True)

        # Filter by archived (default: exclude archived)
        archived = request.args.get('archived', 'false')
        if archived != 'true':
            query = query.filter_by(is_archived=False)

        # Search
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    JobApplication.company_name.ilike(search_term),
                    JobApplication.job_title.ilike(search_term)
                )
            )

        # Get total before pagination
        total = query.count()

        # Sorting
        sort_field = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')

        sort_mapping = {
            'created_at': JobApplication.created_at,
            'date_applied': JobApplication.date_applied,
            'company_name': JobApplication.company_name,
            'status': JobApplication.status,
            'job_title': JobApplication.job_title,
            'follow_up_date': JobApplication.follow_up_date
        }

        sort_column = sort_mapping.get(sort_field, JobApplication.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        query = query.limit(limit).offset(offset)

        applications = query.all()

        return jsonify({
            'status': 'success',
            'data': {
                'applications': [app.to_dict() for app in applications],
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        logging.error(f"Error fetching job applications: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch applications'}), 500


@job_applications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get job application statistics for the current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Get counts by status
        status_counts = db.session.query(
            JobApplication.status,
            db.func.count(JobApplication.id)
        ).filter(
            JobApplication.user_id == user.id,
            JobApplication.is_archived == False
        ).group_by(JobApplication.status).all()

        by_status = {status: count for status, count in status_counts}
        total = sum(by_status.values())

        # Calculate response rate (applications that got a response / total applied)
        applied_statuses = ['applied', 'phone_screen', 'interview', 'offer', 'rejected', 'accepted']
        response_statuses = ['phone_screen', 'interview', 'offer', 'rejected', 'accepted']

        total_applied = sum(by_status.get(s, 0) for s in applied_statuses)
        total_responses = sum(by_status.get(s, 0) for s in response_statuses)
        response_rate = (total_responses / total_applied) if total_applied > 0 else 0

        # Get applications this week and month
        now = datetime.utcnow()
        week_ago = datetime(now.year, now.month, now.day)
        week_ago = week_ago.replace(day=max(1, now.day - 7))
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        apps_this_week = JobApplication.query.filter(
            JobApplication.user_id == user.id,
            JobApplication.created_at >= week_ago
        ).count()

        apps_this_month = JobApplication.query.filter(
            JobApplication.user_id == user.id,
            JobApplication.created_at >= month_start
        ).count()

        # Get upcoming follow-ups
        upcoming_followups = JobApplication.query.filter(
            JobApplication.user_id == user.id,
            JobApplication.follow_up_date != None,
            JobApplication.follow_up_date >= now,
            JobApplication.is_archived == False
        ).count()

        return jsonify({
            'status': 'success',
            'data': {
                'total': total,
                'by_status': by_status,
                'response_rate': round(response_rate, 2),
                'applications_this_week': apps_this_week,
                'applications_this_month': apps_this_month,
                'upcoming_followups': upcoming_followups
            }
        }), 200

    except Exception as e:
        logging.error(f"Error fetching job application stats: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch statistics'}), 500


@job_applications_bp.route('', methods=['POST'])
@jwt_required()
def create_application():
    """Create a new job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        # Validate required fields
        if not data.get('company_name') or not data.get('job_title'):
            return jsonify({
                'status': 'error',
                'message': 'Company name and job title are required'
            }), 400

        # Validate status if provided
        status = data.get('status', 'saved')
        if status not in VALID_STATUSES:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
            }), 400

        # Validate work type if provided
        work_type = data.get('work_type')
        if work_type and work_type not in VALID_WORK_TYPES:
            return jsonify({
                'status': 'error',
                'message': f'Invalid work type. Must be one of: remote, hybrid, onsite'
            }), 400

        # Parse dates
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return None

        application = JobApplication(
            user_id=user.id,
            company_name=data['company_name'].strip()[:200],
            job_title=data['job_title'].strip()[:200],
            job_url=data.get('job_url', '').strip()[:500] if data.get('job_url') else None,
            job_description=data.get('job_description'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            location=data.get('location', '').strip()[:200] if data.get('location') else None,
            work_type=work_type,
            status=status,
            date_applied=parse_date(data.get('date_applied')),
            date_interview=parse_date(data.get('date_interview')),
            follow_up_date=parse_date(data.get('follow_up_date')),
            notes=data.get('notes'),
            resume_version=data.get('resume_version'),
            cover_letter_used=data.get('cover_letter_used', False),
            referral_contact=data.get('referral_contact'),
            is_starred=data.get('is_starred', False),
            analysis_id=data.get('analysis_id')
        )

        # If status is 'applied' and no date_applied, set it
        if status == 'applied' and not application.date_applied:
            application.date_applied = datetime.utcnow()

        db.session.add(application)
        db.session.commit()

        logging.info(f"Job application created: {application.id} for user {user.id}")

        return jsonify({
            'status': 'success',
            'message': 'Application created successfully',
            'data': application.to_dict()
        }), 201

    except Exception as e:
        logging.error(f"Error creating job application: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to create application'}), 500


@job_applications_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """Get a single job application by ID"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        return jsonify({
            'status': 'success',
            'data': application.to_dict()
        }), 200

    except Exception as e:
        logging.error(f"Error fetching job application {app_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch application'}), 500


@job_applications_bp.route('/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    """Update a job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        # Validate status if provided
        if 'status' in data and data['status'] not in VALID_STATUSES:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
            }), 400

        # Validate work type if provided
        if 'work_type' in data and data['work_type'] and data['work_type'] not in VALID_WORK_TYPES:
            return jsonify({
                'status': 'error',
                'message': f'Invalid work type. Must be one of: remote, hybrid, onsite'
            }), 400

        # Parse dates helper
        def parse_date(date_str):
            if date_str is None:
                return None
            if date_str == '':
                return None
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return None

        # Update fields
        updatable_fields = [
            'company_name', 'job_title', 'job_url', 'job_description',
            'salary_min', 'salary_max', 'location', 'work_type', 'status',
            'notes', 'resume_version', 'cover_letter_used', 'referral_contact',
            'interview_notes', 'rejection_reason', 'is_starred', 'is_archived',
            'analysis_id'
        ]

        date_fields = ['date_applied', 'date_response', 'date_interview', 'follow_up_date']

        for field in updatable_fields:
            if field in data:
                value = data[field]
                if field in ['company_name', 'job_title'] and value:
                    value = value.strip()[:200]
                elif field == 'job_url' and value:
                    value = value.strip()[:500]
                elif field == 'location' and value:
                    value = value.strip()[:200]
                setattr(application, field, value)

        for field in date_fields:
            if field in data:
                setattr(application, field, parse_date(data[field]))

        # Auto-set date_applied when status changes to 'applied'
        if data.get('status') == 'applied' and not application.date_applied:
            application.date_applied = datetime.utcnow()

        # Auto-set date_response when status changes to certain statuses
        response_statuses = ['phone_screen', 'interview', 'offer', 'rejected']
        if data.get('status') in response_statuses and not application.date_response:
            application.date_response = datetime.utcnow()

        db.session.commit()

        logging.info(f"Job application updated: {application.id}")

        return jsonify({
            'status': 'success',
            'message': 'Application updated successfully',
            'data': application.to_dict()
        }), 200

    except Exception as e:
        logging.error(f"Error updating job application {app_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to update application'}), 500


@job_applications_bp.route('/<int:app_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(app_id):
    """Quick status update for a job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if not new_status or new_status not in VALID_STATUSES:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}'
            }), 400

        old_status = application.status
        application.status = new_status

        # Auto-set dates based on status change
        if new_status == 'applied' and not application.date_applied:
            application.date_applied = datetime.utcnow()

        response_statuses = ['phone_screen', 'interview', 'offer', 'rejected']
        if new_status in response_statuses and not application.date_response:
            application.date_response = datetime.utcnow()

        db.session.commit()

        logging.info(f"Job application {app_id} status changed: {old_status} -> {new_status}")

        return jsonify({
            'status': 'success',
            'message': 'Status updated successfully',
            'data': application.to_dict()
        }), 200

    except Exception as e:
        logging.error(f"Error updating job application status {app_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to update status'}), 500


@job_applications_bp.route('/<int:app_id>/star', methods=['PATCH'])
@jwt_required()
def toggle_star(app_id):
    """Toggle star status for a job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        application.is_starred = not application.is_starred
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Star toggled successfully',
            'data': {'is_starred': application.is_starred}
        }), 200

    except Exception as e:
        logging.error(f"Error toggling star for job application {app_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to toggle star'}), 500


@job_applications_bp.route('/<int:app_id>/archive', methods=['PATCH'])
@jwt_required()
def toggle_archive(app_id):
    """Toggle archive status for a job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        application.is_archived = not application.is_archived
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Archive toggled successfully',
            'data': {'is_archived': application.is_archived}
        }), 200

    except Exception as e:
        logging.error(f"Error toggling archive for job application {app_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to toggle archive'}), 500


@job_applications_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    """Delete a job application"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        application = JobApplication.query.filter_by(
            id=app_id,
            user_id=user.id
        ).first()

        if not application:
            return jsonify({'status': 'error', 'message': 'Application not found'}), 404

        db.session.delete(application)
        db.session.commit()

        logging.info(f"Job application deleted: {app_id}")

        return jsonify({
            'status': 'success',
            'message': 'Application deleted successfully'
        }), 200

    except Exception as e:
        logging.error(f"Error deleting job application {app_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to delete application'}), 500
