import pytest
import json
from models import User

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/v1/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'access_token' in data['data']
        assert data['data']['user']['email'] == user_data['email']
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        # Register first user
        client.post('/api/v1/auth/register',
                   json=user_data,
                   content_type='application/json')
        
        # Try to register with same email
        response = client.post('/api/v1/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'already registered' in data['message'].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        user_data = {
            'email': 'invalid-email',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/v1/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        user_data = {
            'email': 'test@example.com',
            'password': '123'
        }
        
        response = client.post('/api/v1/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post('/api/v1/auth/register',
                   json=sample_user_data,
                   content_type='application/json')
        
        # Login
        response = client.post('/api/v1/auth/login',
                             json=sample_user_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'access_token' in data['data']
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        user_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/v1/auth/login',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'user' in data['data']
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
    
    def test_logout(self, client, auth_headers):
        """Test logout endpoint"""
        response = client.post('/api/v1/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_change_password(self, client, auth_headers):
        """Test changing password"""
        password_data = {
            'current_password': 'testpassword123',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/v1/auth/change-password',
                             json=password_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password"""
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/v1/auth/change-password',
                             json=password_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['status'] == 'error'
