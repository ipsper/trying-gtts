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
    """Test that audio data starts with valid MP3 header (ID3 or MPEG sync bytes)"""
    response = api_client.post(tts_endpoint, json=valid_tts_payload)
    
    # MP3 files can start with:
    # - ID3 tag (ID3v2)
    # - MPEG frame sync (0xFF followed by 0xFB, 0xFA, 0xF3, 0xF2, or 0xE3)
    first_byte = response.content[0:1]
    second_byte = response.content[1:2] if len(response.content) > 1 else b''
    
    is_valid_mp3 = (
        response.content[:3] == b'ID3' or  # ID3v2 tag
        (first_byte == b'\xff' and second_byte in [b'\xfb', b'\xfa', b'\xf3', b'\xf2', b'\xe3'])  # MPEG sync
    )
    
    assert is_valid_mp3, f"Invalid MP3 header: {response.content[:10].hex()}"


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
    # Reduced from 100 to 30 repetitions to avoid timeout
    long_text = "This is a test sentence. " * 30
    payload = {
        "text": long_text,
        "lang": "en"
    }
    response = api_client.post(tts_endpoint, json=payload)
    
    assert len(response.content) > 0
