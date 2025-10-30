"""
gTTS API - Text-to-Speech FastAPI Application

A RESTful API and WebSocket service for converting text to speech using Google's gTTS library.
"""

from fastapi import FastAPI, WebSocket
from routes import tts_router, library_router, ui_router, websocket_tts_endpoint

# Create FastAPI application
app = FastAPI(
    title="gTTS API",
    version="1.0.0",
    description="Text-to-Speech API with WebSocket streaming support"
)

# Include routers
app.include_router(tts_router)
app.include_router(library_router)
app.include_router(ui_router)


@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint for the container
    
    Returns:
        JSON object with health status
    """
    return {
        "status": "healthy",
        "service": "gTTS API",
        "version": "1.0.0"
    }


@app.websocket("/ws/tts")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS audio
    
    Delegates to websocket_tts_endpoint function from routes
    """
    await websocket_tts_endpoint(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

