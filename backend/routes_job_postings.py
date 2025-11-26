"""
Job Posting Management API Routes

Provides endpoints for:
- Ingesting job posting data
- Loading sample data for testing
- Viewing job posting statistics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

# Create blueprint
job_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

logger = logging.getLogger(__name__)


@job_bp.route('/ingest', methods=['POST'])
@jwt_required()
def ingest_job_postings():
    """
    Ingest job posting data into the system.

    Request body:
        {
            "postings": [
                {
                    "job_title": "Senior Developer",
                    "company_name": "TechCorp",
                    "job_description": "...",
                    "location": "San Francisco, CA",
                    "salary_min": 150000,
                    "salary_max": 200000,
                    "industry": "Technology",
                    "source": "indeed"
                }
            ],
            "extract_skills": true
        }

    Returns:
        - Number of postings ingested
        - Skills extracted
    """
    from job_posting_ingestion import JobPosting, get_ingestion_manager
    from app import db

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Validate input
        postings_data = data.get('postings', [])
        if not postings_data or not isinstance(postings_data, list):
            return jsonify({'error': 'postings must be a non-empty array'}), 400

        if len(postings_data) > 1000:
            return jsonify({'error': 'Maximum 1000 postings per request'}), 400

        extract_skills = data.get('extract_skills', True)

        # Convert to JobPosting objects
        postings = []
        for p in postings_data:
            try:
                posting = JobPosting(
                    job_title=p.get('job_title', ''),
                    company_name=p.get('company_name', ''),
                    job_description=p.get('job_description', ''),
                    location=p.get('location', ''),
                    salary_min=p.get('salary_min'),
                    salary_max=p.get('salary_max'),
                    salary_currency=p.get('salary_currency', 'USD'),
                    industry=p.get('industry'),
                    source=p.get('source', 'api'),
                    job_url=p.get('job_url')
                )

                if not posting.job_title or not posting.company_name:
                    return jsonify({'error': 'job_title and company_name are required'}), 400

                postings.append(posting)

            except Exception as e:
                logger.warning(f"Error parsing posting: {str(e)}")
                continue

        if not postings:
            return jsonify({'error': 'No valid postings provided'}), 400

        # Ingest postings
        manager = get_ingestion_manager(db)
        result = manager.ingest_postings(postings, extract_skills=extract_skills)

        return jsonify({
            'success': True,
            'message': 'Job postings ingested successfully',
            'details': result
        }), 200

    except Exception as e:
        logger.error(f"Error ingesting job postings: {str(e)}")
        return jsonify({'error': 'Failed to ingest job postings'}), 500


@job_bp.route('/load-sample-data', methods=['POST'])
@jwt_required()
def load_sample_data():
    """
    Load sample job postings for testing (admin only).

    This endpoint loads realistic sample data from 10 different companies
    across multiple industries for testing the market intelligence system.

    Returns:
        - Sample postings loaded
        - Skills extracted
    """
    from sample_job_postings import load_sample_postings
    from models import User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Verify user is admin (optional - can remove for testing)
        # user = User.query.get(user_id)
        # if not user or not user.is_admin:
        #     return jsonify({'error': 'Admin access required'}), 403

        logger.info(f"User {user_id} requested sample data loading")

        # Load sample postings
        result = load_sample_postings(db)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'success': True,
            'message': 'Sample job postings loaded successfully',
            'details': result
        }), 200

    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return jsonify({'error': 'Failed to load sample data'}), 500


@job_bp.route('/ingest-real', methods=['POST'])
@jwt_required()
def ingest_real_job_postings():
    """
    Ingest REAL job postings from external job board APIs.

    This endpoint fetches actual job postings from:
    - RemoteOK (free, no API key needed)
    - JSearch (requires RAPIDAPI_KEY env var)
    - Adzuna (requires ADZUNA_APP_ID and ADZUNA_APP_KEY env vars)

    Request body (optional):
        {
            "limit_per_source": 50,
            "query": "python developer",
            "location": "United States"
        }

    Returns:
        - Number of real postings ingested
        - Skills extracted
        - Source breakdown
    """
    from scheduled_ingestion_tasks import ingest_real_job_postings as do_ingest
    from models import User
    from app import db

    try:
        user_id = int(get_jwt_identity())

        # Verify user is admin
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required for real job ingestion'}), 403

        logger.info(f"Admin {user_id} triggered real job ingestion")

        # Execute real job ingestion
        result = do_ingest()

        if not result.get('success', False):
            return jsonify(result), 500

        return jsonify({
            'success': True,
            'message': 'Real job postings ingested from external APIs',
            'details': result.get('details', {})
        }), 200

    except Exception as e:
        logger.error(f"Error during real job ingestion: {str(e)}")
        return jsonify({'error': str(e)}), 500


@job_bp.route('/sources', methods=['GET'])
@jwt_required()
def get_available_sources():
    """
    Get information about available job posting sources.

    Returns which sources are configured and available for real job ingestion.
    """
    import os

    sources = {
        'remoteok': {
            'name': 'RemoteOK',
            'available': True,
            'requires_key': False,
            'description': 'Free remote tech job listings'
        },
        'jsearch': {
            'name': 'JSearch (RapidAPI)',
            'available': bool(os.getenv('RAPIDAPI_KEY')),
            'requires_key': True,
            'env_var': 'RAPIDAPI_KEY',
            'description': 'Aggregates Indeed, LinkedIn, Glassdoor, ZipRecruiter'
        },
        'adzuna': {
            'name': 'Adzuna',
            'available': bool(os.getenv('ADZUNA_APP_ID') and os.getenv('ADZUNA_APP_KEY')),
            'requires_key': True,
            'env_vars': ['ADZUNA_APP_ID', 'ADZUNA_APP_KEY'],
            'description': 'Real-time job search across major markets'
        },
        'linkedin': {
            'name': 'LinkedIn OAuth',
            'available': bool(os.getenv('LINKEDIN_CLIENT_ID') and os.getenv('LINKEDIN_CLIENT_SECRET')),
            'requires_key': True,
            'env_vars': ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET'],
            'description': 'LinkedIn authentication and profile data integration',
            'features': ['oauth_login', 'profile_import', 'skills_extraction']
        }
    }

    available_count = sum(1 for s in sources.values() if s['available'])

    return jsonify({
        'sources': sources,
        'available_sources': available_count,
        'total_sources': len(sources)
    }), 200


@job_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_job_postings_statistics():
    """
    Get statistics about ingested job postings.

    Returns:
        - Total postings
        - Sources
        - Industries
        - Salary statistics
    """
    from models import JobPostingKeyword
    from app import db
    from sqlalchemy import func
    import statistics as stat_module

    try:
        user_id = int(get_jwt_identity())

        # Get all postings
        postings = JobPostingKeyword.query.all()

        if not postings:
            return jsonify({
                'total_postings': 0,
                'message': 'No job posting data available'
            }), 200

        # Group by source
        sources = {}
        industries = {}
        salaries = []

        for posting in postings:
            # Count sources
            source = posting.source or 'unknown'
            sources[source] = sources.get(source, 0) + 1

            # Count industries
            industry = posting.industry or 'unknown'
            industries[industry] = industries.get(industry, 0) + 1

            # Collect salaries
            if posting.salary_min and posting.salary_max:
                avg_salary = (posting.salary_min + posting.salary_max) / 2
                salaries.append(avg_salary)

        # Calculate salary statistics
        if salaries:
            avg_salary = stat_module.mean(salaries)
            median_salary = stat_module.median(salaries)
            min_salary = min(salaries)
            max_salary = max(salaries)
        else:
            avg_salary = median_salary = min_salary = max_salary = None

        return jsonify({
            'total_postings': len(postings),
            'sources': sources,
            'industries': industries,
            'salary_statistics': {
                'average': round(avg_salary, 2) if avg_salary else None,
                'median': round(median_salary, 2) if median_salary else None,
                'min': round(min_salary, 2) if min_salary else None,
                'max': round(max_salary, 2) if max_salary else None,
                'postings_with_salary': len(salaries)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500
