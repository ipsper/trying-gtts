"""
Error handling tests
"""
import pytest
import requests


@pytest.mark.error
def test_tts_with_invalid_language_code_returns_400(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that invalid language code returns HTTP 400"""
    payload = {
        "text": "Hello world",
        "lang": "invalid_language_code_12345"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 400


@pytest.mark.error
def test_invalid_language_error_response_has_detail_field(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that error response contains 'detail' field"""
    payload = {
        "text": "Hello world",
        "lang": "invalid"
    }
    response = api_client.post(tts_endpoint, json=payload)
    data = response.json()
    
    assert "detail" in data


@pytest.mark.error
def test_invalid_language_error_response_is_json(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that error response is JSON"""
    payload = {
        "text": "Hello world",
        "lang": "invalid"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.error
def test_nonexistent_endpoint_returns_404(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that nonexistent endpoint returns HTTP 404"""
    response = api_client.get(f"{api_base_url}/api/v1/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.error
def test_tts_endpoint_with_get_method_returns_405(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that GET request to TTS endpoint returns HTTP 405 (Method Not Allowed)"""
    response = api_client.get(tts_endpoint)
    
    assert response.status_code == 405


@pytest.mark.error
def test_tts_with_form_encoded_data_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that form-encoded data instead of JSON returns HTTP 422"""
    response = api_client.post(
        tts_endpoint,
        data="text=hello&lang=en",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 422


@pytest.mark.error
def test_tts_with_commonly_mistaken_swedish_code_returns_error(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that 'se' (common mistake for Swedish) returns error - should be 'sv'"""
    payload = {
        "text": "Hej världen",
        "lang": "se"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    # Should return 400 or 422 error
    assert response.status_code in [400, 422]


@pytest.mark.error
def test_error_response_for_wrong_method_is_json(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that wrong method error response is JSON"""
    response = api_client.get(tts_endpoint)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.error  
def test_error_response_for_404_is_json(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that 404 error response is JSON"""
    response = api_client.get(f"{api_base_url}/api/v1/nonexistent")
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.error
def test_invalid_language_code_detail_mentions_language(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that invalid language error message mentions language"""
    payload = {
        "text": "Hello world",
        "lang": "invalid"
    }
    response = api_client.post(tts_endpoint, json=payload)
    data = response.json()
    detail = str(data.get("detail", "")).lower()
    
    # Error message should mention language or speech
    assert "language" in detail or "speech" in detail
