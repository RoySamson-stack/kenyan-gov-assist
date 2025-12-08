from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.services.translation_service import TranslationService

router = APIRouter()
translation_service = TranslationService()


class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    domain: str = settings.DEFAULT_DOMAIN
    glossary_hint: Optional[str] = None
    include_backtranslation: bool = False


@router.post("/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate text between languages using the shared Ollama model +
    domain-specific instructions. Falls back to translation memory when possible.
    """
    try:
        domain = request.domain if request.domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN
        if request.include_backtranslation:
            result = await translation_service.mediate_dialogue(
                speaker_text=request.text,
                speaker_language=request.source_language,
                listener_language=request.target_language,
                domain=domain,
                include_backtranslation=True,
            )
            return {"status": "success", "data": result, "domain": domain}

        translated = await translation_service.translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            domain=domain,
            glossary_hint=request.glossary_hint,
        )
        return {"status": "success", "data": {"translation": translated}, "domain": domain}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Translation failed: {exc}") from exc


class PhraseLookupRequest(BaseModel):
    phrase: str
    source_language: str
    target_language: str
    domain: str = settings.DEFAULT_DOMAIN


@router.post("/translate/lookup")
async def lookup_phrase(request: PhraseLookupRequest):
    """
    Check whether a phrase already exists in the offline translation memory.
    """
    domain = request.domain if request.domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN
    match = translation_service.lookup_phrase(
        text=request.phrase,
        source_language=request.source_language,
        target_language=request.target_language,
        domain=domain,
    )
    if match:
        return {
            "status": "success",
            "data": {"translation": match, "source": "memory"},
            "domain": domain,
        }
    raise HTTPException(status_code=404, detail="Phrase not found in translation memory")

