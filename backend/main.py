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
from routes.strategies import router as strategies_router
from routes.reports import router as reports_router
from db.supabase_client import get_db
from services.scheduler import SchedulerService
from services.automation_engine import AutomationEngine
from services.t212_service import T212Service
from services.alert_service import send_alert_if_enabled
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
        # Get Supabase DB instance
        db = get_db()
        logger.info("✅ Conexão com Supabase estabelecida")

        # Item #15: se o código mudou desde o último arranque (novo deploy),
        # desliga a automação por segurança — nunca arranca "sozinha" depois
        # de uma alteração de código. Só corre se RENDER_GIT_COMMIT existir
        # (Render define-a automaticamente; em dev local não existe, e sem
        # um sinal fiável de versão não mexemos no estado da automação).
        if settings.RENDER_GIT_COMMIT:
            try:
                result = db.client.table("app_parameters").select(
                    "id, last_deployed_commit, grid_trading_enabled"
                ).execute()
                if result.data:
                    row = result.data[0]
                    stored_commit = row.get("last_deployed_commit")
                    current_commit = settings.RENDER_GIT_COMMIT
                    if stored_commit != current_commit:
                        logger.warning(
                            f"🚀 Novo deploy detetado ({stored_commit} → {current_commit}) "
                            f"— desativando automação por segurança"
                        )
                        db.client.table("app_parameters").update({
                            "grid_trading_enabled": False,
                            "automation_disabled_reason": f"Novo deploy detetado (commit {current_commit[:8]})",
                            "last_deployed_commit": current_commit,
                            "updated_at": "now()",
                        }).eq("id", row["id"]).execute()
                        send_alert_if_enabled(
                            "deploy_disabled",
                            subject="🚀 Trading 212 Bot — Automação desligada após deploy",
                            body=(
                                f"Foi detetado um novo deploy (commit {current_commit}).\n\n"
                                f"A automação foi desligada automaticamente por segurança. "
                                f"Reativa manualmente quando quiseres."
                            ),
                        )
                    else:
                        logger.info(f"✅ Mesmo commit do arranque anterior ({current_commit[:8]}) — estado da automação mantido")
            except Exception as e:
                logger.error(f"⚠️ Erro ao verificar deploy novo: {e}", exc_info=True)

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
        automation_engine = AutomationEngine(db, t212_service)
        logger.info("✅ AutomationEngine inicializado")

        # Create scheduler service
        scheduler_service = SchedulerService(db, automation_engine)
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
# allow_credentials=True exige origins explícitos (o browser rejeita "*" + credentials)
# — necessário para o cookie httpOnly do login (Item #12) funcionar entre frontend/backend
_cors_origins = [settings.FRONTEND_URL, "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(_cors_origins)),
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
    logger.error(f"Erro não tratado em {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


# ===== IMPORTAR ROUTERS =====
app.include_router(auth_router)
app.include_router(isins_router)
app.include_router(config_router)
app.include_router(automation_router)  # NEW: Automation routes
app.include_router(strategies_router)  # NEW: Strategies routes
app.include_router(reports_router)     # NEW: Reports (PDF import) routes
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
