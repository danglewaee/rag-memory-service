from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import settings
from app.dependencies import get_current_user
from app.schemas_memory import MemorySearchRequest, MemoryUpsertRequest
from app.services.auth import create_access_token, get_password_hash, verify_password
from app.services.memory_store import memory_store

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin_password_hash = get_password_hash(settings.admin_password)


@app.on_event("startup")
def startup() -> None:
    memory_store.ensure_indexes()


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    deps = memory_store.ping()
    return {
        "status": "ok" if all(deps.values()) else "degraded",
        "dependencies": deps,
        "stack": ["fastapi", "mongodb", "redis", "prometheus"],
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics_endpoint() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    if form_data.username != settings.admin_username:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form_data.password, admin_password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(subject=form_data.username, role="admin")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/memory/upsert")
def memory_upsert(payload: MemoryUpsertRequest, user: dict = Depends(get_current_user)) -> dict:
    if payload.user_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="user_id must match authenticated subject")
    record = memory_store.upsert_memory(payload)
    return {"status": "ok", "record": record.model_dump(mode="json")}


@app.post("/api/memory/search")
def memory_search(payload: MemorySearchRequest, user: dict = Depends(get_current_user)) -> dict:
    if payload.user_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="user_id must match authenticated subject")
    response = memory_store.search(payload)
    return response.model_dump(mode="json")


@app.delete("/api/memory/{memory_id}")
def memory_delete(memory_id: str, user: dict = Depends(get_current_user)) -> dict:
    deleted = memory_store.delete_memory(memory_id=memory_id, user_id=user.get("sub"))
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory record not found")
    return {"deleted": True, "memory_id": memory_id}


@app.get("/api/memory/stats")
def memory_stats(user: dict = Depends(get_current_user)) -> dict:
    stats = memory_store.stats()
    return {
        **stats,
        "cache_ttl_seconds": settings.memory_cache_ttl_seconds,
        "requested_by": user.get("sub"),
    }

