from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from gtts import gTTS
import os
import tempfile
import json
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="gTTS API", version="1.0.0")

# Create a router
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
        
        # Trim whitespace
        v = v.strip()
        
        # Ensure the text is JSON-safe by checking it can be serialized
        try:
            json.dumps({"text": v})
        except (TypeError, ValueError) as e:
            raise ValueError(f"Text contains invalid characters for JSON: {str(e)}")
        
        return v
    
    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v: str) -> str:
        """Validate language code"""
        if not v or not v.strip():
            raise ValueError("Language code cannot be empty")
        return v.strip().lower()


@router.get("/", response_model=dict)
async def root():
    """Welcome message with API information"""
    return {
        "message": "Welcome to gTTS API!",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/v1/tts": "Convert text to speech (returns MP3 file)",
            "GET /api/v1/languages": "List available languages"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@router.post("/tts", responses={
    200: {"description": "MP3 audio file", "content": {"audio/mpeg": {}}},
    400: {"description": "Invalid input"},
    500: {"description": "Server error"}
})
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech and return an MP3 file
    
    Args:
        text: The text to convert to speech (1-5000 characters)
        lang: Language code (e.g. 'en' for English, 'sv' for Swedish)
    
    Returns:
        MP3 audio file
    
    Raises:
        HTTPException: If text is invalid or TTS generation fails
    """
    try:
        # Validate that we can serialize the request to JSON
        request_json = request.model_dump_json()
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()
        
        # Generate speech from text
        try:
            tts = gTTS(text=request.text, lang=request.lang, slow=False)
            tts.save(temp_path)
        except Exception as tts_error:
            # Clean up temp file if TTS fails
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate speech: {str(tts_error)}. Please check the language code."
            )
        
        # Return the file
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            filename=f"speech_{request.lang}.mp3",
            background=lambda: os.unlink(temp_path)  # Remove file after it's sent
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
    Return common languages supported by gTTS
    
    Returns:
        JSON object with supported language codes and names
    """
    languages = {
        "sv": "Swedish",
        "en": "English",
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


# Include the router in the app
app.include_router(router)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

