# Promtior RAG Chatbot

A modern Retrieval-Augmented Generation (RAG) chatbot built to answer questions about Promtior's services and company information. Built with LangChain, Ollama, ChromaDB, and deployed with React/Next.js frontend.

## Features

- 🤖 **RAG Pipeline**: Retrieves relevant information from Promtior's website and PDFs
- 💬 **Chat Interface**: Modern React/Next.js UI for conversational queries
- 🗄️ **Vector Database**: ChromaDB for efficient semantic search
- 🏠 **Local LLM**: Ollama + LLaMA2 (no API keys required, fully open-source)
- 🚀 **Production Ready**: Dockerized, deployable to Railway

## Quick Start (Local Development)

### Prerequisites

- Docker & Docker Compose
- Ollama (or will run in Docker)
- Python 3.10+
- Node.js 18+

### Setup

1. Clone and navigate to the project:
   ```bash
   git clone <your-repo-url>
   cd "Challenge Promtior"
   ```

2. Start all services with docker-compose:
   ```bash
   docker-compose up
   ```

3. Open browser to `http://localhost:3000` to access the chat UI

4. Backend API available at `http://localhost:8000`

## Project Structure

```
├── backend/              # Python FastAPI + LangChain RAG
│   ├── src/
│   │   ├── api/         # LangServe FastAPI app
│   │   ├── rag/         # RAG chain logic
│   │   ├── vector_store/ # ChromaDB setup
│   │   └── data_ingestion/ # Web scraping & data prep
│   ├── tests/           # Unit & integration tests
│   └── pyproject.toml   # Python dependencies
├── frontend/            # React/Next.js chat UI
│   ├── app/            # Page components
│   ├── components/     # Chat UI components
│   ├── lib/            # API integration
│   └── package.json
├── doc/                # Documentation & diagrams
├── Dockerfile          # Multi-stage Docker build
└── docker-compose.yml  # Local dev environment
```

## API Endpoints

- `POST /api/chat` - Submit a query and receive RAG response with sources
- `GET /api/health` - Health check for deployment

## Documentation

See `/doc` folder for:
- `README.md` - Implementation details and challenges
- `ARCHITECTURE.md` - Component diagram and system flow
- `DEPLOYMENT.md` - Railway deployment guide
- `SETUP.md` - Local development setup

## Tech Stack

**Backend**:
- Python 3.10+
- FastAPI + LangServe
- LangChain
- ChromaDB
- Ollama + LLaMA2
- BeautifulSoup4 (web scraping)

**Frontend**:
- React 18
- Next.js 14
- TypeScript
- Tailwind CSS

## Deployment

Deploy to Railway by connecting this GitHub repo. The Dockerfile will build both frontend and backend automatically.

## License

MIT
