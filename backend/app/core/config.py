"""
Central application configuration.

All values are loaded from environment variables / a .env file.
Every other module in the RAG pipeline imports `settings` from here
instead of reading os.environ directly, so there is exactly one
source of truth for configuration.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- PostgreSQL ---
    # Individual fields for local dev (docker run with separate
    # user/password/host/port). Render (and most managed Postgres hosts)
    # instead give you ONE connection string — set DATABASE_URL_OVERRIDE
    # and it takes priority over the individual fields below.
    POSTGRES_USER: str = "researchmind"
    POSTGRES_PASSWORD: str = "researchmind"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "researchmind"
    DATABASE_URL_OVERRIDE: str = ""
    # Set to true for managed Postgres hosts requiring SSL (Neon,
    # Supabase, Render Postgres, etc). Left false for local Docker
    # Postgres, which has no SSL configured. See app/db/database.py for
    # why this is a separate setting rather than relying on a
    # "?sslmode=require" query string, which asyncpg doesn't parse the
    # way psycopg/libpq does.
    DB_SSL_REQUIRED: bool = False

    # --- CORS ---
    # Comma-separated list of allowed frontend origins, e.g.
    # "https://your-app.vercel.app,http://localhost:3000"
    # Defaults to "*" (dev-permissive) if unset.
    ALLOWED_ORIGINS: str = "*"

    # --- Embeddings ---
    EMBEDDING_MODEL: str = "text-embedding-001"
    VECTOR_DIM: int = 768

    # --- Reranker ---
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # --- Chunking ---
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # --- Retrieval ---
    VECTOR_TOP_K: int = 20
    BM25_TOP_K: int = 20
    HYBRID_TOP_K: int = 15
    RERANK_TOP_K: int = 5
    RRF_K: int = 60  # Reciprocal Rank Fusion constant

    # --- Device ---
    DEVICE: str = "cpu"

    # --- Gemini (generation) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # --- Auth: JWT (issued by OUR backend, used for both manual and
    # Google-login sessions once either login flow succeeds) ---
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-string-before-deploying"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # --- Auth: Firebase (used only to verify Google Sign-In ID tokens
    # coming from the frontend) ---
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    @property
    def DATABASE_URL(self) -> str:
        """Async SQLAlchemy connection string (asyncpg driver).

        If DATABASE_URL_OVERRIDE is set (e.g. Neon's or Render's provided
        Postgres URL), use it -- converting to the asyncpg driver scheme
        SQLAlchemy needs, and stripping any query string (e.g.
        "?sslmode=require") since asyncpg doesn't understand that
        convention -- SSL is instead controlled explicitly via
        DB_SSL_REQUIRED + connect_args in app/db/database.py. Otherwise,
        build the URL from individual fields (local Docker dev).
        """
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE.split("?")[0]  # drop query string
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Sync connection string, used only by scripts/alembic if needed."""
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parsed, whitespace-trimmed list from ALLOWED_ORIGINS."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — import this everywhere."""
    return Settings()


settings = get_settings()
