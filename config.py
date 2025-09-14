import os
from pathlib import Path

from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")  # Take all environment variables.


def get_env(key, default=None, cast=str):
    """Get an environment variable and cast it to a specific type."""
    value = os.getenv(key, default)
    return cast(value) if value is not None else default


def to_bool(value):
    """Convert a string to a boolean."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


class Config:
    """Base configuration."""

    # Security
    SECRET_KEY = get_env("SECRET_KEY", "you-will-never-guess")

    # Database
    SQLALCHEMY_DATABASE_URI = (
        get_env("DATABASE_URL") or f"sqlite:///{(basedir / 'app.db').as_posix()}"
    )

    # Mail
    MAIL_SERVER = get_env("MAIL_SERVER")
    MAIL_PORT = get_env("MAIL_PORT", 25, int)
    MAIL_USE_TLS = get_env("MAIL_USE_TLS", False, to_bool)
    MAIL_USERNAME = get_env("MAIL_USERNAME")
    MAIL_PASSWORD = get_env("MAIL_PASSWORD")
    ADMINS = [
        admin.strip() for admin in os.getenv("ADMINS", "").splitlines() if admin.strip()
    ]

    # App
    POSTS_PER_PAGE = 20
    LANGUAGES = ["en", "es"]
    TRANSLATOR_KEY = get_env("TRANSLATOR_KEY")

    # Search
    ELASTICSEARCH_URL = get_env("ELASTICSEARCH_URL")
