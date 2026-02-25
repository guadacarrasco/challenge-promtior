# Development Scripts

This directory contains helpful shell scripts for developing and managing the Promtior RAG Chatbot.

## Quick Start

```bash
./scripts/quickstart.sh
```

This script will:
1. Verify Docker and Docker Compose are installed
2. Check available disk space
3. Start all services (Ollama, Backend, Frontend)
4. Wait for services to be ready
5. Initialize the vector store
6. Display access URLs and helpful commands

**First run**: Expect 2-5 minutes (downloading LLaMA2 model)

## Development Helper

```bash
./scripts/dev.sh
```

Interactive menu for common development tasks:

- **1**: Start services (`docker-compose up`)
- **2**: Stop services (`docker-compose down`)
- **3**: View logs (all services)
- **4**: View logs (backend only)
- **5**: Restart backend service
- **6**: Re-initialize vector store
- **7**: Run backend tests
- **8**: Check API health
- **9**: Clean Docker resources
- **10**: Enter backend container shell
- **0**: Exit

Or run individual commands:

```bash
./scripts/dev.sh start              # Start services
./scripts/dev.sh stop               # Stop services
./scripts/dev.sh logs               # Follow logs
./scripts/dev.sh logs-backend       # Backend logs only
./scripts/dev.sh restart-backend    # Restart backend
./scripts/dev.sh init-vector-store  # Reset vector store
./scripts/dev.sh test               # Run tests
./scripts/dev.sh health             # Check health
./scripts/dev.sh clean              # Clean Docker
./scripts/dev.sh shell              # Backend shell
```

## Testing

```bash
./scripts/test.sh
```

Runs comprehensive system tests:

1. ✅ Verifies Docker installation
2. ✅ Checks all services running
3. ✅ Tests Ollama connectivity
4. ✅ Tests API health endpoint
5. ✅ Tests chat endpoint with sample query
6. ✅ Runs backend unit tests (if pytest installed)

## Typical Workflow

### First Time Setup

```bash
# Clone repository
git clone <your-repo>
cd "Challenge Promtior"

# Quick start (builds everything)
./scripts/quickstart.sh

# Open browser
open http://localhost:3000
```

### Daily Development

```bash
# Start services
./scripts/dev.sh start

# Check status
./scripts/dev.sh health

# View logs while developing
./scripts/dev.sh logs-backend

# Test your changes
./scripts/dev.sh test

# When done
./scripts/dev.sh stop
```

### Troubleshooting

```bash
# Check what's running
docker-compose ps

# View specific service logs
./scripts/dev.sh logs-backend

# Restart problematic service
./scripts/dev.sh restart-backend

# Complete reset
./scripts/dev.sh clean
./scripts/quickstart.sh
```

## Manual Commands

If you prefer not to use scripts:

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Re-initialize vector store
curl -X POST http://localhost:8000/api/init

# Test API
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Promtior?"}'
```

## Environment

Scripts use default environment from `docker-compose.yml`:
- API port: 8000
- Frontend port: 3000
- Ollama port: 11434
- Vector store path: `./chroma_data`

To customize, edit `docker-compose.yml` before running scripts.

## Requirements

- Docker & Docker Compose
- 8GB+ RAM
- 10GB+ free disk space
- Bash shell

## Notes

- All scripts are relative path based (run from anywhere in repo)
- Scripts exit on first error to prevent cascading failures
- Use `docker-compose` directly for advanced operations
- Check logs (`./scripts/dev.sh logs-backend`) for debugging

## Support

If scripts fail:

1. Check Docker is running: `docker ps`
2. View error logs: `docker-compose logs`
3. Check requirements: 8GB RAM, 10GB disk space
4. Try clean reset: `./scripts/dev.sh clean && ./scripts/quickstart.sh`

