"""
Automation Routes - Monitor and configure the automation engine
Phase 4: Grid Trading Automation
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, Field

from services import trading_limits_service as limits_service
from services.alert_service import DEFAULT_ALERT_SETTINGS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/automation", tags=["automation"])


# ===== SCHEMAS =====

class AutomationEnableRequest(BaseModel):
    """Request para ativar automação global"""
    pass


class AutomationDisableRequest(BaseModel):
    """Request para desativar automação global"""
    pass


class AutomationStatusResponse(BaseModel):
    """Response com status de automação global"""
    grid_trading_enabled: bool
    scheduler_running: bool
    cycle_count: int
    last_cycle_duration: Optional[float] = None
    automation_disabled_reason: Optional[str] = None


class TradingLimitsRequest(BaseModel):
    """Request para atualizar limites de trading (Item #15). null = sem limite."""
    max_buy_order_value: Optional[float] = Field(None, ge=0)
    max_sell_order_value: Optional[float] = Field(None, ge=0)
    max_daily_spend: Optional[float] = Field(None, ge=0)


class AlertSettingsRequest(BaseModel):
    """Request para atualizar os interruptores de alerta (Item #15)."""
    login_threshold: Optional[bool] = None
    security_events: Optional[bool] = None
    limit_reached: Optional[bool] = None
    order_rejected: Optional[bool] = None
    invalid_credentials: Optional[bool] = None
    cycle_errors: Optional[bool] = None
    deploy_disabled: Optional[bool] = None


class SchedulerIntervalRequest(BaseModel):
    """Request para atualizar intervalo do scheduler"""
    scheduler_interval_seconds: int = Field(..., ge=5, le=3600)


class LogLevelRequest(BaseModel):
    """Request para atualizar log level"""
    log_level: str = Field(..., pattern='^(OFF|LOW|MEDIUM|HIGH)$')


class RunCycleOnceRequest(BaseModel):
    """Request para executar um ciclo uma única vez"""
    pass


def _get_db():
    """Get Supabase DB instance"""
    from db.supabase_client import get_db
    return get_db()


# ===== ENDPOINTS =====

@router.get("/global-status", response_model=AutomationStatusResponse)
async def get_global_automation_status():
    """
    GET /api/v1/automation/global-status

    Retorna status global da automação
    """
    try:
        from main import scheduler_service, automation_engine
        from db.supabase_client import get_db

        db = get_db()

        # Buscar app_parameters
        result = db.client.table("app_parameters").select(
            "grid_trading_enabled, automation_disabled_reason"
        ).execute()
        row = result.data[0] if result.data else {}
        grid_trading_enabled = row.get("grid_trading_enabled", True)
        automation_disabled_reason = row.get("automation_disabled_reason") if not grid_trading_enabled else None

        scheduler_status = scheduler_service.get_status() if scheduler_service else {}
        scheduler_running = scheduler_status.get("running", False)
        cycle_count = automation_engine.cycle_count if automation_engine else 0
        last_cycle_duration = automation_engine.last_cycle_duration if automation_engine else None

        return {
            "grid_trading_enabled": grid_trading_enabled,
            "scheduler_running": scheduler_running,
            "cycle_count": cycle_count,
            "last_cycle_duration": last_cycle_duration,
            "automation_disabled_reason": automation_disabled_reason,
        }

    except Exception as e:
        logger.error(f"Erro ao obter status global: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/enable")
async def enable_global_automation():
    """
    PUT /api/v1/automation/enable

    Ativa automação global (grid_trading_enabled=TRUE em app_parameters)
    """
    try:
        db = _get_db()

        logger.info("Enabling global automation...")

        # Get the singleton row first
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")

        param_id = result.data[0]["id"]

        # Update with WHERE clause — clear the disabled reason (Item #15):
        # a manual re-enable always resets it, even if it was set by an
        # auto-stop (limit hit / deploy detected).
        update_result = db.client.table("app_parameters").update({
            "grid_trading_enabled": True,
            "automation_disabled_reason": None,
            "updated_at": "now()"
        }).eq("id", param_id).execute()

        if update_result.data:
            logger.info("✅ Global automation enabled")
            return {
                "success": True,
                "grid_trading_enabled": True,
                "message": "Automação global ativada"
            }
        else:
            raise Exception("Failed to update app_parameters")

    except Exception as e:
        logger.error(f"Erro ao ativar automação global: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/disable")
async def disable_global_automation():
    """
    PUT /api/v1/automation/disable

    Desativa automação global (grid_trading_enabled=FALSE em app_parameters)
    """
    try:
        db = _get_db()

        logger.info("Disabling global automation...")

        # Get the singleton row first
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")

        param_id = result.data[0]["id"]

        # Update with WHERE clause
        update_result = db.client.table("app_parameters").update({
            "grid_trading_enabled": False,
            "updated_at": "now()"
        }).eq("id", param_id).execute()

        if update_result.data:
            logger.info("✅ Global automation disabled")
            return {
                "success": True,
                "grid_trading_enabled": False,
                "message": "Automação global desativada"
            }
        else:
            raise Exception("Failed to update app_parameters")

    except Exception as e:
        logger.error(f"Erro ao desativar automação global: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_automation_status():
    """
    Get current automation engine status.

    Returns scheduler status, cycle count, last cycle metrics.
    """
    try:
        from main import scheduler_service

        if not scheduler_service:
            return {"error": "Scheduler não inicializado"}

        return {
            "scheduler": scheduler_service.get_status(),
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/interval")
async def get_scheduler_interval():
    """
    GET /api/v1/automation/config/interval

    Retorna o intervalo atual do scheduler

    Returns:
        Current scheduler interval configuration
    """
    try:
        from db.supabase_client import get_db

        db = get_db()

        # Buscar app_parameters
        result = db.client.table("app_parameters").select("scheduler_interval_seconds").execute()
        logger.info(f"Query result: {result}")
        logger.info(f"Query result data: {result.data}")

        scheduler_interval_seconds = result.data[0].get("scheduler_interval_seconds", 15) if result.data else 15

        return {
            "scheduler_interval_seconds": scheduler_interval_seconds,
            "status": "ok"
        }

    except Exception as e:
        logger.error(f"Erro ao obter intervalo do scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/interval")
async def update_scheduler_interval(request: SchedulerIntervalRequest):
    """
    PUT /api/v1/automation/config/interval

    Update scheduler interval at runtime.

    Request body:
        {
            "scheduler_interval_seconds": int (5-300)
        }

    Returns:
        Updated configuration
    """
    try:
        from db.supabase_client import get_db

        scheduler_interval_seconds = request.scheduler_interval_seconds

        if not (5 <= scheduler_interval_seconds <= 3600):
            raise HTTPException(status_code=400, detail="scheduler_interval_seconds must be between 5 and 3600")

        db = get_db()

        # Get the singleton row first
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")

        param_id = result.data[0]["id"]
        logger.info(f"Updating app_parameters id={param_id} with interval={scheduler_interval_seconds}s")

        # Update with WHERE clause
        update_result = db.client.table("app_parameters").update({
            "scheduler_interval_seconds": scheduler_interval_seconds,
            "updated_at": "now()"
        }).eq("id", param_id).execute()

        logger.info(f"Update result: {update_result}")
        logger.info(f"Update result data: {update_result.data}")

        if update_result.data:
            logger.info(f"✅ Scheduler interval updated to {scheduler_interval_seconds}s")

            # Try to update the running scheduler if available
            try:
                from main import scheduler_service
                if scheduler_service:
                    await scheduler_service.update_interval(scheduler_interval_seconds)
            except Exception as update_err:
                logger.warning(f"Could not update running scheduler: {update_err}")

            return {
                "status": "updated",
                "scheduler_interval_seconds": scheduler_interval_seconds,
            }
        else:
            error_msg = f"Failed to update app_parameters. Response: {update_result}"
            logger.error(error_msg)
            raise Exception(error_msg)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar intervalo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/watch")
async def get_watch_orders(limit: int = Query(50, ge=1, le=100)):
    """
    Get all orders with automation_status='W' (Watch).

    Used for monitoring orders waiting for execution.
    """
    try:
        from db.supabase_client import SessionLocal
        from models.db import Order

        db = SessionLocal()
        orders = db.query(Order).filter_by(automation_status="W").limit(limit).all()

        return {
            "count": len(orders),
            "orders": [
                {
                    "id": o.id,
                    "t212_order_id": o.t212_order_id,
                    "ticker": o.ticker,
                    "side": o.side,
                    "quantity": o.quantity,
                    "filled_quantity": o.filled_quantity,
                    "type": o.type,
                    "status": o.status,
                    "limit_price": o.limit_price,
                    "automation_status": o.automation_status,
                    "synced_at": o.synced_at.isoformat() if o.synced_at else None,
                }
                for o in orders
            ],
        }

    except Exception as e:
        logger.error(f"Erro ao obter ordens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_automation_logs(limit: int = Query(50, ge=1, le=500)):
    """
    Get recent automation engine logs.

    Returns last N log entries from BD.
    """
    try:
        from db.supabase_client import SessionLocal
        from models.db import Log

        db = SessionLocal()
        logs = (
            db.query(Log)
            .order_by(Log.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "count": len(logs),
            "logs": [
                {
                    "id": l.id,
                    "nivel": l.nivel,
                    "mensagem": l.mensagem,
                    "detalhes_json": l.detalhes_json,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in reversed(logs)  # Return in chronological order
            ],
        }

    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_automation_metrics():
    """
    Get automation engine metrics and performance data.
    """
    try:
        from main import automation_engine
        from db.supabase_client import SessionLocal
        from models.db import Order

        if not automation_engine:
            return {"error": "AutomationEngine não inicializado"}

        db = SessionLocal()

        # Count orders by status
        total_orders = db.query(Order).count()
        watch_orders = db.query(Order).filter_by(automation_status="W").count()
        executed_orders = db.query(Order).filter_by(automation_status="E").count()
        canceled_orders = db.query(Order).filter_by(automation_status="C").count()

        return {
            "cycle_count": automation_engine.cycle_count,
            "last_cycle_start": (
                automation_engine.last_cycle_start.isoformat()
                if automation_engine.last_cycle_start
                else None
            ),
            "last_cycle_duration_seconds": automation_engine.last_cycle_duration,
            "orders": {
                "total": total_orders,
                "watch": watch_orders,
                "executed": executed_orders,
                "canceled": canceled_orders,
            },
        }

    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-cycle-once")
async def run_cycle_once():
    """
    POST /api/v1/automation/run-cycle-once

    Executa UMA ÚNICA VEZ o ciclo de automação imediatamente.
    Não afeta o estado global da automação (grid_trading_enabled).
    """
    try:
        from main import automation_engine

        if not automation_engine:
            raise HTTPException(status_code=503, detail="AutomationEngine não inicializado")

        logger.info("🚀 Executando ciclo manual via API (run-cycle-once)...")

        # Chamar run_cycle diretamente
        import asyncio
        await automation_engine.run_cycle()

        # Retornar status após execução
        return {
            "success": True,
            "message": "Ciclo executado com sucesso",
            "cycle_number": automation_engine.cycle_count,
            "last_duration": automation_engine.last_cycle_duration
        }

    except Exception as e:
        logger.error(f"❌ Erro ao executar ciclo manual: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao executar ciclo: {str(e)}")


@router.get("/config/log-level")
async def get_log_level():
    """
    GET /api/v1/automation/config/log-level

    Retorna o nível de logging atual
    """
    try:
        db = _get_db()

        result = db.client.table("app_parameters").select("log_level").execute()
        log_level = result.data[0].get("log_level", "OFF") if result.data else "OFF"

        return {
            "log_level": log_level,
            "status": "ok"
        }

    except Exception as e:
        logger.error(f"Erro ao obter log_level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/log-level")
async def update_log_level(request: LogLevelRequest):
    """
    PUT /api/v1/automation/config/log-level

    Atualiza o nível de logging em tempo real.

    Valores válidos: OFF, LOW, MEDIUM, HIGH
    """
    try:
        if request.log_level not in ["OFF", "LOW", "MEDIUM", "HIGH"]:
            raise HTTPException(
                status_code=400,
                detail="log_level deve ser um de: OFF, LOW, MEDIUM, HIGH"
            )

        db = _get_db()

        # Get the singleton row first
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")

        param_id = result.data[0]["id"]
        logger.info(f"Updating log_level to {request.log_level}...")

        # Update with WHERE clause
        update_result = db.client.table("app_parameters").update({
            "log_level": request.log_level,
            "updated_at": "now()"
        }).eq("id", param_id).execute()

        if update_result.data:
            logger.info(f"✅ Log level updated to {request.log_level}")
            return {
                "status": "updated",
                "log_level": request.log_level,
            }
        else:
            error_msg = f"Failed to update app_parameters. Response: {update_result}"
            logger.error(error_msg)
            raise Exception(error_msg)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar log_level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== TRADING LIMITS (Item #15) =====

@router.get("/config/limits")
async def get_trading_limits():
    """
    GET /api/v1/automation/config/limits

    Retorna os limites de trading configurados. null = sem limite.
    """
    try:
        limits = limits_service.get_trading_limits()
        return {
            "max_buy_order_value": limits.get("max_buy_order_value"),
            "max_sell_order_value": limits.get("max_sell_order_value"),
            "max_daily_spend": limits.get("max_daily_spend"),
        }
    except Exception as e:
        logger.error(f"Erro ao obter limites de trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/limits")
async def update_trading_limits(request: TradingLimitsRequest):
    """
    PUT /api/v1/automation/config/limits

    Atualiza os limites de trading. Campo omitido/null = sem limite nesse campo.
    """
    try:
        db = _get_db()
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")
        param_id = result.data[0]["id"]

        update_result = db.client.table("app_parameters").update({
            "max_buy_order_value": request.max_buy_order_value,
            "max_sell_order_value": request.max_sell_order_value,
            "max_daily_spend": request.max_daily_spend,
            "updated_at": "now()",
        }).eq("id", param_id).execute()

        if not update_result.data:
            raise Exception("Failed to update app_parameters")

        logger.info(
            f"✅ Limites de trading atualizados: buy={request.max_buy_order_value}, "
            f"sell={request.max_sell_order_value}, daily={request.max_daily_spend}"
        )
        return {
            "status": "updated",
            "max_buy_order_value": request.max_buy_order_value,
            "max_sell_order_value": request.max_sell_order_value,
            "max_daily_spend": request.max_daily_spend,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar limites de trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumption")
async def get_trading_consumption():
    """
    GET /api/v1/automation/consumption

    Consumo atual face aos limites — usado pela barra de progresso no dashboard.
    """
    try:
        limits = limits_service.get_trading_limits()
        daily_spend = limits_service.get_daily_spend()
        return {
            "daily_spend": daily_spend,
            "max_daily_spend": limits.get("max_daily_spend"),
        }
    except Exception as e:
        logger.error(f"Erro ao obter consumo de trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== ALERT SETTINGS (Item #15) =====

@router.get("/config/alerts")
async def get_alert_settings():
    """
    GET /api/v1/automation/config/alerts

    Retorna os interruptores de alerta configurados (chaves em falta usam o default).
    """
    try:
        db = _get_db()
        result = db.client.table("app_parameters").select("alert_settings").execute()
        stored = (result.data[0].get("alert_settings") if result.data else None) or {}
        return {**DEFAULT_ALERT_SETTINGS, **stored}
    except Exception as e:
        logger.error(f"Erro ao obter alert_settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/alerts")
async def update_alert_settings(request: AlertSettingsRequest):
    """
    PUT /api/v1/automation/config/alerts

    Atualiza os interruptores de alerta (merge parcial — só altera os campos enviados).
    """
    try:
        db = _get_db()
        result = db.client.table("app_parameters").select("id, alert_settings").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")
        row = result.data[0]
        current = {**DEFAULT_ALERT_SETTINGS, **(row.get("alert_settings") or {})}

        updates = request.model_dump(exclude_none=True)
        current.update(updates)

        update_result = db.client.table("app_parameters").update({
            "alert_settings": current,
            "updated_at": "now()",
        }).eq("id", row["id"]).execute()

        if not update_result.data:
            raise Exception("Failed to update app_parameters")

        logger.info(f"✅ Alert settings atualizados: {updates}")
        return current
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar alert_settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
