"""
Strategies Routes - CRUD for trading strategies and their parameters
Phase 5: Strategy Management
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])


# ===== SCHEMAS =====

class StrategyParameterBase(BaseModel):
    """Base schema for strategy parameters"""
    pos: str  # "-1", "0", "1", etc
    param1: float  # Usually negative (buy discount)
    param2: float  # Usually positive (sell premium)
    param3: Optional[float] = None
    param4: Optional[float] = None
    param5: Optional[float] = None
    param6: Optional[float] = None
    param7: Optional[float] = None
    param8: Optional[float] = None
    param9: Optional[float] = None
    param10: Optional[float] = None


class StrategyParameterResponse(StrategyParameterBase):
    """Response for strategy parameter"""
    id: str
    strategy_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StrategyBase(BaseModel):
    """Base schema for strategy"""
    name: str
    description: Optional[str] = None
    initial_investment: Optional[float] = None
    enabled: bool = False


class StrategyCreate(StrategyBase):
    """Create strategy request - initial_investment is required"""
    initial_investment: float  # Required on creation


class StrategyUpdate(BaseModel):
    """Update strategy request"""
    name: Optional[str] = None
    description: Optional[str] = None
    initial_investment: Optional[float] = None
    enabled: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """Response for strategy"""
    id: str
    is_valid: bool  # Indicator: has params for -1, 0, 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StrategyDetailResponse(StrategyResponse):
    """Response with full strategy details including parameters"""
    parameters: List[StrategyParameterResponse] = []


# ===== HELPERS =====

def _get_db():
    """Get Supabase DB instance"""
    from db.supabase_client import get_db
    return get_db()


def _check_strategy_valid(db, strategy_id: str) -> bool:
    """
    Check if strategy is valid (has params for pos=-1, 0, 1)
    """
    try:
        result = db.client.table("strategy_parameters").select("pos").eq("strategy_id", strategy_id).execute()
        positions = [row.get("pos") for row in result.data or []]

        required_positions = {"-1", "0", "1"}
        return required_positions.issubset(set(positions))
    except Exception as e:
        logger.error(f"Error checking strategy validity: {e}")
        return False


# ===== ENDPOINTS =====

@router.get("", response_model=List[StrategyResponse])
async def list_strategies():
    """
    GET /api/v1/strategies - List all strategies
    """
    try:
        db = _get_db()

        logger.info("Fetching strategies...")
        result = db.client.table("strategies").select("*").execute()

        logger.info(f"[DEBUG] Raw DB result: {result.data}")

        strategies = []
        for row in result.data or []:
            logger.info(f"[DEBUG] Processing row: id={row.get('id')}, name='{row.get('strategy_name')}', desc='{row.get('strategy_desc')}'")
            is_valid = _check_strategy_valid(db, row["id"])

            # Map DB columns to API response
            strategy_status = row.get("strategy_status", "D")  # D = disabled, E = enabled
            enabled = strategy_status == "E"

            strategies.append({
                "id": row["id"],
                "name": row.get("strategy_name") or "",
                "description": row.get("strategy_desc") or None,
                "initial_investment": row.get("initial_investment"),
                "enabled": enabled,
                "is_valid": is_valid,
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at")
            })

        # Sort by created_at ascending (oldest first)
        strategies.sort(key=lambda x: x.get("created_at") or "")

        logger.info(f"Returned {len(strategies)} strategies")
        logger.info(f"[DEBUG] Final response: {strategies}")
        return strategies

    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_id}", response_model=StrategyDetailResponse)
async def get_strategy(strategy_id: str):
    """
    GET /api/v1/strategies/{strategy_id} - Get strategy with parameters
    """
    try:
        db = _get_db()

        logger.info(f"Fetching strategy {strategy_id}...")

        # Get strategy
        strategy_result = db.client.table("strategies").select("*").eq("id", strategy_id).execute()
        if not strategy_result.data:
            raise HTTPException(status_code=404, detail="Strategy not found")

        strategy = strategy_result.data[0]
        is_valid = _check_strategy_valid(db, strategy_id)

        # Get parameters
        params_result = db.client.table("strategy_parameters").select("*").eq("strategy_id", strategy_id).execute()
        parameters = params_result.data or []

        return {
            "id": strategy["id"],
            "name": strategy.get("strategy_name") or "",
            "description": strategy.get("strategy_desc") or None,
            "initial_investment": strategy.get("initial_investment"),
            "enabled": strategy.get("strategy_status") == "E",
            "is_valid": is_valid,
            "created_at": strategy.get("created_at"),
            "updated_at": strategy.get("updated_at"),
            "parameters": parameters
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=StrategyResponse)
async def create_strategy(data: StrategyCreate):
    """
    POST /api/v1/strategies - Create new strategy
    """
    try:
        db = _get_db()

        logger.info(f"Creating strategy: {data.name}...")

        strategy_data = {
            "strategy_name": data.name,
            "strategy_desc": data.description,
            "initial_investment": data.initial_investment,
            "strategy_status": "D",  # Always start disabled (D = disabled)
        }

        result = db.client.table("strategies").insert(strategy_data).execute()

        if not result.data:
            raise Exception("Failed to create strategy")

        strategy = result.data[0]
        logger.info(f"✅ Strategy created: {strategy['id']}")

        return {
            "id": strategy["id"],
            "name": strategy.get("strategy_name") or "",
            "description": strategy.get("strategy_desc") or None,
            "initial_investment": strategy.get("initial_investment"),
            "enabled": strategy.get("strategy_status") == "E",
            "is_valid": False,  # New strategy has no params yet
            "created_at": strategy.get("created_at"),
            "updated_at": strategy.get("updated_at")
        }

    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, data: StrategyUpdate):
    """
    PUT /api/v1/strategies/{strategy_id} - Update strategy

    If enabling strategy (enabled=True), validates that it has params for -1, 0, 1
    """
    try:
        db = _get_db()

        logger.info(f"Updating strategy {strategy_id}...")

        # Check if strategy exists
        existing = db.client.table("strategies").select("id").eq("id", strategy_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # If enabling, validate strategy
        if data.enabled is True:
            is_valid = _check_strategy_valid(db, strategy_id)
            if not is_valid:
                logger.warning(f"Cannot enable strategy {strategy_id}: missing required parameters (-1, 0, 1)")
                raise HTTPException(
                    status_code=400,
                    detail="Strategy cannot be enabled. It must have parameters for positions -1, 0, and 1"
                )

        # Build update data
        update_data = {}
        if data.name is not None:
            update_data["strategy_name"] = data.name
        if data.description is not None:
            update_data["strategy_desc"] = data.description
        if data.initial_investment is not None:
            update_data["initial_investment"] = data.initial_investment
        if data.enabled is not None:
            update_data["strategy_status"] = "E" if data.enabled else "D"

        result = db.client.table("strategies").update(update_data).eq("id", strategy_id).execute()

        if not result.data:
            raise Exception("Failed to update strategy")

        strategy = result.data[0]
        is_valid = _check_strategy_valid(db, strategy_id)

        logger.info(f"✅ Strategy updated: {strategy_id}")

        return {
            "id": strategy["id"],
            "name": strategy.get("strategy_name") or "",
            "description": strategy.get("strategy_desc") or None,
            "initial_investment": strategy.get("initial_investment"),
            "enabled": strategy.get("strategy_status") == "E",
            "is_valid": is_valid,
            "created_at": strategy.get("created_at"),
            "updated_at": strategy.get("updated_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_id}/parameters", response_model=StrategyParameterResponse)
async def create_strategy_parameter(strategy_id: str, data: StrategyParameterBase):
    """
    POST /api/v1/strategies/{strategy_id}/parameters - Create parameter
    """
    try:
        db = _get_db()

        logger.info(f"Creating parameter for strategy {strategy_id} pos={data.pos}...")

        # Check strategy exists
        existing = db.client.table("strategies").select("id").eq("id", strategy_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Strategy not found")

        param_data = {
            "strategy_id": strategy_id,
            "pos": data.pos,
            "param1": data.param1,
            "param2": data.param2,
            "param3": data.param3,
            "param4": data.param4,
            "param5": data.param5,
            "param6": data.param6,
            "param7": data.param7,
            "param8": data.param8,
            "param9": data.param9,
            "param10": data.param10,
            "created_at": "now()",
            "updated_at": "now()"
        }

        result = db.client.table("strategy_parameters").insert(param_data).execute()

        if not result.data:
            raise Exception("Failed to create parameter")

        param = result.data[0]
        logger.info(f"✅ Parameter created for strategy {strategy_id}")

        return {
            "id": param["id"],
            "strategy_id": param["strategy_id"],
            "pos": param["pos"],
            "param1": param["param1"],
            "param2": param["param2"],
            "param3": param.get("param3"),
            "param4": param.get("param4"),
            "param5": param.get("param5"),
            "param6": param.get("param6"),
            "param7": param.get("param7"),
            "param8": param.get("param8"),
            "param9": param.get("param9"),
            "param10": param.get("param10"),
            "created_at": param.get("created_at"),
            "updated_at": param.get("updated_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating parameter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{strategy_id}/parameters/{param_id}", response_model=StrategyParameterResponse)
async def update_strategy_parameter(strategy_id: str, param_id: str, data: StrategyParameterBase):
    """
    PUT /api/v1/strategies/{strategy_id}/parameters/{param_id} - Update parameter
    """
    try:
        db = _get_db()

        logger.info(f"Updating parameter {param_id}...")

        # Check parameter exists and belongs to strategy
        existing = db.client.table("strategy_parameters").select("id").eq("id", param_id).eq("strategy_id", strategy_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Parameter not found")

        update_data = {
            "pos": data.pos,
            "param1": data.param1,
            "param2": data.param2,
            "param3": data.param3,
            "param4": data.param4,
            "param5": data.param5,
            "param6": data.param6,
            "param7": data.param7,
            "param8": data.param8,
            "param9": data.param9,
            "param10": data.param10,
            "updated_at": "now()"
        }

        result = db.client.table("strategy_parameters").update(update_data).eq("id", param_id).execute()

        if not result.data:
            raise Exception("Failed to update parameter")

        param = result.data[0]
        logger.info(f"✅ Parameter updated: {param_id}")

        return {
            "id": param["id"],
            "strategy_id": param["strategy_id"],
            "pos": param["pos"],
            "param1": param["param1"],
            "param2": param["param2"],
            "param3": param.get("param3"),
            "param4": param.get("param4"),
            "param5": param.get("param5"),
            "param6": param.get("param6"),
            "param7": param.get("param7"),
            "param8": param.get("param8"),
            "param9": param.get("param9"),
            "param10": param.get("param10"),
            "created_at": param.get("created_at"),
            "updated_at": param.get("updated_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating parameter {param_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_id}/parameters/{param_id}")
async def delete_strategy_parameter(strategy_id: str, param_id: str):
    """
    DELETE /api/v1/strategies/{strategy_id}/parameters/{param_id} - Delete parameter
    """
    try:
        db = _get_db()

        logger.info(f"Deleting parameter {param_id}...")

        # Check parameter exists and belongs to strategy
        existing = db.client.table("strategy_parameters").select("id").eq("id", param_id).eq("strategy_id", strategy_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Parameter not found")

        result = db.client.table("strategy_parameters").delete().eq("id", param_id).execute()

        logger.info(f"✅ Parameter deleted: {param_id}")

        return {"success": True, "message": "Parameter deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting parameter {param_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """
    DELETE /api/v1/strategies/{strategy_id} - Delete strategy and all parameters
    """
    try:
        db = _get_db()

        logger.info(f"Deleting strategy {strategy_id}...")

        # Check strategy exists
        existing = db.client.table("strategies").select("id").eq("id", strategy_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Strategy not found")

        # Delete all parameters first
        db.client.table("strategy_parameters").delete().eq("strategy_id", strategy_id).execute()
        logger.info(f"Deleted all parameters for strategy {strategy_id}")

        # Delete the strategy
        result = db.client.table("strategies").delete().eq("id", strategy_id).execute()

        logger.info(f"✅ Strategy deleted: {strategy_id}")

        return {"success": True, "message": "Strategy and all parameters deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
