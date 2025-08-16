# config.py
import os
from dotenv import load_dotenv

load_dotenv()

def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

def _build_pg_url_from_env() -> str | None:
    host = os.getenv("PGHOST")
    db   = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    pwd  = os.getenv("PGPASSWORD")
    port = os.getenv("PGPORT", "5432")
    if all([host, db, user, pwd]):
        url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
        sslmode = os.getenv("DB_SSLMODE")
        if sslmode:  # e.g., "require" for hosted providers
            url += f"?sslmode={sslmode}"
        return url
    return None

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Priority: PG* env → DATABASE_URL → SQLite fallback
    _pg_env_url = _build_pg_url_from_env()
    _env_url = os.getenv("DATABASE_URL")
    _default_sqlite = "sqlite:///merstat.db"

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        _pg_env_url or (_env_url and _env_url.strip()) or _default_sqlite
    )

    # Optional pool & SSL tuning
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
        # For some providers, you may also pass CA cert paths via connect_args.
        "connect_args": {}  # using sslmode in URL when needed
    }

    # CORS & uploads
    FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000")
    RESUME_UPLOAD_DIR = os.getenv("RESUME_UPLOAD_DIR", "uploads/resumes")

class TestConfig(Config):
    TESTING = True
