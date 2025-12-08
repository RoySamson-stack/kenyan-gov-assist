import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

from app.config import settings
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Shared translation layer for Serikali Yangu (civic) and AfyaTranslate (health).

    The service loads phrase-level translation memories from `data/translations`,
    applies domain-specific glossaries, and falls back to the unified Ollama model
    for free-form translation.
    """

    def __init__(self, memory_path: Optional[str] = None):
        self.memory_path = Path(memory_path or settings.TRANSLATION_MEMORY_PATH)
        self.ollama = OllamaService()
        self.translation_memory = self._load_translation_memory()
        logger.info("TranslationService initialized (memory entries: %s)", len(self.translation_memory))

    def _load_translation_memory(self) -> Dict[Tuple[str, str, str], Dict[str, str]]:
        """
        Load translation memories from JSON files.

        Expected file naming convention:
        `<source>-<target>[__<domain>].json`
        e.g., `english-swahili__health.json`
        """
        memory: Dict[Tuple[str, str, str], Dict[str, str]] = {}
        if not self.memory_path.exists():
            logger.warning("Translation memory path %s does not exist", self.memory_path)
            return memory

        for file_path in self.memory_path.rglob("*.json"):
            filename = file_path.stem.lower()
            try:
                lang_segment, *domain_segment = filename.split("__")
                source_lang, target_lang = lang_segment.split("-")
                domain = domain_segment[0] if domain_segment else "generic"
            except ValueError:
                logger.warning("Skipping translation memory file with unexpected name: %s", file_path)
                continue

            key = (source_lang, target_lang, domain)
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    phrases = json.load(handle)
                if not isinstance(phrases, dict):
                    raise ValueError("Translation memory file must contain a JSON object")
                memory.setdefault(key, {}).update(phrases)
                logger.debug("Loaded %s entries from %s", len(phrases), file_path)
            except Exception as exc:
                logger.error("Failed to load translation memory %s: %s", file_path, exc)
        return memory

    def refresh_memory(self) -> None:
        """Reload translation memories from disk."""
        self.translation_memory = self._load_translation_memory()
        logger.info("Translation memory reloaded (entries: %s)", len(self.translation_memory))

    def _lookup_memory(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: str,
    ) -> Optional[str]:
        """Return a phrase translation if it exists in the memory."""
        source = source_language.lower()
        target = target_language.lower()
        domain_key = domain if domain in settings.SUPPORTED_DOMAINS else "generic"

        key_exact = (source, target, domain_key)
        key_generic = (source, target, "generic")

        for key in (key_exact, key_generic):
            phrase_map = self.translation_memory.get(key)
            if phrase_map:
                translated = phrase_map.get(text)
                if translated:
                    logger.debug("Found translation memory match for '%s' (%s -> %s)", text, source, target)
                    return translated
        return None

    def lookup_phrase(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: str = settings.DEFAULT_DOMAIN,
    ) -> Optional[str]:
        """Public helper for checking the offline memory."""
        return self._lookup_memory(text, source_language, target_language, domain)

    def _build_system_prompt(self, domain: str) -> str:
        """Return domain-specific translation instructions."""
        civic_prompt = (
            "You are a professional translator for Kenyan government and civic information. "
            "Honor official terminology, keep answers concise, and preserve legal accuracy."
        )
        health_prompt = (
            "You are AfyaTranslate, a Kenyan healthcare translation assistant. "
            "Use compassionate tone, maintain medical accuracy, and highlight safety-critical instructions."
        )
        return health_prompt if domain == "health" else civic_prompt

    def _build_user_prompt(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: str,
        glossary_hint: Optional[str] = None,
    ) -> str:
        glossary_section = f"\nGlossary guidance:\n{glossary_hint}\n" if glossary_hint else ""
        return (
            f"Translate the following text from {source_language} to {target_language} "
            f"for the {domain} domain. Return only the translated text.\n"
            f"{glossary_section}\nText:\n{text}"
        )

    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: str = settings.DEFAULT_DOMAIN,
        glossary_hint: Optional[str] = None,
    ) -> str:
        """
        Translate plain text with optional domain-aware glossary hints.
        """
        # Memory lookup first
        cached = self._lookup_memory(text, source_language, target_language, domain)
        if cached:
            return cached

        system_prompt = self._build_system_prompt(domain)
        user_prompt = self._build_user_prompt(text, source_language, target_language, domain, glossary_hint)

        translation = await self.ollama.generate(prompt=user_prompt, system_prompt=system_prompt)
        return translation.strip()

    async def mediate_dialogue(
        self,
        speaker_text: str,
        speaker_language: str,
        listener_language: str,
        domain: str = "health",
        include_backtranslation: bool = False,
    ) -> Dict[str, str]:
        """
        Translate a snippet for two-party conversations (e.g., doctor/patient).
        Returns both forward translation and optional back-translation for confirmation.
        """
        translation = await self.translate_text(
            speaker_text, speaker_language, listener_language, domain=domain
        )
        response = {"translation": translation}
        if include_backtranslation:
            response["back_translation"] = await self.translate_text(
                translation,
                listener_language,
                speaker_language,
                domain=domain,
                glossary_hint="Ensure the back-translation preserves original intent.",
            )
        return response
