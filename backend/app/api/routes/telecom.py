from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Literal

from app.config import settings
from app.services.telecom_service import TelecomGateway

router = APIRouter()
gateway = TelecomGateway()


class VoiceEvent(BaseModel):
    provider: Literal["africastalking", "twilio"]
    payload: Dict[str, Any]
    source_language: str
    target_language: str
    domain: str = settings.DEFAULT_DOMAIN


@router.post("/telecom/voice")
async def relay_voice(event: VoiceEvent):
    """Endpoint to receive voice webhook payloads from Africa's Talking or Twilio."""
    try:
        result = await gateway.handle_voice(
            provider=event.provider,
            payload=event.payload,
            source_language=event.source_language,
            target_language=event.target_language,
            domain=event.domain,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice relay failed: {exc}") from exc


class SMSEvent(BaseModel):
    provider: Literal["africastalking", "twilio"]
    payload: Dict[str, Any]
    source_language: str
    target_language: str
    domain: str = settings.DEFAULT_DOMAIN


@router.post("/telecom/sms")
async def relay_sms(event: SMSEvent):
    """Translate inbound SMS before forwarding to the clinician dashboard."""
    try:
        result = await gateway.handle_sms(
            provider=event.provider,
            payload=event.payload,
            source_language=event.source_language,
            target_language=event.target_language,
            domain=event.domain,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SMS relay failed: {exc}") from exc


class USSDEvent(BaseModel):
    provider: Literal["africastalking"]
    payload: Dict[str, Any]
    domain: str = settings.DEFAULT_DOMAIN


@router.post("/telecom/ussd")
async def relay_ussd(event: USSDEvent):
    """
    Provide a lightweight USSD interaction. In production, this would return
    raw text or XML depending on the provider's requirements.
    """
    try:
        return await gateway.handle_ussd(provider=event.provider, payload=event.payload, domain=event.domain)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"USSD relay failed: {exc}") from exc

