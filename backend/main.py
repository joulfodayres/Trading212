"""
FastAPI Backend - Trading 212 Bot MVP
Entry point da aplicação
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from config.settings import settings
from routes.auth import router as auth_router
from routes.isins import router as isins_router
from routes.config import router as config_router

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title="Trading 212 Bot API",
    description="API para automação de trading com Trading 212",
    version="0.1.0"
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
    return {"status": "healthy"}


# ===== ERROR HANDLERS =====

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler genérico de exceções"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


# ===== STARTUP & SHUTDOWN =====

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    logger.info("Iniciando Trading 212 Bot API")
    logger.info(f"Ambiente: {settings.FASTAPI_ENV}")
    logger.info(f"Debug: {settings.FASTAPI_DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação"""
    logger.info("Encerrando Trading 212 Bot API")


# ===== IMPORTAR ROUTERS =====
app.include_router(auth_router)
app.include_router(isins_router)
app.include_router(config_router)
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
