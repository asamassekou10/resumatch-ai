import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
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

@pytest.fixture(autouse=True)
def mock_gemini_api():
    """Mock Gemini API calls to prevent real API requests in tests"""
    # Mock response object
    mock_response = MagicMock()
    mock_response.text = '{"core_skills": ["Python", "Flask"], "soft_skills": ["communication"], "experience_required": "5+ years", "experience_level": "senior", "industry": "Technology", "key_responsibilities": ["Develop web applications"], "nice_to_have": ["React"], "keywords": ["Python", "Flask", "REST API"], "tools_technologies": ["Docker", "AWS"], "salary_range": "$100k-$150k", "location_requirements": "Remote"}'
    
    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    # Mock GenerativeModel
    mock_generative_model = MagicMock(return_value=mock_model)
    
    # Mock gemini_service functions
    def mock_generate_personalized_feedback(*args, **kwargs):
        return "This is mock personalized feedback for your resume analysis."
    
    def mock_generate_optimized_resume(*args, **kwargs):
        return "Mock optimized resume content with improved keywords."
    
    def mock_generate_cover_letter(*args, **kwargs):
        return "Mock cover letter content tailored to the job description."
    
    def mock_suggest_missing_experience(*args, **kwargs):
        return "Mock suggestions for acquiring missing skills and experience."
    
    # Mock spaCy to prevent slow model loading
    mock_spacy = MagicMock()
    mock_spacy_doc = MagicMock()
    mock_spacy_doc.ents = []
    mock_spacy_doc.__iter__ = lambda self: iter([])
    mock_spacy.return_value = mock_spacy_doc
    
    # Mock the entire google.generativeai module and service functions
    with patch('google.generativeai.GenerativeModel', mock_generative_model), \
         patch('google.generativeai.configure', MagicMock()), \
         patch('intelligent_resume_analyzer.genai.GenerativeModel', mock_generative_model), \
         patch('intelligent_resume_analyzer.genai.configure', MagicMock()), \
         patch('intelligent_resume_analyzer.GEMINI_API_KEY', 'test-key'), \
         patch('gemini_service.genai.GenerativeModel', mock_generative_model), \
         patch('gemini_service.genai.configure', MagicMock()), \
         patch('gemini_service.generate_personalized_feedback', mock_generate_personalized_feedback), \
         patch('gemini_service.generate_optimized_resume', mock_generate_optimized_resume), \
         patch('gemini_service.generate_cover_letter', mock_generate_cover_letter), \
         patch('gemini_service.suggest_missing_experience', mock_suggest_missing_experience), \
         patch('spacy.load', mock_spacy), \
         patch('ai_processor.spacy.load', mock_spacy):
        yield

@pytest.fixture
def mock_gemini_service():
    """Mock gemini_service for testing"""
    with patch('routes.analysis.gemini_service') as mock_service:
        mock_service.generate_personalized_feedback.return_value = "This is mock feedback for your resume."
        mock_service.generate_optimized_resume.return_value = "Mock optimized resume content."
        mock_service.generate_cover_letter.return_value = "Mock cover letter content."
        mock_service.suggest_missing_experience.return_value = "Mock skill suggestions."
        mock_service.detect_language.return_value = 'en'
        mock_service._is_model_available.return_value = True
        yield mock_service

@pytest.fixture
def mock_intelligent_analyzer():
    """Mock intelligent_resume_analyzer for testing"""
    mock_analyzer = MagicMock()
    mock_analyzer.comprehensive_resume_analysis.return_value = {
        'overall_score': 75.5,
        'match_analysis': {
            'keywords_present': ['Python', 'Flask', 'PostgreSQL'],
            'keywords_missing': ['React', 'Docker']
        },
        'interpretation': 'Your resume shows good alignment with the job requirements.',
        'job_industry': 'Technology',
        'ats_score': 80,
        'semantic_match': 70,
        'recommendations': ['Add React experience', 'Highlight Docker skills']
    }
    mock_analyzer.detect_language.return_value = 'en'
    
    with patch('intelligent_resume_analyzer.get_analyzer', return_value=mock_analyzer), \
         patch('app.get_analyzer', return_value=mock_analyzer), \
         patch('routes_guest.get_analyzer', return_value=mock_analyzer):
        yield mock_analyzer
