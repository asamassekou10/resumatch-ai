"""
Database initialization module - single source of truth for SQLAlchemy instance.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance that will be imported by both app.py and models.py
db = SQLAlchemy()
