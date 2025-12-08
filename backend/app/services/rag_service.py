"""
RAG Service for Serikali Yangu
Retrieves relevant documents and generates contextual answers
"""

import logging
from typing import List, Dict, Any, Optional
from app.core.vector_store import VectorStore
from app.services.ollama_service import OllamaService
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self):
        self.vector_store = VectorStore(
            collection_name="kenyan_gov_docs",
            persist_directory=settings.VECTOR_DB_PATH
        )
        self.ollama_service = OllamaService()
        logger.info("RAG Service initialized")
    
    def search_documents(
        self,
        query: str,
        n_results: int = 3,
        document_type: Optional[str] = None,
        domain: Optional[str] = None,
        target_language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: User's question
            n_results: Number of results to return
            document_type: Optional filter by document type
            
        Returns:
            List of relevant document chunks with metadata
        """
        logger.info(f"Searching documents for: '{query}'")
        
        # Build filter if document type specified
        filter_metadata = None
        if document_type or domain:
            filter_metadata = {}
            if document_type:
                filter_metadata["document_type"] = document_type
            if domain:
                filter_metadata["domain"] = domain
        
        # Search vector store
        results = self.vector_store.search(
            query=query,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                translations = metadata.get('translations', {}) if isinstance(metadata, dict) else {}
                display_content = doc
                if target_language and isinstance(translations, dict):
                    display_content = translations.get(target_language, doc)
                formatted_results.append({
                    'content': display_content,
                    'metadata': metadata,
                    'relevance_score': 1 - distance,  # Convert distance to similarity
                    'source': metadata.get('source', 'Unknown'),
                    'page': metadata.get('page_number', '?'),
                    'document_type': metadata.get('document_type', 'general')
                })
        
        logger.info(f"Found {len(formatted_results)} relevant chunks")
        return formatted_results
    
    def create_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Create context from search results for the LLM
        
        Args:
            search_results: List of relevant documents
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant information found in government documents."
        
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            source = result['source']
            page = result['page']
            content = result['content']
            
            context_parts.append(
                f"[Document {i}: {source}, Page {page}]\n{content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        return context
    
    def create_system_prompt(self, domain: str = settings.DEFAULT_DOMAIN) -> str:
        """Return a domain-aware system prompt."""
        civic_prompt = """You are Serikali Yangu, an AI assistant for Kenyan government information.

Your role:
- Answer questions about Kenyan laws, policies, and government services.
- Provide accurate information based on official government documents.
- Always cite your sources when providing information.
- Be helpful, clear, and respectful.
- Use simple language that citizens can understand.

Important rules:
1. ONLY use information from the provided documents.
2. ALWAYS cite which document and page your answer comes from.
3. If the documents don't contain the answer, say so clearly.
4. Never make up information.
5. If a question is unclear, ask for clarification.

Format your answers like this:
- Start with a direct answer.
- Provide relevant details.
- End with source citations in brackets like [Source: constitution.pdf, Page 5].
"""
        health_prompt = """You are AfyaTranslate, a Kenyan healthcare language assistant.

Your role:
- Support clinicians and patients by translating and explaining medical information accurately.
- Use compassionate language and prioritize patient safety.
- Reference Kenyan Ministry of Health guidance and provided medical documents.
- Highlight critical instructions (dosage, follow-up) clearly.

Important rules:
1. Stick to the provided medical context; avoid speculation.
2. Flag emergencies if symptoms sound life threatening and recommend immediate care.
3. Use simple, culturally sensitive explanations.
4. Cite the source document or phrase pack when possible.
"""
        return health_prompt if domain == "health" else civic_prompt
    
    def create_prompt_with_context(
        self,
        query: str,
        context: str,
        domain: str = settings.DEFAULT_DOMAIN
    ) -> str:
        """
        Create the full prompt with context for the LLM
        
        Args:
            query: User's question
            context: Retrieved document context
            
        Returns:
            Formatted prompt
        """
        domain_label = "healthcare guidance" if domain == "health" else "government documents"
        prompt = f"""Context from Kenyan {domain_label}:

{context}

---

User Question: {query}

Based ONLY on the documents provided above, please answer the user's question. 
Remember to cite your sources using the format [Source: document_name, Page X].

If the documents don't contain information to answer the question, say:
"I don't have information about that in the available government documents. Please try rephrasing your question or visit your nearest Huduma Centre for assistance."

Answer:"""
        
        return prompt
    
    def extract_citations(
        self,
        answer: str,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Extract and format citations from search results
        
        Args:
            answer: Generated answer
            search_results: Documents used for context
            
        Returns:
            List of citation objects
        """
        citations = []
        
        for result in search_results:
            citations.append({
                'source': result['source'],
                'page': str(result['page']),
                'document_type': result['document_type'],
                'relevance': f"{result['relevance_score']:.2f}"
            })
        
        return citations
    
    async def query(
        self,
        question: str,
        n_results: int = 3,
        document_type: Optional[str] = None,
        domain: str = settings.DEFAULT_DOMAIN,
        target_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main RAG query method
        
        Args:
            question: User's question
            n_results: Number of documents to retrieve
            document_type: Optional document type filter
            
        Returns:
            Answer with sources and metadata
        """
        logger.info(f"Processing RAG query: '{question}'")
        
        try:
            # Ensure vector store has data before querying
            try:
                self.vector_store.assert_ready()
            except RuntimeError as readiness_error:
                logger.error("Vector store not ready: %s", readiness_error)
                return {
                    "answer": (
                        "Document knowledge base is empty. Please run the ingestion pipeline "
                        "to load Kenyan government documents before chatting."
                    ),
                    "sources": [],
                    "status": "vector_store_not_ready",
                    "error": str(readiness_error)
                }

            # Step 1: Search for relevant documents
            search_results = self.search_documents(
                query=question,
                n_results=n_results,
                document_type=document_type,
                domain=domain,
                target_language=target_language
            )
            
            if not search_results:
                return {
                    "answer": "I couldn't find relevant information in the government documents. Please try rephrasing your question or contact your nearest Huduma Centre for assistance.",
                    "sources": [],
                    "status": "no_results"
                }
            
            # Step 2: Create context from results
            context = self.create_context(search_results)
            
            # Step 3: Create prompt
            system_prompt = self.create_system_prompt(domain)
            user_prompt = self.create_prompt_with_context(question, context, domain)
            
            # Step 4: Generate answer using Ollama
            logger.info("Generating answer with Ollama...")
            answer = await self.ollama_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Step 5: Extract citations
            citations = self.extract_citations(answer, search_results)
            
            logger.info("RAG query completed successfully")
            
            return {
                "answer": answer.strip(),
                "sources": citations,
                "status": "success",
                "retrieved_chunks": len(search_results)
            }
        
        except Exception as e:
            logger.error(f"Error in RAG query: {e}", exc_info=True)
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "status": "error",
                "error": str(e)
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            count = self.vector_store.get_collection_count()
            return {
                "total_chunks": count,
                "status": "healthy" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_chunks": 0,
                "status": "error",
                "error": str(e)
            }
