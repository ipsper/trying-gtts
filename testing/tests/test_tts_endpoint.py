"""
Text-to-Speech endpoint tests
"""
import pytest
import requests


@pytest.mark.api
def test_tts_with_valid_english_payload_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_tts_payload: dict
):
    """Test that valid English TTS request returns HTTP 200"""
    response = api_client.post(tts_endpoint, json=valid_tts_payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_returns_audio_mpeg_content_type(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_tts_payload: dict
):
    """Test that TTS returns audio/mpeg content type"""
    response = api_client.post(tts_endpoint, json=valid_tts_payload)
    
    assert response.headers["Content-Type"] == "audio/mpeg"


@pytest.mark.api
def test_tts_returns_non_empty_audio_data(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_tts_payload: dict
):
    """Test that TTS returns non-empty audio data"""
    response = api_client.post(tts_endpoint, json=valid_tts_payload)
    
    assert len(response.content) > 0


@pytest.mark.api
def test_tts_audio_data_starts_with_valid_mp3_header(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_tts_payload: dict
):
    """Test that audio data starts with valid MP3 header (ID3 or FF FB)"""
    response = api_client.post(tts_endpoint, json=valid_tts_payload)
    
    # MP3 files start with ID3 tag or MPEG sync bytes
    is_valid_mp3 = (
        response.content[:3] == b'ID3' or 
        response.content[0:2] == b'\xff\xfb'
    )
    
    assert is_valid_mp3


@pytest.mark.api
def test_tts_with_swedish_language_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_swedish_payload: dict
):
    """Test that Swedish TTS request returns HTTP 200"""
    response = api_client.post(tts_endpoint, json=valid_swedish_payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_with_swedish_language_returns_audio(
    api_client: requests.Session, 
    tts_endpoint: str, 
    valid_swedish_payload: dict
):
    """Test that Swedish TTS returns audio data"""
    response = api_client.post(tts_endpoint, json=valid_swedish_payload)
    
    assert response.headers["Content-Type"] == "audio/mpeg"
    assert len(response.content) > 0


@pytest.mark.api
def test_tts_with_multiline_text_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str, 
    multiline_payload: dict
):
    """Test that multi-line text TTS request returns HTTP 200"""
    response = api_client.post(tts_endpoint, json=multiline_payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_with_multiline_text_returns_audio(
    api_client: requests.Session, 
    tts_endpoint: str, 
    multiline_payload: dict
):
    """Test that multi-line text TTS returns audio data"""
    response = api_client.post(tts_endpoint, json=multiline_payload)
    
    assert len(response.content) > 0


@pytest.mark.api
def test_tts_uses_default_language_when_not_specified(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that TTS uses default language when lang not provided"""
    payload = {"text": "Hello world!"}
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_with_special_characters_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that TTS handles special characters correctly"""
    payload = {
        "text": "Hello! How are you? I'm fine, thanks.",
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_with_unicode_characters_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that TTS handles Unicode characters"""
    payload = {
        "text": "Héllo Wörld! 你好 Привет",
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.api
def test_tts_with_unicode_characters_returns_audio(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that Unicode text TTS returns audio"""
    payload = {
        "text": "Héllo Wörld! 你好 Привет",
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert len(response.content) > 0


@pytest.mark.api
@pytest.mark.slow
def test_tts_with_long_text_within_limit_returns_200(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that TTS handles long text (within 5000 char limit)"""
    long_text = "This is a test sentence. " * 100  # ~2500 characters
    payload = {
        "text": long_text,
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.slow
def test_tts_with_long_text_returns_audio(
    api_client: requests.Session, 
    tts_endpoint: str
):
    """Test that long text TTS returns audio data"""
    long_text = "This is a test sentence. " * 100
    payload = {
        "text": long_text,
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert len(response.content) > 0
