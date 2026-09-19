"""
FastAPI Backend - Trading 212 Bot MVP
Entry point da aplicação
Phase 4: Grid Trading Automation with APScheduler
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config.settings import settings
from routes.auth import router as auth_router
from routes.isins import router as isins_router
from routes.config import router as config_router
from routes.automation import router as automation_router
from db.supabase_client import SessionLocal
from services.scheduler import SchedulerService
from services.automation_engine import AutomationEngine
from services.t212_service import T212Service
from api.trading212 import Trading212Client

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances (singleton)
scheduler_service: SchedulerService = None
automation_engine: AutomationEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Manages startup and shutdown of the application.

    Startup: Initialize scheduler and automation engine
    Shutdown: Stop scheduler gracefully
    """
    global scheduler_service, automation_engine

    logger.info("=" * 60)
    logger.info("🚀 Iniciando Trading 212 Bot API (Phase 4)")
    logger.info("=" * 60)

    # ===== STARTUP =====
    try:
        # Create database session
        db_session = SessionLocal()
        logger.info("✅ Conexão com Supabase estabelecida")

        # Create T212 client
        t212_client = Trading212Client(
            api_key=settings.T212_API_KEY,
            api_secret=settings.T212_API_SECRET,
            environment=settings.T212_ENVIRONMENT
        )
        logger.info(f"✅ Cliente T212 inicializado ({settings.T212_ENVIRONMENT})")

        # Create T212 service
        t212_service = T212Service(t212_client)
        logger.info("✅ T212Service inicializado")

        # Create automation engine
        automation_engine = AutomationEngine(db_session, t212_service)
        logger.info("✅ AutomationEngine inicializado")

        # Create scheduler service
        scheduler_service = SchedulerService(db_session, automation_engine)
        logger.info("✅ SchedulerService criado")

        # Start scheduler (background thread)
        await scheduler_service.start()
        logger.info("✅ Scheduler iniciado com sucesso")

        logger.info("=" * 60)
        logger.info("✅ Aplicação pronta para aceitar requests")
        logger.info(f"   Ambiente: {settings.FASTAPI_ENV}")
        logger.info(f"   Debug: {settings.FASTAPI_DEBUG}")
        logger.info(f"   Startup time: {datetime.utcnow().isoformat()}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Erro fatal durante startup: {e}", exc_info=True)
        raise

    yield  # App está a correr aqui

    # ===== SHUTDOWN =====
    logger.info("=" * 60)
    logger.info("🛑 Parando Trading 212 Bot API")
    logger.info("=" * 60)

    try:
        if scheduler_service:
            scheduler_service.stop()
            logger.info("✅ Scheduler parado")

        if db_session:
            db_session.close()
            logger.info("✅ Conexão com BD fechada")

        logger.info("=" * 60)
        logger.info("✅ Aplicação parada com sucesso")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Erro durante shutdown: {e}", exc_info=True)


# Criar app FastAPI com lifespan
app = FastAPI(
    title="Trading 212 Bot API",
    description="API para automação de trading com Trading 212",
    version="0.4.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== ROOT ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Trading 212 Bot API",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.FASTAPI_ENV
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    scheduler_status = scheduler_service.get_status() if scheduler_service else {}
    return {
        "status": "healthy",
        "scheduler": scheduler_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# ===== ERROR HANDLERS =====

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler genérico de exceções"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


# ===== IMPORTAR ROUTERS =====
app.include_router(auth_router)
app.include_router(isins_router)
app.include_router(config_router)
app.include_router(automation_router)  # NEW: Automation routes
# from routes import positions, orders


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.FASTAPI_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
