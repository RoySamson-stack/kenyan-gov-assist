"""
Document upload and processing endpoints
Supports PDF, DOCX, XLSX, CSV, TXT, MD, EPUB, HTML
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
import shutil
import os

from app.config import settings
from app.core.document_processors import DocumentProcessorFactory
from app.core.document_processor import DocumentProcessor as PDFProcessor
from app.services.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()
doc_factory = DocumentProcessorFactory()
pdf_processor = PDFProcessor()
embedding_service = EmbeddingService()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    domain: str = "civic",
    process_immediately: bool = True
):
    """
    Upload a document for processing.
    Supports: PDF, DOCX, XLSX, CSV, TXT, MD, EPUB, HTML
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    file_size = 0
    temp_path = f"/tmp/{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(temp_path)
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        
        if file_size > max_size_bytes:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        if not process_immediately:
            return {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "size": file_size,
                "path": temp_path
            }
        
        # Process the document
        chunks = []
        
        # Try the factory first (for non-PDF files)
        processor = doc_factory.get_processor(temp_path)
        if processor:
            doc_chunks = processor.process(temp_path)
            chunks = [{
                'content': c['content'],
                'metadata': {
                    **c['metadata'],
                    'domain': domain,
                    'language': 'english'  # TODO: detect language
                }
            } for c in doc_chunks]
        else:
            # Fallback to PDF processor
            pdf_chunks = pdf_processor.process_pdf(temp_path)
            chunks = [{
                'content': c.content,
                'metadata': {
                    **c.metadata,
                    'domain': domain,
                    'language': pdf_processor._detect_language(file.filename, c.content)
                }
            } for c in pdf_chunks]
        
        if not chunks:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Could not extract content from document")
        
        # Generate embeddings
        texts = [c['content'] for c in chunks]
        embeddings = embedding_service.encode(texts)
        
        # Store in vector database
        vector_store = VectorStore()
        vector_store.add_documents(chunks, embeddings)
        
        # Cleanup
        os.remove(temp_path)
        
        return {
            "status": "success",
            "message": f"Document processed successfully",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "domain": domain,
            "sample_chunk": chunks[0]['content'][:200] if chunks else ""
        }
    
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/documents/supported-formats")
async def get_supported_formats():
    """Return list of supported file formats."""
    return {
        "formats": settings.ALLOWED_EXTENSIONS,
        "max_size_mb": settings.MAX_FILE_SIZE_MB,
        "description": {
            ".pdf": "PDF documents",
            ".docx": "Word documents",
            ".xlsx": "Excel spreadsheets",
            ".csv": "CSV files",
            ".txt": "Text files",
            ".md": "Markdown files",
            ".epub": "EPUB ebooks",
            ".html": "HTML files"
        }
    }


@router.post("/documents/process-directory")
async def process_directory(path: str, domain: str = "civic"):
    """
    Process all supported documents in a directory.
    Admin endpoint for bulk processing.
    """
    from pathlib import Path as PathLib
    
    dir_path = PathLib(path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    all_chunks = []
    
    for ext in settings.ALLOWED_EXTENSIONS:
        for file_path in dir_path.rglob(f"*{ext}"):
            try:
                processor = doc_factory.get_processor(str(file_path))
                if processor:
                    doc_chunks = processor.process(str(file_path))
                    all_chunks.extend(doc_chunks)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
    
    return {
        "status": "success",
        "files_processed": len(all_chunks),
        "total_chunks": len(all_chunks)
    }
