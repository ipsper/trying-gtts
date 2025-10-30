"""
Audio Library management routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from gtts import gTTS
from pathlib import Path
from datetime import datetime
from .tts_routes import TextToSpeechRequest

router = APIRouter(prefix="/api/v1", tags=["Audio Library"])

# Audio library directory
AUDIO_LIBRARY_DIR = Path("/app/audio_library")
AUDIO_LIBRARY_DIR.mkdir(exist_ok=True)


@router.post("/tts/save", responses={
    200: {"description": "Audio saved successfully"},
    400: {"description": "Invalid input"},
    500: {"description": "Server error"}
})
async def text_to_speech_save(request: TextToSpeechRequest):
    """
    Convert text to speech and save to audio library
    
    Returns: Information about the saved file
    """
    try:
        # Generate a unique filename - only allow English letters, numbers, and safe chars
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Only allow a-z, A-Z, 0-9, space, hyphen, underscore
        safe_text = "".join(c for c in request.text[:30] if c.isascii() and (c.isalnum() or c in (' ', '-', '_'))).strip()
        safe_text = safe_text.replace(' ', '_')
        
        # Fallback to generic name if no safe characters remain
        if not safe_text:
            safe_text = "audio"
        
        filename = f"{timestamp}_{request.lang}_{safe_text}.mp3"
        filepath = AUDIO_LIBRARY_DIR / filename
        
        # Generate speech
        try:
            tts = gTTS(text=request.text, lang=request.lang, slow=False)
            tts.save(str(filepath))
        except Exception as tts_error:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate speech: {str(tts_error)}"
            )
        
        return {
            "status": "success",
            "message": "Audio saved to library",
            "filename": filename,
            "text": request.text,
            "lang": request.lang,
            "size": filepath.stat().st_size,
            "created": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/library", response_model=dict)
async def list_audio_library():
    """
    List all MP3 files in the audio library
    
    Returns: List of audio files with metadata
    """
    try:
        files = []
        
        for mp3_file in sorted(AUDIO_LIBRARY_DIR.glob("*.mp3"), reverse=True):
            stat = mp3_file.stat()
            files.append({
                "filename": mp3_file.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            "total_files": len(files),
            "files": files
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list audio library: {str(e)}"
        )


@router.get("/library/{filename}")
async def get_audio_file(filename: str):
    """
    Stream or download a specific MP3 file from the library
    
    Args:
        filename: Name of the MP3 file
    
    Returns: MP3 audio file
    """
    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    filepath = AUDIO_LIBRARY_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Audio file '{filename}' not found"
        )
    
    if not filepath.suffix.lower() == ".mp3":
        raise HTTPException(
            status_code=400,
            detail="Only MP3 files are allowed"
        )
    
    return FileResponse(
        filepath,
        media_type="audio/mpeg",
        filename=filename
    )


@router.delete("/library/{filename}")
async def delete_audio_file(filename: str):
    """
    Delete a specific MP3 file from the library
    
    Args:
        filename: Name of the MP3 file to delete
    
    Returns: Confirmation message
    """
    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )
    
    filepath = AUDIO_LIBRARY_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Audio file '{filename}' not found"
        )
    
    try:
        filepath.unlink()
        return {
            "status": "success",
            "message": f"File '{filename}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

