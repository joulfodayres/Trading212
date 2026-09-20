"""
Automation Routes - Monitor and configure the automation engine
Phase 4: Grid Trading Automation
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

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


# ===== HELPERS =====

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
        result = db.client.table("app_parameters").select("grid_trading_enabled").execute()
        grid_trading_enabled = result.data[0].get("grid_trading_enabled", True) if result.data else True

        scheduler_status = scheduler_service.get_status() if scheduler_service else {}
        scheduler_running = scheduler_status.get("running", False)
        cycle_count = automation_engine.cycle_count if automation_engine else 0
        last_cycle_duration = automation_engine.last_cycle_duration if automation_engine else None

        return {
            "grid_trading_enabled": grid_trading_enabled,
            "scheduler_running": scheduler_running,
            "cycle_count": cycle_count,
            "last_cycle_duration": last_cycle_duration
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

        # Update app_parameters
        result = db.client.table("app_parameters").update({
            "grid_trading_enabled": True,
            "updated_at": "now()"
        }).execute()

        if result.data:
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

        # Update app_parameters
        result = db.client.table("app_parameters").update({
            "grid_trading_enabled": False,
            "updated_at": "now()"
        }).execute()

        if result.data:
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


@router.put("/config/interval")
async def update_scheduler_interval(interval: int = Query(..., ge=5, le=300)):
    """
    Update scheduler interval at runtime.

    Args:
        interval: New interval in seconds (5-300)

    Returns:
        Updated configuration
    """
    try:
        from main import scheduler_service

        if not scheduler_service:
            raise HTTPException(status_code=500, detail="Scheduler não inicializado")

        await scheduler_service.update_interval(interval)

        return {
            "status": "updated",
            "new_interval": interval,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
