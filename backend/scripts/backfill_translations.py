import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.vector_store import VectorStore
from app.services.translation_service import TranslationService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TranslationBackfill:
    def __init__(self, processed_dir: str):
        self.processed_dir = Path(processed_dir)
        self.translation_service = TranslationService()
        self.vector_store = VectorStore(persist_directory=settings.VECTOR_DB_PATH)
        self.translation_targets = [
            lang for lang in settings.TRANSLATION_TARGET_LANGUAGES
            if lang != settings.SOURCE_LANGUAGE
        ]

    def run(self) -> None:
        chunk_dir = self.processed_dir / "chunks"
        if not chunk_dir.exists():
            logger.error("Chunk directory %s not found", chunk_dir)
            return

        chunk_files = list(chunk_dir.glob("*_chunks.json"))
        if not chunk_files:
            logger.warning("No chunk JSON files found in %s", chunk_dir)
            return

        for chunk_file in chunk_files:
            self._process_chunk_file(chunk_file)

    def _process_chunk_file(self, chunk_file: Path) -> None:
        logger.info("Processing chunk file %s", chunk_file.name)
        with open(chunk_file, "r", encoding="utf-8") as handle:
            chunks: List[Dict] = json.load(handle)

        updated_ids: List[str] = []
        updated_metadatas: List[Dict] = []

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            translations = metadata.get("translations", {})
            source_lang = metadata.get("language", settings.SOURCE_LANGUAGE)
            domain = metadata.get("domain", settings.DEFAULT_DOMAIN)
            missing_targets = [
                lang for lang in self.translation_targets
                if lang not in translations and lang != source_lang
            ]
            if not missing_targets:
                continue
            text = chunk.get("content", "").strip()
            if not text:
                continue
            for target in missing_targets:
                try:
                    translated = asyncio.run(
                        self.translation_service.translate_text(
                            text=text,
                            source_language=source_lang,
                            target_language=target,
                            domain=domain
                        )
                    )
                    translations[target] = translated
                except Exception as exc:
                    logger.error(
                        "Failed to translate chunk %s (%s→%s): %s",
                        chunk.get("chunk_id"),
                        source_lang,
                        target,
                        exc
                    )
            if translations:
                metadata["translations"] = translations
                updated_ids.append(chunk.get("chunk_id"))
                updated_metadatas.append(metadata)

        if updated_ids:
            self.vector_store.update_metadatas(updated_ids, updated_metadatas)
            logger.info("Updated %d chunks from %s", len(updated_ids), chunk_file.name)


def main():
    parser = argparse.ArgumentParser(description="Backfill translations for existing chunks.")
    parser.add_argument(
        "--processed-path",
        type=str,
        default="../data/processed",
        help="Directory containing processed chunk JSON files."
    )
    args = parser.parse_args()

    backfill = TranslationBackfill(args.processed_path)
    backfill.run()


if __name__ == "__main__":
    main()

