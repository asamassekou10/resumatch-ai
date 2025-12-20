import sys
from unittest.mock import MagicMock
import pytest
import tempfile
import os

# FORCE MOCKS: Stop ALL Google network calls
# These must run BEFORE 'app' is imported
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["google.oauth2"] = MagicMock()
sys.modules["google.auth.transport.requests"] = MagicMock()

from app import create_app
from models import db
from config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_resume_file():
    """Create a sample resume file for testing"""
    content = """
    John Doe
    Software Engineer
    
    Experience:
    - Developed web applications using Python and Flask
    - Worked with databases including PostgreSQL and MySQL
    - Implemented REST APIs and microservices
    - Used Git for version control and CI/CD pipelines
    
    Skills:
    - Python, JavaScript, SQL
    - Flask, Django, React
    - AWS, Docker, Kubernetes
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    We are looking for a Senior Software Engineer to join our team.
    
    Requirements:
    - 5+ years of experience with Python and web frameworks
    - Strong knowledge of databases (PostgreSQL, MySQL)
    - Experience with REST APIs and microservices architecture
    - Familiarity with cloud platforms (AWS, Azure)
    - Knowledge of containerization (Docker, Kubernetes)
    - Experience with version control (Git) and CI/CD pipelines
    - Strong problem-solving and communication skills
    
    Nice to have:
    - Experience with machine learning and data analysis
    - Knowledge of frontend frameworks (React, Vue.js)
    - Experience with agile development methodologies
    """

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }

@pytest.fixture
def auth_headers(client, sample_user_data):
    """Get authentication headers for testing"""
    # Register user
    response = client.post('/api/v1/auth/register', 
                          json=sample_user_data,
                          content_type='application/json')
    
    if response.status_code == 201:
        data = response.get_json()
        token = data['data']['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    # If registration fails, try login
    response = client.post('/api/v1/auth/login',
                          json=sample_user_data,
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.get_json()
        token = data['data']['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    return {}
