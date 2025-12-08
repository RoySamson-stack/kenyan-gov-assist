import logging
from typing import Dict, Any, Optional

from app.config import settings
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


class TelecomGateway:
    """
    Orchestrates interactions with Africa's Talking (voice/SMS/USSD) and
    Twilio (voice/verify). This now includes provider-aware payload parsing so
    each channel can re-use the shared translation service.
    """

    def __init__(self):
        self.translation_service = TranslationService()

    # ------------------------------------------------------------------ #
    # Normalization helpers
    # ------------------------------------------------------------------ #
    def _extract_voice_payload(self, provider: str, payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
        provider = provider.lower()
        if provider == "africastalking":
            return {
                "transcript": payload.get("speechResult") or payload.get("dtmfDigits"),
                "recording_url": payload.get("recordingUrl"),
                "session_id": payload.get("sessionId"),
                "caller": payload.get("callerNumber"),
            }
        if provider == "twilio":
            return {
                "transcript": payload.get("SpeechResult") or payload.get("Digits"),
                "recording_url": payload.get("RecordingUrl"),
                "session_id": payload.get("CallSid"),
                "caller": payload.get("From"),
            }
        return {
            "transcript": payload.get("transcript") or payload.get("text"),
            "recording_url": payload.get("recordingUrl"),
            "session_id": payload.get("sessionId"),
            "caller": payload.get("caller"),
        }

    def _extract_sms_text(self, provider: str, payload: Dict[str, Any]) -> Optional[str]:
        provider = provider.lower()
        if provider == "africastalking":
            return payload.get("text")
        if provider == "twilio":
            return payload.get("Body")
        return payload.get("message") or payload.get("text")

    def _normalize_ussd(self, provider: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        provider = provider.lower()
        if provider == "africastalking":
            return {
                "session_id": payload.get("sessionId"),
                "phone_number": payload.get("phoneNumber"),
                "service_code": payload.get("serviceCode"),
                "text": payload.get("text") or "",
            }
        return {
            "session_id": payload.get("sessionId"),
            "phone_number": payload.get("phoneNumber"),
            "service_code": payload.get("serviceCode"),
            "text": payload.get("text") or "",
        }

    # ------------------------------------------------------------------ #
    # Channel handlers
    # ------------------------------------------------------------------ #
    async def handle_voice(
        self,
        provider: str,
        payload: Dict[str, Any],
        source_language: str,
        target_language: str,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Handle an inbound voice snippet (transcript proxy for MVP) and return the translated response.
        """
        domain_key = domain if domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN
        normalized = self._extract_voice_payload(provider, payload)
        transcript = normalized.get("transcript")

        if not transcript and normalized.get("recording_url"):
            logger.info(
                "Voice payload from %s lacks transcript; returning recording URL for async processing",
                provider,
            )
            return {
                "status": "pending_transcription",
                "provider": provider,
                "domain": domain_key,
                "recording_url": normalized.get("recording_url"),
                "session_id": normalized.get("session_id"),
            }

        if not transcript:
            logger.warning("Voice payload from %s is missing transcript text", provider)
            return {"status": "error", "message": "Missing transcript"}

        translation = await self.translation_service.translate_text(
            text=transcript,
            source_language=source_language,
            target_language=target_language,
            domain=domain_key,
        )

        logger.info("Voice event processed via %s (domain=%s)", provider, domain_key)
        return {
            "status": "success",
            "provider": provider,
            "domain": domain_key,
            "session_id": normalized.get("session_id"),
            "caller": normalized.get("caller"),
            "translation": translation,
        }

    async def handle_sms(
        self,
        provider: str,
        payload: Dict[str, Any],
        source_language: str,
        target_language: str,
        domain: str,
    ) -> Dict[str, Any]:
        """Translate SMS text before forwarding to the clinic portal."""
        message = self._extract_sms_text(provider, payload)
        if not message:
            logger.warning("SMS payload from %s missing body field", provider)
            return {"status": "error", "message": "Missing SMS body"}

        domain_key = domain if domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN
        translation = await self.translation_service.translate_text(
            text=message,
            source_language=source_language,
            target_language=target_language,
            domain=domain_key,
        )
        logger.info("SMS event processed via %s (domain=%s)", provider, domain_key)
        return {
            "status": "success",
            "provider": provider,
            "domain": domain_key,
            "translation": translation,
        }

    async def handle_ussd(
        self,
        provider: str,
        payload: Dict[str, Any],
        domain: str,
    ) -> Dict[str, Any]:
        """
        Basic USSD flow placeholder. Africa's Talking flavor is the primary use case.
        """
        normalized = self._normalize_ussd(provider, payload)
        session_id = normalized["session_id"]
        text = normalized["text"]
        domain_key = domain if domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN

        if not text or text.strip() == "":
            menu = "CON AfyaTranslate\n1. Triage\n2. Prescription tips\n3. Government FAQs"
        elif text.endswith("1"):
            menu = "END Please describe the symptoms to the nurse at the clinic."
        elif text.endswith("2"):
            menu = "END Take medicines exactly as prescribed. Visit the clinic if symptoms persist."
        else:
            menu = "END For government services, dial *123*2#. Stay healthy!"

        logger.info("USSD session %s via %s responded (domain=%s)", session_id, provider, domain_key)
        return {
            "status": "success",
            "provider": provider,
            "domain": domain_key,
            "session_id": session_id,
            "payload": menu,
        }

