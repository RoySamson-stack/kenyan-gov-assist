"""
Chat API routes with RAG integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.config import settings
from app.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()


class ChatRequest(BaseModel):
    message: str
    language: str = "english"
    use_rag: bool = True  # Toggle RAG on/off
    document_type: Optional[str] = None  # Filter by document type
    domain: str = settings.DEFAULT_DOMAIN


class Source(BaseModel):
    source: str
    page: str
    document_type: str
    relevance: str


class ChatResponse(BaseModel):
    response: str
    sources: List[Source] = []
    language: str
    status: str
    retrieved_chunks: Optional[int] = None
    domain: str = settings.DEFAULT_DOMAIN


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with RAG integration
    
    Args:
        request: ChatRequest with user message and preferences
        
    Returns:
        ChatResponse with answer and source citations
    """
    try:
        logger.info(
            "Chat request: '%s' (RAG: %s, Lang: %s, Domain: %s)",
            request.message,
            request.use_rag,
            request.language,
            request.domain,
        )
        domain = request.domain if request.domain in settings.SUPPORTED_DOMAINS else settings.DEFAULT_DOMAIN
        
        if request.use_rag:
            # Use RAG to answer from documents
            result = await rag_service.query(
                question=request.message,
                n_results=3,
                document_type=request.document_type,
                domain=domain,
                target_language=request.language
            )
            
            # Convert sources to Source objects
            sources = [
                Source(
                    source=src['source'],
                    page=src['page'],
                    document_type=src['document_type'],
                    relevance=src['relevance']
                )
                for src in result.get('sources', [])
            ]
            
            return ChatResponse(
                response=result['answer'],
                sources=sources,
                language=request.language,
                status=result['status'],
                retrieved_chunks=result.get('retrieved_chunks', 0),
                domain=domain
            )
        else:
            # Direct Ollama call without RAG (fallback)
            from app.services.ollama_service import OllamaService
            ollama = OllamaService()
            
            response = await ollama.generate(
                prompt=request.message,
                system_prompt=rag_service.create_system_prompt(domain)
            )
            
            return ChatResponse(
                response=response,
                sources=[],
                language=request.language,
                status="direct_ollama",
                domain=domain
            )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/chat/stats")
async def get_chat_stats():
    """
    Get statistics about the document collection
    
    Returns:
        Collection statistics
    """
    try:
        stats = rag_service.get_collection_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/search")
async def search_documents(query: str, document_type: Optional[str] = None):
    """
    Search documents without generating an answer
    
    Args:
        query: Search query
        document_type: Optional document type filter
        
    Returns:
        Relevant document chunks
    """
    try:
        results = rag_service.search_documents(
            query=query,
            n_results=5,
            document_type=document_type
        )
        
        return {
            "status": "success",
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
