"""
Scheduled Job Posting Ingestion System

This module handles automatic ingestion of job postings from various sources
on a scheduled basis. It uses APScheduler to manage recurring tasks.

Features:
- Automatic job posting ingestion from sample data
- Configurable scheduling intervals
- Task monitoring and logging
- Graceful error handling
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


class JobPostingScheduler:
    """Manages scheduled job posting ingestion tasks"""

    def __init__(self):
        """Initialize the scheduler"""
        self.scheduler = BackgroundScheduler()
        self.tasks = {}
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                logger.info("Job Posting Scheduler started successfully")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")
                raise

    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Job Posting Scheduler stopped successfully")
            except Exception as e:
                logger.error(f"Failed to stop scheduler: {str(e)}")

    def add_interval_job(self, func, seconds=None, minutes=None, hours=None,
                        days=None, job_id=None, replace_existing=True):
        """
        Add a job that runs at regular intervals

        Args:
            func: Function to execute
            seconds/minutes/hours/days: Interval parameters
            job_id: Unique identifier for the job
            replace_existing: Replace existing job if ID matches
        """
        if not self.is_running:
            logger.warning("Scheduler not running, starting it first")
            self.start()

        try:
            # Build trigger kwargs with only non-None values
            trigger_kwargs = {}
            if seconds is not None:
                trigger_kwargs['seconds'] = seconds
            if minutes is not None:
                trigger_kwargs['minutes'] = minutes
            if hours is not None:
                trigger_kwargs['hours'] = hours
            if days is not None:
                trigger_kwargs['days'] = days

            job = self.scheduler.add_job(
                func,
                trigger=IntervalTrigger(**trigger_kwargs),
                id=job_id,
                replace_existing=replace_existing,
                max_instances=1
            )
            self.tasks[job_id] = {
                'job': job,
                'status': 'scheduled',
                'created_at': datetime.utcnow(),
                'last_run': None,
                'next_run': job.next_run_time
            }
            logger.info(f"Job '{job_id}' scheduled successfully")
            return job
        except Exception as e:
            logger.error(f"Failed to schedule job '{job_id}': {str(e)}")
            raise

    def add_cron_job(self, func, cron_expression, job_id=None, replace_existing=True):
        """
        Add a job that runs on a cron schedule

        Args:
            func: Function to execute
            cron_expression: Cron expression (hour, minute, etc.)
            job_id: Unique identifier for the job
            replace_existing: Replace existing job if ID matches
        """
        if not self.is_running:
            logger.warning("Scheduler not running, starting it first")
            self.start()

        try:
            job = self.scheduler.add_job(
                func,
                trigger=CronTrigger(**cron_expression),
                id=job_id,
                replace_existing=replace_existing,
                max_instances=1
            )
            self.tasks[job_id] = {
                'job': job,
                'status': 'scheduled',
                'created_at': datetime.utcnow(),
                'last_run': None,
                'next_run': job.next_run_time
            }
            logger.info(f"Cron job '{job_id}' scheduled successfully")
            return job
        except Exception as e:
            logger.error(f"Failed to schedule cron job '{job_id}': {str(e)}")
            raise

    def remove_job(self, job_id):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            del self.tasks[job_id]
            logger.info(f"Job '{job_id}' removed successfully")
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {str(e)}")

    def get_job_status(self, job_id):
        """Get the status of a scheduled job"""
        if job_id in self.tasks:
            task = self.tasks[job_id]
            return {
                'id': job_id,
                'status': task['status'],
                'created_at': task['created_at'].isoformat(),
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None
            }
        return None

    def get_all_jobs(self):
        """Get all scheduled jobs"""
        return [
            {
                'id': job_id,
                'status': task['status'],
                'created_at': task['created_at'].isoformat(),
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None
            }
            for job_id, task in self.tasks.items()
        ]

    def pause_job(self, job_id):
        """Pause a scheduled job"""
        try:
            self.scheduler.pause_job(job_id)
            if job_id in self.tasks:
                self.tasks[job_id]['status'] = 'paused'
            logger.info(f"Job '{job_id}' paused")
        except Exception as e:
            logger.error(f"Failed to pause job '{job_id}': {str(e)}")

    def resume_job(self, job_id):
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            if job_id in self.tasks:
                self.tasks[job_id]['status'] = 'scheduled'
            logger.info(f"Job '{job_id}' resumed")
        except Exception as e:
            logger.error(f"Failed to resume job '{job_id}': {str(e)}")


def create_scheduler():
    """Create and return a global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = JobPostingScheduler()
    return scheduler


def get_scheduler():
    """Get the global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = create_scheduler()
    return scheduler


def scheduled_job(job_id, minutes=None, hours=None, days=None):
    """
    Decorator to register a function as a scheduled job

    Usage:
        @scheduled_job('daily_ingestion', hours=1)
        def ingest_daily_postings():
            # ingestion logic
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store job metadata
        wrapper._job_id = job_id
        wrapper._job_params = {
            'minutes': minutes,
            'hours': hours,
            'days': days
        }
        return wrapper
    return decorator


def log_job_execution(job_id, func_name, status, duration=None, error=None):
    """Log job execution details"""
    scheduler_instance = get_scheduler()
    if job_id in scheduler_instance.tasks:
        scheduler_instance.tasks[job_id]['last_run'] = datetime.utcnow()
        if scheduler_instance.tasks[job_id]['job']:
            scheduler_instance.tasks[job_id]['next_run'] = scheduler_instance.tasks[job_id]['job'].next_run_time

    log_entry = {
        'job_id': job_id,
        'function': func_name,
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'duration': duration
    }

    if error:
        log_entry['error'] = str(error)
        logger.error(f"Job '{job_id}' failed: {error}")
    else:
        logger.info(f"Job '{job_id}' executed successfully in {duration}s")

    return log_entry
