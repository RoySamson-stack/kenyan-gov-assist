"""
REST API endpoints for voice processing (fallback when WebSocket unavailable)
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from app.services.speech_service import SpeechService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
speech_service = SpeechService()


@router.post("/voice/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Transcribe uploaded audio file to text.
    Uses Whisper for speech-to-text.
    """
    try:
        audio_bytes = await audio.read()
        
        result = await speech_service.speech_to_text(
            audio_data=audio_bytes,
            language=language,
            format=audio.filename.split('.')[-1] if audio.filename else "wav"
        )
        
        return {
            "status": "success",
            "text": result.get("text", ""),
            "language": result.get("language", language or "unknown"),
            "confidence": result.get("confidence", 0.0)
        }
    
    except Exception as e:
        logger.error("Transcription failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Transcription failed: " + str(e))


@router.post("/voice/synthesize")
async def synthesize_speech(
    text: str,
    language: str = "english",
    speaker: Optional[str] = None
):
    """
    Convert text to speech.
    Returns audio file.
    """
    try:
        audio_bytes = await speech_service.text_to_speech(
            text=text,
            language=language,
            speaker=speaker
        )
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Speech synthesis failed")
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech_{}.wav".format(language)
            }
        )
    
    except Exception as e:
        logger.error("Speech synthesis failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Speech synthesis failed: " + str(e))


@router.get("/voice/capabilities")
async def get_voice_capabilities():
    """Return available voice processing capabilities."""
    return {
        "services": speech_service.is_available(),
        "supported_languages": speech_service.get_supported_languages(),
        "whisper_model": settings.WHISPER_MODEL,
        "tts_enabled": settings.TTS_ENABLED,
        "supported_formats": ["wav", "mp3", "m4a", "webm", "ogg"]
    }
