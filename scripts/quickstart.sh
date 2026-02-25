#!/bin/bash
# Quick start script for Promtior RAG Chatbot

set -e

echo "🚀 Promtior RAG Chatbot - Quick Start"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found. Checking for 'docker compose'..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    alias docker-compose="docker compose"
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Check available disk space
AVAILABLE_SPACE=$(df /Users/guadalupe.carrascoibm.com | tail -1 | awk '{print $4}')
REQUIRED_SPACE=$((10 * 1024 * 1024))  # 10GB in KB

if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    echo "⚠️  Warning: Less than 10GB available disk space"
    echo "   Ollama model (~3.5GB) and vector store (~1GB) will be downloaded"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop existing containers if running
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "🛑 Stopping existing containers..."
    docker-compose down
fi

# Start services
echo ""
echo "🐳 Starting Docker services..."
echo "   - Ollama (LLaMA2 model)"
echo "   - FastAPI Backend"
echo "   - React Frontend"
echo ""

docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
echo "   This will take 1-2 minutes on first run (downloading LLaMA2 model)..."

# Wait for Ollama to be ready
max_attempts=120
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "   ⏳ Still waiting... ($attempt/$max_attempts)"
    fi
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama did not start in time"
    docker-compose logs ollama | tail -20
    exit 1
fi

# Wait for API to be ready
echo "⏳ Waiting for FastAPI backend..."
attempt=0
while [ $attempt -lt 30 ]; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ FastAPI backend is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

# Initialize vector store
echo ""
echo "📚 Initializing vector store..."
echo "   Scraping https://promtior.ai..."
echo "   This will take 1-3 minutes..."

curl -s -X POST http://localhost:8000/api/init > /dev/null 2>&1

echo "✅ Vector store initialized"

# Final status
echo ""
echo "🎉 All systems ready!"
echo ""
echo "📍 Access the application:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔌 API: http://localhost:8000"
echo "   📊 API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Try these questions:"
echo "   • What services does Promtior offer?"
echo "   • When was Promtior founded?"
echo "   • Tell me about Promtior's AI capabilities?"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f           # Follow logs"
echo "   docker-compose down              # Stop services"
echo "   docker-compose restart backend   # Restart backend"
echo ""
echo "📖 Documentation:"
echo "   doc/README.md          - Project overview"
echo "   doc/ARCHITECTURE.md    - System architecture"
echo "   doc/SETUP.md           - Setup guide"
echo "   doc/API.md             - API documentation"
echo ""
