"""
Embedding Service for document vectorization
Uses sentence-transformers for generating embeddings
"""
import logging
from typing import List, Optional
import numpy as np

from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    Falls back to simple TF-IDF if model loading fails.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or "all-MiniLM-L6-v2"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings (n_texts x embedding_dim)
        """
        if not texts:
            return np.array([])
        
        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                return embeddings
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
        
        # Fallback: simple character n-gram embeddings
        logger.warning("Using fallback embedding method")
        return self._fallback_embeddings(texts)
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Returns:
            Embedding vector as numpy array
        """
        result = self.encode([text])
        return result[0] if len(result) > 0 else np.array([])
    
    def _fallback_embeddings(self, texts: List[str], dim: int = 384) -> np.ndarray:
        """
        Simple fallback embedding using character n-grams.
        Not as good as transformer models but works without dependencies.
        """
        embeddings = []
        for text in texts:
            # Create a simple character n-gram representation
            text_lower = text.lower()
            vector = np.zeros(dim)
            
            # Use character trigrams
            for i in range(len(text_lower) - 2):
                ngram = text_lower[i:i+3]
                # Simple hash to dim dimensions
                idx = hash(ngram) % dim
                vector[idx] += 1
            
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            embeddings.append(vector)
        
        return np.array(embeddings)
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Returns:
            Similarity score between -1 and 1
        """
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))
