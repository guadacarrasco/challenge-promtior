# Project Overview: Promtior RAG Chatbot

## Executive Summary

This project implements a complete Retrieval-Augmented Generation (RAG) pipeline that enables users to ask questions about Promtior's services and company information through an intuitive chat interface. The system combines modern NLP technologies with a modern web UI to deliver accurate, source-backed responses.

## Architecture

The system consists of three main layers:

### 1. **Data Ingestion & Processing** (`backend/src/data_ingestion/`)
- **Web Scraper**: Extracts content from Promtior.ai website using LangChain's WebBaseLoader
- **PDF Loader**: Optionally ingests PDF presentations containing company information
- **Text Chunker**: Splits documents into optimal chunks (1000 chars with 200-char overlap) for retrieval
- **Pipeline Orchestrator**: Coordinates the entire ingestion workflow

### 2. **Vector Storage & Embeddings** (`backend/src/vector_store/`)
- **EmbeddingModel**: Uses sentence-transformers (`all-MiniLM-L6-v2`) to generate semantic embeddings
- **ChromaDB Store**: Persists embeddings and documents with cosine similarity search
- **Initialization**: One-time script to populate the vector database with ingested data

### 3. **RAG Chain** (`backend/src/rag/`)
- **LLM Integration**: Ollama + LLaMA2 for local, cost-free LLM inference
- **Retriever**: Fetches relevant documents (top-3) based on query similarity
- **Chain**: Combines retrieved context with user query to generate answers

### 4. **API Layer** (`backend/src/api/`)
- **FastAPI + LangServe**: Exposes REST endpoints for chat and health checks
- **CORS Enabled**: Allows requests from frontend
- **Development Endpoints**: Vector store initialization endpoint for testing

### 5. **Frontend** (`frontend/`)
- **React/Next.js**: Modern, performant UI with TypeScript
- **Chat Components**: Reusable components for message display, input, and header
- **Axios Client**: Communicates with backend API
- **Tailwind CSS**: Professional styling

## Key Design Decisions

### 1. **LLM Choice: Ollama + LLaMA2 (Open Source)**
- **Pros**: No API costs, local execution, privacy, can run offline
- **Cons**: Slower inference than GPT-4, requires system resources
- **Decision Rationale**: Aligns with challenge requirements for open-source approach; eliminates API costs for extended development

### 2. **Vector Database: ChromaDB**
- **Pros**: Persistent storage, embeddable, metadata support, lightweight
- **Cons**: Less scalable than enterprise solutions
- **Decision Rationale**: Perfect for MVP; easy to migrate to production solutions later

### 3. **Frontend: React/Next.js**
- **Pros**: Modern, SSR, TypeScript support, excellent ecosystem
- **Decision Rationale**: Provides professional UX; Next.js simplifies deployment

### 4. **Embedding Model: sentence-transformers (all-MiniLM-L6-v2)**
- **Pros**: Fast, small (~33MB), excellent for semantic search
- **Decision Rationale**: Lightweight model suitable for development; can upgrade to larger models in production

## Challenges & Solutions

### Challenge 1: LLaMA2 Inference Speed
**Issue**: LLaMA2 is slower than GPT-4, causing delays in response generation.
**Solution**: Implemented query preprocessing and implemented retrieval caching where possible. Add streaming responses in future versions.

### Challenge 2: Vector Store Initialization
**Issue**: Web scraping may fail or capture limited data initially.
**Solution**: Created comprehensive error handling; graceful fallbacks; support for supplementary PDF ingestion.

### Challenge 3: CORS Between Frontend and Backend
**Issue**: Frontend and backend on different ports during development.
**Solution**: Enabled CORS in FastAPI with `allow_origins=["*"]` for development; production setup uses reverse proxy.

### Challenge 4: Docker Compose Orchestration
**Issue**: Ollama requires time to start; dependencies between services.
**Solution**: Implemented health checks and wait logic in docker-compose; Ollama container depends on network availability.

## Data Flow

```
User Query
    ↓
[Frontend React UI]
    ↓ (Axios POST /api/chat)
[FastAPI Backend]
    ↓
[RAG Chain]
    ├→ [Retriever] → [ChromaDB Embeddings] → Top-3 Similar Documents
    ├→ [Context Formatting]
    └→ [Ollama LLM] → Generate Answer
    ↓
[Response + Sources]
    ↓ (JSON response)
[Frontend Display]
    ↓
User sees answer with citations
```

## Tested Capabilities

✅ Website scraping from Promtior.ai
✅ Text chunking and preprocessing
✅ Embedding generation using sentence-transformers
✅ Vector store creation and persistence
✅ Document retrieval based on semantic similarity
✅ LLM integration with Ollama
✅ FastAPI endpoint serving
✅ React frontend chat UI
✅ Error handling and graceful degradation
✅ Docker containerization

## Known Limitations & Future Improvements

1. **LLM Performance**: LLaMA2 is slower; consider deploying dedicated LLM service for production
2. **Vector Store Scaling**: ChromaDB suitable for MVP; migrate to pgvector/Weaviate for production
3. **Caching**: No query result caching; add Redis for repeated queries
4. **User Feedback**: No user feedback mechanism; add thumbs up/down for model improvement
5. **Multi-Language**: Currently English only; add translation layer for internationalization
6. **Advanced RAG**: No reranking; add cross-encoder reranking for better context selection

## Deployment

- **Local Development**: `docker-compose up`
- **Production**: Docker push to Railway; automatic deployment via GitHub integration
- **Environment Variables**: See `.env.example`; configure Ollama URL, models, storage paths

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Manual API testing
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services does Promtior offer?"}'
```

## File Structure

```
.
├── backend/
│   ├── src/
│   │   ├── api/             # FastAPI application
│   │   ├── data_ingestion/  # Web scraping and PDF loading
│   │   ├── rag/             # RAG chain, LLM, retriever
│   │   └── vector_store/    # ChromaDB embeddings and storage
│   ├── tests/               # Unit and integration tests
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── lib/                 # API client
│   ├── styles/              # Tailwind CSS
│   └── package.json
├── doc/                     # Documentation and diagrams
├── Dockerfile               # Multi-stage Docker build
└── docker-compose.yml       # Local development setup
```

## Conclusion

This RAG pipeline demonstrates a complete, production-ready architecture for building AI-powered information retrieval systems. The modular design allows easy updates to individual components (embedder, LLM, vector store) without affecting the overall system.
