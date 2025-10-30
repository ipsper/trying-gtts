"""
Manual WebSocket test that saves audio file for playback

Run this test manually to generate and save audio:
    pytest tests/test_websocket_manual.py -v --no-cov
"""

import pytest
import json
import asyncio
import websockets
from pathlib import Path


@pytest.mark.manual
@pytest.mark.asyncio
async def test_websocket_save_audio_for_playback(websocket_url):
    """
    Manual test that saves audio to a file for playback
    
    This test generates audio via WebSocket and saves it to output.mp3
    You can then play it manually to verify audio quality.
    """
    output_file = Path("output_websocket.mp3")
    
    async with websockets.connect(websocket_url) as websocket:
        print("\n📤 Sending TTS request via WebSocket...")
        
        await websocket.send(json.dumps({
            "text": "Hello! This is a test of WebSocket audio streaming. The audio should sound clear and natural.",
            "lang": "en"
        }))
        
        audio_chunks = []
        complete = False
        
        print("📥 Receiving audio chunks...")
        
        async with asyncio.timeout(15):
            while not complete:
                message = await websocket.recv()
                
                if isinstance(message, str):
                    data = json.loads(message)
                    status = data.get("status")
                    
                    if status == "generating":
                        print(f"   ⏳ {data.get('message')}")
                    elif status == "ready":
                        print(f"   ✅ Ready to stream (size: {data.get('size')} bytes)")
                    elif status == "complete":
                        print(f"   ✅ {data.get('message')}")
                        complete = True
                    elif status == "error":
                        print(f"   ❌ Error: {data.get('error')}")
                        pytest.fail(f"WebSocket error: {data.get('error')}")
                else:
                    # Binary audio chunk
                    audio_chunks.append(message)
                    if len(audio_chunks) % 10 == 0:
                        print(f"   📦 Received {len(audio_chunks)} chunks...")
        
        # Save audio to file
        total_bytes = sum(len(chunk) for chunk in audio_chunks)
        print(f"\n💾 Saving {len(audio_chunks)} chunks ({total_bytes} bytes) to {output_file}...")
        
        with output_file.open("wb") as f:
            for chunk in audio_chunks:
                f.write(chunk)
        
        print(f"✅ Audio saved to: {output_file.absolute()}")
        print(f"\n🔊 To play the audio, run:")
        print(f"   afplay {output_file}  # macOS")
        print(f"   mpg123 {output_file}  # Linux")
        print(f"   vlc {output_file}     # Any OS with VLC")
        
        # Verify file was created and has content
        assert output_file.exists(), "Audio file should be created"
        assert output_file.stat().st_size > 0, "Audio file should have content"
        assert len(audio_chunks) > 0, "Should receive audio chunks"


@pytest.mark.manual
@pytest.mark.asyncio
async def test_websocket_save_multiple_languages(websocket_url):
    """
    Manual test that saves audio in multiple languages
    """
    test_cases = [
        ("Hello world", "en", "english.mp3"),
        ("Hej världen", "sv", "swedish.mp3"),
        ("Hola mundo", "es", "spanish.mp3"),
    ]
    
    for text, lang, filename in test_cases:
        print(f"\n🌍 Generating {lang}: {text}")
        
        async with websockets.connect(websocket_url) as websocket:
            await websocket.send(json.dumps({"text": text, "lang": lang}))
            
            audio_chunks = []
            complete = False
            
            async with asyncio.timeout(10):
                while not complete:
                    message = await websocket.recv()
                    
                    if isinstance(message, str):
                        data = json.loads(message)
                        if data.get("status") == "complete":
                            complete = True
                    else:
                        audio_chunks.append(message)
            
            output_path = Path(filename)
            with output_path.open("wb") as f:
                for chunk in audio_chunks:
                    f.write(chunk)
            
            print(f"   ✅ Saved to: {output_path.absolute()}")
    
    print(f"\n🔊 Play all audio files:")
    for _, _, filename in test_cases:
        print(f"   afplay {filename}")

