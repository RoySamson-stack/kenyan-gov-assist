"""
Vector Store using ChromaDB for document embeddings
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document embeddings"""
    
    def __init__(
        self,
        collection_name: str = "kenyan_gov_docs",
        persist_directory: str = "../data/vector_db/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        self._init_chromadb()
        self._init_embedding_model()
    
    def _init_chromadb(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            logger.info("Initializing ChromaDB at %s", self.persist_directory)
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB initialized successfully")
        
        except ImportError:
            logger.warning("ChromaDB not available. Install with: pip install chromadb")
        except Exception as exc:
            logger.error("Failed to initialize ChromaDB: %s", str(exc))
    
    def _init_embedding_model(self):
        """Initialize sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Loading embedding model: %s", self.embedding_model_name)
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded successfully")
        
        except ImportError:
            logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
        except Exception as exc:
            logger.error("Failed to load embedding model: %s", str(exc))
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dicts with 'content' and 'metadata'
            embeddings: Optional pre-computed embeddings
            
        Returns:
            True if successful
        """
        if not self.collection:
            logger.error("ChromaDB not initialized")
            return False
        
        try:
            ids = [f"doc_{i}" for i in range(len(documents))]
            texts = [doc.get('content', '') for doc in documents]
            metadatas = [doc.get('metadata', {}) for doc in documents]
            
            # Generate embeddings if not provided
            if embeddings is None and self.embedding_model:
                embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            else:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            
            logger.info("Added %d documents to vector store", len(documents))
            return True
        
        except Exception as exc:
            logger.error("Failed to add documents: %s", str(exc))
            return False
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Returns:
            List of dicts with 'content', 'metadata', and 'distance'
        """
        if not self.collection:
            logger.error("ChromaDB not initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = None
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=filter_metadata,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=filter_metadata,
                    include=["documents", "metadatas", "distances"]
                )
            
            # Format results
            formatted = []
            if results and results.get('documents'):
                for i, doc in enumerate(results['documents'][0]):
                    formatted.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 1.0
                    })
            
            return formatted
        
        except Exception as exc:
            logger.error("Search failed: %s", str(exc))
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        if not self.collection:
            return {"error": "ChromaDB not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection_name
            }
        except Exception as exc:
            return {"error": str(exc)}
    
    def reset_collection(self) -> bool:
        """Reset (delete and recreate) the collection."""
        if not self.client:
            return False
        
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection reset successfully")
            return True
        except Exception as exc:
            logger.error("Failed to reset collection: %s", str(exc))
            return False
