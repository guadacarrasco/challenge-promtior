"""FastAPI application with LangServe endpoints"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        logger.info(f"Initializing Ollama LLM: {ollama_model} at {ollama_base_url}")
        
        llm = OllamaLLM(
            base_url=ollama_base_url,
            model=ollama_model,
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
    if vector_store:
        vector_store.persist()
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
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str


class SourceInfo(BaseModel):
    content: str
    metadata: dict = {}


class ChatResponse(BaseModel):
    response: str
    sources: list[SourceInfo] = []


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


# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for asking questions about Promtior.
    
    Args:
        request: ChatRequest with user message
        
    Returns:
        ChatResponse with answer and sources
    """
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not initialized")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        logger.info(f"Processing chat message: {request.message[:100]}")
        
        # Invoke RAG chain
        result = rag_chain.invoke(request.message)
        
        # Format response
        sources = [
            SourceInfo(content=src['content'], metadata=src['metadata'])
            for src in result['sources']
        ]
        
        response = ChatResponse(
            response=result['answer'],
            sources=sources,
        )
        
        logger.info(f"Chat response generated (length: {len(result['answer'])})")
        return response
    
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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
        vector_store.persist()
        
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
