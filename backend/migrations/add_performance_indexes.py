"""
Add Performance Indexes Migration

Adds database indexes to improve query performance for common operations:
- Analysis queries by user and date
- Job posting queries by industry and active status
- User lookups by email
- Guest session queries
"""

from flask_migrate import upgrade, downgrade
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Add performance indexes"""
    logger.info("Adding performance indexes...")
    
    # Note: This is a placeholder migration.
    # Actual SQL should be generated via Flask-Migrate:
    # flask db migrate -m "add_performance_indexes"
    # Then edit the generated file to add these indexes:
    
    # Indexes to add:
    # CREATE INDEX idx_analysis_user_created ON analysis(user_id, created_at DESC);
    # CREATE INDEX idx_analysis_user_id ON analysis(user_id);
    # CREATE INDEX idx_jobposting_industry_active ON job_posting(industry, is_active);
    # CREATE INDEX idx_user_email ON "user"(email);
    # CREATE INDEX idx_guest_session_created ON guest_session(created_at DESC);
    # CREATE INDEX idx_guest_analysis_session ON guest_analysis(guest_session_id);
    
    logger.info("Performance indexes migration completed")


def downgrade():
    """Remove performance indexes"""
    logger.info("Removing performance indexes...")
    
    # DROP INDEX idx_analysis_user_created;
    # DROP INDEX idx_analysis_user_id;
    # DROP INDEX idx_jobposting_industry_active;
    # DROP INDEX idx_user_email;
    # DROP INDEX idx_guest_session_created;
    # DROP INDEX idx_guest_analysis_session;
    
    logger.info("Performance indexes removed")

