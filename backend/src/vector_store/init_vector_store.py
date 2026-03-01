"""Vector store initialization script"""

import logging
import os
from pathlib import Path

from src.data_ingestion.pipeline import DataIngestionPipeline
from src.vector_store.store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_vector_store(
    urls: list[str] = None,
    pdf_dir: str = None,
    persist_dir: str = "./chroma_data",
):
    """
    Initialize and populate the vector store with data.
    
    Args:
        urls: List of URLs to scrape
        pdf_dir: Directory containing PDFs to ingest
        persist_dir: Directory to persist the vector store
    """
    if urls is None:
        urls = ["https://promtior.ai"]
    
    logger.info("Starting vector store initialization")
    
    # Initialize pipeline
    pipeline = DataIngestionPipeline(chunk_size=1000, chunk_overlap=200)
    
    # Ingest websites
    logger.info(f"Ingesting {len(urls)} website(s)")
    for url in urls:
        pipeline.ingest_website(url)
    
    # Ingest PDFs if directory provided
    if pdf_dir and Path(pdf_dir).exists():
        logger.info(f"Ingesting PDFs from {pdf_dir}")
        pipeline.ingest_pdf_directory(pdf_dir)
    
    # Chunk documents
    chunked_docs = pipeline.chunk_all_documents()
    
    if not chunked_docs:
        logger.warning("No documents to add to vector store")
        return
    
    # Initialize vector store
    vector_store = VectorStore(persist_dir=persist_dir)
    
    # Add documents
    added = vector_store.add_documents(chunked_docs)
    
    # Persist
    # Vector store auto-persists with PersistentClient
    
    # Print stats
    stats = vector_store.get_stats()
    logger.info(f"Vector store stats: {stats}")
    
    return vector_store


if __name__ == "__main__":
    init_vector_store()
