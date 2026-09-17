"""
Configuração centralizada do backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # ===== SUPABASE =====
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # ===== TRADING 212 =====
    T212_API_KEY: str
    T212_API_SECRET: str
    T212_ENVIRONMENT: str = "demo"  # 'demo' ou 'live'
    T212_BASE_URL: str

    # ===== FASTAPI =====
    FASTAPI_ENV: str = "development"
    FASTAPI_DEBUG: bool = True
    FASTAPI_PORT: int = 8000
    FASTAPI_HOST: str = "0.0.0.0"

    # ===== JWT =====
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # ===== DATABASE =====
    DATABASE_URL: Optional[str] = None

    # ===== ENCRYPTION =====
    ENCRYPTION_KEY: str

    # ===== LOGGING =====
    LOG_LEVEL: str = "INFO"

    # ===== SCHEDULER =====
    SCHEDULER_CHECK_INTERVAL: int = 300  # 5 minutos

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global
settings = Settings()
