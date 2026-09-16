"""
Rotas para ISINs (Simplified - Opção 1)
Dados vêm sempre da T212 API (source of truth)
BD guarda apenas configurações (automation_enabled, strategy_params)
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any, List
from config.settings import settings
from api.trading212 import Trading212Client
from db.supabase_client import get_db

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


# ===== SCHEMAS =====

class ISINResponse(BaseModel):
    """Resposta com informações de ISIN (dados frescos da T212)"""
    isin: str
    ticker: str
    name: str
    currency: str
    quantity: float
    currentPrice: float
    averagePricePaid: float
    automation_enabled: bool
    pnl: float = 0.0
    pnl_percent: float = 0.0


class ISINConfigUpdate(BaseModel):
    """Atualizar configurações de ISIN"""
    automation_enabled: Optional[bool] = None
    strategy_params: Optional[Dict[str, Any]] = None


class ISINConfigResponse(BaseModel):
    """Configuração de ISIN"""
    isin: str
    automation_enabled: bool
    strategy_params: Dict[str, Any]


# ===== HELPERS =====

def _format_t212_position(position: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Formata posição da T212 API para ISINResponse
    Enriquece com configuração local (automation_enabled, strategy_params)
    """
    instrument = position.get("instrument", {})
    isin = instrument.get("isin", "")

    # Calcular P&L
    quantity = position.get("quantity", 0)
    current_price = position.get("currentPrice", 0)
    avg_paid = position.get("averagePricePaid", 0)

    pnl = (current_price - avg_paid) * quantity if avg_paid > 0 else 0
    pnl_percent = ((current_price - avg_paid) / avg_paid * 100) if avg_paid > 0 else 0

    return {
        "isin": isin,
        "ticker": instrument.get("ticker", ""),
        "name": instrument.get("name", ""),
        "currency": instrument.get("currency", "EUR"),
        "quantity": quantity,
        "currentPrice": current_price,
        "averagePricePaid": avg_paid,
        "automation_enabled": config.get("automation_enabled", False) if config else False,
        "pnl": pnl,
        "pnl_percent": pnl_percent
    }


async def _get_isin_configs() -> Dict[str, Dict[str, Any]]:
    """Obter todas as configurações de ISINs (keyed by ISIN)"""
    try:
        result = db.client.table("isin_config").select("*").execute()
        configs = {}
        for row in result.data or []:
            configs[row["isin"]] = {
                "automation_enabled": row.get("automation_enabled", False),
                "strategy_params": row.get("strategy_params", {})
            }
        return configs
    except Exception as e:
        logger.warning(f"Failed to get ISIN configs: {e}")
        return {}


# ===== ENDPOINTS =====

@router.get("", response_model=List[ISINResponse])
async def list_isins():
    """
    GET /api/isins - Listar ISINs do utilizador

    Retorna posições abertas da T212 API com configurações locais
    Dados sempre frescos (não há cache)
    """
    try:
        logger.info("Fetching ISINs from T212 API...")

        # Obter posições da T212
        t212_client = get_t212_client()
        positions = t212_client.get_positions()

        if not positions:
            logger.info("No positions found in T212")
            return []

        logger.info(f"T212 returned {len(positions)} positions")

        # Obter configurações locais
        configs = await _get_isin_configs()
        logger.info(f"Found configs for {len(configs)} ISINs")

        # Formatar resposta
        result = []
        for pos in positions:
            isin = pos.get("instrument", {}).get("isin", "")
            config = configs.get(isin)
            formatted = _format_t212_position(pos, config)
            result.append(formatted)

        logger.info(f"Returning {len(result)} formatted ISINs")
        return result

    except Exception as e:
        logger.error(f"Error fetching ISINs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar ISINs: {str(e)}"
        )


@router.put("/{isin}/config", response_model=ISINConfigResponse)
async def update_isin_config(isin: str, data: ISINConfigUpdate):
    """
    PUT /api/isins/{isin}/config - Atualizar configurações de um ISIN

    Permite mudar:
    - automation_enabled: ativar/desativar automação
    - strategy_params: parâmetros da estratégia
    """
    try:
        logger.info(f"Updating config for ISIN: {isin}")

        # Verificar se ISIN existe em T212
        t212_client = get_t212_client()
        positions = t212_client.get_positions()

        isin_exists = any(
            pos.get("instrument", {}).get("isin") == isin
            for pos in positions
        )

        if not isin_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN {isin} não encontrado em T212"
            )

        # Preparar updates
        updates = {}
        if data.automation_enabled is not None:
            updates["automation_enabled"] = data.automation_enabled
        if data.strategy_params is not None:
            updates["strategy_params"] = data.strategy_params

        if not updates:
            # Retornar config atual sem mudanças
            try:
                result = db.client.table("isin_config").select("*").eq("isin", isin).execute()
                if result.data:
                    config = result.data[0]
                    return {
                        "isin": isin,
                        "automation_enabled": config.get("automation_enabled", False),
                        "strategy_params": config.get("strategy_params", {})
                    }
            except:
                pass

            # Retornar defaults se não existe
            return {
                "isin": isin,
                "automation_enabled": False,
                "strategy_params": {}
            }

        # Fazer upsert (atualizar ou criar)
        updates["isin"] = isin
        db.client.table("isin_config").upsert(updates).execute()

        logger.info(f"Config updated for ISIN: {isin}")

        return {
            "isin": isin,
            "automation_enabled": updates.get("automation_enabled", False),
            "strategy_params": updates.get("strategy_params", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ISIN config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar configuração: {str(e)}"
        )


@router.get("/{isin}/config", response_model=ISINConfigResponse)
async def get_isin_config(isin: str):
    """
    GET /api/isins/{isin}/config - Obter configurações de um ISIN
    """
    try:
        result = db.client.table("isin_config").select("*").eq("isin", isin).execute()

        if result.data:
            config = result.data[0]
            return {
                "isin": isin,
                "automation_enabled": config.get("automation_enabled", False),
                "strategy_params": config.get("strategy_params", {})
            }

        # Retornar defaults se não existe
        return {
            "isin": isin,
            "automation_enabled": False,
            "strategy_params": {}
        }

    except Exception as e:
        logger.error(f"Error getting ISIN config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração: {str(e)}"
        )
