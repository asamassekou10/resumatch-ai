"""
Scheduled Job Posting Ingestion Tasks

Defines recurring tasks for automatic job posting ingestion, data updates,
and market intelligence refreshes.
"""

from datetime import datetime, timedelta
import logging
from job_scheduler import get_scheduler, log_job_execution

logger = logging.getLogger(__name__)


def ingest_sample_job_postings():
    """
    Scheduled task: Ingest sample job postings daily

    This task loads a fresh batch of realistic sample job postings
    to keep the market intelligence data updated for demonstration
    and testing purposes.
    """
    from sample_job_postings import load_sample_postings
    from app import db

    job_id = 'daily_sample_ingestion'
    start_time = datetime.utcnow()

    try:
        logger.info("Starting scheduled sample job posting ingestion...")
        result = load_sample_postings(db)

        if 'error' in result:
            raise Exception(result['error'])

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='ingest_sample_job_postings',
            status='success',
            duration=duration
        )

        logger.info(f"Sample ingestion completed: {result}")
        return {
            'success': True,
            'message': 'Sample job postings ingested successfully',
            'details': result
        }

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='ingest_sample_job_postings',
            status='failed',
            duration=duration,
            error=str(e)
        )
        logger.error(f"Error during sample ingestion: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def ingest_real_job_postings():
    """
    Scheduled task: Ingest REAL job postings from job board APIs

    This task fetches actual job postings from sources like:
    - RemoteOK (free, no API key needed)
    - JSearch (RapidAPI - requires RAPIDAPI_KEY)
    - Adzuna (requires ADZUNA_APP_ID and ADZUNA_APP_KEY)

    Run manually or schedule for periodic execution.
    """
    from app import db
    from real_job_sources import fetch_all_real_postings
    from job_posting_ingestion import get_ingestion_manager

    job_id = 'real_job_ingestion'
    start_time = datetime.utcnow()

    try:
        logger.info("Starting REAL job posting ingestion from external APIs...")

        # Fetch real postings from all configured sources
        postings = fetch_all_real_postings(limit_per_source=50)

        if not postings:
            logger.warning("No real job postings fetched - check API configurations")
            return {
                'success': True,
                'message': 'No postings available from configured sources',
                'postings_ingested': 0
            }

        # Ingest the postings
        manager = get_ingestion_manager(db)
        result = manager.ingest_postings(postings, extract_skills=True)

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='ingest_real_job_postings',
            status='success',
            duration=duration
        )

        logger.info(f"Real job ingestion completed: {result}")
        return {
            'success': True,
            'message': 'Real job postings ingested successfully',
            'details': result
        }

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='ingest_real_job_postings',
            status='failed',
            duration=duration,
            error=str(e)
        )
        logger.error(f"Error during real job ingestion: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def refresh_market_statistics():
    """
    Scheduled task: Refresh market intelligence statistics

    This task recalculates market statistics including:
    - Top demanded skills
    - Salary trends by skill and location
    - Industry distribution
    - Skill relationships
    """
    from app import db
    from market_intelligence_analyzer import MarketIntelligenceAnalyzer

    job_id = 'refresh_market_stats'
    start_time = datetime.utcnow()

    try:
        logger.info("Starting market statistics refresh...")

        analyzer = MarketIntelligenceAnalyzer(db)

        # Refresh all market data
        stats = analyzer.get_market_summary()
        top_skills = analyzer.get_top_demanded_skills(limit=20)
        salary_trends = analyzer.get_salary_trends_by_skill()

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='refresh_market_statistics',
            status='success',
            duration=duration
        )

        logger.info("Market statistics refreshed successfully")
        return {
            'success': True,
            'message': 'Market statistics refreshed',
            'stats_updated': datetime.utcnow().isoformat()
        }

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='refresh_market_statistics',
            status='failed',
            duration=duration,
            error=str(e)
        )
        logger.error(f"Error refreshing market statistics: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def cleanup_old_data():
    """
    Scheduled task: Cleanup and archive old data

    This task removes or archives job postings and analysis data
    older than a specified retention period to maintain database performance.
    """
    from app import db
    from models import JobPostingKeyword

    job_id = 'cleanup_old_data'
    start_time = datetime.utcnow()

    try:
        logger.info("Starting data cleanup...")

        # Define retention period (e.g., 90 days)
        retention_days = 90
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Count old records before deletion
        old_records = JobPostingKeyword.query.filter(
            JobPostingKeyword.created_at < cutoff_date
        ).count()

        # Delete old records (optional - can also archive to another table)
        JobPostingKeyword.query.filter(
            JobPostingKeyword.created_at < cutoff_date
        ).delete()
        db.session.commit()

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='cleanup_old_data',
            status='success',
            duration=duration
        )

        logger.info(f"Cleaned up {old_records} old records")
        return {
            'success': True,
            'message': f'Cleaned up {old_records} old records',
            'retention_days': retention_days
        }

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='cleanup_old_data',
            status='failed',
            duration=duration,
            error=str(e)
        )
        logger.error(f"Error during cleanup: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def rebuild_skill_relationships():
    """
    Scheduled task: Rebuild skill relationship cache

    This task recalculates skill co-occurrence relationships and
    updates the skill recommendation cache based on current job postings.
    """
    from app import db
    from skill_relationship_analyzer import SkillRelationshipAnalyzer

    job_id = 'rebuild_skill_relationships'
    start_time = datetime.utcnow()

    try:
        logger.info("Starting skill relationship rebuild...")

        analyzer = SkillRelationshipAnalyzer(db)

        # Rebuild all relationships
        result = analyzer.build_relationships()

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='rebuild_skill_relationships',
            status='success',
            duration=duration
        )

        logger.info("Skill relationships rebuilt successfully")
        return {
            'success': True,
            'message': 'Skill relationships rebuilt',
            'relationships_updated': result
        }

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='rebuild_skill_relationships',
            status='failed',
            duration=duration,
            error=str(e)
        )
        logger.error(f"Error rebuilding skill relationships: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def register_scheduled_tasks(app_instance):
    """
    Register all scheduled tasks with the job scheduler

    Args:
        app_instance: Flask application instance
    """
    scheduler = get_scheduler()

    try:
        # Schedule real job ingestion every 24 hours (primary data source)
        scheduler.add_interval_job(
            func=ingest_real_job_postings,
            hours=24,
            job_id='real_job_ingestion'
        )
        logger.info("Scheduled: Real job ingestion every 24 hours")

        # Schedule market statistics refresh every 24 hours
        scheduler.add_interval_job(
            func=refresh_market_statistics,
            hours=24,
            job_id='refresh_market_stats'
        )
        logger.info("Scheduled: Market statistics refresh every 24 hours")

        # Schedule data cleanup weekly on Sundays at 3 AM UTC
        scheduler.add_cron_job(
            func=cleanup_old_data,
            cron_expression={'day_of_week': 6, 'hour': 3, 'minute': 0},
            job_id='cleanup_old_data'
        )
        logger.info("Scheduled: Weekly data cleanup on Sundays at 03:00 UTC")

        # Schedule skill relationship rebuild every 7 days
        scheduler.add_interval_job(
            func=rebuild_skill_relationships,
            days=7,
            job_id='rebuild_skill_relationships'
        )
        logger.info("Scheduled: Skill relationship rebuild every 7 days")

    except Exception as e:
        logger.error(f"Failed to register scheduled tasks: {str(e)}")
        raise


def init_scheduler(app_instance):
    """
    Initialize the job scheduler with all tasks

    Args:
        app_instance: Flask application instance
    """
    try:
        scheduler = get_scheduler()
        scheduler.start()
        register_scheduled_tasks(app_instance)
        logger.info("Job scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
        raise
