"""PDF loading module for document ingestion"""

import logging
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
    """
    Load a PDF file using LangChain's PyPDFLoader.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of Document objects from the PDF
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"PDF file not found: {file_path}")
            return []
        
        logger.info(f"Loading PDF from {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        logger.info(f"Successfully loaded {len(docs)} pages from {file_path}")
        for i, doc in enumerate(docs):
            doc.metadata['source'] = str(path.name)
            doc.metadata['type'] = 'pdf'
            doc.metadata['page'] = i + 1
        
        return docs
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        return []


def load_pdfs_from_directory(directory: str) -> List[Document]:
    """Load all PDF files from a directory"""
    all_docs = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.warning(f"Directory not found: {directory}")
        return all_docs
    
    for pdf_file in dir_path.glob("*.pdf"):
        docs = load_pdf(str(pdf_file))
        all_docs.extend(docs)
    
    return all_docs
