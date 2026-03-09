from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG Memory Service"
    app_version: str = "1.0.0"

    jwt_secret_key: str = "replace-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    admin_username: str = "admin"
    admin_password: str = "admin123"

    redis_url: str = "redis://redis:6379/0"
    memory_cache_ttl_seconds: int = 300

    mongodb_url: str = "mongodb://mongo:27017"
    mongodb_database: str = "rag_memory_service"
    mongodb_memory_collection: str = "memories"


settings = Settings()
