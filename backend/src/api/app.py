"""FastAPI application with LangServe endpoints - Pure LangServe implementation"""

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
from src.rag.llm import OllamaLLM

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
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting up application...")
    
    try:
        global vector_store, rag_chain
        
        # Initialize vector store
        persist_dir = os.getenv("VECTOR_STORE_PATH", "./chroma_data")
        logger.info(f"Loading vector store from {persist_dir}")
        vector_store = VectorStore(persist_dir=persist_dir)
        
        stats = vector_store.get_stats()
        logger.info(f"Vector store stats: {stats}")
        
        if stats['document_count'] == 0:
            logger.warning("Vector store is empty! Run init_vector_store first.")
        
        # Initialize LLM
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Initializing OpenAI LLM: {openai_model}")
        
        llm = OllamaLLM(
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
    description="RAG API for asking questions about Promtior using LangChain with LangServe",
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


# LangServe Input/Output models following LangChain conventions
class QueryInput(BaseModel):
    """Input model for RAG queries"""
    query: str


class QueryOutput(BaseModel):
    """Output model for RAG responses"""
    answer: str
    sources: list = []


class RAGChainRunnable(Runnable):
    """
    LangServe-compatible Runnable wrapper for the RAG chain.
    This follows LangChain's Runnable protocol.
    """
    
    def invoke(self, input_data, config=None):
        """Invoke the RAG chain with a query"""
        global rag_chain
        
        if rag_chain is None:
            raise RuntimeError("RAG chain not initialized")
        
        # Handle both dict and QueryInput
        if isinstance(input_data, dict):
            query = input_data.get("query")
        else:
            query = input_data.query
        
        logger.info(f"RAG Chain invoked with query: {query}")
        
        # Invoke the RAG chain
        result = rag_chain.invoke(query)
        
        return QueryOutput(
            answer=result.get("answer", ""),
            sources=result.get("sources", [])
        )
    
    def stream(self, input_data, config=None):
        """Stream the RAG chain with progressive token output"""
        global rag_chain
        
        if rag_chain is None:
            raise RuntimeError("RAG chain not initialized")
        
        # Handle both dict and QueryInput
        if isinstance(input_data, dict):
            query = input_data.get("query")
        else:
            query = input_data.query
        
        logger.info(f"RAG Chain streaming with query: {query}")
        
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


# Add LangServe routes
# The RAG chain is exposed at /chain with invoke and stream endpoints
add_routes(
    app,
    RAGChainRunnable(),
    path="/chain",
    enable_feedback_endpoint=False,  # Disable feedback for now
)

logger.info("LangServe routes added at /chain (invoke, stream)")


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


# Initialize vector store endpoint (for development)
@app.post("/api/init")
async def init_vector_store_endpoint():
    """
    Re-initialize vector store with fresh data (development only).
    This is useful for testing and development.
    """
    global rag_chain, vector_store
    
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(status_code=403, detail="Not allowed in production")
    
    try:
        logger.info("Re-initializing vector store...")
        
        from src.data_ingestion.pipeline import DataIngestionPipeline
        
        # Re-initialize pipeline
        pipeline = DataIngestionPipeline()
        pipeline.ingest_website("https://promtior.ai")
        chunked_docs = pipeline.chunk_all_documents()
        
        # Clear and re-populate vector store
        vector_store.clear()
        added = vector_store.add_documents(chunked_docs)
        # Vector store auto-persists with PersistentClient
        
        stats = vector_store.get_stats()
        logger.info(f"Vector store re-initialized: {added} documents added")
        
        return {
            "status": "success",
            "documents_added": added,
            "stats": stats,
        }
    
    except Exception as e:
        logger.error(f"Error re-initializing vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
    )
