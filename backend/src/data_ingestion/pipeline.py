"""Data ingestion pipeline orchestration"""

import logging
from typing import List
from langchain_core.documents import Document

from .web_scraper import scrape_website
from .pdf_loader import load_pdf, load_pdfs_from_directory
from .chunker import chunk_documents

logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """Orchestrate data ingestion from multiple sources"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: List[Document] = []
    
    def ingest_website(self, url: str) -> int:
        """Ingest content from a website"""
        logger.info(f"Ingesting website: {url}")
        docs = scrape_website(url)
        self.documents.extend(docs)
        logger.info(f"Added {len(docs)} documents from website")
        return len(docs)
    
    def ingest_pdf(self, file_path: str) -> int:
        """Ingest content from a single PDF"""
        logger.info(f"Ingesting PDF: {file_path}")
        docs = load_pdf(file_path)
        self.documents.extend(docs)
        logger.info(f"Added {len(docs)} pages from PDF")
        return len(docs)
    
    def ingest_pdf_directory(self, directory: str) -> int:
        """Ingest all PDFs from a directory"""
        logger.info(f"Ingesting PDFs from directory: {directory}")
        docs = load_pdfs_from_directory(directory)
        self.documents.extend(docs)
        logger.info(f"Added {len(docs)} pages from PDFs")
        return len(docs)
    
    def chunk_all_documents(self) -> List[Document]:
        """Chunk all ingested documents"""
        logger.info(f"Chunking {len(self.documents)} documents")
        chunked = chunk_documents(
            self.documents,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        logger.info(f"Created {len(chunked)} chunks")
        return chunked
    
