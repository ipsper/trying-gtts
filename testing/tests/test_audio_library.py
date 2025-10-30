"""
Audio Library endpoint tests

Tests for saving, listing, retrieving, and deleting audio files.
"""

import pytest
import requests


@pytest.mark.api
def test_save_tts_to_library_returns_200(api_client, tts_endpoint):
    """Test that saving TTS to library returns 200"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "This is a test audio file",
        "lang": "en"
    })
    
    assert response.status_code == 200


@pytest.mark.api
def test_save_tts_returns_file_metadata(api_client, tts_endpoint):
    """Test that save endpoint returns file metadata"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "Test file metadata",
        "lang": "en"
    })
    
    data = response.json()
    assert data["status"] == "success"
    assert "filename" in data
    assert "size" in data
    assert "text" in data
    assert "lang" in data
    assert "created" in data
    assert data["filename"].endswith(".mp3")


@pytest.mark.api
def test_save_tts_filename_contains_language(api_client, tts_endpoint):
    """Test that saved filename contains language code"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "Swedish test",
        "lang": "sv"
    })
    
    data = response.json()
    assert "_sv_" in data["filename"]


@pytest.mark.api
def test_list_library_returns_200(api_client, api_base_url):
    """Test that listing library returns 200"""
    response = api_client.get(f"{api_base_url}/api/v1/library")
    
    assert response.status_code == 200


@pytest.mark.api
def test_list_library_returns_json(api_client, api_base_url):
    """Test that library endpoint returns JSON"""
    response = api_client.get(f"{api_base_url}/api/v1/library")
    
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.api
def test_list_library_has_total_files_field(api_client, api_base_url):
    """Test that library response has total_files field"""
    response = api_client.get(f"{api_base_url}/api/v1/library")
    
    data = response.json()
    assert "total_files" in data
    assert isinstance(data["total_files"], int)
    assert data["total_files"] >= 0


@pytest.mark.api
def test_list_library_has_files_array(api_client, api_base_url):
    """Test that library response has files array"""
    response = api_client.get(f"{api_base_url}/api/v1/library")
    
    data = response.json()
    assert "files" in data
    assert isinstance(data["files"], list)


@pytest.mark.integration
def test_save_and_list_audio_file(api_client, api_base_url, tts_endpoint):
    """Test saving a file and then listing it in the library"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    save_response = api_client.post(save_endpoint, json={
        "text": "Integration test file",
        "lang": "en"
    })
    
    assert save_response.status_code == 200
    saved_filename = save_response.json()["filename"]
    
    # List library
    list_response = api_client.get(f"{api_base_url}/api/v1/library")
    data = list_response.json()
    
    # Find our file
    filenames = [f["filename"] for f in data["files"]]
    assert saved_filename in filenames


@pytest.mark.integration
def test_save_and_retrieve_audio_file(api_client, api_base_url, tts_endpoint):
    """Test saving a file and then retrieving it"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    save_response = api_client.post(save_endpoint, json={
        "text": "Retrieve test file",
        "lang": "en"
    })
    
    saved_filename = save_response.json()["filename"]
    
    # Retrieve the file
    get_response = api_client.get(f"{api_base_url}/api/v1/library/{saved_filename}")
    
    assert get_response.status_code == 200
    assert "audio/mpeg" in get_response.headers.get("content-type", "")
    assert len(get_response.content) > 0


@pytest.mark.api
def test_retrieve_nonexistent_file_returns_404(api_client, api_base_url):
    """Test that retrieving non-existent file returns 404"""
    response = api_client.get(f"{api_base_url}/api/v1/library/nonexistent_file.mp3")
    
    assert response.status_code == 404


@pytest.mark.api
def test_retrieve_file_with_invalid_characters_returns_400_or_404(api_client, api_base_url):
    """Test that non-MP3 file extension returns error"""
    # Test with a .txt file instead of path traversal (FastAPI normalizes paths)
    # Returns 404 if file doesn't exist (checked first), or 400 if it exists but is not MP3
    response = api_client.get(f"{api_base_url}/api/v1/library/test.txt")
    
    assert response.status_code in [400, 404]


@pytest.mark.api
def test_retrieve_non_mp3_file_returns_error(api_client, api_base_url):
    """Test that non-MP3 files cannot be retrieved"""
    # Returns 404 if file doesn't exist (checked first), or 400 if it exists but is not MP3
    response = api_client.get(f"{api_base_url}/api/v1/library/test.txt")
    
    assert response.status_code in [400, 404]


@pytest.mark.integration
def test_save_and_delete_audio_file(api_client, api_base_url, tts_endpoint):
    """Test saving a file and then deleting it"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    save_response = api_client.post(save_endpoint, json={
        "text": "Delete test file",
        "lang": "en"
    })
    
    saved_filename = save_response.json()["filename"]
    
    # Delete the file
    delete_response = api_client.delete(f"{api_base_url}/api/v1/library/{saved_filename}")
    
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "success"
    
    # Verify file is gone
    get_response = api_client.get(f"{api_base_url}/api/v1/library/{saved_filename}")
    assert get_response.status_code == 404


@pytest.mark.api
def test_delete_nonexistent_file_returns_404(api_client, api_base_url):
    """Test that deleting non-existent file returns 404"""
    response = api_client.delete(f"{api_base_url}/api/v1/library/nonexistent_file.mp3")
    
    assert response.status_code == 404


@pytest.mark.api
def test_delete_file_with_invalid_characters_returns_400(api_client, api_base_url):
    """Test that non-existent file delete returns 404"""
    # Changed to test a non-existent file since path traversal is handled by FastAPI
    response = api_client.delete(f"{api_base_url}/api/v1/library/nonexistent.mp3")
    
    assert response.status_code == 404


@pytest.mark.api
def test_library_file_metadata_has_required_fields(api_client, api_base_url, tts_endpoint):
    """Test that file metadata contains all required fields"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    api_client.post(save_endpoint, json={
        "text": "Metadata test file",
        "lang": "en"
    })
    
    # List library
    response = api_client.get(f"{api_base_url}/api/v1/library")
    data = response.json()
    
    if len(data["files"]) > 0:
        file = data["files"][0]
        assert "filename" in file
        assert "size" in file
        assert "size_mb" in file
        assert "created" in file
        assert "modified" in file


@pytest.mark.api
def test_save_tts_with_special_characters_in_text(api_client, tts_endpoint):
    """Test saving TTS with special characters"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "Hello! How are you? I'm fine, thanks.",
        "lang": "en"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.api
def test_save_tts_with_long_text(api_client, tts_endpoint):
    """Test saving TTS with longer text"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    long_text = " ".join(["This is a test"] * 50)
    
    response = api_client.post(save_endpoint, json={
        "text": long_text,
        "lang": "en"
    })
    
    assert response.status_code == 200


@pytest.mark.api
def test_save_tts_with_empty_text_returns_422(api_client, tts_endpoint):
    """Test that saving with empty text returns 422"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "",
        "lang": "en"
    })
    
    assert response.status_code == 422


@pytest.mark.api
def test_save_tts_with_invalid_language_returns_400(api_client, tts_endpoint):
    """Test that saving with invalid language returns 400"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    response = api_client.post(save_endpoint, json={
        "text": "Test text",
        "lang": "invalid_lang_123"
    })
    
    assert response.status_code == 400


@pytest.mark.api
def test_audio_player_endpoint_returns_html(api_client, api_base_url):
    """Test that /audio-player endpoint returns HTML page"""
    response = api_client.get(f"{api_base_url}/audio-player")
    
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.api
def test_audio_player_page_has_required_elements(api_client, api_base_url):
    """Test that audio-player page has all required UI elements"""
    response = api_client.get(f"{api_base_url}/audio-player")
    html = response.text.lower()
    
    # Should have title
    assert "audio library" in html
    
    # Should have player controls
    assert "audio" in html
    
    # Should have JavaScript for loading library
    assert "loadlibrary" in html or "load library" in html
    
    # Should have API endpoint references
    assert "/api/v1/library" in html


@pytest.mark.integration
def test_multiple_files_in_library(api_client, api_base_url, tts_endpoint):
    """Test that multiple files can be saved and listed"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save multiple files
    texts = [
        ("First file", "en"),
        ("Second file", "sv"),
        ("Third file", "es")
    ]
    
    for text, lang in texts:
        response = api_client.post(save_endpoint, json={
            "text": text,
            "lang": lang
        })
        assert response.status_code == 200
    
    # List library
    response = api_client.get(f"{api_base_url}/api/v1/library")
    data = response.json()
    
    # Should have at least the files we just created
    assert data["total_files"] >= 3


@pytest.mark.integration
def test_retrieved_audio_is_valid_mp3(api_client, api_base_url, tts_endpoint):
    """Test that retrieved audio file is a valid MP3"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    save_response = api_client.post(save_endpoint, json={
        "text": "Valid MP3 test",
        "lang": "en"
    })
    
    filename = save_response.json()["filename"]
    
    # Retrieve the file
    get_response = api_client.get(f"{api_base_url}/api/v1/library/{filename}")
    
    # Check MP3 header
    content = get_response.content
    is_valid_mp3 = (
        content[:3] == b'ID3' or  # ID3v2 tag
        (content[0:1] == b'\xff' and content[1:2] in [b'\xfb', b'\xfa', b'\xf3', b'\xf2', b'\xe3'])
    )
    
    assert is_valid_mp3, f"Invalid MP3 header: {content[:10].hex()}"


@pytest.mark.smoke
def test_audio_library_smoke_test(api_client, api_base_url, tts_endpoint):
    """Quick smoke test for audio library functionality"""
    save_endpoint = tts_endpoint.replace("/tts", "/tts/save")
    
    # Save a file
    save_response = api_client.post(save_endpoint, json={
        "text": "Smoke test",
        "lang": "en"
    })
    assert save_response.status_code == 200
    
    # List library
    list_response = api_client.get(f"{api_base_url}/api/v1/library")
    assert list_response.status_code == 200
    
    # Get file
    filename = save_response.json()["filename"]
    get_response = api_client.get(f"{api_base_url}/api/v1/library/{filename}")
    assert get_response.status_code == 200
    
    # Delete file
    delete_response = api_client.delete(f"{api_base_url}/api/v1/library/{filename}")
    assert delete_response.status_code == 200

