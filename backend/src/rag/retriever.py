
import logging
from typing import List, Dict, Any

from src.vector_store.store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    
    
    def __init__(self, vector_store: VectorStore, top_k: int = 3):
        
        self.vector_store = vector_store
        self.top_k = top_k

    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        

        results = self.vector_store.search(query, k=self.top_k)

        return results
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
       
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc['metadata'].get('source', 'Unknown source')
            content = doc['content']
            context_parts.append(f"[{i}] ({source}): {content}")
        
        return "\n\n".join(context_parts)
