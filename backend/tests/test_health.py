import pytest

class TestHealth:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['status'] == 'healthy'
        assert 'database' in data['data']
        assert 'version' in data['data']
    
    def test_detailed_health_check(self, client, auth_headers):
        """Test detailed health check with authentication"""
        response = client.get('/api/v1/health/detailed', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['status'] == 'healthy'
        assert 'database' in data['data']
        assert 'user_access' in data['data']
        assert 'features' in data['data']
    
    def test_detailed_health_check_unauthorized(self, client):
        """Test detailed health check without authentication"""
        response = client.get('/api/v1/health/detailed')
        
        assert response.status_code == 401
