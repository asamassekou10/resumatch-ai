"""
Simple migration to create job_applications table
"""
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///resume_analyzer.db')

# For Render PostgreSQL, convert postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define job_applications table
job_applications = Table(
    'job_applications',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False, index=True),

    # Job Details
    Column('company_name', String(200), nullable=False),
    Column('job_title', String(200), nullable=False),
    Column('job_url', String(500)),
    Column('job_description', Text),
    Column('salary_min', Integer),
    Column('salary_max', Integer),
    Column('location', String(200)),
    Column('work_type', String(50)),  # remote, hybrid, onsite

    # Application Status
    Column('status', String(50), nullable=False, default='saved', index=True),

    # Important Dates
    Column('date_saved', DateTime, default=datetime.utcnow),
    Column('date_applied', DateTime),
    Column('date_response', DateTime),
    Column('date_interview', DateTime),
    Column('follow_up_date', DateTime),

    # Notes & Tracking
    Column('notes', Text),
    Column('resume_version', String(200)),
    Column('cover_letter_used', Boolean, default=False),
    Column('referral_contact', String(200)),
    Column('interview_notes', Text),
    Column('rejection_reason', String(500)),

    # UI State
    Column('is_starred', Boolean, default=False, index=True),
    Column('is_archived', Boolean, default=False, index=True),

    # Linked Analysis (optional)
    Column('analysis_id', Integer, ForeignKey('analyses.id'), nullable=True),

    # Timestamps
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),

    # Composite indexes
    Index('idx_job_app_user_status', 'user_id', 'status'),
    Index('idx_job_app_user_created', 'user_id', 'created_at'),
    Index('idx_job_app_user_starred', 'user_id', 'is_starred'),
    Index('idx_job_app_follow_up', 'user_id', 'follow_up_date'),
)

# Create table
print("Creating job_applications table...")
try:
    job_applications.create(engine, checkfirst=True)
    print("✓ job_applications table created successfully!")
except Exception as e:
    if 'already exists' in str(e).lower():
        print("✓ job_applications table already exists")
    else:
        print(f"✗ Error: {e}")
        raise
