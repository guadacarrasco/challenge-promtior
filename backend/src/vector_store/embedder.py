"""Embedding model setup and management"""

import logging
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"Embedding model loaded successfully")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            # Convert numpy arrays to lists
            return [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise
    
    def embed_single(self, text: str) -> List[float]:
        """Embed a single text string"""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.model.get_sentence_embedding_dimension()
