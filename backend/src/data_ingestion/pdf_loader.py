import logging
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"PDF file not found: {file_path}")
            return []
        
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        

        for i, doc in enumerate(docs):
            doc.metadata['source'] = str(path.name)
            doc.metadata['type'] = 'pdf'
            doc.metadata['page'] = i + 1
        
        return docs
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        return []


def load_pdfs_from_directory(directory: str) -> List[Document]:
    
    all_docs = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.warning(f"Directory not found: {directory}")
        return all_docs
    
    for pdf_file in dir_path.glob("*.pdf"):
        docs = load_pdf(str(pdf_file))
        all_docs.extend(docs)
    
    return all_docs
