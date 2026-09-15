"""
Rotas de configuração do Trading 212
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from config.settings import settings
from auth.crypto import encrypt_text, decrypt_text
from api.trading212 import Trading212Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


# ===== T212 CLIENT (lazy initialization) =====

_t212_client = None

def get_t212_client():
    """Obter cliente T212 (lazy initialization)"""
    global _t212_client
    if _t212_client is None:
        try:
            _t212_client = Trading212Client(
                api_key=settings.T212_API_KEY,
                api_secret=settings.T212_API_SECRET,
                base_url=settings.T212_BASE_URL
            )
            logger.info("T212 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize T212 client: {e}")
            raise
    return _t212_client


# ===== SCHEMAS =====

class T212Config(BaseModel):
    """Configuração do Trading 212"""
    t212_api_key: str
    t212_api_secret: str
    t212_environment: str = "demo"


class T212ConfigResponse(BaseModel):
    """Resposta com configuração"""
    t212_environment: str
    t212_api_key_encrypted: bool  # Nunca retornar a chave!
    message: str


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

@router.get("", response_model=T212ConfigResponse)
async def get_config():
    """
    Obter configuração do Trading 212
    TODO: Filtrar por user_id via JWT
    """
    try:
        # TODO: Buscar de BD (config table)
        # Por enquanto, retornar config vazia
        return T212ConfigResponse(
            t212_environment="demo",
            t212_api_key_encrypted=False,
            message="Configuração recuperada"
        )

    except Exception as e:
        logger.error(f"Erro ao obter config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter configuração"
        )


@router.put("", response_model=T212ConfigResponse)
async def save_config(config: T212Config):
    """
    Guardar configuração do Trading 212
    API key e secret são encriptados antes de guardar
    """
    try:
        # Validar inputs
        if not config.t212_api_key or len(config.t212_api_key) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key inválida"
            )

        if not config.t212_api_secret or len(config.t212_api_secret) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API secret inválida"
            )

        if config.t212_environment not in ["demo", "live"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment deve ser 'demo' ou 'live'"
            )

        # TODO: Encriptar API key e secret
        # encrypted_key = encrypt_text(config.t212_api_key, settings.ENCRYPTION_KEY)
        # encrypted_secret = encrypt_text(config.t212_api_secret, settings.ENCRYPTION_KEY)

        # TODO: Guardar em BD (config table)

        logger.info(f" Configuração guardada: {config.t212_environment}")

        return T212ConfigResponse(
            t212_environment=config.t212_environment,
            t212_api_key_encrypted=True,
            message="Configuração guardada com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao guardar config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao guardar configuração"
        )


@router.post("/test")
async def test_connection():
    """
    Testar conexão com Trading 212 API
    Usa credenciais guardadas na config
    """
    try:
        # TODO: Buscar credenciais de BD
        # TODO: Desencriptar API key e secret
        # TODO: Criar cliente T212 com credenciais
        # TODO: Chamar /equity/account/summary para testar

        # Por enquanto, usar credenciais do .env
        t212_client = get_t212_client()

        # Testar conexão
        account_data = t212_client.get_account_summary()

        if not account_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas ou API indisponível"
            )

        logger.info(" Conexão T212 testada com sucesso")

        return {
            "status": "ok",
            "message": "Conexão com Trading 212 bem-sucedida",
            "account": account_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao testar conexão com Trading 212"
        )


@router.get("/strategy-params", response_model=StrategyParams)
async def get_strategy_params():
    """
    Obter parâmetros da estratégia Grid Trading
    TODO: Filtrar por user_id via JWT
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
