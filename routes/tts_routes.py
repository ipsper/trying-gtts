"""
Text-to-Speech API routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from gtts import gTTS
import os
import tempfile
import json
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/api/v1", tags=["Text-to-Speech"])


class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    lang: str = Field(default="en", description="Language code (e.g. 'en', 'sv')")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and sanitize text input"""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or only whitespace")
        
        # Ensure the text is JSON-safe
        try:
            json.dumps(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Text contains invalid characters: {str(e)}")
        
        return v.strip()
    
    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v: str) -> str:
        """Validate and normalize language code"""
        if not v or not v.strip():
            raise ValueError("Language code cannot be empty")
        return v.lower().strip()


@router.get("/", response_model=dict)
async def root():
    """
    Root endpoint with API information
    
    Returns:
        JSON object with API info and available endpoints
    """
    return {
        "message": "Welcome to gTTS API!",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/v1/tts": "Convert text to speech (returns MP3 file)",
            "POST /api/v1/tts/save": "Convert text to speech and save to library",
            "GET /api/v1/library": "List all saved audio files",
            "GET /api/v1/library/{filename}": "Download a specific audio file",
            "DELETE /api/v1/library/{filename}": "Delete a specific audio file",
            "GET /api/v1/languages": "List available languages",
            "WebSocket /ws/tts": "Stream TTS audio in real-time"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@router.post("/tts", responses={
    200: {"description": "Audio file generated successfully"},
    400: {"description": "Invalid input"},
    422: {"description": "Validation error"},
    500: {"description": "Server error"}
})
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech and return as MP3 file
    
    Args:
        request: TextToSpeechRequest with text and language
    
    Returns:
        MP3 audio file
    
    Validation:
        - Text must be non-empty and valid JSON
        - Language code must be supported by gTTS
    
    Error Responses:
        - 400: Invalid language code or text format
        - 422: Validation error (empty text, etc.)
        - 500: Server error during generation
    """
    try:
        # Validate JSON serialization
        try:
            request.model_dump_json()
        except Exception as json_error:
            raise HTTPException(
                status_code=400,
                detail=f"Request data is not JSON serializable: {str(json_error)}"
            )
        
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate speech
            tts = gTTS(text=request.text, lang=request.lang, slow=False)
            tts.save(temp_path)
        except Exception as tts_error:
            # Clean up temp file if generation fails
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate speech. Please check language code and text: {str(tts_error)}"
            )
        
        # Return the audio file and schedule cleanup
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            filename=f"speech_{request.lang}.mp3",
            background=BackgroundTask(os.unlink, temp_path)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/languages", response_model=dict)
async def get_languages():
    """
    Get list of supported languages
    
    Returns:
        JSON object with language codes and names
    """
    # Common languages supported by gTTS
    languages = {
        "en": "English",
        "sv": "Swedish",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "zh-CN": "Chinese (Simplified)",
        "ar": "Arabic",
        "hi": "Hindi",
        "ko": "Korean"
    }
    return {"languages": languages}

