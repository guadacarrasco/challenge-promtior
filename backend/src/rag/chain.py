
import logging
from typing import List, Dict, Any, Optional

from src.rag.llm import OpenAILLM
from src.rag.retriever import Retriever
from src.vector_store.store import VectorStore

logger = logging.getLogger(__name__)

QUESTION_TEMPLATE = """Context:
{context}

Question: {question}

Answer: """


class RAGChain:
  
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm: Optional[OpenAILLM] = None,
        top_k: int = 3,
    ):
        
        self.vector_store = vector_store
        self.llm = llm or OpenAILLM()
        self.retriever = Retriever(vector_store, top_k=top_k)
      
    
    def invoke(self, query: str) -> Dict[str, Any]:
        
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(query)
        
        # Format context
        context = self.retriever.format_context(retrieved_docs)
        
        # Generate prompt
        prompt = QUESTION_TEMPLATE.format(
            context=context,
            question=query,
        )
        
       
        
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
        

        
        # Yield sources first
       
        yield {
            'type': 'sources',
            'sources': sources,
        }
        
        # Stream the answer
        try:
            answer_length = 0
            chunk_count = 0
            
            
            for chunk in self.llm.stream(prompt):
                chunk_count += 1
                chunk_len = len(chunk)
                answer_length += chunk_len
                

                
                yield {
                    'type': 'chunk',
                    'chunk': chunk,
                }
            

        except Exception as e:
            logger.error(f"Error streaming answer: {str(e)}", exc_info=True)
            yield {
                'type': 'error',
                'error': str(e),
            }
