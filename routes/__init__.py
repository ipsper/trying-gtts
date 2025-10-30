"""
Route modules for gTTS API
"""

from .tts_routes import router as tts_router
from .library_routes import router as library_router
from .ui_routes import router as ui_router
from .websocket_routes import websocket_tts_endpoint

__all__ = ['tts_router', 'library_router', 'ui_router', 'websocket_tts_endpoint']

