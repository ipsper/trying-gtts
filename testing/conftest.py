"""
Pytest configuration and fixtures for gTTS API testing
"""
import os
import pytest
import requests
from typing import Generator

# API Configuration
# Use host.docker.internal to reach host machine from Docker container
API_HOST = os.getenv("API_HOST", "host.docker.internal")
API_PORT = os.getenv("API_PORT", "8088")
BASE_URL = f"http://{API_HOST}:{API_PORT}"


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for the API"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_client(api_base_url: str) -> Generator[requests.Session, None, None]:
    """
    HTTP client for making API requests
    
    This fixture verifies that:
    1. The API is reachable
    2. It's the correct gTTS API service
    3. The service is healthy
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    # Wait for API to be ready and verify it's our service
    max_retries = 30
    for i in range(max_retries):
        try:
            response = session.get(f"{api_base_url}/health", timeout=2)
            if response.status_code == 200:
                health_data = response.json()
                
                # CRITICAL: Verify this is the gTTS API
                if health_data.get("service") != "gTTS API":
                    pytest.fail(
                        f"Wrong service at {api_base_url}! "
                        f"Expected 'gTTS API' but got '{health_data.get('service')}'. "
                        f"Please ensure the correct API is running."
                    )
                
                # Verify it's healthy
                if health_data.get("status") != "healthy":
                    pytest.fail(
                        f"API at {api_base_url} is not healthy! "
                        f"Status: {health_data.get('status')}"
                    )
                
                print(f"\n✓ Verified gTTS API is ready at {api_base_url}")
                print(f"  Service: {health_data.get('service')}")
                print(f"  Version: {health_data.get('version')}")
                print(f"  Status: {health_data.get('status')}")
                break
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                pytest.fail(
                    f"Cannot reach API at {api_base_url} after {max_retries} attempts. "
                    f"Error: {e}. Please ensure the API is running on the host."
                )
            import time
            time.sleep(1)
    
    yield session
    session.close()


@pytest.fixture
def tts_endpoint(api_base_url: str) -> str:
    """TTS endpoint URL"""
    return f"{api_base_url}/api/v1/tts"


@pytest.fixture
def languages_endpoint(api_base_url: str) -> str:
    """Languages endpoint URL"""
    return f"{api_base_url}/api/v1/languages"


@pytest.fixture
def health_endpoint(api_base_url: str) -> str:
    """Health check endpoint URL"""
    return f"{api_base_url}/health"


@pytest.fixture
def root_endpoint(api_base_url: str) -> str:
    """Root API endpoint URL"""
    return f"{api_base_url}/api/v1/"


@pytest.fixture
def valid_tts_payload() -> dict:
    """Valid TTS request payload"""
    return {
        "text": "Hello, this is a test message.",
        "lang": "en"
    }


@pytest.fixture
def valid_swedish_payload() -> dict:
    """Valid Swedish TTS request payload"""
    return {
        "text": "Hej, detta är ett testmeddelande.",
        "lang": "sv"
    }


@pytest.fixture
def multiline_payload() -> dict:
    """Valid multi-line TTS request payload"""
    return {
        "text": "Line one.\nLine two.\nLine three.",
        "lang": "en"
    }


# Pytest hooks
def pytest_configure(config):
    """Called after command line options have been parsed"""
    print(f"\n{'='*60}")
    print(f"gTTS API Test Suite")
    print(f"{'='*60}")
    print(f"API URL: {BASE_URL}")
    print(f"{'='*60}\n")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print(f"\n{'='*60}")
    print(f"Test session finished with status: {exitstatus}")
    print(f"{'='*60}\n")

