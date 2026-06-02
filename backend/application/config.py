import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "dev-only-change-me-too")
    SECURITY_PASSWORD_HASH = os.getenv("SECURITY_PASSWORD_HASH", "argon2")
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_TOKEN_AUTHENTICATION_KEY = "auth_token"
    SECURITY_RETURN_GENERIC_RESPONSES = True
    SECURITY_CSRF_PROTECT_MECHANISMS = []
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "false").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'homeservices.sqlite3'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
        if origin.strip()
    ]
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


class LocalDevelopmentConfig(Config):
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECURITY_PASSWORD_HASH = "bcrypt"
    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "adminpassword"
