import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import chromadb
except ImportError:
    raise ImportError("Please install chromadb: pip install chromadb")

from langchain_core.documents import Document
from .embedder import EmbeddingModel

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "promtior_docs"


class VectorStore:
    
    def __init__(
        self,
        persist_dir: str = "./chroma_data",
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedding_model = EmbeddingModel(embedding_model_name)
        
        # Create persist directory if it doesn't exist
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        
        # Initialize ChromaDB client with persistence (new API)
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        
        logger.info(f"Vector store initialized with collection: {collection_name}")
    
    def add_documents(self, documents: List[Document]) -> int:
        
        if not documents:
            logger.warning("No documents to add")
            return 0
        
        
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Embed all texts
        embeddings = self.embedding_model.embed(texts)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        

        return len(documents)
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        
        
        # Embed the query
        query_embedding = self.embedding_model.embed_single(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
        
        # Format results
        documents = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                })
        
        logger.info(f"Found {len(documents)} relevant documents")
        return documents
    
    def clear(self):
        
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    
    def get_stats(self) -> Dict[str, Any]:
      
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'document_count': count,
            'embedding_dimension': self.embedding_model.get_dimension(),
        }
