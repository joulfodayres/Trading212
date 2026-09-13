"""
Rotas para ISINs e sincronização com Trading 212
"""
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
import logging
from config.settings import settings
from api.trading212 import Trading212Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/isins", tags=["isins"])

# Cliente T212
t212_client = Trading212Client(
    api_key=settings.T212_API_KEY,
    api_secret=settings.T212_API_SECRET,
    base_url=settings.T212_BASE_URL
)


# ===== SCHEMAS =====

class ISINResponse(BaseModel):
    """Resposta com informações de ISIN"""
    id: str
    isin: str
    ticker: str
    name: str
    currency: str
    price: float
    automation_enabled: bool
    pnl: float
    pnl_percent: float


class SyncResponse(BaseModel):
    """Resposta da sincronização"""
    synced_count: int
    updated_count: int
    isins: list
    message: str


# ===== ENDPOINTS =====

@router.get("/sync-from-trading212", response_model=SyncResponse)
async def sync_from_trading212():
    """
    Sincronizar ISINs da carteira Trading 212
    Fetch positions via T212 API e guardar em BD
    """
    try:
        logger.info("🔄 Sincronizando ISINs da carteira T212...")

        # Fetch positions de T212
        positions_data = t212_client.get_positions()

        if not positions_data:
            logger.warning("⚠️ Nenhuma posição encontrada")
            return SyncResponse(
                synced_count=0,
                updated_count=0,
                isins=[],
                message="Nenhuma posição encontrada na carteira"
            )

        # TODO: Verificar se ISIN já existe em BD
        # TODO: Se não existe, criar novo registo com automation_enabled = FALSE
        # TODO: Se existe, atualizar price e quantity

        synced_count = len(positions_data)
        updated_count = 0

        # Formatar resposta
        isins_response = []
        for pos in positions_data:
            isins_response.append({
                "id": f"pos_{pos.get('ticker')}",  # TODO: Use real ID from DB
                "isin": pos.get("isin", ""),
                "ticker": pos.get("ticker", ""),
                "name": pos.get("name", pos.get("ticker", "")),
                "currency": pos.get("currency", "EUR"),
                "price": float(pos.get("current_price", 0)),
                "automation_enabled": False,  # Always OFF on first sync
                "pnl": float(pos.get("pnl", 0)),
                "pnl_percent": float(pos.get("pnl_percent", 0))
            })

        logger.info(f"✅ Sincronização completa: {synced_count} posições")

        return SyncResponse(
            synced_count=synced_count,
            updated_count=updated_count,
            isins=isins_response,
            message=f"Sincronização completa: {synced_count} posições"
        )

    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao sincronizar ISINs: {str(e)}"
        )


@router.get("", response_model=list[dict])
async def list_isins(limit: int = Query(20), offset: int = Query(0)):
    """
    Listar ISINs do utilizador autenticado
    TODO: Filtrar por user_id via JWT
    """
    try:
        # TODO: Buscar de BD (isins table)
        # Por enquanto, retornar vazio
        return []

    except Exception as e:
        logger.error(f"Erro ao listar ISINs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao listar ISINs"
        )


@router.get("/{isin_id}")
async def get_isin(isin_id: str):
    """
    Obter detalhes de um ISIN
    TODO: Buscar de BD
    """
    try:
        # TODO: Buscar de BD
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISIN não encontrado"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter ISIN"
        )


@router.put("/{isin_id}/automation/toggle")
async def toggle_automation(isin_id: str):
    """
    Ativar/desativar automação para um ISIN
    """
    try:
        # TODO: Buscar ISIN de BD
        # TODO: Inverter automation_enabled
        # TODO: Guardar em BD

        return {
            "id": isin_id,
            "automation_enabled": True,  # Novo estado
            "message": "Automação toggled com sucesso"
        }

    except Exception as e:
        logger.error(f"Erro ao toggle automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao toggle automation"
        )
