
import logging
from typing import List, Dict, Any

from src.vector_store.store import VectorStore

logger = logging.getLogger(__name__)


# Maximum cosine distance to consider a document relevant.
# ChromaDB cosine distance ranges from 0 (identical) to 2 (opposite).
# Documents further than this threshold are discarded as irrelevant.
MAX_RELEVANCE_DISTANCE = 1.2


class Retriever:
    
    
    def __init__(self, vector_store: VectorStore, top_k: int = 3, max_distance: float = MAX_RELEVANCE_DISTANCE):
        
        self.vector_store = vector_store
        self.top_k = top_k
        self.max_distance = max_distance

    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        

        results = self.vector_store.search(query, k=self.top_k)

        # Filter out documents that are too far from the query (irrelevant)
        filtered = [doc for doc in results if doc.get('distance', 0) <= self.max_distance]
        if len(filtered) < len(results):
            logger.info(f"Filtered out {len(results) - len(filtered)} irrelevant documents (distance > {self.max_distance})")

        return filtered
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
       
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc['metadata'].get('source', 'Unknown source')
            content = doc['content']
            context_parts.append(f"[{i}] ({source}): {content}")
        
        return "\n\n".join(context_parts)
