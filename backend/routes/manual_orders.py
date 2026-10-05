"""
Manual Orders Routes (Item #22, NEW)

Endpoints for the "Gerir Ordens" screen, reached from the ISIN list. This is
a manual, deliberate action path — NOT part of AutomationEngine, and
deliberately NOT subject to the Item #15/#19 trading limits.

T212 has no "edit order" endpoint, only DELETE (cancel) and POST (create
limit order). An "edit" to an existing pending order is therefore always
executed as cancel-then-create; UI-level "editing" is cosmetic over that.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

from config.settings import settings
from api.trading212 import Trading212Client
from routes.auth import get_current_user
from services import manual_orders_service as mo_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manual-orders", tags=["manual-orders"])

Side = Literal["BUY", "SELL"]


def _get_db():
    from db.supabase_client import get_db
    return get_db()


def _get_t212_client() -> Trading212Client:
    return Trading212Client(
        api_key=settings.T212_API_KEY,
        api_secret=settings.T212_API_SECRET,
        environment=settings.T212_ENVIRONMENT,
    )


def _get_validation_thresholds() -> dict:
    """Reads the mo_* columns from app_parameters (Item #22). Falls back to
    the documented defaults if the row/columns aren't there for any reason,
    so a stale/missing migration degrades safely instead of crashing."""
    defaults = {
        "mo_price_max_variation_pct": 10,
        "mo_price_alert_variation_pct": 1,
        "mo_price_max_interval_bp": 100,
        "mo_amount_max": 100,
        "mo_amount_max_interval_pct": 10,
        "mo_quantity_max": 10,
        "mo_quantity_max_interval_pct": 10,
    }
    try:
        db = _get_db()
        result = db.client.table("app_parameters").select(",".join(defaults.keys())).execute()
        if result.data:
            row = result.data[0]
            return {k: (row.get(k) if row.get(k) is not None else v) for k, v in defaults.items()}
    except Exception as e:
        logger.warning(f"Failed to read manual-orders validation thresholds, using defaults: {e}")
    return defaults


# ===== Schemas =====

class CurrentOrderOut(BaseModel):
    t212_order_id: int
    created_at: str
    side: Side
    price: float
    quantity: float
    variation_pct: float  # vs current_price snapshotted at screen load


class ScreenInitResponse(BaseModel):
    isin: str
    ticker: str
    name: str
    current_price: float
    quantity: float
    portfolio_value: float
    pnl_percent: float
    current_orders: List[CurrentOrderOut]
    quantity_precision: int
    price_precision: int = 2
    validation_thresholds: dict
    last_params: Optional[dict] = None


class OrderEditItem(BaseModel):
    t212_order_id: int
    side: Side  # needed to sign the quantity correctly when recreating the order
    new_price: float = Field(..., gt=0)
    new_quantity: float = Field(..., gt=0)  # always positive; sign resolved from `side`


class ExecuteCurrentOrdersRequest(BaseModel):
    """Apply pending edits/cancellations from the Current Orders list."""
    edits: List[OrderEditItem] = []
    cancels: List[int] = []  # t212_order_id list


class ExecuteResultItem(BaseModel):
    t212_order_id: Optional[int]
    new_t212_order_id: Optional[int] = None
    action: Literal["edited", "cancelled", "created"]
    status: Literal["ok", "error"]
    error: Optional[str] = None


class ExecuteCurrentOrdersResponse(BaseModel):
    created: int
    deleted: int
    errors: int
    results: List[ExecuteResultItem]


class SideParams(BaseModel):
    initial_price: float
    initial_gap_bp: float = Field(..., ge=0)
    price_interval_bp: float = Field(..., ge=0)
    acc_price: Literal["Y", "N"]
    use_amount: bool  # True = use amount zone, False = use quantity zone
    initial_amount: Optional[float] = None
    amount_interval_pct: Optional[float] = None
    acc_amount: Optional[Literal["Y", "N"]] = None
    initial_quantity: Optional[float] = None
    quantity_interval_pct: Optional[float] = None
    acc_quantity: Optional[Literal["Y", "N"]] = None
    number_of_orders: int = Field(..., ge=1, le=50)
    step: int = Field(0, ge=0)  # Zone 4: 0 = disabled (no-op)
    multiplier: float = Field(1.0, gt=0)  # Zone 4: 1.0 = no-op


class GenerateOrdersRequest(BaseModel):
    isin: str
    current_price: float
    quantity_precision: int
    price_precision: int = 2
    sell: SideParams
    buy: SideParams
    confirmed_soft_alerts: bool = False  # true once user confirmed the soft-alert modal


class GeneratedOrder(BaseModel):
    side: Side
    price: float
    quantity: float


class GenerateOrdersResponse(BaseModel):
    hard_errors: List[str] = []
    soft_alerts: List[str] = []
    requires_confirmation: bool = False
    orders: List[GeneratedOrder] = []


class ApplyNewOrdersRequest(BaseModel):
    isin: str
    ticker: str
    new_orders: List[GeneratedOrder]
    quantity_precision: int
    price_precision: int = 2
    confirmed_empty_list: bool = False  # true once user confirmed wiping all current orders


class ApplyNewOrdersResponse(BaseModel):
    requires_empty_confirmation: bool = False
    created: int = 0
    deleted: int = 0
    unchanged: int = 0
    errors: int = 0
    results: List[ExecuteResultItem] = []


class ValidationThresholdsRequest(BaseModel):
    """Request to update the Item #22 validation thresholds. Independent per
    environment (DEMO/PROD each have their own app_parameters row)."""
    mo_price_max_variation_pct: float = Field(..., ge=0)
    mo_price_alert_variation_pct: float = Field(..., ge=0)
    mo_price_max_interval_bp: float = Field(..., ge=0)
    mo_amount_max: float = Field(..., ge=0)
    mo_amount_max_interval_pct: float = Field(..., ge=0)
    mo_quantity_max: float = Field(..., ge=0)
    mo_quantity_max_interval_pct: float = Field(..., ge=0)


def _save_last_manual_order_params(isin: str, sell: "SideParams", buy: "SideParams") -> None:
    """Persists the full Sell+Buy param set used for a successful "GERAR",
    overwriting whatever was saved before (Item #22/#24 — no history kept).
    Best-effort: a failure here must never break the generate response,
    since the generation itself already succeeded and that's what matters
    most to the caller."""
    try:
        db = _get_db()
        db.client.table("isins").update({
            "last_manual_order_params": {"sell": sell.dict(), "buy": buy.dict()},
        }).eq("isin", isin).execute()
    except Exception as e:
        logger.warning(f"Failed to save last manual order params for {isin}: {e}")


# ===== Endpoints =====

@router.get("/config/validation-thresholds")
async def get_validation_thresholds(current_user: dict = Depends(get_current_user)):
    """
    GET /api/v1/manual-orders/config/validation-thresholds

    Used by the ConfigPage (Item #22) to show/edit the 7 validation
    thresholds for the "Gerir Ordens" feature. Independent per environment.
    """
    return _get_validation_thresholds()


@router.put("/config/validation-thresholds")
async def update_validation_thresholds(
    request: ValidationThresholdsRequest, current_user: dict = Depends(get_current_user)
):
    """PUT /api/v1/manual-orders/config/validation-thresholds"""
    try:
        db = _get_db()
        result = db.client.table("app_parameters").select("id").execute()
        if not result.data:
            raise Exception("app_parameters table is empty")
        param_id = result.data[0]["id"]

        update_result = db.client.table("app_parameters").update({
            **request.dict(),
            "updated_at": "now()",
        }).eq("id", param_id).execute()

        if not update_result.data:
            raise Exception("Failed to update app_parameters")

        logger.info(f"✅ Manual Orders validation thresholds updated: {request.dict()}")
        return {"status": "updated", **request.dict()}
    except Exception as e:
        logger.error(f"Erro ao atualizar validation thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{isin}/screen", response_model=ScreenInitResponse)
async def get_screen_data(isin: str, current_user: dict = Depends(get_current_user)):
    """
    GET /api/v1/manual-orders/{isin}/screen

    Loads everything the "Gerir Ordens" screen needs on open: header info
    (from T212 positions — this ISIN MUST already have an open position),
    pending orders for this ISIN (T212 GET /equity/orders, filtered by ISIN,
    sorted SELL-first then price descending), and the validation thresholds
    from app_parameters so the frontend can pre-check without a round trip.

    current_price is the snapshot used for the whole screen session — the
    frontend must NOT refresh it on every keystroke (confirmed product
    decision: "pricing atual" stays fixed from screen load).
    """
    try:
        client = _get_t212_client()
        positions = client.get_positions()
        position = next((p for p in positions if p.get("instrument", {}).get("isin") == isin), None)
        if not position:
            raise HTTPException(status_code=404, detail=f"Nenhuma posição aberta para o ISIN {isin}")

        instrument = position.get("instrument", {})
        current_price = position.get("currentPrice", 0)
        quantity = position.get("quantity", 0)
        avg_paid = position.get("averagePricePaid", 0)
        pnl_percent = ((current_price - avg_paid) / avg_paid * 100) if avg_paid else 0
        price_precision = position.get("_price_precision", 2)

        db = _get_db()
        isin_row = db.client.table("isins").select("quantity_precision, last_manual_order_params").eq("isin", isin).execute()
        quantity_precision = (isin_row.data[0]["quantity_precision"] if isin_row.data else 3)
        last_params = (isin_row.data[0].get("last_manual_order_params") if isin_row.data else None)

        ticker = instrument.get("ticker", "")
        all_orders = client.get_pending_orders()
        isin_orders = [o for o in all_orders if o.get("ticker") == ticker]

        current_orders = []
        for o in isin_orders:
            side = o.get("side", "BUY")
            price = o.get("limitPrice") or 0
            variation_pct = ((price - current_price) / current_price * 100) if current_price else 0
            current_orders.append(CurrentOrderOut(
                t212_order_id=o.get("id"),
                created_at=o.get("createdAt") or "",
                side=side,
                price=price,
                quantity=abs(o.get("quantity", 0)),
                variation_pct=variation_pct,
            ))

        # Sort: SELL first, then price descending within each group
        current_orders.sort(key=lambda o: (0 if o.side == "SELL" else 1, -o.price))

        return ScreenInitResponse(
            isin=isin,
            ticker=ticker,
            name=instrument.get("name", ""),
            current_price=current_price,
            quantity=quantity,
            portfolio_value=current_price * quantity,
            pnl_percent=pnl_percent,
            current_orders=current_orders,
            quantity_precision=quantity_precision,
            price_precision=price_precision,
            validation_thresholds=_get_validation_thresholds(),
            last_params=last_params,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao carregar ecrã de gestão de ordens para {isin}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{isin}/execute-current", response_model=ExecuteCurrentOrdersResponse)
async def execute_current_order_changes(
    isin: str, ticker: str, request: ExecuteCurrentOrdersRequest, current_user: dict = Depends(get_current_user)
):
    """
    POST /api/v1/manual-orders/{isin}/execute-current?ticker=...

    Applies pending edits/cancellations from the Current Orders list.
    - cancels: single DELETE /equity/orders/{id} each.
    - edits: DELETE the old order, then POST a new limit order with the
      edited price/quantity. If the DELETE succeeds but the POST fails, the
      old order is gone and the new one was never created — this is an
      accepted risk (explicit product decision), surfaced via the per-item
      result + the aggregate created/deleted/errors counts in the response.

    NOT subject to Item #15/#19 trading limits by design (manual path).
    """
    client = _get_t212_client()
    results: List[ExecuteResultItem] = []
    created = deleted = errors = 0

    for order_id in request.cancels:
        try:
            client.cancel_order(str(order_id))
            deleted += 1
            results.append(ExecuteResultItem(t212_order_id=order_id, action="cancelled", status="ok"))
        except Exception as e:
            errors += 1
            results.append(ExecuteResultItem(t212_order_id=order_id, action="cancelled", status="error", error=str(e)))

    for edit in request.edits:
        try:
            client.cancel_order(str(edit.t212_order_id))
            deleted += 1
        except Exception as e:
            errors += 1
            results.append(ExecuteResultItem(t212_order_id=edit.t212_order_id, action="edited", status="error", error=f"Falha ao cancelar ordem original: {e}"))
            continue

        try:
            quantity_signed = edit.new_quantity if edit.side == "BUY" else -edit.new_quantity
            new_order = client.place_limit_order(ticker=ticker, quantity=quantity_signed, limit_price=edit.new_price)
            created += 1
            results.append(ExecuteResultItem(
                t212_order_id=edit.t212_order_id,
                new_t212_order_id=new_order.get("id"),
                action="edited",
                status="ok",
            ))
        except Exception as e:
            errors += 1
            results.append(ExecuteResultItem(
                t212_order_id=edit.t212_order_id,
                action="edited",
                status="error",
                error=f"Ordem original cancelada, mas recriação falhou: {e}",
            ))

    logger.info(f"Manual Orders | EXECUTE current orders for {isin}: created={created} deleted={deleted} errors={errors}")
    return ExecuteCurrentOrdersResponse(created=created, deleted=deleted, errors=errors, results=results)


@router.post("/generate", response_model=GenerateOrdersResponse)
async def generate_new_orders(request: GenerateOrdersRequest, current_user: dict = Depends(get_current_user)):
    """
    POST /api/v1/manual-orders/generate

    Generates the "New Orders" list from Sell/Buy parameters, enforcing the
    validation rules (Item #22): only price_max_variation is a hard block;
    all other violations are returned as soft_alerts requiring the caller to
    resubmit with confirmed_soft_alerts=true to actually get `orders` back.
    """
    thresholds = _get_validation_thresholds()

    sell_v = mo_service.validate_side_params(
        "SELL", request.current_price, request.sell.initial_price, request.sell.price_interval_bp,
        request.sell.use_amount, request.sell.initial_amount, request.sell.amount_interval_pct,
        request.sell.initial_quantity, request.sell.quantity_interval_pct, thresholds,
    )
    buy_v = mo_service.validate_side_params(
        "BUY", request.current_price, request.buy.initial_price, request.buy.price_interval_bp,
        request.buy.use_amount, request.buy.initial_amount, request.buy.amount_interval_pct,
        request.buy.initial_quantity, request.buy.quantity_interval_pct, thresholds,
    )

    hard_errors = sell_v["hard_errors"] + buy_v["hard_errors"]
    soft_alerts = sell_v["soft_alerts"] + buy_v["soft_alerts"]

    if hard_errors:
        return GenerateOrdersResponse(hard_errors=hard_errors, soft_alerts=soft_alerts, requires_confirmation=False, orders=[])

    if soft_alerts and not request.confirmed_soft_alerts:
        return GenerateOrdersResponse(hard_errors=[], soft_alerts=soft_alerts, requires_confirmation=True, orders=[])

    sell_orders = mo_service.generate_side_orders(
        "SELL", request.sell.initial_price, request.sell.price_interval_bp, request.sell.acc_price,
        request.sell.use_amount, request.sell.initial_amount, request.sell.amount_interval_pct, request.sell.acc_amount,
        request.sell.initial_quantity, request.sell.quantity_interval_pct, request.sell.acc_quantity,
        request.sell.number_of_orders, request.quantity_precision, request.price_precision,
        request.sell.step, request.sell.multiplier, request.sell.initial_gap_bp,
    )
    buy_orders = mo_service.generate_side_orders(
        "BUY", request.buy.initial_price, request.buy.price_interval_bp, request.buy.acc_price,
        request.buy.use_amount, request.buy.initial_amount, request.buy.amount_interval_pct, request.buy.acc_amount,
        request.buy.initial_quantity, request.buy.quantity_interval_pct, request.buy.acc_quantity,
        request.buy.number_of_orders, request.quantity_precision, request.price_precision,
        request.buy.step, request.buy.multiplier, request.buy.initial_gap_bp,
    )

    all_orders = sell_orders + buy_orders
    all_orders.sort(key=lambda o: (0 if o["side"] == "SELL" else 1, -o["price"]))

    _save_last_manual_order_params(request.isin, request.sell, request.buy)

    return GenerateOrdersResponse(
        hard_errors=[], soft_alerts=[], requires_confirmation=False,
        orders=[GeneratedOrder(**o) for o in all_orders],
    )


@router.post("/{isin}/apply-new", response_model=ApplyNewOrdersResponse)
async def apply_new_orders(isin: str, request: ApplyNewOrdersRequest, current_user: dict = Depends(get_current_user)):
    """
    POST /api/v1/manual-orders/{isin}/apply-new

    Matches the generated New Orders list against the CURRENT real T212
    state (fetched fresh here — not against any locally-pending edits in
    the Current Orders list, which is an independent action/screen mode).

    Match = same side + price (2dp) + quantity (ISIN precision) -> left
    alone. Unmatched current orders are cancelled; unmatched new orders are
    created. If new_orders is empty, this wipes ALL current pending orders
    for the ISIN — requires confirmed_empty_list=true or the endpoint
    returns requires_empty_confirmation=true without doing anything.
    """
    client = _get_t212_client()

    if not request.new_orders and not request.confirmed_empty_list:
        return ApplyNewOrdersResponse(requires_empty_confirmation=True)

    all_orders = client.get_pending_orders()
    isin_orders = [o for o in all_orders if o.get("ticker") == request.ticker]
    current_orders = []
    for o in isin_orders:
        side = o.get("side", "BUY")
        price = o.get("limitPrice") or 0
        current_orders.append({"t212_order_id": o.get("id"), "side": side, "price": price, "quantity": abs(o.get("quantity", 0))})

    match = mo_service.match_new_orders_against_current(
        [o.dict() for o in request.new_orders], current_orders, request.quantity_precision, request.price_precision
    )

    results: List[ExecuteResultItem] = []
    created = deleted = errors = 0

    for co in match["to_cancel"]:
        try:
            client.cancel_order(str(co["t212_order_id"]))
            deleted += 1
            results.append(ExecuteResultItem(t212_order_id=co["t212_order_id"], action="cancelled", status="ok"))
        except Exception as e:
            errors += 1
            results.append(ExecuteResultItem(t212_order_id=co["t212_order_id"], action="cancelled", status="error", error=str(e)))

    for no in match["to_create"]:
        try:
            signed_qty = no["quantity"] if no["side"] == "BUY" else -no["quantity"]
            new_order = client.place_limit_order(ticker=request.ticker, quantity=signed_qty, limit_price=no["price"])
            created += 1
            results.append(ExecuteResultItem(t212_order_id=None, new_t212_order_id=new_order.get("id"), action="created", status="ok"))
        except Exception as e:
            errors += 1
            results.append(ExecuteResultItem(t212_order_id=None, action="created", status="error", error=str(e)))

    logger.info(
        f"Manual Orders | APPLY new orders for {isin}: created={created} deleted={deleted} "
        f"unchanged={len(match['unchanged'])} errors={errors}"
    )
    return ApplyNewOrdersResponse(
        created=created, deleted=deleted, unchanged=len(match["unchanged"]), errors=errors, results=results,
    )
