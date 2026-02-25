#!/bin/bash
# Test script - runs various tests and verifications

set -e

echo "🧪 Testing Promtior RAG System"
echo "=============================="
echo ""

cd "$(dirname "$0")/.."

# Test 1: Check Docker
echo "Test 1: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi
echo "✅ Docker available"

# Test 2: Check services running
echo ""
echo "Test 2: Checking running services..."
RUNNING=$(docker-compose ps -q | wc -l)
if [ "$RUNNING" -lt 3 ]; then
    echo "⚠️  Not all services running. Starting..."
    docker-compose up -d
fi
echo "✅ Services running"

# Test 3: Check Ollama
echo ""
echo "Test 3: Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama responding"
else
    echo "❌ Ollama not responding"
fi

# Test 4: Check API health
echo ""
echo "Test 4: Checking API health..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | jq . > /dev/null 2>&1; then
    DOCS=$(echo "$HEALTH" | jq '.vector_store.document_count')
    echo "✅ API responding (Documents in store: $DOCS)"
else
    echo "❌ API not responding"
fi

# Test 5: Test chat endpoint
echo ""
echo "Test 5: Testing chat endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What is Promtior?"}')

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    LENGTH=$(echo "$RESPONSE" | jq '.response' | wc -c)
    echo "✅ Chat endpoint working (Response length: $LENGTH)"
else
    echo "❌ Chat endpoint failed"
fi

# Test 6: Run unit tests
echo ""
echo "Test 6: Running backend unit tests..."
if command -v pytest &> /dev/null; then
    cd backend
    pytest tests/ -q --tb=short
    echo "✅ Unit tests passed"
    cd ..
else
    echo "⚠️  pytest not installed (install with: pip install pytest)"
fi

echo ""
echo "🎉 All tests completed!"
