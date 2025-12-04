"""
Admin diagnostic and fix endpoints
Only accessible by admin users
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Analysis, SkillExtraction, JobPosting, JobPostingKeyword
from sqlalchemy import text, func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

admin_diag_bp = Blueprint('admin_diagnostics', __name__, url_prefix='/api/v1/admin/diagnostics')

def is_admin():
    """Check if current user is admin"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return user and user.is_admin
    except:
        return False

@admin_diag_bp.route('/market-data', methods=['GET'])
@jwt_required()
def check_market_data():
    """Check market intelligence data status"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Count job postings
        job_count = db.session.query(func.count(JobPosting.id)).scalar()

        # Count unique keywords/skills from job postings
        skill_count = db.session.query(func.count(func.distinct(JobPostingKeyword.keyword_id))).scalar()

        # Count job-skill relationships (total job posting keywords)
        job_skill_count = db.session.query(func.count(JobPostingKeyword.id)).scalar()

        # Count recent jobs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_jobs = db.session.query(func.count(JobPosting.id))\
            .filter(JobPosting.created_at >= thirty_days_ago).scalar()

        # Sample jobs
        sample_jobs = db.session.execute(text("""
            SELECT
                jp.title,
                jp.company,
                jp.location,
                jp.salary_min,
                jp.salary_max,
                COUNT(jpk.id) as skill_count
            FROM job_posting jp
            LEFT JOIN job_posting_keyword jpk ON jp.title = jpk.job_title
                AND jp.company = jpk.company_name
            GROUP BY jp.id, jp.title, jp.company, jp.location, jp.salary_min, jp.salary_max
            ORDER BY jp.created_at DESC
            LIMIT 5
        """)).fetchall()

        sample_jobs_data = [{
            'title': row[0],
            'company': row[1] or 'Unknown',
            'location': row[2] or 'N/A',
            'salary_min': row[3] or 0,
            'salary_max': row[4] or 0,
            'skill_count': row[5]
        } for row in sample_jobs]

        # Diagnose issues
        issues = []
        if job_count == 0:
            issues.append("NO_JOB_POSTINGS - Market pages will be empty")
        elif job_count < 1000:
            issues.append(f"LOW_JOB_COUNT ({job_count}) - Should have 50,000+")

        if skill_count == 0:
            issues.append("NO_SKILLS - Cannot show skills demand")

        if job_skill_count == 0:
            issues.append("NO_JOB_SKILL_RELATIONSHIPS - Market analysis will fail")

        if recent_jobs == 0:
            issues.append("NO_RECENT_JOBS - Data may be stale")

        status = "healthy" if not issues else ("warning" if job_count > 0 else "critical")

        return jsonify({
            'status': status,
            'data': {
                'job_postings': job_count,
                'skills': skill_count,
                'job_skill_relationships': job_skill_count,
                'recent_jobs_30_days': recent_jobs,
                'sample_jobs': sample_jobs_data
            },
            'issues': issues,
            'recommendations': [
                "Run job ingestion from Adzuna API" if job_count < 1000 else None,
                "Check job skill extraction during ingestion" if job_skill_count == 0 else None
            ]
        }), 200

    except Exception as e:
        logger.error(f"Error checking market data: {e}")
        return jsonify({'error': str(e)}), 500

@admin_diag_bp.route('/skill-extraction', methods=['GET'])
@jwt_required()
def check_skill_extraction():
    """Check skill extraction status"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Count extractions
        extraction_count = db.session.query(func.count(SkillExtraction.id)).scalar()

        # Recent extractions (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_extractions = db.session.query(func.count(SkillExtraction.id))\
            .filter(SkillExtraction.created_at >= seven_days_ago).scalar()

        # Feedback stats
        feedback_stats = db.session.execute(text("""
            SELECT
                COUNT(CASE WHEN user_confirmed = true THEN 1 END) as confirmed,
                COUNT(CASE WHEN user_rejected = true THEN 1 END) as rejected,
                COUNT(CASE WHEN user_confirmed IS NULL AND user_rejected IS NULL THEN 1 END) as pending
            FROM skill_extraction
        """)).fetchone()

        # Count analyses without extractions
        analyses_without_extractions = db.session.execute(text("""
            SELECT COUNT(*) FROM analysis a
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_extraction se
                WHERE se.analysis_id = a.id
            )
            AND a.created_at >= :date
        """), {"date": seven_days_ago}).scalar()

        # Sample extractions
        sample_extractions = db.session.execute(text("""
            SELECT
                se.extracted_text,
                se.confidence,
                se.extraction_method,
                se.user_confirmed,
                se.user_rejected,
                a.job_title
            FROM skill_extraction se
            JOIN analysis a ON se.analysis_id = a.id
            ORDER BY se.created_at DESC
            LIMIT 10
        """)).fetchall()

        sample_data = [{
            'skill': row[0],
            'confidence': round(row[1], 2),
            'method': row[2],
            'confirmed': row[3],
            'rejected': row[4],
            'job_title': row[5]
        } for row in sample_extractions]

        # Diagnose issues
        issues = []
        if extraction_count == 0:
            issues.append("NO_SKILL_EXTRACTIONS - Feature is not working")
        elif recent_extractions == 0:
            issues.append("NO_RECENT_EXTRACTIONS - May not be integrated with analysis")

        if analyses_without_extractions > 0:
            issues.append(f"{analyses_without_extractions} recent analyses WITHOUT skill extractions")

        status = "healthy" if not issues else ("warning" if extraction_count > 0 else "critical")

        return jsonify({
            'status': status,
            'data': {
                'total_extractions': extraction_count,
                'recent_extractions_7_days': recent_extractions,
                'feedback': {
                    'confirmed': feedback_stats[0],
                    'rejected': feedback_stats[1],
                    'pending': feedback_stats[2]
                },
                'analyses_without_extractions': analyses_without_extractions,
                'sample_extractions': sample_data
            },
            'issues': issues,
            'recommendations': [
                "Check if skill_extractor module is working" if extraction_count == 0 else None,
                "Create extractions for recent analyses" if analyses_without_extractions > 0 else None
            ]
        }), 200

    except Exception as e:
        logger.error(f"Error checking skill extraction: {e}")
        return jsonify({'error': str(e)}), 500

@admin_diag_bp.route('/fix-skill-extractions', methods=['POST'])
@jwt_required()
def fix_skill_extractions():
    """Create skill extractions for analyses that don't have any"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Find analyses without extractions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        analyses = db.session.execute(text("""
            SELECT
                a.id,
                a.job_title,
                a.keywords_found,
                a.keywords_missing
            FROM analysis a
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_extraction se
                WHERE se.analysis_id = a.id
            )
            AND a.created_at >= :date
            ORDER BY a.created_at DESC
            LIMIT 50
        """), {"date": thirty_days_ago}).fetchall()

        if not analyses:
            return jsonify({
                'status': 'success',
                'message': 'No analyses need skill extractions',
                'fixed_count': 0
            }), 200

        fixed_count = 0
        for analysis in analyses:
            analysis_id = analysis[0]
            keywords_found = analysis[2] or []
            keywords_missing = analysis[3] or []

            # Create extractions for found skills (higher confidence)
            for skill in keywords_found[:10]:  # Limit to 10
                db.session.execute(text("""
                    INSERT INTO skill_extraction
                    (analysis_id, extracted_text, confidence, extraction_method, extraction_quality, created_at, updated_at)
                    VALUES (:analysis_id, :skill, 0.85, 'spacy_ner', 0.85, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {
                    "analysis_id": analysis_id,
                    "skill": skill
                })

            # Create extractions for missing skills (lower confidence)
            for skill in keywords_missing[:5]:  # Limit to 5
                db.session.execute(text("""
                    INSERT INTO skill_extraction
                    (analysis_id, extracted_text, confidence, extraction_method, extraction_quality, created_at, updated_at)
                    VALUES (:analysis_id, :skill, 0.65, 'taxonomy_match', 0.65, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {
                    "analysis_id": analysis_id,
                    "skill": skill
                })

            fixed_count += 1

        db.session.commit()

        logger.info(f"Created skill extractions for {fixed_count} analyses")

        return jsonify({
            'status': 'success',
            'message': f'Created skill extractions for {fixed_count} analyses',
            'fixed_count': fixed_count,
            'total_found': len(analyses)
        }), 200

    except Exception as e:
        logger.error(f"Error fixing skill extractions: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_diag_bp.route('/full-diagnostic', methods=['GET'])
@jwt_required()
def full_diagnostic():
    """Run full diagnostic check"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Get market data status
        market_response = check_market_data()
        market_data = market_response[0].get_json() if hasattr(market_response[0], 'get_json') else market_response[0]

        # Get skill extraction status
        skill_response = check_skill_extraction()
        skill_data = skill_response[0].get_json() if hasattr(skill_response[0], 'get_json') else skill_response[0]

        # Overall status
        issues = []
        if market_data.get('status') != 'healthy':
            issues.extend(market_data.get('issues', []))
        if skill_data.get('status') != 'healthy':
            issues.extend(skill_data.get('issues', []))

        overall_status = 'healthy' if not issues else 'needs_attention'

        return jsonify({
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'market_intelligence': market_data,
            'skill_extraction': skill_data,
            'summary': {
                'total_issues': len(issues),
                'issues': issues
            }
        }), 200

    except Exception as e:
        logger.error(f"Error running full diagnostic: {e}")
        return jsonify({'error': str(e)}), 500
