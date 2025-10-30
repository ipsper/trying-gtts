"""
Integration tests - testing complete workflows
"""
import pytest
import requests


@pytest.mark.integration
def test_health_check_passes_before_using_api(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that health check passes before using API"""
    health_response = api_client.get(f"{api_base_url}/health")
    
    assert health_response.status_code == 200


@pytest.mark.integration
def test_can_get_languages_list(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that we can retrieve languages list"""
    lang_response = api_client.get(languages_endpoint)
    
    assert lang_response.status_code == 200
    assert "languages" in lang_response.json()


@pytest.mark.integration
def test_can_generate_speech_for_listed_language(
    api_client: requests.Session, 
    languages_endpoint: str,
    tts_endpoint: str
):
    """Test that we can generate speech for a language from the list"""
    # Get languages
    lang_response = api_client.get(languages_endpoint)
    languages = lang_response.json()["languages"]
    
    # Verify English is supported
    assert "en" in languages
    
    # Generate speech for English
    tts_payload = {"text": "Hello world!", "lang": "en"}
    tts_response = api_client.post(tts_endpoint, json=tts_payload)
    
    assert tts_response.status_code == 200
    assert len(tts_response.content) > 0


@pytest.mark.integration
def test_multiple_sequential_tts_requests_all_succeed(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that multiple sequential TTS requests all succeed"""
    test_cases = [
        ("Hello world!", "en"),
        ("Hej världen!", "sv"),
        ("Bonjour le monde!", "fr"),
    ]
    
    for text, lang in test_cases:
        payload = {"text": text, "lang": lang}
        response = api_client.post(tts_endpoint, json=payload)
        
        assert response.status_code == 200, f"Failed for {lang}: {text}"
        assert len(response.content) > 0


@pytest.mark.integration
def test_swagger_ui_is_accessible(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that Swagger UI documentation is accessible"""
    swagger_response = api_client.get(f"{api_base_url}/docs")
    
    assert swagger_response.status_code == 200


@pytest.mark.integration
def test_redoc_documentation_is_accessible(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that ReDoc documentation is accessible"""
    redoc_response = api_client.get(f"{api_base_url}/redoc")
    
    assert redoc_response.status_code == 200


@pytest.mark.integration
def test_openapi_json_is_accessible(
    api_client: requests.Session, 
    api_base_url: str
):
    """Test that OpenAPI JSON schema is accessible"""
    openapi_response = api_client.get(f"{api_base_url}/openapi.json")
    
    assert openapi_response.status_code == 200
    assert "application/json" in openapi_response.headers["Content-Type"]


@pytest.mark.integration
def test_api_recovers_after_validation_error(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that API continues to work after encountering validation error"""
    # Send invalid request
    invalid_payload = {"text": "", "lang": "en"}
    error_response = api_client.post(tts_endpoint, json=invalid_payload)
    assert error_response.status_code == 422
    
    # Send valid request immediately after
    valid_payload = {"text": "Hello world!", "lang": "en"}
    success_response = api_client.post(tts_endpoint, json=valid_payload)
    
    assert success_response.status_code == 200


@pytest.mark.integration
def test_api_recovers_after_invalid_language_error(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that API continues to work after invalid language error"""
    # Send request with invalid language
    invalid_payload = {"text": "Hello", "lang": "invalid"}
    error_response = api_client.post(tts_endpoint, json=invalid_payload)
    assert error_response.status_code == 400
    
    # Send valid request
    valid_payload = {"text": "Hello world!", "lang": "en"}
    success_response = api_client.post(tts_endpoint, json=valid_payload)
    
    assert success_response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
def test_api_handles_rapid_sequential_requests(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that API handles rapid sequential requests successfully"""
    payload = {"text": "Quick test.", "lang": "en"}
    
    # Send 10 rapid requests
    for i in range(10):
        response = api_client.post(tts_endpoint, json=payload)
        assert response.status_code == 200, f"Request {i+1} failed"


@pytest.mark.integration
def test_english_tts_request_generates_audio(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test complete English TTS workflow generates audio"""
    payload = {"text": "This is a test.", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mpeg"
    assert len(response.content) > 0


@pytest.mark.integration
def test_swedish_tts_request_generates_audio(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test complete Swedish TTS workflow generates audio"""
    payload = {"text": "Detta är ett test.", "lang": "sv"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mpeg"
    assert len(response.content) > 0


@pytest.mark.integration
def test_multiline_tts_request_generates_audio(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test complete multi-line TTS workflow generates audio"""
    payload = {"text": "Line one.\nLine two.\nLine three.", "lang": "en"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mpeg"
    assert len(response.content) > 0
