"""FastAPI application with LangServe endpoints"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.runnables import Runnable, RunnablePassthrough
from langserve import add_routes
import json
import asyncio
import time

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
        
        # Setup LangServe routes
        setup_langserve_routes()
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # Vector store auto-persists with PersistentClient
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Promtior RAG Chatbot API",
    description="RAG API for asking questions about Promtior (LangServe)",
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


# Streaming chat endpoint with SSE
@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    Stream chat responses using Server-Sent Events.
    Returns chunks of the answer as they are generated.
    """
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not ready")
    
    async def generate():
        """Async generator for streaming responses with proper flushing"""
        try:
            logger.info(f"Starting streaming response for query: {request.message}")
            start_time = time.time()
            chunk_count = 0
            
            # Run the blocking generator in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            generator = rag_chain.stream(request.message)
            
            for item in generator:
                chunk_count += 1
                # Log for debugging
                if chunk_count == 1:
                    logger.info(f"First chunk received after {time.time() - start_time:.2f}s")
                
                # Convert to JSON and send as SSE format with explicit newlines
                sse_data = f"data: {json.dumps(item)}\n\n"
                logger.debug(f"Sending SSE chunk {chunk_count}: {item.get('type', 'unknown')}")
                yield sse_data
                
                # Allow other tasks to run
                await asyncio.sleep(0)
            
            elapsed = time.time() - start_time
            logger.info(f"Streaming complete: {chunk_count} chunks sent in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Error during streaming: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# Fallback non-streaming endpoint (for backward compatibility)
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint (fallback if streaming has issues).
    Returns the complete answer at once.
    """
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not ready")
    
    try:
        logger.info(f"Chat invoked with query: {request.message}")
        result = rag_chain.invoke(request.message)
        
        return {
            "response": result.get('answer', ''),
            "sources": result.get('sources', [])
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Add LangServe routes for RAG chain
def setup_langserve_routes():
    """Setup LangServe routes after app is created"""
    global rag_chain
    
    if rag_chain is None:
        logger.warning("RAG chain not initialized, LangServe routes not added")
        return
    
    from langchain_core.runnables import Runnable
    from pydantic import BaseModel

    class ChatInput(BaseModel):
        query: str

    class ChatOutput(BaseModel):
        answer: str
        sources: list = []

    class RAGRunnable(Runnable):
        def invoke(self, input: ChatInput, config=None):
            # Handle both ChatInput object and dict
            if isinstance(input, dict):
                query = input.get('query')
            else:
                query = input.query
            
            result = rag_chain.invoke(query)
            answer = result.get('answer') if isinstance(result, dict) else str(result)
            sources = result.get('sources', []) if isinstance(result, dict) else []
            return ChatOutput(answer=answer, sources=sources)

    add_routes(app, RAGRunnable(), path="/chain")
    logger.info("LangServe routes added at /chain")


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
