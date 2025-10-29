"""
Root API endpoint tests
"""
import pytest
import requests


@pytest.mark.smoke
@pytest.mark.api
def test_root_endpoint_returns_200_status_code(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root endpoint returns HTTP 200 OK"""
    response = api_client.get(root_endpoint)
    
    assert response.status_code == 200


@pytest.mark.api
def test_root_endpoint_returns_json_content_type(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root endpoint returns JSON"""
    response = api_client.get(root_endpoint)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.api
def test_root_response_contains_message_field(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root response has 'message' field"""
    response = api_client.get(root_endpoint)
    data = response.json()
    
    assert "message" in data


@pytest.mark.api
def test_root_response_contains_version_field(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root response has 'version' field"""
    response = api_client.get(root_endpoint)
    data = response.json()
    
    assert "version" in data


@pytest.mark.api
def test_root_response_contains_endpoints_field(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root response has 'endpoints' field"""
    response = api_client.get(root_endpoint)
    data = response.json()
    
    assert "endpoints" in data


@pytest.mark.api
def test_root_response_contains_documentation_field(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that root response has 'documentation' field"""
    response = api_client.get(root_endpoint)
    data = response.json()
    
    assert "documentation" in data


@pytest.mark.api
def test_root_endpoints_lists_tts_post_endpoint(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that TTS POST endpoint is listed in endpoints"""
    response = api_client.get(root_endpoint)
    data = response.json()
    endpoints = data["endpoints"]
    
    assert "POST /api/v1/tts" in endpoints


@pytest.mark.api
def test_root_endpoints_lists_languages_get_endpoint(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that languages GET endpoint is listed"""
    response = api_client.get(root_endpoint)
    data = response.json()
    endpoints = data["endpoints"]
    
    assert "GET /api/v1/languages" in endpoints


@pytest.mark.api
def test_root_documentation_has_swagger_link(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that documentation includes Swagger UI link"""
    response = api_client.get(root_endpoint)
    data = response.json()
    docs = data["documentation"]
    
    assert "swagger" in docs
    assert docs["swagger"] == "/docs"


@pytest.mark.api
def test_root_documentation_has_redoc_link(
    api_client: requests.Session, 
    root_endpoint: str
):
    """Test that documentation includes ReDoc link"""
    response = api_client.get(root_endpoint)
    data = response.json()
    docs = data["documentation"]
    
    assert "redoc" in docs
    assert docs["redoc"] == "/redoc"
