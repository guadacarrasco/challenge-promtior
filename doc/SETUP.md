# Setup & Deployment Guide

## Prerequisites

### For Local Development
- **Docker & Docker Compose** (latest versions)
- **Git**
- **8GB+ RAM** (for Ollama + services)
- **Disk Space**: 10GB+ (for models and data)

### For Production (Railway)
- **GitHub Account** connected to Railway
- **Railway Account** (free tier available)
- **Git repository** with code pushed to GitHub

## Local Development Setup

### Step 1: Clone the Repository

```bash
git clone <your-github-repo-url>
cd "Challenge Promtior"
```

### Step 2: Configure Environment

Copy the example environment file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` if needed:
```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
VECTOR_STORE_PATH=/app/chroma_data
DEBUG=True
LOG_LEVEL=INFO
```

### Step 3: Start Services with Docker Compose

```bash
docker-compose up --build
```

This will:
1. Start Ollama service (~60s startup time for first pull)
2. Pull and load LLaMA2 model (~3.5GB)
3. Start FastAPI backend (port 8000)
4. Start React frontend (port 3000)

**First Run Note**: The first time you run this, it will download the LLaMA2 model (~3.5GB). This may take 5-15 minutes depending on your internet speed.

### Step 4: Initialize Vector Store

Once services are running, populate the vector store:

```bash
# Option A: Using the API endpoint (for development)
curl -X POST http://localhost:8000/api/init

# Option B: Using Python directly (if not using Docker)
cd backend
python -m src.vector_store.init_vector_store
```

This will:
- Scrape https://promtior.ai
- Chunk the content
- Generate embeddings
- Store in ChromaDB

### Step 5: Access the Application

- **Frontend**: Open http://localhost:3000 in your browser
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Ollama**: http://localhost:11434

### Step 6: Test the Chatbot

In the web UI, try these questions:
- "What services does Promtior offer?"
- "When was Promtior founded?"
- "Tell me about Promtior's AI capabilities"

You should see responses with source citations.

## Testing

### Backend Tests

```bash
cd backend

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Promtior?"}'
```

### Frontend Testing

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check
```

## Troubleshooting

### Issue: "Failed to pull model"
**Cause**: Ollama service not running or network issue
**Solution**: 
```bash
# Check Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Wait 60+ seconds for it to fully start
```

### Issue: "Vector store is empty"
**Cause**: init_vector_store script not run
**Solution**:
```bash
# Via API
curl -X POST http://localhost:8000/api/init -H "Content-Type: application/json"

# Or manually
cd backend && python -m src.vector_store.init_vector_store
```

### Issue: "Cannot connect to backend" (frontend error)
**Cause**: Backend not running or CORS issue
**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Verify API is responding
curl http://localhost:8000/api/health

# Check NEXT_PUBLIC_API_URL in frontend
# Should be http://localhost:8000 for local dev
```

### Issue: "Frontend not loading"
**Cause**: Node dependencies not installed or build failed
**Solution**:
```bash
# Rebuild frontend
docker-compose down
docker-compose up --build frontend

# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

## Performance Tuning

### Faster LLM Responses
- Use smaller chat or quantized models
- Configure max_tokens in LangChain prompts
- Implement streaming responses
- Add response caching

### Faster Retrieval
- Use smaller embedding models
- Implement query expansion/decomposition
- Add BM25 hybrid search
- Use approximate nearest neighbor search (ANN)

### Reduced Memory Usage
- Use quantized models (already done with LLaMA2)
- Implement prompt caching
- Batch embeddings
- Use smaller chunk sizes

## Production Deployment on Railway

### Step 1: Push to GitHub

Ensure your code is on GitHub:

```bash
git add -A
git commit -m "Production ready"
git push origin main
```

### Step 2: Create Railway Project

1. Login to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub and select your repository

### Step 3: Configure Environment Variables

In Railway dashboard, add:

```env
OLLAMA_BASE_URL=http://ollama:11434  # Or separate Ollama service URL
OLLAMA_MODEL=llama2
VECTOR_STORE_PATH=/app/chroma_data
DEBUG=False
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### Step 4: Configure Port

Railway automatically detects the port from Dockerfile (8000).
Set custom domain in Railway settings if desired.

### Step 5: Deploy

Push a commit to trigger deployment:

```bash
git commit --allow-empty -m "Trigger Railway deployment"
git push origin main
```

Railway will:
1. Build the Docker image
2. Run health checks
3. Deploy to public URL
4. Auto-restart on errors

### Step 6: Database Persistence

For production, you'll want persistent storage:

1. Add PostgreSQL service in Railway
2. Update `vector_store/store.py` to use PostgreSQL backend
3. Mount persistent volumes for chroma_data

### Step 7: Monitoring

In Railway dashboard:
- Monitor logs
- Check deployment status
- View metrics (CPU, memory, network)
- Set up alerts

## Ollama Service Setup (Advanced)

### Running Ollama Separately

For production, run Ollama on a separate server:

```bash
# On Ollama server
ollama serve

# On application server, set:
OLLAMA_BASE_URL=http://ollama-server:11434
```

### Using Different Models

Update `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_MODEL=mistral  # or neural-chat, dolphin-mixtral, etc.
```

Then pull the model:
```bash
docker-compose exec ollama ollama pull mistral
```

## Backup & Recovery

### Backup Vector Store

```bash
# Copy chroma_data directory
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_data/

# Store in safe location
```

### Restore Vector Store

```bash
# Extract backup
tar -xzf chroma_backup_20240225.tar.gz

# Restart services
docker-compose down
docker-compose up
```

## Scaling Considerations

For production scale:

1. **Vector Database**: Migrate to pgvector or Weaviate
2. **LLM Service**: Use dedicated LLM inference server (vLLM, TGI)
3. **Caching**: Add Redis for query results
4. **API Scaling**: Use load balancer (nginx, Railway)
5. **Monitoring**: Add Prometheus/Grafana
6. **Logging**: Use ELK stack or similar

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS/TLS for all connections
- [ ] Implement authentication for API endpoints
- [ ] Validate and sanitize user inputs
- [ ] Rate limit API endpoints
- [ ] Keep dependencies updated
- [ ] Use secure environment variable management
- [ ] Monitor logs for suspicious activity
- [ ] Backup data regularly
- [ ] Test disaster recovery procedures

