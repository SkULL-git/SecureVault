import os
from dotenv import load_dotenv

load_dotenv()


def database_url():
    """Read the database URL from the environment and normalize common provider URLs."""
    url = os.getenv("DATABASE_URL", "sqlite:///securevault.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # Refuse to start with predictable secrets outside an explicitly marked development run.
    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY and JWT_SECRET_KEY must be configured."
        )
