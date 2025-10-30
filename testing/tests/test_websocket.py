"""
WebSocket TTS endpoint tests

Tests for real-time audio streaming via WebSocket.
"""

import pytest
import json
import asyncio
import websockets


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_connection_establishes(websocket_url):
    """Test that WebSocket connection can be established"""
    async with websockets.connect(websocket_url) as websocket:
        assert websocket is not None
        assert websocket.open


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_accepts_valid_tts_request(websocket_url):
    """Test that WebSocket accepts and processes valid TTS request"""
    async with websockets.connect(websocket_url) as websocket:
        # Send TTS request
        await websocket.send(json.dumps({
            "text": "Hello, this is a test",
            "lang": "en"
        }))
        
        # Should receive generating status
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"
        assert "message" in message


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_streams_audio_after_ready(websocket_url):
    """Test that WebSocket sends ready message and then audio chunks"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "Test audio streaming",
            "lang": "en"
        }))
        
        # Track what we receive
        generating_received = False
        ready_received = False
        audio_chunks_received = 0
        complete_received = False
        
        # Receive messages with timeout
        try:
            async with asyncio.timeout(10):
                while not complete_received:
                    message = await websocket.recv()
                    
                    # Try to parse as JSON
                    if isinstance(message, str):
                        data = json.loads(message)
                        
                        if data["status"] == "generating":
                            generating_received = True
                        elif data["status"] == "ready":
                            ready_received = True
                            assert "size" in data
                        elif data["status"] == "complete":
                            complete_received = True
                    else:
                        # Binary audio chunk
                        audio_chunks_received += 1
        except asyncio.TimeoutError:
            pass
        
        assert generating_received, "Should receive 'generating' status"
        assert ready_received, "Should receive 'ready' status"
        assert audio_chunks_received > 0, "Should receive audio chunks"
        assert complete_received, "Should receive 'complete' status"


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_rejects_empty_text(websocket_url):
    """Test that WebSocket rejects requests with empty text"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "",
            "lang": "en"
        }))
        
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "error"
        assert "empty" in message["error"].lower()


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_rejects_whitespace_only_text(websocket_url):
    """Test that WebSocket rejects requests with whitespace-only text"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "   ",
            "lang": "en"
        }))
        
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "error"
        assert "empty" in message["error"].lower()


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_handles_invalid_language_gracefully(websocket_url):
    """Test that WebSocket handles invalid language codes"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "Test with invalid language",
            "lang": "invalid_lang_123"
        }))
        
        # Should receive generating message first
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"
        
        # Then should receive ready or error
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] in ["ready", "error"]


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_handles_multiple_requests(websocket_url):
    """Test that WebSocket can handle multiple sequential requests"""
    async with websockets.connect(websocket_url) as websocket:
        # First request
        await websocket.send(json.dumps({
            "text": "First message",
            "lang": "en"
        }))
        
        # Wait for completion
        complete_count = 0
        async with asyncio.timeout(10):
            while complete_count < 1:
                response = await websocket.recv()
                if isinstance(response, str):
                    message = json.loads(response)
                    if message.get("status") == "complete":
                        complete_count += 1
        
        # Second request
        await websocket.send(json.dumps({
            "text": "Second message",
            "lang": "en"
        }))
        
        # Should receive generating status for second request
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_handles_different_languages(websocket_url):
    """Test that WebSocket handles different languages"""
    languages = ["en", "sv"]
    
    async with websockets.connect(websocket_url) as websocket:
        for lang in languages:
            await websocket.send(json.dumps({
                "text": f"Test in {lang}",
                "lang": lang
            }))
            
            # Should receive generating status
            response = await websocket.recv()
            message = json.loads(response)
            assert message["status"] == "generating"
            
            # Wait for completion
            async with asyncio.timeout(10):
                while True:
                    response = await websocket.recv()
                    if isinstance(response, str):
                        message = json.loads(response)
                        if message.get("status") == "complete":
                            break


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_audio_chunks_are_binary(websocket_url):
    """Test that audio data is sent as binary"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "Test binary data",
            "lang": "en"
        }))
        
        # Skip status messages until we get audio
        audio_found = False
        
        async with asyncio.timeout(10):
            for _ in range(50):  # Limit iterations
                message = await websocket.recv()
                
                if isinstance(message, bytes):
                    # Found binary audio data
                    audio_found = True
                    assert len(message) > 0
                    break
        
        assert audio_found, "Should receive binary audio data"


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_with_long_text(websocket_url):
    """Test that WebSocket handles longer text"""
    long_text = " ".join(["This is a longer text"] * 20)
    
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": long_text,
            "lang": "en"
        }))
        
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_with_special_characters(websocket_url):
    """Test that WebSocket handles special characters"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "Hello! How are you? I'm fine, thanks.",
            "lang": "en"
        }))
        
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"


@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_with_multiline_text(websocket_url):
    """Test that WebSocket handles multiline text"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "text": "Line one.\nLine two.\nLine three.",
            "lang": "en"
        }))
        
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] == "generating"


@pytest.mark.websocket
def test_stream_player_endpoint_returns_html(api_client, api_base_url):
    """Test that /stream-player endpoint returns HTML page"""
    response = api_client.get(f"{api_base_url}/stream-player")
    
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    
    # Check for key HTML elements
    html_content = response.text
    assert "WebSocket" in html_content
    assert "TTS" in html_content or "text-to-speech" in html_content.lower()
    assert "<form" in html_content
    assert "ws://" in html_content or "WebSocket" in html_content


@pytest.mark.websocket
def test_stream_player_page_has_required_elements(api_client, api_base_url):
    """Test that stream-player page has all required UI elements"""
    response = api_client.get(f"{api_base_url}/stream-player")
    html = response.text.lower()
    
    # Should have text input
    assert "textarea" in html or "text" in html
    
    # Should have language selector
    assert "select" in html or "language" in html
    
    # Should have submit button
    assert "button" in html or "speak" in html
    
    # Should have WebSocket connection code
    assert "websocket" in html
    assert "ws" in html


@pytest.mark.smoke
@pytest.mark.websocket
@pytest.mark.asyncio
async def test_websocket_smoke_test(websocket_url):
    """Quick smoke test for WebSocket functionality"""
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({"text": "Test", "lang": "en"}))
        response = await websocket.recv()
        message = json.loads(response)
        assert message["status"] in ["generating", "ready", "complete", "error"]
