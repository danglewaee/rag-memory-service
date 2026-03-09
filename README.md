# RAG Memory Service (MongoDB + Redis)

This branch adds a memory retrieval module on top of the existing FastAPI backend.

## Scope

Compared to branch `codex/vn-real-data-mvp`, only these files changed:

- `README.md`
- `backend/.env.example`
- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/services/metrics.py`
- `backend/requirements.txt`
- `docker-compose.yml`
- `backend/app/schemas_memory.py` (new)
- `backend/app/services/memory_store.py` (new)

Everything else is unchanged from the previous project baseline.

## What Was Added

- MongoDB-backed memory storage for chat/session context
- Redis caching for repeated memory search queries
- Ranking by keyword overlap + optional embedding cosine similarity + recency bonus
- New API endpoints:
  - `POST /api/memory/upsert`
  - `POST /api/memory/search`
  - `DELETE /api/memory/{memory_id}`
  - `GET /api/memory/stats`

## Tech

- API: FastAPI
- Memory Store: MongoDB
- Cache: Redis
- Existing stack retained: PostgreSQL, Celery, Kafka, Prometheus, Grafana

## Quick Start (Docker)

```powershell
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`

## Environment

Memory-specific variables in `backend/.env.example`:

- `MEMORY_CACHE_TTL_SECONDS=300`
- `MONGODB_URL=mongodb://mongo:27017`
- `MONGODB_DATABASE=anomalyguard`
- `MONGODB_MEMORY_COLLECTION=rag_memory`

## Authentication

Get token:

```powershell
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Use bearer token for memory endpoints.

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

Memory stats:

```powershell
curl -X GET "http://localhost:8000/api/memory/stats" \
  -H "Authorization: Bearer <TOKEN>"
```

## Metrics

Prometheus endpoint: `GET /metrics`

Memory metrics:

- `anomalyguard_memory_upsert_total`
- `anomalyguard_memory_delete_total`
- `anomalyguard_memory_search_total{cache="hit|miss"}`
- `anomalyguard_memory_search_duration_seconds`
