"""
Server verification tests - ALWAYS RUN FIRST

These tests verify that we're testing against the correct server
before running any other tests. The filename starts with '00_' to
ensure pytest runs it first alphabetically.
"""
import pytest
import requests


@pytest.mark.smoke
def test_00_server_is_reachable(
    api_client: requests.Session,
    health_endpoint: str
):
    """CRITICAL: Verify that the server is reachable before running any tests"""
    response = api_client.get(health_endpoint)
    
    assert response.status_code == 200, (
        f"Server not reachable. Expected 200 but got {response.status_code}. "
        f"Is the API running?"
    )


@pytest.mark.smoke
def test_00_server_is_gtts_api(
    api_client: requests.Session,
    health_endpoint: str
):
    """CRITICAL: Verify that we're testing the correct service (gTTS API)"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "service" in data, "Health response missing 'service' field"
    
    assert data["service"] == "gTTS API", (
        f"Wrong service! Expected 'gTTS API' but got '{data['service']}'. "
        f"Are you testing the correct server?"
    )


@pytest.mark.smoke
def test_00_server_is_healthy(
    api_client: requests.Session,
    health_endpoint: str
):
    """CRITICAL: Verify that the server reports healthy status"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "status" in data, "Health response missing 'status' field"
    
    assert data["status"] == "healthy", (
        f"Server is not healthy! Status: {data['status']}. "
        f"Please check the server before running tests."
    )


@pytest.mark.smoke
def test_00_server_has_version(
    api_client: requests.Session,
    health_endpoint: str
):
    """CRITICAL: Verify that the server has version information"""
    response = api_client.get(health_endpoint)
    data = response.json()
    
    assert "version" in data, "Health response missing 'version' field"
    assert len(data["version"]) > 0, "Version field is empty"


@pytest.mark.smoke
def test_00_server_api_root_is_accessible(
    api_client: requests.Session,
    root_endpoint: str
):
    """CRITICAL: Verify that the API root endpoint is accessible"""
    response = api_client.get(root_endpoint)
    
    assert response.status_code == 200, (
        f"API root not accessible. Expected 200 but got {response.status_code}"
    )


@pytest.mark.smoke
def test_00_server_api_has_expected_endpoints(
    api_client: requests.Session,
    root_endpoint: str
):
    """CRITICAL: Verify that the API has expected endpoints listed"""
    response = api_client.get(root_endpoint)
    data = response.json()
    
    assert "endpoints" in data, "API root missing 'endpoints' field"
    
    endpoints = data["endpoints"]
    
    # Check for critical endpoints
    assert "POST /api/v1/tts" in endpoints, (
        "TTS endpoint not listed! Is this the correct API version?"
    )
    assert "GET /api/v1/languages" in endpoints, (
        "Languages endpoint not listed! Is this the correct API version?"
    )


@pytest.mark.smoke  
def test_00_can_reach_host_from_container(
    api_base_url: str
):
    """CRITICAL: Verify that we can reach the host machine from test container"""
    import socket
    
    # Parse host and port from URL
    parts = api_base_url.replace("http://", "").replace("https://", "").split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 80
    
    # Try to connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        assert result == 0, (
            f"Cannot reach {host}:{port} from test container. "
            f"If running in Docker, ensure host.docker.internal is working or "
            f"use appropriate network configuration."
        )
    except Exception as e:
        pytest.fail(
            f"Network error when trying to reach {host}:{port}: {e}. "
            f"Check Docker network configuration."
        )

