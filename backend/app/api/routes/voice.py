"""
WebSocket endpoint for realtime voice translation
Supports streaming audio in and returning translated audio out
"""
import logging
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from app.config import settings
from app.services.speech_service import SpeechService
from app.services.translation_service import TranslationService
from app.core.language_detector import LanguageDetector

logger = logging.getLogger(__name__)
router = APIRouter()
speech_service = SpeechService()
translation_service = TranslationService()
language_detector = LanguageDetector()


@router.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    """
    WebSocket endpoint for realtime voice translation.
    
    Protocol:
    - Client sends: JSON with 'audio' (base64), 'source_lang', 'target_lang', 'domain'
    - Server sends: JSON with 'text', 'translation', 'audio' (base64), 'language'
    
    Flow:
    1. Receive audio chunk
    2. Speech-to-text (Whisper)
    3. Detect language if not specified
    4. Translate text
    5. Text-to-speech (optional)
    6. Return results
    """
    await websocket.accept()
    logger.info("WebSocket connection established for realtime translation")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Extract parameters
            audio_b64 = message.get("audio", "")
            source_lang = message.get("source_lang", "english")
            target_lang = message.get("target_lang", "swahili")
            domain = message.get("domain", settings.DEFAULT_DOMAIN)
            return_audio = message.get("return_audio", False)
            auto_detect = message.get("auto_detect_lang", False)
            
            if not audio_b64:
                await websocket.send_json({
                    "error": "No audio data provided",
                    "status": "error"
                })
                continue
            
            try:
                # Decode base64 audio
                import base64
                audio_bytes = base64.b64decode(audio_b64)
                
                # Step 1: Speech-to-text
                stt_result = await speech_service.speech_to_text(
                    audio_data=audio_bytes,
                    language=source_lang if not auto_detect else None
                )
                
                original_text = stt_result.get("text", "")
                
                if not original_text:
                    await websocket.send_json({
                        "error": "Could not transcribe audio",
                        "status": "error",
                        "details": stt_result
                    })
                    continue
                
                # Step 2: Detect language if requested
                if auto_detect:
                    detected = language_detector.detect_primary(original_text)
                    source_lang = detected
                    stt_result["detected_language"] = detected
                
                # Step 3: Translate
                translated_text = await translation_service.translate_text(
                    text=original_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    domain=domain
                )
                
                response = {
                    "status": "success",
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "domain": domain
                }
                
                # Step 4: Text-to-speech (optional)
                if return_audio:
                    tts_audio = await speech_service.text_to_speech(
                        text=translated_text,
                        language=target_lang
                    )
                    if tts_audio:
                        response["audio"] = base64.b64encode(tts_audio).decode("utf-8")
                
                await websocket.send_json(response)
                
            except Exception as e:
                logger.error(f"Translation error: {e}")
                await websocket.send_json({
                    "error": str(e),
                    "status": "error"
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for realtime transcription only.
    Streams audio and returns transcribed text.
    """
    await websocket.accept()
    logger.info("WebSocket connection established for transcription")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            audio_b64 = message.get("audio", "")
            language = message.get("language")
            
            if not audio_b64:
                continue
            
            try:
                import base64
                audio_bytes = base64.b64decode(audio_b64)
                
                result = await speech_service.speech_to_text(
                    audio_data=audio_bytes,
                    language=language
                )
                
                await websocket.send_json(result)
                
            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "text": ""
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
