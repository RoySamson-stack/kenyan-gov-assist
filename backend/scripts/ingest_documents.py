
import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.document_processor import DocumentProcessor, DocumentChunk
from app.core.vector_store import VectorStore
from app.services.translation_service import TranslationService
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """Pipeline for ingesting documents into the system"""
    
    def __init__(
        self,
        raw_docs_path: str = None,
        processed_docs_path: str = None,
        vector_db_path: str = None
    ):
        self.raw_docs_path = raw_docs_path or settings.RAW_DOCS_PATH
        self.processed_docs_path = processed_docs_path or "../data/processed"
        self.vector_db_path = vector_db_path or settings.VECTOR_DB_PATH
        
        # Initialize components
        self.processor = DocumentProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.vector_store = VectorStore(persist_directory=self.vector_db_path)
        self.translation_service = TranslationService()
        self.translation_targets = [
            lang for lang in settings.TRANSLATION_TARGET_LANGUAGES
            if lang != settings.SOURCE_LANGUAGE
        ]
        
        # Create directories
        os.makedirs(self.processed_docs_path, exist_ok=True)
        os.makedirs(os.path.join(self.processed_docs_path, "chunks"), exist_ok=True)
        
        logger.info("Document Ingestion Pipeline initialized")
        logger.info(f"Raw docs path: {self.raw_docs_path}")
        logger.info(f"Processed docs path: {self.processed_docs_path}")
        logger.info(f"Vector DB path: {self.vector_db_path}")
    
    def save_chunks_to_json(self, chunks: List[DocumentChunk], source_name: str):
        """Save processed chunks to JSON for inspection"""
        output_file = os.path.join(
            self.processed_docs_path,
            "chunks",
            f"{source_name}_chunks.json"
        )
        
        chunks_data = [chunk.to_dict() for chunk in chunks]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(chunks)} chunks to {output_file}")
    
    def update_metadata(self, stats: Dict[str, Any]):
        """Update metadata file with ingestion statistics"""
        metadata_file = os.path.join(self.processed_docs_path, "metadata.json")
        
        # Load existing metadata if it exists
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                'documents': {},
                'total_chunks': 0,
                'last_updated': None
            }
        
        # Update with new stats
        from datetime import datetime
        metadata['documents'][stats['source']] = {
            'chunks': stats['chunks'],
            'pages': stats['pages'],
            'document_type': stats['document_type'],
            'processed_at': datetime.now().isoformat()
        }
        metadata['total_chunks'] = sum(doc['chunks'] for doc in metadata['documents'].values())
        metadata['last_updated'] = datetime.now().isoformat()
        
        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Updated metadata file: {metadata_file}")
    
    def ingest_single_pdf(self, pdf_path: str) -> int:
        """
        Ingest a single PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of chunks created
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {os.path.basename(pdf_path)}")
        logger.info(f"{'='*60}")
        
        try:
            # Process PDF into chunks
            chunks = self.processor.process_pdf(pdf_path)
            
            if not chunks:
                logger.warning(f"No chunks created from {pdf_path}")
                return 0
            
            # Language and domain are already detected by DocumentProcessor
            # Just ensure they're set (should already be there from detection)
            for chunk in chunks:
                if "language" not in chunk.metadata:
                    chunk.metadata["language"] = settings.SOURCE_LANGUAGE
                if "domain" not in chunk.metadata:
                    chunk.metadata["domain"] = settings.DEFAULT_DOMAIN
            
            if self.translation_targets:
                self._attach_translations(chunks)
            
            # Save chunks to JSON
            source_name = Path(pdf_path).stem
            self.save_chunks_to_json(chunks, source_name)
            
            # Add to vector store
            texts = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]
            
            self.vector_store.add_documents(texts, metadatas, ids)
            
            # Update metadata
            stats = {
                'source': os.path.basename(pdf_path),
                'chunks': len(chunks),
                'pages': chunks[0].metadata.get('total_pages', 0) if chunks else 0,
                'document_type': chunks[0].metadata.get('document_type', 'unknown') if chunks else 'unknown'
            }
            self.update_metadata(stats)
            
            logger.info(f"✓ Successfully ingested {len(chunks)} chunks from {os.path.basename(pdf_path)}")
            return len(chunks)
        
        except Exception as e:
            logger.error(f"✗ Error ingesting {pdf_path}: {e}", exc_info=True)
            return 0
    
    def ingest_directory(self, directory_path: str = None) -> Dict[str, Any]:
        """
        Ingest all PDFs from a directory
        
        Args:
            directory_path: Path to directory (uses default if None)
            
        Returns:
            Statistics about the ingestion
        """
        directory_path = directory_path or self.raw_docs_path
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"# STARTING DOCUMENT INGESTION PIPELINE")
        logger.info(f"# Directory: {directory_path}")
        logger.info(f"{'#'*60}\n")
        
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return {'success': False, 'error': 'Directory not found'}
        
        # Find all PDFs
        pdf_files = list(Path(directory_path).rglob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {'success': False, 'error': 'No PDF files found'}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process\n")
        
        # Process each PDF
        total_chunks = 0
        successful = 0
        failed = 0
        
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"[{i}/{len(pdf_files)}] Processing {os.path.basename(pdf_path)}")
            
            chunks_created = self.ingest_single_pdf(str(pdf_path))
            
            if chunks_created > 0:
                successful += 1
                total_chunks += chunks_created
            else:
                failed += 1
        
        # Get collection stats / verify readiness
        try:
            collection_count = self.vector_store.assert_ready()
            logger.info(f"Vector store ready with {collection_count} chunks.")
        except RuntimeError as readiness_error:
            logger.error("Vector store is not ready: %s", readiness_error)
            collection_count = 0
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"INGESTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total PDFs processed: {len(pdf_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total chunks created: {total_chunks}")
        logger.info(f"Chunks in vector DB: {collection_count}")
        logger.info(f"{'='*60}\n")
        
        return {
            'success': collection_count > 0,
            'total_pdfs': len(pdf_files),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks,
            'vector_db_count': collection_count
        }
    
    def _attach_translations(self, chunks: List[DocumentChunk]) -> None:
        """
        Translate chunk content into configured target languages and store in metadata.
        Uses Ollama for full document translation (JSON files are only for phrase lookups).
        """
        if not self.translation_targets:
            logger.info("No target languages configured, skipping translation")
            return
        
        total_chunks = len(chunks)
        total_translations = total_chunks * len(self.translation_targets)
        logger.info(f"\n{'='*60}")
        logger.info(f"TRANSLATING DOCUMENT CHUNKS")
        logger.info(f"Chunks to translate: {total_chunks}")
        logger.info(f"Target languages: {', '.join(self.translation_targets)}")
        logger.info(f"Total translations needed: {total_translations}")
        logger.info(f"{'='*60}\n")
        
        translated_count = 0
        skipped_count = 0
        failed_count = 0
        
        for idx, chunk in enumerate(chunks, 1):
            base_text = chunk.content.strip()
            if not base_text:
                skipped_count += 1
                continue
            
            # Detect source language from metadata or default to configured source
            source_language = chunk.metadata.get("language", settings.SOURCE_LANGUAGE)
            domain = chunk.metadata.get("domain", settings.DEFAULT_DOMAIN)
            translations: Dict[str, str] = chunk.metadata.get("translations", {})
            
            for target_language in self.translation_targets:
                # Skip if same language or already translated
                if target_language == source_language:
                    skipped_count += 1
                    continue
                if target_language in translations:
                    skipped_count += 1
                    continue
                
                try:
                    # Show progress
                    progress = ((idx - 1) * len(self.translation_targets) + 
                               list(self.translation_targets).index(target_language) + 1)
                    logger.info(
                        f"[{progress}/{total_translations}] Translating chunk {idx}/{total_chunks} "
                        f"({source_language} → {target_language})..."
                    )
                    
                    # Translate using Ollama (falls back from JSON memory if phrase exists)
                    translated = asyncio.run(
                        self.translation_service.translate_text(
                            text=base_text,
                            source_language=source_language,
                            target_language=target_language,
                            domain=domain
                        )
                    )
                    translations[target_language] = translated
                    translated_count += 1
                    
                except Exception as exc:
                    logger.error(
                        f"✗ Failed translating chunk {idx} ({source_language}→{target_language}): {exc}",
                        exc_info=False
                    )
                    failed_count += 1
            
            # Store translations in metadata
            if translations:
                chunk.metadata["translations"] = translations
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TRANSLATION SUMMARY")
        logger.info(f"✓ Successfully translated: {translated_count}")
        logger.info(f"⊘ Skipped (already translated/same language): {skipped_count}")
        logger.info(f"✗ Failed: {failed_count}")
        logger.info(f"{'='*60}\n")
    
    def test_search(self, query: str, n_results: int = 3):
        """
        Test search functionality
        
        Args:
            query: Search query
            n_results: Number of results to return
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"TESTING SEARCH")
        logger.info(f"Query: '{query}'")
        logger.info(f"{'='*60}\n")
        
        results = self.vector_store.search(query, n_results=n_results)
        
        if not results['documents']:
            logger.info("No results found")
            return
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            logger.info(f"\n--- Result {i} (Distance: {distance:.4f}) ---")
            logger.info(f"Source: {metadata.get('source', 'Unknown')}")
            logger.info(f"Page: {metadata.get('page_number', '?')}")
            logger.info(f"Type: {metadata.get('document_type', 'Unknown')}")
            logger.info(f"Content: {doc[:200]}...")
        
        logger.info(f"\n{'='*60}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest Kenyan government documents')
    parser.add_argument('--directory', type=str, help='Directory containing PDFs')
    parser.add_argument('--file', type=str, help='Single PDF file to process')
    parser.add_argument('--test-search', type=str, help='Test search with a query')
    parser.add_argument('--reset', action='store_true', help='Reset vector database before ingestion')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = DocumentIngestionPipeline()
    
    # Reset if requested
    if args.reset:
        logger.info("Resetting vector database...")
        pipeline.vector_store.reset()
    
    # Process files
    if args.file:
        # Single file
        pipeline.ingest_single_pdf(args.file)
    elif args.directory:
        # Directory
        pipeline.ingest_directory(args.directory)
    else:
        # Use default directory
        pipeline.ingest_directory()
    
    # Test search if requested
    if args.test_search:
        pipeline.test_search(args.test_search)
    else:
        # Run default test searches
        logger.info("\n" + "="*60)
        logger.info("Running test searches...")
        logger.info("="*60 + "\n")
        
        test_queries = [
            "How do I register a business in Kenya?",
            "What are my constitutional rights?",
            "How do I get a title deed?"
        ]
        
        for query in test_queries:
            pipeline.test_search(query, n_results=2)


if __name__ == "__main__":
    main()