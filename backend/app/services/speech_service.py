"""
Speech Service for realtime voice translation
Supports: Speech-to-Text (Whisper) and Text-to-Speech for African languages
"""
import logging
import io
import wave
import numpy as np
from typing import Optional, Dict, List, BinaryIO
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    TTS = None

logger = logging.getLogger(__name__)


class SpeechService:
    """
    Handles speech-to-text and text-to-speech for Kenyan languages.
    Uses Whisper for STT and Coqui TTS / pyttsx3 for TTS.
    """
    
    def __init__(self, whisper_model: str = "base"):
        self.whisper_model_name = whisper_model
        self.whisper_model = None
        self.tts_engine = None
        self.tts_fallback = None
        
        self._init_whisper()
        self._init_tts()
    
    def _init_whisper(self):
        """Initialize Whisper STT model."""
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            return
        
        try:
            logger.info(f"Loading Whisper model: {self.whisper_model_name}")
            self.whisper_model = whisper.load_model(self.whisper_model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def _init_tts(self):
        """Initialize TTS engine."""
        # Try Coqui TTS first (better quality, supports some African languages)
        if TTS_AVAILABLE:
            try:
                # Use a multilingual model
                self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                logger.info("Coqui TTS initialized with XTTS v2")
                return
            except Exception as e:
                logger.warning(f"Coqui TTS init failed: {e}")
        
        # Fallback to pyttsx3 (offline, basic quality)
        try:
            import pyttsx3
            self.tts_fallback = pyttsx3.init()
            # Set properties
            self.tts_fallback.setProperty('rate', 150)
            self.tts_fallback.setProperty('volume', 0.9)
            logger.info("Fallback TTS (pyttsx3) initialized")
        except Exception as e:
            logger.warning(f"pyttsx3 init failed: {e}")
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "wav"
    ) -> Dict[str, any]:
        """
        Convert speech audio to text using Whisper.
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language hint (e.g., 'en', 'sw', 'ki')
            format: Audio format ('wav', 'mp3', 'm4a', etc.)
            
        Returns:
            Dict with 'text', 'language', 'confidence'
        """
        if not self.whisper_model:
            return {
                "text": "",
                "language": language or "unknown",
                "confidence": 0.0,
                "error": "Whisper model not loaded"
            }
        
        try:
            # Save audio to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            # Map language codes
            lang_map = {
                "english": "en",
                "swahili": "sw",
                "kikuyu": "ki",
                "luo": "luo",
                "kamba": "kam",
                "kalenjin": "kln",
                "luhya": "luy",
                "somali": "so",
            }
            
            whisper_lang = lang_map.get(language, language) if language else None
            
            # Transcribe
            result = self.whisper_model.transcribe(
                tmp_path,
                language=whisper_lang,
                task="transcribe"
            )
            
            # Cleanup
            import os
            os.unlink(tmp_path)
            
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", language or "unknown"),
                "confidence": 1.0,  # Whisper doesn't provide confidence scores directly
                "segments": result.get("segments", [])
            }
        
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return {
                "text": "",
                "language": language or "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "english",
        speaker: Optional[str] = None,
        output_format: str = "wav"
    ) -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            language: Target language (english, swahili, kikuyu, etc.)
            speaker: Optional speaker voice
            output_format: Output audio format
            
        Returns:
            Audio bytes
        """
        # Language to speaker mapping for XTTS
        lang_map = {
            "english": "en",
            "swahili": "sw",
            "kikuyu": "en",  # Fallback to English speaker
            "luo": "en",
            "kamba": "en",
            "kalenjin": "en",
            "luhya": "en",
            "somali": "so",
        }
        
        tts_lang = lang_map.get(language, "en")
        
        # Try Coqui TTS first
        if self.tts_engine:
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as tmp:
                    tmp_path = tmp.name
                
                self.tts_engine.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    language=tts_lang,
                    speaker=speaker
                )
                
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                
                import os
                os.unlink(tmp_path)
                return audio_data
            
            except Exception as e:
                logger.error(f"Coqui TTS failed: {e}")
        
        # Fallback to pyttsx3
        if self.tts_fallback:
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                
                self.tts_fallback.save_to_file(text, tmp_path)
                self.tts_fallback.runAndWait()
                
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                
                import os
                os.unlink(tmp_path)
                return audio_data
            
            except Exception as e:
                logger.error(f"Fallback TTS failed: {e}")
        
        return b""
    
    def get_supported_languages(self) -> List[str]:
        """Return list of supported languages for TTS."""
        return [
            "english", "swahili", "kikuyu", "luo", 
            "kamba", "kalenjin", "luhya", "somali"
        ]
    
    def is_available(self) -> Dict[str, bool]:
        """Check which services are available."""
        return {
            "stt": self.whisper_model is not None,
            "tts": self.tts_engine is not None or self.tts_fallback is not None,
            "whisper": WHISPER_AVAILABLE,
            "coqui_tts": TTS_AVAILABLE
        }
