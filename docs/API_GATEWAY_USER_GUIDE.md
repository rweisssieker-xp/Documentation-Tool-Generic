# API-First Gateway - User Guide

**Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Target Audience:** Developers, DevOps Engineers, System Integrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [REST API Reference](#rest-api-reference)
4. [GraphQL API](#graphql-api)
5. [WebSocket Real-Time](#websocket-real-time)
6. [Authentication](#authentication)
7. [Rate Limiting](#rate-limiting)
8. [OpenAPI Specification](#openapi-specification)
9. [Integration Examples](#integration-examples)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is the API-First Gateway?

The API-First Gateway provides a complete REST/GraphQL API layer over all AHG features, enabling integration, automation, and headless operation. The API becomes the primary interface, with the GUI acting as a client.

### Key Benefits

- **CI/CD Integration**: Automate documentation generation in build pipelines
- **Headless Operation**: Run documentation generation on servers without GUI
- **Third-Party Integration**: Connect with Confluence, Notion, GitHub Actions, and more
- **Custom Dashboards**: Build custom dashboards using API data
- **Mobile Apps**: Access documentation features from native mobile applications

### Architecture Overview

The API Gateway is built on FastAPI and provides:

- **REST API**: Standard HTTP endpoints for all features
- **GraphQL API**: Flexible queries for complex data structures
- **WebSocket**: Real-time updates for collaboration features
- **Authentication**: JWT and OAuth2 support
- **Rate Limiting**: Protect against abuse
- **OpenAPI Spec**: Auto-generated API documentation

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- FastAPI and Uvicorn installed: `pip install fastapi uvicorn`
- AHG application configured

### Starting the API Server

#### Using CLI

```bash
python cli/innovation_cli.py api start --port 8000
```

#### Using Python

```python
from src.api import APIGateway

gateway = APIGateway()
gateway.run(host="0.0.0.0", port=8000)
```

#### Using GUI

1. Open AHG application
2. Navigate to: **🚀 Innovation** → **🔌 API Gateway...**
3. Configure port and settings
4. Click **Start Server**

### Verifying the Server

Once started, verify the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "3.0.0"
}
```

### Accessing API Documentation

- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

---

## REST API Reference

### Base URL

All REST endpoints are prefixed with `/api/v1/`

### Endpoints Overview

#### Sessions

- `GET /api/v1/sessions` - List all sessions
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session by ID
- `PUT /api/v1/sessions/{session_id}` - Update session
- `DELETE /api/v1/sessions/{session_id}` - Delete session

#### Documents

- `POST /api/v1/documents/generate` - Generate document from session
- `GET /api/v1/documents/{document_id}` - Get document by ID
- `GET /api/v1/documents/session/{session_id}` - List documents for session

#### Knowledge Base

- `POST /api/v1/knowledge/documents` - Add document to knowledge base
- `GET /api/v1/knowledge/documents` - List all documents
- `POST /api/v1/knowledge/search` - Search knowledge base
- `POST /api/v1/knowledge/rag/query` - Query RAG engine
- `GET /api/v1/knowledge/stats` - Get knowledge base statistics

#### Voice

- `POST /api/v1/voice/transcribe` - Transcribe audio file
- `POST /api/v1/voice/transcribe/upload` - Transcribe uploaded audio
- `POST /api/v1/voice/command` - Process voice command

#### Collaboration

- `GET /api/v1/collaboration/presence` - Get active users
- `POST /api/v1/collaboration/comments` - Create comment
- `GET /api/v1/collaboration/comments` - List all comments
- `GET /api/v1/collaboration/crdt/state` - Get CRDT state

#### Analytics

- `GET /api/v1/analytics/metrics` - Get metrics
- `GET /api/v1/analytics/roi` - Calculate ROI
- `GET /api/v1/analytics/predictions` - Get predictions
- `GET /api/v1/analytics/dashboard` - Get dashboard data

### Example Requests

#### Create Session

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Documentation Session",
    "app_name": "MyApp",
    "description": "Documenting login process"
  }'
```

Response:

```json
{
  "id": "session_20251201_120000",
  "name": "My Documentation Session",
  "app_name": "MyApp",
  "description": "Documenting login process",
  "status": "stopped",
  "created_at": "2025-12-01T12:00:00",
  "updated_at": "2025-12-01T12:00:00",
  "step_count": 0
}
```

#### Generate Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_20251201_120000",
    "format": "docx",
    "template": "default",
    "language": "en"
  }'
```

#### Search Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to create a user account?",
    "top_k": 5,
    "use_semantic": true
  }'
```

---

## GraphQL API

### Endpoint

`POST /graphql`

### Schema Overview

```graphql
type Query {
  sessions: [Session!]!
  session(sessionId: String!): Session
}

type Session {
  id: String!
  name: String!
  appName: String
  status: String!
  stepCount: Int!
  createdAt: String!
}
```

### Example Query

```graphql
query {
  sessions {
    id
    name
    status
    stepCount
  }
}
```

Request:

```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { sessions { id name status stepCount } }"
  }'
```

---

## WebSocket Real-Time

### Endpoint

`WS /ws`

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Subscribe to channel
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'sessions'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### Message Types

- `ping` - Keep-alive ping
- `subscribe` - Subscribe to channel
- `message` - Broadcast message
- `pong` - Ping response

---

## Authentication

### JWT Authentication

#### Get Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "password": "password"
  }'
```

#### Use Token

```bash
curl -X GET "http://localhost:8000/api/v1/sessions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### OAuth2

OAuth2 support is available for enterprise integrations. See OpenAPI spec for details.

---

## Rate Limiting

The API Gateway includes rate limiting middleware:

- **Default**: 60 requests per minute per IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- **Response**: 429 Too Many Requests when limit exceeded

---

## OpenAPI Specification

### Accessing the Spec

```bash
curl http://localhost:8000/openapi.json
```

### Using the Spec

The OpenAPI specification can be used with:

- **Swagger UI**: Interactive API documentation
- **Code Generation**: Generate client libraries
- **API Testing**: Import into Postman, Insomnia
- **Documentation**: Generate static documentation

---

## Integration Examples

### CI/CD Integration (GitHub Actions)

```yaml
name: Generate Documentation

on:
  release:
    types: [published]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate Documentation
        run: |
          curl -X POST "http://api-server:8000/api/v1/documents/generate" \
            -H "Content-Type: application/json" \
            -d '{
              "session_id": "${{ secrets.SESSION_ID }}",
              "format": "markdown"
            }'
```

### Python Client Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Create session
response = requests.post(
    f"{API_BASE}/sessions",
    json={
        "name": "API Test Session",
        "app_name": "TestApp"
    }
)
session = response.json()

# Generate document
response = requests.post(
    f"{API_BASE}/documents/generate",
    json={
        "session_id": session["id"],
        "format": "docx"
    }
)
document = response.json()
print(f"Document generated: {document['path']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000/api/v1';

async function generateDocument(sessionId) {
  const response = await axios.post(
    `${API_BASE}/documents/generate`,
    {
      session_id: sessionId,
      format: 'html'
    }
  );
  return response.data;
}
```

---

## Troubleshooting

### Common Issues

#### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install dependencies:
```bash
pip install fastapi uvicorn
```

#### Port Already in Use

**Problem**: `Address already in use`

**Solution**: Use a different port:
```bash
python cli/innovation_cli.py api start --port 8001
```

#### CORS Errors

**Problem**: CORS errors when accessing from browser

**Solution**: Enable CORS in gateway configuration (enabled by default)

#### Authentication Errors

**Problem**: 401 Unauthorized

**Solution**: Ensure JWT token is valid and included in Authorization header

---

## Best Practices

1. **Use HTTPS in Production**: Always use HTTPS for production deployments
2. **Implement Retry Logic**: Handle transient failures with exponential backoff
3. **Cache Responses**: Cache static data to reduce API calls
4. **Monitor Rate Limits**: Check rate limit headers to avoid throttling
5. **Error Handling**: Implement comprehensive error handling for all API calls
6. **Versioning**: Use API versioning for breaking changes

---

## Additional Resources

- [OpenAPI Specification](http://localhost:8000/openapi.json)
- [Interactive API Docs](http://localhost:8000/docs)
- [GraphQL Playground](http://localhost:8000/graphql)
- [Developer Manual](./DEVELOPER_MANUAL.md)

---

**Document Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Maintained By:** Technical Writing Team




