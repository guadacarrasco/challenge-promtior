"""Tests for data ingestion"""

from src.data_ingestion.chunker import chunk_documents
from langchain_core.documents import Document


class TestChunker:
    """Test text chunking"""
    
    def test_chunk_documents(self):
        """Test document chunking"""
        docs = [
            Document(
                page_content="This is a long document. " * 100,
                metadata={"source": "test"}
            )
        ]
        
        chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
        assert len(chunks) > 1
    
    def test_chunk_empty_list(self):
        """Test chunking empty list"""
        chunks = chunk_documents([])
        assert len(chunks) == 0
