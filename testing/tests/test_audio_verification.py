"""
Audio verification tests - validates audio quality and properties

Tests audio files programmatically without requiring actual playback.
Verifies duration, format, volume, and other technical properties.
"""

import pytest
import requests
import io
from pydub import AudioSegment


@pytest.mark.audio
def test_audio_has_valid_duration(api_client, tts_endpoint):
    """Verify audio file has measurable duration"""
    response = api_client.post(tts_endpoint, json={
        "text": "This is a test sentence.",
        "lang": "en"
    })
    
    assert response.status_code == 200
    
    # Load MP3 from bytes
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Verify audio has duration
    assert len(audio) > 0, "Audio has no duration"
    assert len(audio) > 500, f"Audio too short: {len(audio)}ms (expected > 500ms)"


@pytest.mark.audio
def test_audio_technical_properties(api_client, tts_endpoint):
    """Verify audio has correct technical properties"""
    response = api_client.post(tts_endpoint, json={
        "text": "Hello world",
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Verify sample rate (gTTS typically uses 24kHz)
    assert audio.frame_rate >= 16000, f"Sample rate too low: {audio.frame_rate}Hz"
    assert audio.frame_rate <= 48000, f"Sample rate too high: {audio.frame_rate}Hz"
    
    # Verify channels (mono or stereo)
    assert audio.channels in [1, 2], f"Invalid channel count: {audio.channels}"
    
    # Verify sample width (bit depth)
    assert audio.sample_width in [1, 2, 3, 4], f"Invalid sample width: {audio.sample_width}"
    
    # Verify duration
    assert len(audio) > 0, "No audio data"


@pytest.mark.audio
def test_audio_is_not_silent(api_client, tts_endpoint):
    """Verify audio contains actual sound (not silence)"""
    response = api_client.post(tts_endpoint, json={
        "text": "Test audio verification",
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Verify RMS (Root Mean Square) - audio volume
    rms = audio.rms
    assert rms > 50, f"Audio too quiet (RMS: {rms}), might be silent or corrupted"
    
    # Verify dBFS (decibels relative to full scale)
    # -60 dBFS is very quiet, normal speech is around -20 to -10 dBFS
    assert audio.dBFS > -60, f"Audio too quiet ({audio.dBFS:.1f} dBFS), might be silent"


@pytest.mark.audio
def test_audio_duration_matches_text_length(api_client, tts_endpoint):
    """Verify audio duration roughly matches text length"""
    text = "This is a test sentence with several words."
    
    response = api_client.post(tts_endpoint, json={
        "text": text,
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Rough estimate: ~150 words per minute for TTS
    # = 2.5 words per second = 400ms per word
    word_count = len(text.split())
    expected_min_duration_ms = word_count * 250  # 250ms per word (minimum)
    expected_max_duration_ms = word_count * 800  # 800ms per word (maximum)
    
    actual_duration = len(audio)
    
    assert actual_duration >= expected_min_duration_ms, \
        f"Audio too short: {actual_duration}ms for {word_count} words (expected >= {expected_min_duration_ms}ms)"
    assert actual_duration <= expected_max_duration_ms, \
        f"Audio too long: {actual_duration}ms for {word_count} words (expected <= {expected_max_duration_ms}ms)"


@pytest.mark.audio
def test_longer_text_produces_longer_audio(api_client, tts_endpoint):
    """Verify longer text produces proportionally longer audio"""
    short_text = "Hello"
    long_text = "This is a much longer sentence with many more words to speak."
    
    short_response = api_client.post(tts_endpoint, json={
        "text": short_text,
        "lang": "en"
    })
    long_response = api_client.post(tts_endpoint, json={
        "text": long_text,
        "lang": "en"
    })
    
    short_audio = AudioSegment.from_mp3(io.BytesIO(short_response.content))
    long_audio = AudioSegment.from_mp3(io.BytesIO(long_response.content))
    
    # Long text should produce significantly longer audio
    assert len(long_audio) > len(short_audio) * 2, \
        f"Long audio ({len(long_audio)}ms) not significantly longer than short ({len(short_audio)}ms)"


@pytest.mark.audio
def test_different_languages_produce_different_audio(api_client, tts_endpoint):
    """Verify different languages produce different audio output"""
    # Same meaning, different languages
    english = api_client.post(tts_endpoint, json={
        "text": "Hello, how are you?",
        "lang": "en"
    })
    swedish = api_client.post(tts_endpoint, json={
        "text": "Hej, hur mår du?",
        "lang": "sv"
    })
    
    # Audio content should be different
    assert english.content != swedish.content, "Different languages produced identical audio"
    
    # Both should have valid audio
    en_audio = AudioSegment.from_mp3(io.BytesIO(english.content))
    sv_audio = AudioSegment.from_mp3(io.BytesIO(swedish.content))
    
    assert en_audio.rms > 50, "English audio too quiet"
    assert sv_audio.rms > 50, "Swedish audio too quiet"
    
    # Both should have reasonable durations
    assert len(en_audio) > 500, "English audio too short"
    assert len(sv_audio) > 500, "Swedish audio too short"


@pytest.mark.audio
def test_same_text_produces_consistent_audio_length(api_client, tts_endpoint):
    """Verify same text produces consistent audio length"""
    text = "This is a consistency test."
    
    # Generate audio twice
    response1 = api_client.post(tts_endpoint, json={
        "text": text,
        "lang": "en"
    })
    response2 = api_client.post(tts_endpoint, json={
        "text": text,
        "lang": "en"
    })
    
    audio1 = AudioSegment.from_mp3(io.BytesIO(response1.content))
    audio2 = AudioSegment.from_mp3(io.BytesIO(response2.content))
    
    # Duration should be very similar (within 10% tolerance)
    duration_diff = abs(len(audio1) - len(audio2))
    tolerance = len(audio1) * 0.1  # 10% tolerance
    
    assert duration_diff <= tolerance, \
        f"Audio durations inconsistent: {len(audio1)}ms vs {len(audio2)}ms (diff: {duration_diff}ms)"


@pytest.mark.audio
def test_special_characters_dont_break_audio(api_client, tts_endpoint):
    """Verify special characters in text produce valid audio"""
    text = "Hello! How are you? I'm fine, thanks. Numbers: 1, 2, 3."
    
    response = api_client.post(tts_endpoint, json={
        "text": text,
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Audio should still be valid
    assert len(audio) > 0, "No audio generated from text with special characters"
    assert audio.rms > 50, "Audio with special characters too quiet"


@pytest.mark.audio
def test_multiline_text_produces_longer_audio(api_client, tts_endpoint):
    """Verify multiline text produces appropriate audio length"""
    text = """This is the first line.
This is the second line.
This is the third line."""
    
    response = api_client.post(tts_endpoint, json={
        "text": text,
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Count total words
    word_count = len(text.replace('\n', ' ').split())
    expected_min_duration = word_count * 250  # 250ms per word
    
    assert len(audio) >= expected_min_duration, \
        f"Multiline audio too short: {len(audio)}ms for {word_count} words"
    assert audio.rms > 50, "Multiline audio too quiet"


@pytest.mark.audio
def test_audio_format_is_valid_mp3(api_client, tts_endpoint):
    """Verify returned audio is a valid MP3 file"""
    response = api_client.post(tts_endpoint, json={
        "text": "Format verification test",
        "lang": "en"
    })
    
    # Should be able to load as MP3 without errors
    try:
        audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    except Exception as e:
        pytest.fail(f"Failed to load audio as MP3: {e}")
    
    # Verify it has content
    assert len(audio) > 0, "MP3 loaded but has no duration"
    assert len(response.content) > 1000, "MP3 file too small (< 1KB)"


@pytest.mark.audio
@pytest.mark.slow
@pytest.mark.timeout(60)
def test_long_text_audio_quality(api_client, tts_endpoint):
    """Verify long text produces good quality audio"""
    long_text = " ".join(["This is sentence number " + str(i) + "." for i in range(1, 11)])
    
    response = api_client.post(tts_endpoint, json={
        "text": long_text,
        "lang": "en"
    })
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    
    # Should have substantial duration
    assert len(audio) > 5000, f"Long text audio too short: {len(audio)}ms"
    
    # Should maintain good volume throughout
    assert audio.rms > 50, "Long text audio too quiet"
    
    # Check that audio doesn't degrade at the end by comparing first and last 2 seconds
    first_segment = audio[:2000]
    last_segment = audio[-2000:]
    
    first_rms = first_segment.rms
    last_rms = last_segment.rms
    
    # RMS shouldn't drop significantly at the end
    assert last_rms > first_rms * 0.5, \
        f"Audio quality degraded at end (first RMS: {first_rms}, last RMS: {last_rms})"


@pytest.mark.audio
def test_multiple_languages_all_produce_valid_audio(api_client, tts_endpoint):
    """Verify multiple languages all produce valid audio"""
    languages = [
        ("en", "Hello world"),
        ("sv", "Hej världen"),
        ("es", "Hola mundo"),
        ("fr", "Bonjour le monde"),
        ("de", "Hallo Welt"),
    ]
    
    for lang, text in languages:
        response = api_client.post(tts_endpoint, json={
            "text": text,
            "lang": lang
        })
        
        audio = AudioSegment.from_mp3(io.BytesIO(response.content))
        
        assert len(audio) > 500, f"{lang}: Audio too short"
        assert audio.rms > 50, f"{lang}: Audio too quiet"
        assert audio.frame_rate >= 16000, f"{lang}: Sample rate too low"


@pytest.mark.audio
@pytest.mark.smoke
def test_audio_verification_smoke_test(api_client, tts_endpoint):
    """Quick smoke test for audio verification"""
    response = api_client.post(tts_endpoint, json={
        "text": "Smoke test",
        "lang": "en"
    })
    
    assert response.status_code == 200
    
    # Quick basic checks
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    assert len(audio) > 0, "No audio"
    assert audio.rms > 0, "Silent audio"
    assert audio.frame_rate > 0, "Invalid sample rate"

