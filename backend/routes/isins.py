"""
Rotas para ISINs e sincronização com Trading 212
Implementa CRUD completo com integração Supabase e T212 API
"""
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any, List
from config.settings import settings
from api.trading212 import Trading212Client
from db.supabase_client import get_db
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/isins", tags=["isins"])

# Cliente T212 (lazy initialization)
_t212_client = None

def get_t212_client():
    """Obter cliente T212 (lazy initialization)"""
    global _t212_client
    if _t212_client is None:
        try:
            _t212_client = Trading212Client(
                api_key=settings.T212_API_KEY,
                api_secret=settings.T212_API_SECRET,
                environment=settings.T212_ENVIRONMENT
            )
            logger.info("T212 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize T212 client: {e}")
            raise
    return _t212_client

# Cliente BD
db = get_db()

# Teste user_id (created in Supabase - teste@trading212.com)
TEST_USER_ID = "17780beb-e61f-4604-ba5a-b6329312ac90"


# ===== SCHEMAS =====

class ISINResponse(BaseModel):
    """Resposta com informações de ISIN"""
    id: str
    isin: str
    ticker: Optional[str] = None
    name: Optional[str] = None
    currency: str
    price: Optional[float] = None
    automation_enabled: bool
    pnl: float = 0.0
    pnl_percent: float = 0.0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ISINCreate(BaseModel):
    """Criar novo ISIN"""
    isin: str


class ISINUpdate(BaseModel):
    """Atualizar ISIN"""
    name: Optional[str] = None
    ticker: Optional[str] = None
    automation_enabled: Optional[bool] = None


class ISINDeleteResponse(BaseModel):
    """Resposta de deleção"""
    id: str
    message: str


class ISINToggleResponse(BaseModel):
    """Resposta de toggle automation"""
    id: str
    automation_enabled: bool
    message: str


class SyncResponse(BaseModel):
    """Resposta da sincronização"""
    synced_count: int
    updated_count: int
    isins: List[Dict[str, Any]]
    message: str


# ===== ENDPOINTS =====

@router.post("", response_model=ISINResponse)
async def create_isin(data: ISINCreate):
    """
    POST /api/isins - Criar novo ISIN

    Input: { isin: "IE00BK5BQT80" }

    Valida ISIN, fetch dados de T212 API, guarda em Supabase
    com automation_enabled = false por padrão
    """
    try:
        # Validar ISIN
        if not data.isin or len(data.isin.strip()) < 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISIN inválido (mínimo 12 caracteres)"
            )

        isin_code = data.isin.upper().strip()

        # Verificar se ISIN já existe para este user
        existing = db.get_isin_by_isin_code(isin_code, TEST_USER_ID)
        if existing:
            logger.warning(f" ISIN já existe: {isin_code}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ISIN já existe para este utilizador"
            )

        # Fetch dados do instrumento via T212 API
        logger.info(f"📡 Buscando dados de T212 API para: {isin_code}")

        # Para este MVP, usar dados mock da T212 API
        # Em produção, seria: t212_client.search_instrument(isin_code)
        t212_data = {
            "ticker": "VWRX",  # Mock - substituir com dados reais
            "name": "Vanguard FTSE All-World",  # Mock
            "currency": "EUR"
        }

        # Guardar em BD
        isin_record = db.create_isin(
            user_id=TEST_USER_ID,
            isin=isin_code,
            ticker=t212_data.get("ticker", ""),
            name=t212_data.get("name", ""),
            currency=t212_data.get("currency", "EUR"),
            fields_json=t212_data
        )

        logger.info(f" ISIN criado com sucesso: {isin_code}")

        return ISINResponse(
            id=isin_record["id"],
            isin=isin_record["isin"],
            ticker=isin_record.get("ticker"),
            name=isin_record.get("name"),
            currency=isin_record.get("currency", "EUR"),
            automation_enabled=isin_record.get("automation_enabled", False),
            pnl=0.0,
            pnl_percent=0.0,
            created_at=str(isin_record.get("created_at")),
            updated_at=str(isin_record.get("updated_at"))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao criar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao adicionar ISIN: {str(e)}"
        )


@router.get("", response_model=List[ISINResponse])
async def list_isins(limit: int = Query(20), offset: int = Query(0)):
    """
    GET /api/isins - Listar todos os ISINs do utilizador

    Query params:
    - limit: Número máximo de resultados (default 20)
    - offset: Offset para paginação (default 0)

    Retorna lista de ISINs com P&L calculado
    """
    try:
        # Buscar ISINs da BD
        isins = db.list_isins(TEST_USER_ID, limit=limit, offset=offset)

        result = []
        for isin in isins:
            # Calcular P&L para cada ISIN
            pnl_data = db.get_isin_pnl(isin["id"], TEST_USER_ID)

            result.append(ISINResponse(
                id=isin["id"],
                isin=isin["isin"],
                ticker=isin.get("ticker"),
                name=isin.get("name"),
                currency=isin.get("currency", "EUR"),
                automation_enabled=isin.get("automation_enabled", False),
                pnl=pnl_data["pnl"],
                pnl_percent=pnl_data["pnl_percent"],
                created_at=str(isin.get("created_at")),
                updated_at=str(isin.get("updated_at"))
            ))

        logger.info(f" Listados {len(result)} ISINs")
        return result

    except Exception as e:
        logger.error(f" Erro ao listar ISINs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar ISINs: {str(e)}"
        )


@router.get("/{isin_id}", response_model=ISINResponse)
async def get_isin(isin_id: str):
    """
    GET /api/isins/{isin_id} - Obter detalhes de um ISIN

    Retorna informações completas do ISIN com P&L calculado
    """
    try:
        # Buscar ISIN de BD
        isin = db.get_isin(isin_id, TEST_USER_ID)

        if not isin:
            logger.warning(f" ISIN não encontrado: {isin_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN não encontrado"
            )

        # Calcular P&L
        pnl_data = db.get_isin_pnl(isin_id, TEST_USER_ID)

        logger.info(f"📖 ISIN obtido: {isin['isin']}")

        return ISINResponse(
            id=isin["id"],
            isin=isin["isin"],
            ticker=isin.get("ticker"),
            name=isin.get("name"),
            currency=isin.get("currency", "EUR"),
            automation_enabled=isin.get("automation_enabled", False),
            pnl=pnl_data["pnl"],
            pnl_percent=pnl_data["pnl_percent"],
            created_at=str(isin.get("created_at")),
            updated_at=str(isin.get("updated_at"))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao obter ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter ISIN: {str(e)}"
        )


@router.put("/{isin_id}", response_model=ISINResponse)
async def update_isin(isin_id: str, data: ISINUpdate):
    """
    PUT /api/isins/{isin_id} - Atualizar ISIN

    Permite editar: name, ticker, automation_enabled
    """
    try:
        # Verificar se ISIN existe
        isin = db.get_isin(isin_id, TEST_USER_ID)
        if not isin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN não encontrado"
            )

        # Preparar updates (apenas campos fornecidos)
        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.ticker is not None:
            updates["ticker"] = data.ticker
        if data.automation_enabled is not None:
            updates["automation_enabled"] = data.automation_enabled

        if not updates:
            # Se nenhum campo foi fornecido, retornar o ISIN sem mudanças
            logger.info(f"ℹ️ Nenhum campo para atualizar em ISIN: {isin_id}")
            pnl_data = db.get_isin_pnl(isin_id, TEST_USER_ID)
            return ISINResponse(
                id=isin["id"],
                isin=isin["isin"],
                ticker=isin.get("ticker"),
                name=isin.get("name"),
                currency=isin.get("currency", "EUR"),
                automation_enabled=isin.get("automation_enabled", False),
                pnl=pnl_data["pnl"],
                pnl_percent=pnl_data["pnl_percent"],
                created_at=str(isin.get("created_at")),
                updated_at=str(isin.get("updated_at"))
            )

        # Atualizar em BD
        updated_isin = db.update_isin(isin_id, TEST_USER_ID, updates)

        logger.info(f" ISIN atualizado: {isin_id}")

        # Calcular P&L
        pnl_data = db.get_isin_pnl(isin_id, TEST_USER_ID)

        return ISINResponse(
            id=updated_isin["id"],
            isin=updated_isin["isin"],
            ticker=updated_isin.get("ticker"),
            name=updated_isin.get("name"),
            currency=updated_isin.get("currency", "EUR"),
            automation_enabled=updated_isin.get("automation_enabled", False),
            pnl=pnl_data["pnl"],
            pnl_percent=pnl_data["pnl_percent"],
            created_at=str(updated_isin.get("created_at")),
            updated_at=str(updated_isin.get("updated_at"))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao atualizar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar ISIN: {str(e)}"
        )


@router.delete("/{isin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_isin(isin_id: str):
    """
    DELETE /api/isins/{isin_id} - Deletar um ISIN

    Cascade delete: Remove ISIN e todos os trades associados
    Retorna 204 No Content
    """
    try:
        # Verificar se ISIN existe
        isin = db.get_isin(isin_id, TEST_USER_ID)
        if not isin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN não encontrado"
            )

        # Deletar ISIN (cascade delete de trades é automático em BD)
        db.delete_isin(isin_id, TEST_USER_ID)

        logger.info(f" ISIN deletado: {isin_id}")
        # Retorna 204 No Content (sem body)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao deletar ISIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar ISIN: {str(e)}"
        )


@router.put("/{isin_id}/automation/toggle", response_model=ISINToggleResponse)
async def toggle_automation(isin_id: str):
    """
    PUT /api/isins/{isin_id}/automation/toggle - Toggle automação

    Inverte o estado de automation_enabled para um ISIN
    """
    try:
        # Verificar se ISIN existe
        isin = db.get_isin(isin_id, TEST_USER_ID)
        if not isin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN não encontrado"
            )

        # Toggle automation
        updated_isin = db.toggle_automation(isin_id, TEST_USER_ID)

        logger.info(f" Automação toggled: {isin_id} = {updated_isin['automation_enabled']}")

        return ISINToggleResponse(
            id=updated_isin["id"],
            automation_enabled=updated_isin.get("automation_enabled", False),
            message=f"Automação {'ativada' if updated_isin.get('automation_enabled') else 'desativada'}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao toggle automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao toggle automation: {str(e)}"
        )


@router.get("/{isin_id}/trades", response_model=List[Dict])
async def get_isin_trades(isin_id: str, limit: int = Query(50)):
    """
    GET /api/isins/{isin_id}/trades - Obter histórico de trades

    Query params:
    - limit: Número máximo de trades (default 50)

    Retorna lista de trades para um ISIN específico
    """
    try:
        # Verificar se ISIN existe
        isin = db.get_isin(isin_id, TEST_USER_ID)
        if not isin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN não encontrado"
            )

        # Buscar trades
        trades = db.list_isin_trades(isin_id, TEST_USER_ID, limit=limit)

        logger.info(f" Listados {len(trades)} trades para ISIN: {isin_id}")

        return trades

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro ao obter trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter trades: {str(e)}"
        )


@router.get("/sync-from-trading212", response_model=SyncResponse)
async def sync_from_trading212():
    """
    GET /api/isins/sync-from-trading212 - Sincronizar ISINs da carteira T212

    Fetch positions via T212 API e guardar em Supabase
    Cria novos registos se não existem, atualiza se existem
    """
    try:
        logger.info(" Sincronizando ISINs da carteira T212...")

        # Fetch positions de T212
        t212_client = get_t212_client()
        positions_data = t212_client.get_positions()

        if not positions_data:
            logger.warning(" Nenhuma posição encontrada")
            return SyncResponse(
                synced_count=0,
                updated_count=0,
                isins=[],
                message="Nenhuma posição encontrada na carteira"
            )

        synced_count = 0
        updated_count = 0
        isins_response = []

        # Processar cada posição
        for pos in positions_data:
            try:
                isin_code = pos.get("isin", "").upper()
                ticker = pos.get("ticker", "")
                name = pos.get("name", ticker)
                currency = pos.get("currency", "EUR")

                if not isin_code:
                    logger.warning(f" Posição sem ISIN: {ticker}")
                    continue

                # Verificar se ISIN já existe
                existing = db.get_isin_by_isin_code(isin_code, TEST_USER_ID)

                if existing:
                    # Atualizar
                    updates = {
                        "ticker": ticker,
                        "name": name,
                        "currency": currency,
                        "fields_json": pos
                    }
                    updated = db.update_isin(existing["id"], TEST_USER_ID, updates)
                    updated_count += 1
                    isin_record = updated
                    logger.info(f" ISIN atualizado: {isin_code}")
                else:
                    # Criar novo
                    isin_record = db.create_isin(
                        user_id=TEST_USER_ID,
                        isin=isin_code,
                        ticker=ticker,
                        name=name,
                        currency=currency,
                        fields_json=pos
                    )
                    synced_count += 1
                    logger.info(f"✨ ISIN criado: {isin_code}")

                # Adicionar à resposta
                pnl_data = db.get_isin_pnl(isin_record["id"], TEST_USER_ID)
                isins_response.append({
                    "id": isin_record["id"],
                    "isin": isin_record["isin"],
                    "ticker": ticker,
                    "name": name,
                    "currency": currency,
                    "automation_enabled": isin_record.get("automation_enabled", False),
                    "pnl": pnl_data["pnl"],
                    "pnl_percent": pnl_data["pnl_percent"]
                })

                # Rate limit
                time.sleep(0.5)

            except Exception as e:
                logger.error(f" Erro ao processar posição {pos.get('ticker')}: {str(e)}")
                continue

        logger.info(f" Sincronização completa: {synced_count} criados, {updated_count} atualizados")

        return SyncResponse(
            synced_count=synced_count,
            updated_count=updated_count,
            isins=isins_response,
            message=f"Sincronização completa: {synced_count} criados, {updated_count} atualizados"
        )

    except Exception as e:
        logger.error(f" Erro ao sincronizar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao sincronizar ISINs: {str(e)}"
        )
