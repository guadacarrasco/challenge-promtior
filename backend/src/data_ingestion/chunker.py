"""Text chunking and preprocessing module"""

import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.

    Args:
        documents: List of Document objects to chunk
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of chunked Document objects
    """
    if not documents:
        logger.warning("No documents provided for chunking")
        return []
    
    logger.info(f"Chunking {len(documents)} documents (size={chunk_size}, overlap={chunk_overlap})")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    
    chunked_docs = splitter.split_documents(documents)
    logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    
    return chunked_docs
