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
    strategy_name: Optional[str] = None
    pnl: float = 0.0
    pnl_percent: float = 0.0


class StrategyOption(BaseModel):
    """Opção de estratégia para seleção no dialog"""
    id: str
    strategy_name: str


class AutomationToggleRequest(BaseModel):
    """Request para alternar automação"""
    automation_enabled: bool
    strategy_id: Optional[str] = None
    initial_investment: Optional[float] = None


class AutomationUpdateResponse(BaseModel):
    """Response com configuração atualizada de automação"""
    isin_id: str
    automation_enabled: bool
    strategy_id: Optional[str] = None
    strategy_name: Optional[str] = None
    initial_investment: Optional[float] = None


# ===== HELPERS =====

def _format_t212_position(position: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Formata posição da T212 API para ISINResponse
    Enriquece com configuração local (automation_enabled, strategy_id, strategy_name)
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
        "strategy_name": config.get("strategy_name") if config else None,
        "pnl": pnl,
        "pnl_percent": pnl_percent
    }


async def _get_isin_configs() -> Dict[str, Dict[str, Any]]:
    """Obter todas as configurações de ISINs (keyed by ISIN)"""
    try:
        result = db.client.table("isins").select("isin, automation_enabled, strategy_id").execute()
        configs = {}

        # Carregar todos os dados de ISINs
        for row in result.data or []:
            isin = row["isin"]
            strategy_id = row.get("strategy_id")
            strategy_name = None

            # Se tem estratégia, buscar o nome
            if strategy_id:
                try:
                    strategy_result = db.client.table("strategies").select("strategy_name").eq("id", strategy_id).single().execute()
                    if strategy_result.data:
                        strategy_name = strategy_result.data.get("strategy_name")
                except:
                    pass

            configs[isin] = {
                "automation_enabled": row.get("automation_enabled", False),
                "strategy_name": strategy_name
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


# ===== AUTOMATION ENDPOINTS =====

@router.get("/strategies", response_model=List[StrategyOption])
async def get_enabled_strategies():
    """
    GET /api/isins/strategies - Obter estratégias habilitadas

    Retorna apenas estratégias com strategy_status = 'E' (Enabled)
    Estratégias públicas (user_id IS NULL) e próprias do user
    Usado para o dialog de seleção de estratégia na automação
    """
    try:
        logger.info("Fetching enabled strategies...")

        # Buscar estratégias habilitadas (públicas e próprias)
        result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()

        strategies = []
        for row in result.data or []:
            strategies.append({
                "id": row["id"],
                "strategy_name": row.get("strategy_name", "Unnamed Strategy")
            })

        logger.info(f"Found {len(strategies)} enabled strategies")
        return strategies

    except Exception as e:
        logger.error(f"Error fetching strategies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estratégias: {str(e)}"
        )


@router.post("/sync", response_model=Dict[str, Any])
async def sync_positions():
    """
    POST /api/isins/sync - Sincronizar carteira com T212

    Chama T212 API /equity/positions e atualiza todos os registos em 'isins' table.
    Insere novos ISINs se não existirem, atualiza existentes.

    Campos atualizados:
    - quantity, currentPrice, averagePricePaid
    - quantityAvailableForTrading, quantityInPies
    - walletImpact (currency, currentValue, fxImpact, totalCost, unrealizedProfitLoss)

    Retorna:
    {
        "success": true,
        "synced": 5,
        "created": 1,
        "updated": 4,
        "errors": 0
    }
    """
    try:
        logger.info("Starting portfolio sync with T212...")

        # Chama T212 API
        t212_client = get_t212_client()
        positions = t212_client.get_positions()

        if not positions:
            logger.info("No positions found in T212")
            return {
                "success": True,
                "synced": 0,
                "created": 0,
                "updated": 0,
                "errors": 0,
                "message": "No positions found"
            }

        logger.info(f"T212 returned {len(positions)} positions")

        synced = 0
        created = 0
        updated = 0
        errors = 0

        # Processar cada posição
        for position in positions:
            try:
                instrument = position.get("instrument", {})
                isin = instrument.get("isin")

                if not isin:
                    logger.warning("Position without ISIN found, skipping")
                    errors += 1
                    continue

                # Preparar dados para atualizar/inserir
                # Cross-check com API T212 - guardar TODOS os campos
                wallet_impact = position.get("walletImpact", {})
                instrument = position.get("instrument", {})

                isin_data = {
                    # Identificadores
                    "isin": isin,
                    "ticker": instrument.get("ticker", ""),
                    "name": instrument.get("name", ""),

                    # Preços e quantidades
                    "quantity": position.get("quantity", 0),
                    "current_price": position.get("currentPrice", 0),
                    "average_price_paid": position.get("averagePricePaid", 0),
                    "quantity_available_for_trading": position.get("quantityAvailableForTrading", 0),
                    "quantity_in_pies": position.get("quantityInPies", 0),

                    # Wallet impact (P&L, valores)
                    "wi_currency": wallet_impact.get("currency", "EUR"),
                    "wi_current_value": wallet_impact.get("currentValue", 0),
                    "wi_fx_impact": wallet_impact.get("fxImpact", 0),
                    "wi_total_cost": wallet_impact.get("totalCost", 0),
                    "wi_unrealized_profit_loss": wallet_impact.get("unrealizedProfitLoss", 0),

                    # Timestamps
                    "api_created_at": position.get("createdAt"),
                    "position_created_at": position.get("createdAt"),

                    # JSON backup (completo)
                    "instrument_json": instrument,

                    "updated_at": "now()"
                }

                # Verificar se ISIN já existe
                existing = db.client.table("isins").select("id").eq("isin", isin).execute()

                if existing.data:
                    # UPDATE
                    db.client.table("isins").update(isin_data).eq("isin", isin).execute()
                    logger.debug(f"Updated ISIN: {isin}")
                    updated += 1
                else:
                    # INSERT
                    db.client.table("isins").insert(isin_data).execute()
                    logger.debug(f"Created ISIN: {isin}")
                    created += 1

                synced += 1

            except Exception as e:
                logger.error(f"Error syncing position {isin}: {e}")
                errors += 1
                continue

        response = {
            "success": True,
            "synced": synced,
            "created": created,
            "updated": updated,
            "errors": errors,
            "message": f"Synced {synced} positions ({created} new, {updated} updated)"
        }

        logger.info(f"Portfolio sync completed: {response}")
        return response

    except Exception as e:
        logger.error(f"Error during portfolio sync: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sincronizar carteira: {str(e)}"
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
                    strategy_result = db.client.table("strategies").select("id", "strategy_name").eq("id", data.strategy_id).execute()
                    if strategy_result.data:
                        strategy_row = strategy_result.data[0]
                        strategy_id = data.strategy_id
                        strategy_name = strategy_row.get("strategy_name", "Unknown")
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
            "automation_enabled": data.automation_enabled,
            "strategy_id": strategy_id,
            "updated_at": "now()"
        }

        # Adicionar initial_investment se fornecido
        if data.initial_investment is not None:
            isin_data["initial_investment"] = data.initial_investment
            logger.info(f"Setting initial_investment={data.initial_investment} for ISIN {isin_id}")

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
            "strategy_name": strategy_name,
            "initial_investment": data.initial_investment
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
