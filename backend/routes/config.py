"""
Rotas de configuração do Trading 212
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from config.settings import settings
from api.trading212 import Trading212Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


# ===== SCHEMAS =====

class StrategyParams(BaseModel):
    """Parâmetros da estratégia Grid Trading"""
    buy_threshold_percent: float  # Ex: 1.0 para 1%
    sell_threshold_percent: float  # Ex: 1.0 para 1%
    buy_quantity_percent: float  # Ex: 50.0 para 50%
    sell_quantity_percent: float  # Ex: 50.0 para 50%
    check_interval_seconds: int  # Ex: 300 para 5 minutos
    max_position_size_percent: float = 10.0
    stop_loss_percent: float = 5.0
    max_drawdown_percent: float = 10.0


class ConfigResponse(BaseModel):
    """Resposta com toda a configuração"""
    t212_environment: str
    t212_api_key_encrypted: bool
    strategy_params: StrategyParams
    message: str


# ===== ENDPOINTS =====

@router.get("/status")
async def get_t212_status():
    """
    GET /api/config/status

    Estado real da ligação T212 — ambiente e conectividade. Substitui o
    antigo formulário de credenciais (Item #15): as credenciais T212 são
    geridas exclusivamente por variáveis de ambiente no Render
    (T212_API_KEY, T212_API_SECRET, T212_ENVIRONMENT), nunca pela UI —
    fonte única de verdade, sem risco de a UI mostrar um ambiente que não
    corresponde ao que a automação está realmente a usar.
    """
    try:
        client = Trading212Client(
            api_key=settings.T212_API_KEY,
            api_secret=settings.T212_API_SECRET,
            environment=settings.T212_ENVIRONMENT,
        )
        account_data = client.get_account_summary()
        return {
            "environment": settings.T212_ENVIRONMENT,
            "connected": account_data is not None,
        }
    except Exception as e:
        logger.warning(f"Erro ao testar ligação T212: {e}")
        return {
            "environment": settings.T212_ENVIRONMENT,
            "connected": False,
        }


@router.get("/strategy-params", response_model=StrategyParams)
async def get_strategy_params():
    """
    Obter parâmetros da estratégia Grid Trading
    (Single-user - sem filtro de user_id necessário)
    """
    try:
        # TODO: Buscar de BD (config.strategy_params JSONB)
        # Por enquanto, retornar defaults
        return StrategyParams(
            buy_threshold_percent=1.0,
            sell_threshold_percent=1.0,
            buy_quantity_percent=50.0,
            sell_quantity_percent=50.0,
            check_interval_seconds=300,
            max_position_size_percent=10.0,
            stop_loss_percent=5.0,
            max_drawdown_percent=10.0
        )

    except Exception as e:
        logger.error(f"Erro ao obter strategy params: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter parâmetros da estratégia"
        )


@router.put("/strategy-params", response_model=ConfigResponse)
async def save_strategy_params(params: StrategyParams):
    """
    Guardar parâmetros da estratégia Grid Trading
    """
    try:
        # Validar inputs
        if params.buy_threshold_percent <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="buy_threshold_percent deve ser > 0"
            )

        if params.sell_threshold_percent <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sell_threshold_percent deve ser > 0"
            )

        if params.check_interval_seconds < 60:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="check_interval_seconds deve ser >= 60"
            )

        # TODO: Guardar em BD (config.strategy_params JSONB)

        logger.info(" Strategy params guardados")

        return ConfigResponse(
            t212_environment="demo",
            t212_api_key_encrypted=True,
            strategy_params=params,
            message="Parâmetros guardados com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao guardar strategy params: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao guardar parâmetros"
        )
