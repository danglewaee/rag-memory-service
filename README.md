# RAG Memory Service

Standalone FastAPI service for long-term memory storage and retrieval in RAG systems.

## Features

- Memory upsert/search/delete APIs
- MongoDB persistence for memory documents
- Redis query caching for repeated retrievals
- JWT auth with protected APIs
- Prometheus metrics for cache hit/miss and latency

## Project Layout

- `backend/app/main.py`: API routes and auth flow
- `backend/app/services/memory_store.py`: MongoDB + Redis memory engine
- `backend/app/services/metrics.py`: Prometheus metrics
- `backend/app/schemas_memory.py`: request/response schemas
- `docker-compose.yml`: local stack (`backend`, `mongo`, `redis`)

## Run With Docker

```powershell
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`

## Local Backend Run

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Auth

Get token:

```powershell
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Use the token as bearer auth for `/api/memory/*` endpoints.

## API Examples

Upsert memory:

```powershell
curl -X POST "http://localhost:8000/api/memory/upsert" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "session_id": "session-1",
    "text": "User prefers anomaly alerts every morning",
    "tags": ["preference", "alerts"],
    "metadata": {"source": "chat"}
  }'
```

Search memory:

```powershell
curl -X POST "http://localhost:8000/api/memory/search" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "session_id": "session-1",
    "query": "alert schedule preference",
    "top_k": 5
  }'
```

Stats:

```powershell
curl -X GET "http://localhost:8000/api/memory/stats" \
  -H "Authorization: Bearer <TOKEN>"
```

## Metrics

`GET /metrics` exports:

- `rag_memory_upsert_total`
- `rag_memory_delete_total`
- `rag_memory_search_total{cache="hit|miss"}`
- `rag_memory_search_duration_seconds`
