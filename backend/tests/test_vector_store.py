"""Tests for vector store"""

import pytest
import tempfile
import shutil
from pathlib import Path
from langchain.schema import Document

from src.vector_store.store import VectorStore


class TestVectorStore:
    """Test VectorStore functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_init(self, temp_dir):
        """Test vector store initialization"""
        store = VectorStore(persist_dir=temp_dir)
        assert store is not None
        assert store.collection is not None
    
    def test_add_documents(self, temp_dir):
        """Test adding documents"""
        store = VectorStore(persist_dir=temp_dir)
        
        docs = [
            Document(
                page_content="Promtior offers AI solutions",
                metadata={"source": "website"}
            ),
            Document(
                page_content="Promtior was founded in 2020",
                metadata={"source": "website"}
            ),
        ]
        
        added = store.add_documents(docs)
        assert added == 2
    
    def test_search(self, temp_dir):
        """Test searching documents"""
        store = VectorStore(persist_dir=temp_dir)
        
        # Add documents
        docs = [
            Document(
                page_content="Promtior specializes in enterprise AI",
                metadata={"source": "website"}
            ),
            Document(
                page_content="Founded in 2020, Promtior has grown rapidly",
                metadata={"source": "website"}
            ),
        ]
        store.add_documents(docs)
        
        # Search
        results = store.search("When was Promtior founded?", k=1)
        assert len(results) > 0
        assert "2020" in results[0]['content'] or "founded" in results[0]['content'].lower()
