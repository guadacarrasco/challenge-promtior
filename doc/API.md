# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://your-railway-url.com
```

## Authentication

Currently no authentication required. For production, implement:
- API Key authentication
- OAuth 2.0
- JWT tokens

## Endpoints

### 1. Health Check

**Check if the API and vector store are ready.**

```http
GET /api/health
```

**Response (200 OK)**:
```json
{
  "status": "ok",
  "vector_store": {
    "collection_name": "promtior_docs",
    "document_count": 127,
    "embedding_dimension": 384
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "detail": "Service not ready - Vector store not initialized"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/health
```

---

### 2. Chat Endpoint

**Submit a query and receive a RAG-generated response with sources.**

```http
POST /api/chat
```

**Request Body**:
```json
{
  "message": "What services does Promtior offer?"
}
```

**Response (200 OK)**:
```json
{
  "response": "Promtior offers comprehensive enterprise AI solutions including custom machine learning models, natural language processing capabilities, and computer vision systems. These services are designed to help businesses automate processes and gain insights from their data.",
  "sources": [
    {
      "content": "Promtior specializes in enterprise AI solutions and services including machine learning, NLP, and computer vision. We help businesses transform with AI.",
      "metadata": {
        "source": "https://promtior.ai/",
        "type": "website"
      }
    },
    {
      "content": "Our services include: Custom ML Models, NLP Solutions, Computer Vision, Data Analysis, and AI Consulting",
      "metadata": {
        "source": "https://promtior.ai/services",
        "type": "website"
      }
    },
    {
      "content": "Founded in 2020, Promtior has been at the forefront of enterprise AI innovation.",
      "metadata": {
        "source": "https://promtior.ai/about",
        "type": "website"
      }
    }
  ]
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "Message cannot be empty"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "detail": "RAG chain not initialized"
}
```

**Response (500 Internal Server Error)**:
```json
{
  "detail": "Error: [error details]"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services does Promtior offer?"}'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "When was Promtior founded?"}
)

data = response.json()
print(f"Answer: {data['response']}")
print(f"Sources: {len(data['sources'])} document(s)")
```

**JavaScript/TypeScript Example**:
```typescript
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Tell me about Promtior' })
});

const data = await response.json();
console.log(data.response);
console.log(data.sources);
```

**Response Time**: 3-15 seconds (depends on LLM speed and system resources)

---

### 3. Initialize Vector Store (Development Only)

**Re-initialize the vector store with fresh data from Promtior.ai.**

This endpoint is only available when `DEBUG=True` in environment variables.

```http
POST /api/init
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "documents_added": 127,
  "stats": {
    "collection_name": "promtior_docs",
    "document_count": 127,
    "embedding_dimension": 384
  }
}
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Not allowed in production"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/init
```

---

## Response Models

### ChatResponse

```typescript
interface ChatResponse {
  response: string;           // Generated answer from LLM
  sources: SourceInfo[];      // List of retrieved source documents
}
```

### SourceInfo

```typescript
interface SourceInfo {
  content: string;            // Relevant excerpt from source (≤200 chars)
  metadata: {
    source?: string;          // URL or filename
    type?: string;            // "website" or "pdf"
    page?: number;            // For PDFs, the page number
    chunk_id?: number;        // Document chunk identifier
  }
}
```

### HealthResponse

```typescript
interface HealthResponse {
  status: string;             // "ok" or error detail
  vector_store: {
    collection_name: string;
    document_count: number;
    embedding_dimension: number;
  }
}
```

---

## Error Handling

### Standard HTTP Status Codes

| Code | Meaning | Response |
|------|---------|----------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid message (empty, null) |
| 404 | Not Found | Endpoint does not exist |
| 500 | Internal Server Error | Server error (see detail) |
| 503 | Service Unavailable | Vector store or RAG chain not initialized |

### Error Response Format

```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting

Currently no rate limiting. For production, implement:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
@app.post("/api/chat")
async def chat(request: ChatRequest):
    ...
```

---

## Query Examples

### Fact-Based Questions

```json
{
  "message": "When was Promtior founded?"
}
```

Expected: Direct answer with founding year

### Service Questions

```json
{
  "message": "What does Promtior offer for machine learning?"
}
```

Expected: Detailed description with service examples

### Comparison Questions

```json
{
  "message": "How does Promtior's AI differ from competitors?"
}
```

Expected: Comparison based on available information

### Complex Questions

```json
{
  "message": "Can I use Promtior's services for real-time data analysis?"
}
```

Expected: Contextual answer based on service descriptions

---

## Performance Considerations

### Typical Latency

- Health check: ~10ms
- Chat (end-to-end): 3-15 seconds
  - Retrieval: ~100ms
  - LLM generation: 2-10s (depends on hardware)
  - Response formatting: ~50ms

### Request Limits

- Maximum message length: No strict limit (recommend <1000 chars)
- Timeout: 30 seconds default in client

### Optimization Tips

1. **Batch requests**: Don't send multiple simultaneous requests
2. **Cache results**: Store frequently asked questions locally
3. **Streaming**: Implement streaming responses for real-time feedback
4. **Query optimization**: Keep queries focused and specific

---

## Versioning

Current API Version: **v1** (implicit, no prefix)

Future versions may be at:
- `/api/v2/chat`
- `/api/v2/health`

Migration path will be provided with advance notice.

---

## CORS Policy

**Development**: All origins allowed (`*`)
**Production**: Restrict to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Webhook/Callbacks (Future)

Planned for future versions:
- Asynchronous chat responses via webhooks
- Streaming responses
- Real-time updates

---

## Support & Feedback

For API issues or feedback:
1. Check error message detail
2. Review logs: `docker-compose logs backend`
3. Verify vector store is initialized: `GET /api/health`
4. Test with simple queries first

