"""
Configuração centralizada do backend
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


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
    JWT_EXPIRATION_HOURS: int = 24  # Access token lifetime
    JWT_REFRESH_EXPIRATION_DAYS: int = 30  # Refresh token lifetime

    # ===== LOGIN SECURITY (Item #12) =====
    LOGIN_DELAY_MAX_MINUTES: int = 15  # Teto do atraso progressivo (1-60)
    TRUSTED_DEVICE_DAYS: int = 30  # Duração do "trusted device" (0-90, 0=always MFA)
    LOGIN_ALERT_THRESHOLD: int = 5  # Falhas antes de enviar alerta por email
    COOKIE_SECURE: bool = True  # False só em dev local (http://localhost)
    FRONTEND_URL: str = "http://localhost:5173"  # Para CORS explícito

    # ===== EMAIL ALERTS (opcional — sem SMTP configurado, cai em log) =====
    ALERT_EMAIL_TO: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None

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

    # ===== VALIDATION (clamp to safe ranges — a bad env var never weakens security) =====

    @field_validator("LOGIN_DELAY_MAX_MINUTES")
    @classmethod
    def _clamp_login_delay(cls, v: int) -> int:
        clamped = max(1, min(v, 60))
        if clamped != v:
            logger.warning(f"LOGIN_DELAY_MAX_MINUTES={v} fora do intervalo [1,60], ajustado para {clamped}")
        return clamped

    @field_validator("TRUSTED_DEVICE_DAYS")
    @classmethod
    def _clamp_trusted_device_days(cls, v: int) -> int:
        clamped = max(0, min(v, 90))
        if clamped != v:
            logger.warning(f"TRUSTED_DEVICE_DAYS={v} fora do intervalo [0,90], ajustado para {clamped}")
        return clamped


# Instância global
settings = Settings()
