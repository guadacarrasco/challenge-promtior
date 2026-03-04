

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from langserve import add_routes

# Import RAG components
from src.vector_store.store import VectorStore
from src.rag.chain import RAGChain
from src.rag.llm import OpenAILLM

# Logging setup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
rag_chain: Optional[RAGChain] = None
vector_store: Optional[VectorStore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("Starting up application...")
    
    try:
        global vector_store, rag_chain
        
        # Initialize vector store
        persist_dir = os.getenv("VECTOR_STORE_PATH", "./chroma_data")

        vector_store = VectorStore(persist_dir=persist_dir)
        
        stats = vector_store.get_stats()
     
        
        if stats['document_count'] == 0:
            logger.info("Vector store is empty — running automatic ingestion")
            from src.vector_store.init_vector_store import init_vector_store
            init_vector_store(persist_dir=persist_dir)
            # Reload store after population
            vector_store = VectorStore(persist_dir=persist_dir)
            stats = vector_store.get_stats()
           
        
        # Initialize LLM
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        
        llm = OpenAILLM(
            api_key=openai_api_key,
            model=openai_model,
            temperature=0.7,
        )
        
        # Initialize RAG chain
        rag_chain = RAGChain(vector_store=vector_store, llm=llm, top_k=3)
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Promtior RAG Chatbot API",
    description="RAG API for asking questions about Promtior",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryOutput(BaseModel):

    answer: str
    sources: list = []


class RAGChainRunnable(Runnable):
   
    
    def invoke(self, input_data, config=None):
      
        global rag_chain
        
        if rag_chain is None:
            raise RuntimeError("RAG chain not initialized")
        
        if isinstance(input_data, dict):
            query = input_data.get("query")
        else:
            query = input_data.query
        
    
        
        # Invoke the RAG chain
        result = rag_chain.invoke(query)
        
        return QueryOutput(
            answer=result.get("answer", ""),
            sources=result.get("sources", [])
        )
    
    def stream(self, input_data, config=None):
       
        global rag_chain
        
        if rag_chain is None:
            raise RuntimeError("RAG chain not initialized")
        
        if isinstance(input_data, dict):
            query = input_data.get("query")
        else:
            query = input_data.query
        
       
        
        # Stream the RAG chain
        full_answer = ""
        sources = None
        
        for item in rag_chain.stream(query):
            if item.get("type") == "sources":
                sources = item.get("sources", [])
                # Yield sources first
                yield QueryOutput(answer="", sources=sources)
            elif item.get("type") == "chunk":
                chunk = item.get("chunk", "")
                full_answer += chunk
                # Yield progressive updates with accumulated answer
                yield QueryOutput(answer=full_answer, sources=sources or [])
            elif item.get("type") == "error":
                error_msg = item.get("error", "Unknown error")
                logger.error(f"Error in stream: {error_msg}")
                raise RuntimeError(error_msg)



add_routes(
    app,
    RAGChainRunnable(),
    path="/chain",
    enable_feedback_endpoint=False,  # Disable feedback for now
)




# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    global rag_chain, vector_store
    
    if rag_chain is None or vector_store is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    stats = vector_store.get_stats()
    return {
        "status": "ok",
        "vector_store": stats,
    }




if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
    )
