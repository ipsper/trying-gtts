"""
Languages endpoint tests
"""
import pytest
import requests


@pytest.mark.api
def test_languages_endpoint_returns_200_status_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that languages endpoint returns HTTP 200 OK"""
    response = api_client.get(languages_endpoint)
    
    assert response.status_code == 200


@pytest.mark.api
def test_languages_endpoint_returns_json_content_type(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that languages endpoint returns JSON"""
    response = api_client.get(languages_endpoint)
    
    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.api
def test_languages_response_has_languages_field(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that response contains 'languages' field"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    
    assert "languages" in data


@pytest.mark.api
def test_languages_field_is_dictionary(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that languages field is a dictionary"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert isinstance(languages, dict)


@pytest.mark.api
def test_languages_contains_swedish_language_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that Swedish (sv) is in supported languages"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert "sv" in languages


@pytest.mark.api
def test_languages_contains_english_language_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that English (en) is in supported languages"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert "en" in languages


@pytest.mark.api
def test_languages_contains_spanish_language_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that Spanish (es) is in supported languages"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert "es" in languages


@pytest.mark.api
def test_languages_contains_french_language_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that French (fr) is in supported languages"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert "fr" in languages


@pytest.mark.api
def test_languages_contains_german_language_code(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that German (de) is in supported languages"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    assert "de" in languages


@pytest.mark.api
def test_language_codes_are_strings(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that all language codes are strings"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    for code in languages.keys():
        assert isinstance(code, str)


@pytest.mark.api
def test_language_names_are_strings(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that all language names are strings"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    for name in languages.values():
        assert isinstance(name, str)


@pytest.mark.api
def test_language_names_are_not_empty(
    api_client: requests.Session, 
    languages_endpoint: str
):
    """Test that all language names are non-empty"""
    response = api_client.get(languages_endpoint)
    data = response.json()
    languages = data["languages"]
    
    for code, name in languages.items():
        assert len(name) > 0, f"Language name for {code} is empty"
