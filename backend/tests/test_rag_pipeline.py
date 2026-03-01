"""Integration tests for RAG pipeline"""

import tempfile
import shutil
from langchain_core.documents import Document

from src.vector_store.store import VectorStore
from src.rag.retriever import Retriever


class TestRetriever:
    """Test retriever functionality"""
    
    def test_retrieve_documents(self):
        """Test document retrieval"""
        # Create temp store
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_dir=temp_dir)
            
            # Add test documents
            docs = [
                Document(
                    page_content="Promtior provides enterprise AI solutions for businesses",
                    metadata={"source": "homepage"}
                ),
                Document(
                    page_content="Promtior was founded in 2020 by technology leaders",
                    metadata={"source": "about"}
                ),
                Document(
                    page_content="Services include machine learning, NLP, and computer vision",
                    metadata={"source": "services"}
                ),
            ]
            
            store.add_documents(docs)
            
            # Test retriever
            retriever = Retriever(store, top_k=2)
            results = retriever.retrieve("What services does Promtior offer?")
            
            assert len(results) > 0
            assert any("services" in result['content'].lower() for result in results)
        
        finally:
            shutil.rmtree(temp_dir)
