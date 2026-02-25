"""Retriever module for vector store retrieval"""

import logging
from typing import List, Dict, Any

from src.vector_store.store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents from vector store"""
    
    def __init__(self, vector_store: VectorStore, top_k: int = 3):
        """
        Initialize retriever.
        
        Args:
            vector_store: VectorStore instance
            top_k: Number of results to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
        logger.info(f"Retriever initialized with top_k={top_k}")
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            
        Returns:
            List of relevant documents
        """
        logger.info(f"Retrieving documents for query: {query}")
        results = self.vector_store.search(query, k=self.top_k)
        logger.info(f"Retrieved {len(results)} documents")
        return results
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc['metadata'].get('source', 'Unknown source')
            content = doc['content']
            context_parts.append(f"[{i}] ({source}): {content}")
        
        return "\n\n".join(context_parts)
