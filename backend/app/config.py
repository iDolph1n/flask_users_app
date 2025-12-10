import os
from pathlib import Path

# BASE_DIR указывает на корень проекта backend/
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Базовая конфигурация."""

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-2024")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'data' / 'users.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000",
    ).split(",")

    # Pagination
    USERS_PER_PAGE = int(os.getenv("USERS_PER_PAGE", 20))

    # JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Конфигурация разработки."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Конфигурация продакшена."""

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")


class TestingConfig(Config):
    """Конфигурация тестов (in-memory SQLite)."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
