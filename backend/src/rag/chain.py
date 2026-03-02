"""RAG Chain orchestration"""

import logging
from typing import List, Dict, Any, Optional

from src.rag.llm import OllamaLLM
from src.rag.retriever import Retriever
from src.vector_store.store import VectorStore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant answering questions about Promtior.
Use the provided context to answer the user's question accurately.
If the context doesn't contain the answer, say so honestly.
Keep your answers clear and concise."""

QUESTION_TEMPLATE = """Context:
{context}

Question: {question}

Answer: """


class RAGChain:
    """Complete RAG pipeline: retrieval + generation"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm: Optional[OllamaLLM] = None,
        top_k: int = 3,
    ):
        """
        Initialize RAG chain.
        
        Args:
            vector_store: Vector store for retrieval
            llm: LLM instance (will create if not provided)
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store
        self.llm = llm or OllamaLLM()
        self.retriever = Retriever(vector_store, top_k=top_k)
        logger.info("RAG Chain initialized")
    
    def invoke(self, query: str) -> Dict[str, Any]:
        """
        Execute the full RAG pipeline.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with response and sources
        """
        logger.info(f"RAG Chain invoked with query: {query}")
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(query)
        
        # Format context
        context = self.retriever.format_context(retrieved_docs)
        
        # Generate prompt
        prompt = QUESTION_TEMPLATE.format(
            context=context,
            question=query,
        )
        
        logger.debug(f"Generated prompt: {prompt[:200]}...")
        
        # Generate answer
        try:
            answer = self.llm.invoke(prompt)
            logger.info(f"Generated answer (length: {len(answer)})")
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            answer = f"Error generating answer: {str(e)}"
        
        # Extract source information
        sources = [
            {
                'content': doc['content'][:200],
                'metadata': doc['metadata'],
            }
            for doc in retrieved_docs
        ]
        
        return {
            'query': query,
            'answer': answer,
            'sources': sources,
        }
    
    def stream(self, query: str):
        """
        Stream the RAG pipeline with streaming answer generation.
        
        Args:
            query: User query
            
        Yields:
            Dictionary chunks with incrementally built answer and sources
        """
        logger.info(f"RAG Chain streaming with query: {query}")
        
        # Retrieve relevant documents (non-streaming)
        retrieved_docs = self.retriever.retrieve(query)
        
        # Extract source information
        sources = [
            {
                'content': doc['content'][:200],
                'metadata': doc['metadata'],
            }
            for doc in retrieved_docs
        ]
        
        # Format context
        context = self.retriever.format_context(retrieved_docs)
        
        # Generate prompt
        prompt = QUESTION_TEMPLATE.format(
            context=context,
            question=query,
        )
        
        logger.debug(f"Generated prompt for streaming: {prompt[:200]}...")
        
        # Yield sources first
        logger.info(f"Yielding {len(sources)} sources")
        yield {
            'type': 'sources',
            'sources': sources,
        }
        
        # Stream the answer
        try:
            answer_length = 0
            chunk_count = 0
            logger.info("Starting LLM stream generation")
            
            for chunk in self.llm.stream(prompt):
                chunk_count += 1
                chunk_len = len(chunk)
                answer_length += chunk_len
                
                logger.debug(f"Chunk {chunk_count}: {chunk_len} chars, total: {answer_length}")
                
                yield {
                    'type': 'chunk',
                    'chunk': chunk,
                }
            
            logger.info(f"Finished streaming answer - {chunk_count} chunks, {answer_length} total chars")
        except Exception as e:
            logger.error(f"Error streaming answer: {str(e)}", exc_info=True)
            yield {
                'type': 'error',
                'error': str(e),
            }
