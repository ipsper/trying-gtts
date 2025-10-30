"""
Health check endpoint tests
"""
import pytest
import requests


@pytest.mark.smoke
def test_health_check_returns_200_status_code(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health endpoint returns HTTP 200 OK status"""
    response = api_client.get(health_endpoint)
    
    assert response.status_code == 200


@pytest.mark.smoke
def test_health_check_returns_json_content_type(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health endpoint returns JSON content type"""
    response = api_client.get(health_endpoint)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.smoke
def test_health_check_response_has_status_field(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health response contains 'status' field"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "status" in data


@pytest.mark.smoke
def test_health_check_response_has_service_field(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health response contains 'service' field"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "service" in data


@pytest.mark.smoke
def test_health_check_response_has_version_field(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health response contains 'version' field"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "version" in data


@pytest.mark.smoke
def test_health_check_status_is_healthy(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that health status reports 'healthy'"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert data["status"] == "healthy"


@pytest.mark.smoke
def test_health_check_service_name_is_gtts_api(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that service name is 'gTTS API'"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert data["service"] == "gTTS API"


@pytest.mark.smoke
def test_health_check_version_is_not_empty(
    api_client: requests.Session, 
    health_endpoint: str
):
    """Test that version field is not empty"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "version" in data
    assert len(data["version"]) > 0
