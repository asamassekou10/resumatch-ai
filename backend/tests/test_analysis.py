import pytest
import json
import io
from models import Analysis

class TestAnalysis:
    """Test analysis endpoints"""
    
    def test_analyze_resume_success(self, client, auth_headers, sample_resume_file, sample_job_description):
        """Test successful resume analysis"""
        with open(sample_resume_file, 'rb') as f:
            resume_content = f.read()
        
        data = {
            'resume': (io.BytesIO(resume_content), 'resume.txt'),
            'job_description': sample_job_description,
            'job_title': 'Software Engineer',
            'company_name': 'Test Company'
        }
        
        response = client.post('/api/v1/analysis/analyze',
                             data=data,
                             headers=auth_headers,
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['status'] == 'success'
        assert 'analysis_id' in response_data['data']
        assert 'match_score' in response_data['data']
        assert 'keywords_found' in response_data['data']
        assert 'keywords_missing' in response_data['data']
        assert 'suggestions' in response_data['data']
    
    def test_analyze_resume_no_file(self, client, auth_headers, sample_job_description):
        """Test resume analysis without file"""
        data = {
            'job_description': sample_job_description
        }
        
        response = client.post('/api/v1/analysis/analyze',
                             data=data,
                             headers=auth_headers,
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
    
    def test_analyze_resume_no_job_description(self, client, auth_headers, sample_resume_file):
        """Test resume analysis without job description"""
        with open(sample_resume_file, 'rb') as f:
            resume_content = f.read()
        
        data = {
            'resume': (io.BytesIO(resume_content), 'resume.txt')
        }
        
        response = client.post('/api/v1/analysis/analyze',
                             data=data,
                             headers=auth_headers,
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['status'] == 'error'
    
    def test_analyze_resume_unauthorized(self, client, sample_resume_file, sample_job_description):
        """Test resume analysis without authentication"""
        with open(sample_resume_file, 'rb') as f:
            resume_content = f.read()
        
        data = {
            'resume': (io.BytesIO(resume_content), 'resume.txt'),
            'job_description': sample_job_description
        }
        
        response = client.post('/api/v1/analysis/analyze',
                             data=data,
                             content_type='multipart/form-data')
        
        assert response.status_code == 401
    
    def test_get_analyses(self, client, auth_headers):
        """Test getting user's analyses"""
        response = client.get('/api/v1/analysis/analyses', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['status'] == 'success'
        assert 'analyses' in response_data['data']
        assert 'pagination' in response_data['data']
    
    def test_get_analyses_unauthorized(self, client):
        """Test getting analyses without authentication"""
        response = client.get('/api/v1/analysis/analyses')
        
        assert response.status_code == 401
    
    def test_get_analysis_by_id(self, client, auth_headers, sample_resume_file, sample_job_description):
        """Test getting specific analysis by ID"""
        # First create an analysis
        with open(sample_resume_file, 'rb') as f:
            resume_content = f.read()
        
        data = {
            'resume': (io.BytesIO(resume_content), 'resume.txt'),
            'job_description': sample_job_description
        }
        
        create_response = client.post('/api/v1/analysis/analyze',
                                    data=data,
                                    headers=auth_headers,
                                    content_type='multipart/form-data')
        
        assert create_response.status_code == 200
        analysis_id = create_response.get_json()['data']['analysis_id']
        
        # Get the analysis
        response = client.get(f'/api/v1/analysis/analyses/{analysis_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['status'] == 'success'
        assert response_data['data']['analysis']['id'] == analysis_id
    
    def test_get_analysis_not_found(self, client, auth_headers):
        """Test getting non-existent analysis"""
        response = client.get('/api/v1/analysis/analyses/99999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['status'] == 'error'
    
    def test_delete_analysis(self, client, auth_headers, sample_resume_file, sample_job_description):
        """Test deleting an analysis"""
        # First create an analysis
        with open(sample_resume_file, 'rb') as f:
            resume_content = f.read()
        
        data = {
            'resume': (io.BytesIO(resume_content), 'resume.txt'),
            'job_description': sample_job_description
        }
        
        create_response = client.post('/api/v1/analysis/analyze',
                                    data=data,
                                    headers=auth_headers,
                                    content_type='multipart/form-data')
        
        assert create_response.status_code == 200
        analysis_id = create_response.get_json()['data']['analysis_id']
        
        # Delete the analysis
        response = client.delete(f'/api/v1/analysis/analyses/{analysis_id}', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['status'] == 'success'
        
        # Verify it's deleted
        get_response = client.get(f'/api/v1/analysis/analyses/{analysis_id}', headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_analysis_not_found(self, client, auth_headers):
        """Test deleting non-existent analysis"""
        response = client.delete('/api/v1/analysis/analyses/99999', headers=auth_headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert response_data['status'] == 'error'
