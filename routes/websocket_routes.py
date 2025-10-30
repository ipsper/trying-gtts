"""
WebSocket routes for real-time TTS streaming
"""

from fastapi import WebSocket, WebSocketDisconnect
from gtts import gTTS
import os
import tempfile


async def websocket_tts_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS audio
    
    Client sends JSON: {"text": "Your text", "lang": "en"}
    Server streams back MP3 audio data in chunks
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive text and language from client
            data = await websocket.receive_json()
            text = data.get("text", "")
            lang = data.get("lang", "en")
            
            if not text or not text.strip():
                await websocket.send_json({
                    "error": "Text cannot be empty",
                    "status": "error"
                })
                continue
            
            # Send status update
            await websocket.send_json({
                "status": "generating",
                "message": f"Generating speech for: {text[:50]}..."
            })
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Generate speech
                tts = gTTS(text=text.strip(), lang=lang.strip().lower(), slow=False)
                tts.save(temp_path)
                
                # Send audio metadata
                file_size = os.path.getsize(temp_path)
                await websocket.send_json({
                    "status": "ready",
                    "message": "Audio ready, streaming...",
                    "size": file_size
                })
                
                # Stream audio data in chunks
                chunk_size = 8192  # 8KB chunks
                with open(temp_path, "rb") as audio_file:
                    while True:
                        chunk = audio_file.read(chunk_size)
                        if not chunk:
                            break
                        await websocket.send_bytes(chunk)
                
                # Send completion message
                await websocket.send_json({
                    "status": "complete",
                    "message": "Audio streaming complete"
                })
                
            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "status": "error"
                })
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "error": str(e),
                "status": "error"
            })
        except:
            pass


# This is registered separately in main.py as @app.websocket("/ws/tts")
# because it needs to be at the app level, not in a router
router = None  # Placeholder - websocket registered in main.py

