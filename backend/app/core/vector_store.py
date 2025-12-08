"""
Vector Store using ChromaDB for document embeddings
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

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
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
        except Exception as exc:
            error_message = (
                f"Failed to load embedding model '{embedding_model}'. "
                "Ensure the 'sentence-transformers' package is installed and the model is available. "
                "You can install the dependency with 'pip install sentence-transformers'."
            )
            logger.error(error_message, exc_info=True)
            raise RuntimeError(error_message) from exc
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection '{collection_name}' with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Kenyan government documents"}
            )
            logger.info(f"Created new collection '{collection_name}'")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dicts
            ids: List of unique IDs
        """
        if not texts:
            logger.warning("No texts provided to add_documents")
            return
        
        logger.info(f"Adding {len(texts)} documents to vector store")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Add to collection
        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(texts)} documents")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def update_metadatas(self, ids: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Update metadata for existing documents."""
        if not ids:
            return
        try:
            self.collection.update(ids=ids, metadatas=metadatas)
            logger.info("Updated metadata for %d ids", len(ids))
        except Exception as exc:
            logger.error("Failed to update metadata: %s", exc)
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            Search results with documents, metadatas, and distances
        """
        logger.info(f"Searching for: '{query}' (n_results={n_results})")
        
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]
        
        # Search
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            logger.info(f"Found {len(results['documents'][0])} results")
            return results
        
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        try:
            return self.collection.count()
        except Exception as exc:
            logger.error("Unable to read collection count from ChromaDB", exc_info=True)
            raise RuntimeError("ChromaDB collection is unavailable.") from exc

    def is_empty(self) -> bool:
        """Return True when the collection has no documents"""
        try:
            return self.get_collection_count() == 0
        except RuntimeError:
            # get_collection_count already logged the error
            raise

    def assert_ready(self) -> int:
        """
        Ensure the vector store contains data.

        Returns:
            Document count when ready.

        Raises:
            RuntimeError: if the collection is empty or inaccessible.
        """
        count = self.get_collection_count()
        if count == 0:
            raise RuntimeError(
                "Vector store is empty. Run 'python backend/scripts/ingest_documents.py "
                "--reset --directory data/raw' to ingest documents before serving requests."
            )
        return count
    
    def reset(self) -> None:
        """Reset the collection (delete all documents)"""
        logger.warning(f"Resetting collection '{self.collection_name}'")
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Kenyan government documents"}
            )
            logger.info("Collection reset successfully")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
    
    def get_by_source(self, source: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Get documents by source file
        
        Args:
            source: Source filename
            n_results: Number of results
            
        Returns:
            Documents from the specified source
        """
        logger.info(f"Getting documents from source: {source}")
        
        try:
            results = self.collection.get(
                where={"source": source},
                limit=n_results
            )
            
            logger.info(f"Found {len(results['documents'])} documents from {source}")
            return results
        
        except Exception as e:
            logger.error(f"Error getting documents by source: {e}")
            return {
                'documents': [],
                'metadatas': [],
                'ids': []
            }
    
    def get_by_type(self, document_type: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Get documents by document type
        
        Args:
            document_type: Type of document (constitution, business, etc.)
            n_results: Number of results
            
        Returns:
            Documents of the specified type
        """
        logger.info(f"Getting documents of type: {document_type}")
        
        try:
            results = self.collection.get(
                where={"document_type": document_type},
                limit=n_results
            )
            
            logger.info(f"Found {len(results['documents'])} documents of type {document_type}")
            return results
        
        except Exception as e:
            logger.error(f"Error getting documents by type: {e}")
            return {
                'documents': [],
                'metadatas': [],
                'ids': []
            }


# Test function
def test_vector_store():
    """Test the vector store"""
    logger.info("Testing VectorStore...")
    
    # Initialize
    store = VectorStore()
    
    # Add test documents
    texts = [
        "Every person has the right to education under Article 43 of the Constitution.",
        "Business registration in Kenya requires a valid ID and business name.",
        "Land title deeds are issued by the Ministry of Lands."
    ]
    
    metadatas = [
        {"source": "constitution.pdf", "page_number": 1, "document_type": "constitution"},
        {"source": "business_act.pdf", "page_number": 5, "document_type": "business"},
        {"source": "land_act.pdf", "page_number": 10, "document_type": "land"}
    ]
    
    ids = ["test_1", "test_2", "test_3"]
    
    # Reset and add
    store.reset()
    store.add_documents(texts, metadatas, ids)
    
    # Test search
    results = store.search("How do I register a business?", n_results=2)
    
    print("\nSearch Results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n{i}. {doc}")
        print(f"   Source: {metadata['source']}")
        print(f"   Type: {metadata['document_type']}")
    
    print(f"\nCollection count: {store.get_collection_count()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_vector_store()