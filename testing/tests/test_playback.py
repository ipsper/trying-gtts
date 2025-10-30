"""
Playback tests - saves audio files for manual listening

Run with: pytest -m playback
Or: ./run_tests.sh && ./play_audio.sh
"""

import pytest
import requests
from pathlib import Path


@pytest.mark.playback
def test_english_greeting_playback(api_client, tts_endpoint, audio_output_dir):
    """Generate English greeting for playback"""
    response = api_client.post(tts_endpoint, json={
        "text": "Hello! Welcome to the text-to-speech API. This is a test of English audio output.",
        "lang": "en"
    })
    
    assert response.status_code == 200
    
    # Save audio for playback
    output_file = audio_output_dir / "01_english_greeting.mp3"
    output_file.write_bytes(response.content)
    print(f"\n   Saved: {output_file.name}")


@pytest.mark.playback
def test_swedish_greeting_playback(api_client, tts_endpoint, audio_output_dir):
    """Generate Swedish greeting for playback"""
    response = api_client.post(tts_endpoint, json={
        "text": "Hej! Välkommen till text-till-tal API:et. Detta är ett test av svensk ljudutmatning.",
        "lang": "sv"
    })
    
    assert response.status_code == 200
    
    output_file = audio_output_dir / "02_swedish_greeting.mp3"
    output_file.write_bytes(response.content)
    print(f"\n   Saved: {output_file.name}")


@pytest.mark.playback
def test_spanish_greeting_playback(api_client, tts_endpoint, audio_output_dir):
    """Generate Spanish greeting for playback"""
    response = api_client.post(tts_endpoint, json={
        "text": "¡Hola! Bienvenido a la API de texto a voz. Esta es una prueba de salida de audio en español.",
        "lang": "es"
    })
    
    assert response.status_code == 200
    
    output_file = audio_output_dir / "03_spanish_greeting.mp3"
    output_file.write_bytes(response.content)
    print(f"\n   Saved: {output_file.name}")


@pytest.mark.playback
def test_multilingual_demo_playback(api_client, tts_endpoint, audio_output_dir):
    """Generate demo in multiple languages"""
    
    languages = [
        ("en", "Thank you for using our API", "04_english_thanks.mp3"),
        ("sv", "Tack för att du använder vårt API", "05_swedish_thanks.mp3"),
        ("fr", "Merci d'utiliser notre API", "06_french_thanks.mp3"),
        ("de", "Vielen Dank für die Nutzung unserer API", "07_german_thanks.mp3"),
    ]
    
    for lang, text, filename in languages:
        response = api_client.post(tts_endpoint, json={
            "text": text,
            "lang": lang
        })
        
        assert response.status_code == 200
        
        output_file = audio_output_dir / filename
        output_file.write_bytes(response.content)
        print(f"\n   Saved: {filename}")


@pytest.mark.playback
def test_long_text_playback(api_client, tts_endpoint, audio_output_dir):
    """Generate longer text for playback"""
    long_text = """
    This is a longer text to speech example. 
    It demonstrates how the API handles multiple sentences. 
    The text-to-speech engine converts this entire paragraph into speech.
    You can use this to test the quality and naturalness of the generated audio.
    """
    
    response = api_client.post(tts_endpoint, json={
        "text": long_text,
        "lang": "en"
    })
    
    assert response.status_code == 200
    
    output_file = audio_output_dir / "08_long_text_demo.mp3"
    output_file.write_bytes(response.content)
    print(f"\n   Saved: {output_file.name}")

