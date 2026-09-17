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


class StrategyOption(BaseModel):
    """Opção de estratégia para seleção no dialog"""
    id: str
    strategy_name: str


class AutomationToggleRequest(BaseModel):
    """Request para alternar automação"""
    automation_enabled: bool
    strategy_id: Optional[str] = None


class AutomationUpdateResponse(BaseModel):
    """Response com configuração atualizada de automação"""
    isin_id: str
    automation_enabled: bool
    strategy_id: Optional[str] = None
    strategy_name: Optional[str] = None


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


# ===== AUTOMATION ENDPOINTS =====

@router.get("/strategies", response_model=List[StrategyOption])
async def get_enabled_strategies():
    """
    GET /api/isins/strategies - Obter estratégias habilitadas

    Retorna apenas estratégias com strategy_status = 'E' (Enabled)
    Usado para o dialog de seleção de estratégia na automação
    """
    try:
        logger.info("Fetching enabled strategies...")

        # Buscar estratégias habilitadas
        result = db.client.table("strategies").select("id", "name").eq("strategy_status", "E").execute()

        strategies = []
        for row in result.data or []:
            strategies.append({
                "id": row["id"],
                "strategy_name": row.get("name", "Unnamed Strategy")
            })

        logger.info(f"Found {len(strategies)} enabled strategies")
        return strategies

    except Exception as e:
        logger.error(f"Error fetching strategies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estratégias: {str(e)}"
        )


@router.put("/{isin_id}/automation", response_model=AutomationUpdateResponse)
async def toggle_automation(isin_id: str, data: AutomationToggleRequest):
    """
    PUT /api/isins/{isin_id}/automation - Alternar automação de um ISIN

    Permite ativar/desativar automação com estratégia associada.

    Request body:
    {
        "automation_enabled": true/false,
        "strategy_id": "uuid-da-estrategia" ou null
    }

    Lógica:
    1. Valida que ISIN existe em T212 positions
    2. Se automation_enabled=true:
       - Cria ou atualiza linha em 'isins' table
       - Associa strategy_id
    3. Se automation_enabled=false:
       - Desativa automação (strategy_id = null)
    4. Após UPDATE/INSERT em 'isins', insere audit record em 'isin_strategy_history'
    5. Retorna configuração atualizada
    """
    try:
        logger.info(f"Toggling automation for ISIN: {isin_id}, enabled: {data.automation_enabled}")

        # Step 1: Verificar se ISIN existe em T212
        t212_client = get_t212_client()
        positions = t212_client.get_positions()

        # Encontrar posição T212
        t212_position = None
        for pos in positions:
            instrument = pos.get("instrument", {})
            if instrument.get("isin") == isin_id:
                t212_position = pos
                break

        if not t212_position:
            logger.warning(f"ISIN {isin_id} not found in T212 positions")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISIN {isin_id} não encontrado nas posições da T212"
            )

        logger.info(f"ISIN {isin_id} found in T212 positions")

        # Step 2 & 3: Processar automação
        strategy_id = None
        strategy_name = None

        if data.automation_enabled:
            # Validar strategy_id se fornecido
            if data.strategy_id:
                try:
                    strategy_result = db.client.table("strategies").select("id", "name").eq("id", data.strategy_id).execute()
                    if strategy_result.data:
                        strategy_row = strategy_result.data[0]
                        strategy_id = data.strategy_id
                        strategy_name = strategy_row.get("name", "Unknown")
                        logger.info(f"Strategy {strategy_id} ({strategy_name}) selected for automation")
                    else:
                        logger.warning(f"Strategy {data.strategy_id} not found")
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Estratégia {data.strategy_id} não encontrada"
                        )
                except Exception as e:
                    if isinstance(e, HTTPException):
                        raise
                    logger.error(f"Error validating strategy: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Erro ao validar estratégia: {str(e)}"
                    )
            else:
                logger.warning("automation_enabled=true but no strategy_id provided")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="strategy_id é obrigatório quando automation_enabled=true"
                )

        # Step 4: Inserir ou atualizar em 'isins' table
        instrument = t212_position.get("instrument", {})
        isin_data = {
            "isin": isin_id,
            "ticker": instrument.get("ticker", ""),
            "name": instrument.get("name", ""),
            "currency": instrument.get("currency", "EUR"),
            "automation_enabled": data.automation_enabled,
            "strategy_id": strategy_id,
            "updated_at": "now()"
        }

        # Tentar encontrar ISIN existente
        existing_result = db.client.table("isins").select("id").eq("isin", isin_id).execute()

        if existing_result.data:
            # UPDATE existente
            logger.info(f"Updating existing ISIN record: {isin_id}")
            db.client.table("isins").update(isin_data).eq("isin", isin_id).execute()
            isin_row_id = existing_result.data[0]["id"]
        else:
            # INSERT novo
            logger.info(f"Creating new ISIN record: {isin_id}")
            insert_result = db.client.table("isins").insert(isin_data).execute()
            if insert_result.data:
                isin_row_id = insert_result.data[0]["id"]
            else:
                raise Exception("Failed to insert ISIN record")

        # Step 5: Auditar em 'isin_strategy_history'
        try:
            audit_data = {
                "isin_id": isin_row_id,
                "strategy_id": strategy_id,
                "automated": data.automation_enabled,
                "created_at": "now()",
                "updated_at": "now()"
            }

            db.client.table("isin_strategy_history").insert(audit_data).execute()
            logger.info(f"Audit record created for ISIN {isin_id}")
        except Exception as e:
            logger.error(f"Warning: Failed to create audit record: {e}")
            # Não falha a operação se audit falhar

        # Step 6: Preparar resposta
        response = {
            "isin_id": isin_row_id,
            "automation_enabled": data.automation_enabled,
            "strategy_id": strategy_id,
            "strategy_name": strategy_name
        }

        logger.info(f"Automation toggle completed for ISIN {isin_id}: {response}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling automation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alternar automação: {str(e)}"
        )
