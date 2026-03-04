import logging
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingModel:
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
       
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise
    
    def embed_single(self, text: str) -> List[float]:

        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
    
    def get_dimension(self) -> int:
        
        return self.model.get_sentence_embedding_dimension()
