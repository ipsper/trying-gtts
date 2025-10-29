"""
Input validation tests
"""
import pytest
import requests


@pytest.mark.validation
def test_tts_with_empty_text_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that empty text returns HTTP 422 validation error"""
    payload = {"text": "", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 422


@pytest.mark.validation
def test_tts_with_whitespace_only_text_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that whitespace-only text returns HTTP 422"""
    payload = {"text": "   ", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 422


@pytest.mark.validation
def test_tts_without_text_field_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that missing text field returns HTTP 422"""
    payload = {"lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 422


@pytest.mark.validation
def test_tts_with_text_over_5000_characters_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that text over 5000 characters returns HTTP 422"""
    payload = {
        "text": "a" * 5001,  # 5001 characters
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 422


@pytest.mark.validation
def test_tts_with_invalid_json_returns_422(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that invalid JSON returns HTTP 422"""
    response = api_client.post(
        tts_endpoint, 
        data="this is not valid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 422


@pytest.mark.validation
def test_validation_error_response_has_detail_field(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that validation errors contain 'detail' field"""
    payload = {"text": "", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    data = response.json()
    
    assert response.status_code == 422
    assert "detail" in data


@pytest.mark.validation
def test_tts_with_minimum_text_length_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that minimum text length (1 character) is accepted"""
    payload = {"text": "a", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.validation
def test_tts_with_maximum_text_length_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that maximum text length (5000 characters) is accepted"""
    payload = {
        "text": "a" * 5000,
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.validation
def test_empty_text_error_response_is_json(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that validation error response is JSON"""
    payload = {"text": "", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.validation
def test_text_over_limit_error_response_is_json(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that text over limit error is JSON"""
    payload = {"text": "a" * 5001, "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.validation
def test_missing_text_field_error_response_is_json(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that missing field error is JSON"""
    payload = {"lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert "application/json" in response.headers["Content-Type"]
