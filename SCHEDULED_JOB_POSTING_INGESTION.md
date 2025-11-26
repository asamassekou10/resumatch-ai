# Phase 6: Scheduled Job Posting Ingestion

## Overview

Phase 6 implements an automated system for scheduling and managing job posting ingestion tasks. This allows the application to automatically refresh market intelligence data, ingest new job postings, and maintain database health on a recurring schedule without manual intervention.

## Features

### 1. **Background Job Scheduler**
- Uses APScheduler for reliable task scheduling
- Supports both interval-based and cron-based scheduling
- Runs jobs in background threads without blocking API requests
- Automatic error handling and logging

### 2. **Scheduled Ingestion Tasks**

#### Daily Sample Ingestion (02:00 UTC)
- Automatically loads fresh sample job postings
- Keeps market intelligence data current
- Ideal for demonstration and testing environments

#### Market Statistics Refresh (Every 12 hours)
- Recalculates top demanded skills
- Updates salary trends and statistics
- Refreshes skill relationships
- Maintains accurate market data

#### Data Cleanup (Weekly on Sundays at 03:00 UTC)
- Removes outdated job postings (>90 days old)
- Optimizes database performance
- Configurable retention period

#### Skill Relationship Rebuild (Weekly)
- Recalculates skill co-occurrence patterns
- Updates skill recommendations
- Maintains recommendation cache accuracy

### 3. **Admin Management API**

Full REST API for managing scheduled tasks:

```
POST   /api/admin/scheduler/start              - Start scheduler
POST   /api/admin/scheduler/stop               - Stop scheduler
GET    /api/admin/scheduler/status             - Get scheduler status
GET    /api/admin/scheduler/jobs               - List all jobs
GET    /api/admin/scheduler/jobs/<job_id>     - Get job details
POST   /api/admin/scheduler/jobs/<job_id>/trigger - Execute job manually
POST   /api/admin/scheduler/jobs/<job_id>/pause   - Pause job
POST   /api/admin/scheduler/jobs/<job_id>/resume  - Resume job
DELETE /api/admin/scheduler/jobs/<job_id>     - Remove job
GET    /api/admin/scheduler/config            - Get scheduler configuration
```

## Architecture

### Components

#### 1. **job_scheduler.py**
Core scheduling engine with features:
- `JobPostingScheduler` class managing background jobs
- Global scheduler instance management
- Job lifecycle methods (start, stop, pause, resume)
- Task tracking and status monitoring
- Decorator support for custom scheduled jobs

#### 2. **scheduled_ingestion_tasks.py**
Predefined ingestion tasks:
- `ingest_sample_job_postings()` - Load sample data
- `refresh_market_statistics()` - Update market intelligence
- `cleanup_old_data()` - Archive and delete old records
- `rebuild_skill_relationships()` - Refresh skill cache
- `register_scheduled_tasks()` - Register all tasks
- `init_scheduler()` - Initialize on app startup

#### 3. **routes_scheduler.py**
Admin REST API endpoints:
- Scheduler status monitoring
- Job lifecycle management
- Job execution and monitoring
- Task configuration viewing
- Admin-only access with JWT authentication

### Task Flow

```
App Startup
    ↓
initialize_app()
    ↓
init_scheduler(app)
    ↓
get_scheduler().start()
    ↓
register_scheduled_tasks(app)
    ↓
All jobs queued and waiting for execution times
    ↓
Scheduler loop continuously monitors and executes jobs
    ↓
log_job_execution() records results
```

## Configuration

### Default Schedule

| Task | Schedule | Frequency | Purpose |
|------|----------|-----------|---------|
| Sample Ingestion | 02:00 UTC | Daily | Refresh demo data |
| Market Stats Refresh | Every 12 hours | 2x daily | Keep statistics current |
| Data Cleanup | Sunday 03:00 UTC | Weekly | Optimize database |
| Skill Rebuild | Every 7 days | Weekly | Update recommendations |

### Customization

To modify schedules, edit `scheduled_ingestion_tasks.py`:

```python
# Change daily ingestion to 3 AM UTC
scheduler.add_cron_job(
    func=ingest_sample_job_postings,
    cron_expression={'hour': 3, 'minute': 0},  # Changed from 2
    job_id='daily_sample_ingestion'
)

# Change market refresh to every 6 hours
scheduler.add_interval_job(
    func=refresh_market_statistics,
    hours=6,  # Changed from 12
    job_id='refresh_market_stats'
)
```

## Usage

### Starting the Scheduler

The scheduler automatically starts when the Flask app initializes:

```python
# In app.py - called automatically
initialize_app()
```

### Manual Control via API

```bash
# Check scheduler status
curl -X GET http://localhost:5000/api/admin/scheduler/status \
  -H "Authorization: Bearer <token>"

# List all scheduled jobs
curl -X GET http://localhost:5000/api/admin/scheduler/jobs \
  -H "Authorization: Bearer <token>"

# Manually trigger a job
curl -X POST http://localhost:5000/api/admin/scheduler/jobs/daily_sample_ingestion/trigger \
  -H "Authorization: Bearer <token>"

# Pause a job
curl -X POST http://localhost:5000/api/admin/scheduler/jobs/refresh_market_stats/pause \
  -H "Authorization: Bearer <token>"

# Resume a paused job
curl -X POST http://localhost:5000/api/admin/scheduler/jobs/refresh_market_stats/resume \
  -H "Authorization: Bearer <token>"

# Stop all scheduling
curl -X POST http://localhost:5000/api/admin/scheduler/stop \
  -H "Authorization: Bearer <token>"
```

### Creating Custom Scheduled Tasks

Add new tasks using the decorator pattern:

```python
from job_scheduler import scheduled_job, get_scheduler, log_job_execution
from datetime import datetime

@scheduled_job('my_custom_job', hours=1)
def my_custom_ingestion():
    """Custom ingestion task"""
    job_id = 'my_custom_job'
    start_time = datetime.utcnow()

    try:
        # Your ingestion logic here
        result = perform_ingestion()

        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='my_custom_ingestion',
            status='success',
            duration=duration
        )

        return {'success': True, 'details': result}

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_execution(
            job_id=job_id,
            func_name='my_custom_ingestion',
            status='failed',
            duration=duration,
            error=str(e)
        )
        return {'success': False, 'error': str(e)}


# Register the task
scheduler = get_scheduler()
scheduler.add_interval_job(
    func=my_custom_ingestion,
    hours=1,
    job_id='my_custom_job'
)
```

## Monitoring

### Log Files

Check logs for scheduler activity:

```bash
# View scheduler startup
docker-compose logs backend | grep "scheduler"

# Monitor specific job execution
docker-compose logs backend | grep "daily_sample_ingestion"
```

### Dashboard Monitoring

Monitor jobs through admin API:

```python
import requests

headers = {'Authorization': f'Bearer {token}'}

# Get all job statuses
response = requests.get(
    'http://localhost:5000/api/admin/scheduler/jobs',
    headers=headers
)

for job in response.json()['jobs']:
    print(f"{job['id']}: {job['status']}")
    print(f"  Next run: {job['next_run']}")
    print(f"  Last run: {job['last_run']}")
```

## Error Handling

### Task Failures

Failed tasks are logged and reported but don't stop the scheduler:

```
Task execution failed: ❌ cleanup_old_data
Reason: Database connection timeout
Status: Scheduled for retry at next scheduled time
```

### Recovery

- Failed jobs are automatically retried at the next scheduled interval
- Use `/trigger` endpoint to manually retry immediately
- Check logs for detailed error messages

## Docker Deployment

The scheduler runs automatically in Docker:

```yaml
# In docker-compose.yml
backend:
  build: ./backend
  environment:
    - FLASK_ENV=production
    # Scheduler starts automatically with the app
```

To start scheduler manually:

```bash
# Start scheduler service
docker-compose up backend

# Verify scheduler is running
docker-compose logs backend | grep "scheduler"
```

## Dependencies

- **APScheduler (3.10.4)**: Background job scheduling
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database queries
- **Existing analyzers**: MarketIntelligenceAnalyzer, SkillRelationshipAnalyzer

## Performance Considerations

### Resource Usage

- **Memory**: ~50MB for scheduler + job queue
- **CPU**: Minimal (only active during execution)
- **Database**: One connection per job execution
- **Threading**: Background threads managed by APScheduler

### Optimization Tips

1. **Stagger Jobs**: Run jobs at different times to avoid database congestion
2. **Off-Peak Hours**: Schedule intensive tasks during low-traffic periods
3. **Batch Operations**: Group related operations in single jobs
4. **Caching**: Cache results from frequently accessed data

## Troubleshooting

### Scheduler Not Starting

```bash
# Check if scheduler initialized
docker-compose logs backend | grep "scheduler initialized"

# Verify APScheduler installed
docker-compose exec backend pip list | grep APScheduler
```

### Job Not Executing

```bash
# Verify job exists
curl http://localhost:5000/api/admin/scheduler/jobs -H "Authorization: Bearer $TOKEN"

# Check job status
curl http://localhost:5000/api/admin/scheduler/jobs/daily_sample_ingestion -H "Authorization: Bearer $TOKEN"

# Manually trigger
curl -X POST http://localhost:5000/api/admin/scheduler/jobs/daily_sample_ingestion/trigger \
  -H "Authorization: Bearer $TOKEN"
```

### Database Connection Errors

- Ensure database is accessible from backend container
- Check `DATABASE_URL` environment variable
- Verify database credentials in `.env`

## Security

### Access Control

- All scheduler endpoints require JWT authentication
- Only admins (users with `is_admin=True`) can manage scheduler
- API endpoints validate admin status before processing

### Safe Operations

- Jobs execute with current database session
- Failed jobs don't corrupt data
- Automatic rollback on transaction failures
- Rate limiting applies to API endpoints

## Future Enhancements

1. **Distributed Scheduling**: Support multiple backend instances
2. **Job Persistence**: Store job state in database for recovery
3. **Advanced Filtering**: Schedule jobs based on data conditions
4. **Notifications**: Alert admins of failed jobs
5. **Job Templates**: Pre-built job configurations
6. **Real-time Monitoring**: WebSocket updates for job status
7. **Job Metrics**: Performance analytics and dashboards

## Files Added/Modified

### New Files
- `backend/job_scheduler.py` - Core scheduler engine
- `backend/scheduled_ingestion_tasks.py` - Predefined tasks
- `backend/routes_scheduler.py` - Admin API endpoints

### Modified Files
- `backend/app.py` - Added scheduler initialization
- `backend/requirements.txt` - Added APScheduler dependency

## Testing

### Unit Tests

```python
# Test scheduler initialization
def test_scheduler_start():
    scheduler = JobPostingScheduler()
    scheduler.start()
    assert scheduler.is_running == True
    scheduler.stop()

# Test job scheduling
def test_add_interval_job():
    scheduler = JobPostingScheduler()
    scheduler.start()
    job = scheduler.add_interval_job(test_func, hours=1, job_id='test')
    assert 'test' in scheduler.tasks
    scheduler.stop()
```

### Integration Tests

```bash
# Test scheduler endpoints
pytest tests/test_scheduler_endpoints.py

# Test scheduled task execution
pytest tests/test_scheduled_tasks.py
```

## Summary

Phase 6 delivers a production-ready scheduled job ingestion system that:

✅ Automatically refreshes job postings and market data
✅ Maintains database health with cleanup tasks
✅ Provides admin control via REST API
✅ Logs all task execution with detailed metrics
✅ Handles failures gracefully with automatic retries
✅ Scales efficiently in containerized environments

The system ensures that market intelligence data remains current and accurate without requiring manual intervention, improving user experience and platform reliability.
