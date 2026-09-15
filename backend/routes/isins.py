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
    environment=settings.T212_ENVIRONMENT
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


class ISINCreate(BaseModel):
    """Criar novo ISIN"""
    isin: str


class ISINUpdate(BaseModel):
    """Atualizar ISIN"""
    name: str | None = None
    notes: str | None = None


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

        # TODO: Verificar se ISIN já existe em BD (user_id + isin)
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


@router.post("", response_model=dict)
async def create_isin(data: ISINCreate):
    """
    Criar novo ISIN
    Valida ISIN, fetch dados T212, guarda em BD
    """
    try:
        if not data.isin or len(data.isin) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISIN inválido"
            )

        # TODO: Verificar se ISIN já existe para este user
        # TODO: Fetch dados do instrumento via T212 API
        # TODO: Guardar em BD com automation_enabled = FALSE

        logger.info(f"✅ ISIN criado: {data.isin}")

        return {
            "id": "new-id",
            "isin": data.isin,
            "ticker": "",
            "name": "",
            "automation_enabled": False,
            "message": "ISIN adicionado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao adicionar ISIN"
        )


@router.get("/{isin_id}")
async def get_isin(isin_id: str):
    """
    Obter detalhes de um ISIN
    TODO: Buscar de BD
    """
    try:
        # TODO: Buscar de BD
        # TODO: Fetch preço atual de T212 API
        # TODO: Calcular P&L

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


@router.get("/{isin_id}/trades")
async def get_isin_trades(isin_id: str, limit: int = Query(50)):
    """
    Obter histórico de trades para um ISIN
    """
    try:
        # TODO: Buscar trades de BD (trades table)
        # Filtrar por isin_id

        return []

    except Exception as e:
        logger.error(f"Erro ao obter trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter trades"
        )


@router.put("/{isin_id}")
async def update_isin(isin_id: str, data: ISINUpdate):
    """
    Atualizar ISIN (nome custom, notas, etc)
    """
    try:
        # TODO: Buscar ISIN de BD
        # TODO: Atualizar apenas os campos fornecidos
        # TODO: Guardar em BD

        logger.info(f"✅ ISIN atualizado: {isin_id}")

        return {
            "id": isin_id,
            "message": "ISIN atualizado com sucesso"
        }

    except Exception as e:
        logger.error(f"Erro ao atualizar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar ISIN"
        )


@router.delete("/{isin_id}")
async def delete_isin(isin_id: str):
    """
    Deletar um ISIN
    Cascade delete trades associated
    """
    try:
        # TODO: Buscar ISIN de BD
        # TODO: Deletar trades associados (cascade)
        # TODO: Deletar ISIN

        logger.info(f"✅ ISIN deletado: {isin_id}")

        return {
            "id": isin_id,
            "message": "ISIN deletado com sucesso"
        }

    except Exception as e:
        logger.error(f"Erro ao deletar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao deletar ISIN"
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

        logger.info(f"✅ Automação toggled: {isin_id}")

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
