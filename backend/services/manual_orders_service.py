"""
Manual Orders Service (Item #22, NEW)

Business logic for the "Gerir Ordens" screen: a manual, deliberate path to
edit/cancel pending T212 orders for a single ISIN, and to generate+apply a
new set of orders from a parametric series (Sell/Buy price/amount/quantity
ladders).

Deliberately NOT subject to the Item #15/#19 automation trading limits
(max_buy_order_value, max_sell_order_value, max_daily_spend) — this is a
manual action path, not automation. See db/manual_orders_validation_params.sql
for the separate validation thresholds this feature DOES respect.

T212 has no "edit order" endpoint — only DELETE (cancel) and POST (create).
An "edited" order is therefore always a cancel-then-create pair; a "deleted"
order is a single cancel.
"""

import logging
from typing import Optional, Dict, Any, List, Literal

logger = logging.getLogger(__name__)

Side = Literal["BUY", "SELL"]


# ===== Series generation (Zone 1/2/3 math) =====

def build_series(seed: float, interval: float, acc: str, n: int, direction: int, unit_divisor: float, index_offset: int = 0) -> List[float]:
    """
    Builds a progression of n values from a seed, an interval, and an
    accumulation mode.

    - direction: +1 or -1. For price: +1 for SELL (price rises per order),
      -1 for BUY (price falls per order). For amount/quantity: always +1
      (magnitude only grows), direction is purely a price concept.
    - unit_divisor: 10000 for basis points (price interval), 100 for
      percentage (amount/quantity interval).
    - acc == "Y": compounds on the previous value (geometric-like growth).
    - acc == "N": always applies i * interval against the original seed.
    - index_offset: shifts the starting point of the progression by this
      many steps. Used for price (index_offset=1) so the FIRST generated
      order already has one interval applied from the Initial Price,
      instead of starting exactly at Initial Price. Amount/Quantity always
      use the default index_offset=0 (first order = exactly the Initial
      Amount/Quantity, unaffected by this).

    Example (seed=100, interval=50bp, direction=+1, unit_divisor=10000):
      index_offset=0, Acc=Y -> [100, 100.5, 101.0025, ...]
      index_offset=0, Acc=N -> [100, 100.5, 101.0,    ...]
      index_offset=1, Acc=Y -> [100.5, 101.0025, 101.507..., ...]
      index_offset=1, Acc=N -> [100.5, 101.0,    101.5,      ...]
    """
    if n <= 0:
        return []
    factor = 1 + direction * interval / unit_divisor
    if acc == "Y":
        # values[k] = seed * factor^(index_offset + k)
        values = [seed * (factor ** (index_offset + k)) for k in range(n)]
    else:
        # values[k] = seed * (1 + direction*(index_offset + k)*interval/unit_divisor)
        values = [seed * (1 + direction * (index_offset + k) * interval / unit_divisor) for k in range(n)]
    return values


def generate_side_orders(
    side: Side,
    initial_price: float,
    price_interval_bp: float,
    acc_price: str,
    use_amount: bool,
    initial_amount: Optional[float],
    amount_interval_pct: Optional[float],
    acc_amount: Optional[str],
    initial_quantity: Optional[float],
    quantity_interval_pct: Optional[float],
    acc_quantity: Optional[str],
    number_of_orders: int,
    quantity_precision: int,
    price_precision: int = 2,
) -> List[Dict[str, Any]]:
    """Generates `number_of_orders` {side, price, quantity} dicts for one side (BUY or SELL).

    The price series starts already shifted by one interval from
    Initial Price (index_offset=1) — the first generated order is never
    exactly at Initial Price, it's Initial Price + 1 interval. Amount and
    Quantity series are NOT shifted: the first order's amount/quantity is
    exactly Initial Amount/Initial Quantity.

    Prices are rounded to `price_precision` decimal places — inferred
    per-ISIN from T212's raw currentPrice (see utils/price_precision.py),
    NOT a hardcoded 2dp. Falls back to 2 if the caller doesn't pass one
    (backward-compatible default).
    """
    price_direction = 1 if side == "SELL" else -1
    prices = build_series(initial_price, price_interval_bp, acc_price, number_of_orders, price_direction, 10000, index_offset=1)

    orders = []
    if use_amount:
        amounts = build_series(initial_amount, amount_interval_pct, acc_amount, number_of_orders, 1, 100)
        for i in range(number_of_orders):
            qty = round(amounts[i] / prices[i], quantity_precision)
            orders.append({"side": side, "price": round(prices[i], price_precision), "quantity": qty})
    else:
        quantities = build_series(initial_quantity, quantity_interval_pct, acc_quantity, number_of_orders, 1, 100)
        for i in range(number_of_orders):
            qty = round(quantities[i], quantity_precision)
            orders.append({"side": side, "price": round(prices[i], price_precision), "quantity": qty})
    return orders


# ===== Validation (Zone 4 + app_parameters thresholds) =====

def validate_side_params(
    side: Side,
    current_price: float,
    initial_price: float,
    price_interval_bp: float,
    use_amount: bool,
    initial_amount: Optional[float],
    amount_interval_pct: Optional[float],
    initial_quantity: Optional[float],
    quantity_interval_pct: Optional[float],
    thresholds: Dict[str, float],
) -> Dict[str, List[str]]:
    """
    Returns {"hard_errors": [...], "soft_alerts": [...]}.

    Only price_max_variation_pct is a hard block (prevents generating).
    All other 6 conditions are soft alerts requiring user confirmation.
    Amount/Quantity max checks are against ABSOLUTE ceilings, not variations
    (there's no "current amount" reference, unlike price which has market price).
    """
    hard_errors: List[str] = []
    soft_alerts: List[str] = []

    price_var_pct = abs((initial_price - current_price) / current_price) * 100 if current_price else 0

    if price_var_pct > thresholds["mo_price_max_variation_pct"]:
        hard_errors.append(
            f"[{side}] Initial Price ({initial_price}) varia {price_var_pct:.2f}% face ao preço atual "
            f"— acima do máximo permitido ({thresholds['mo_price_max_variation_pct']}%)."
        )
    elif price_var_pct > thresholds["mo_price_alert_variation_pct"]:
        soft_alerts.append(
            f"[{side}] Initial Price varia {price_var_pct:.2f}% face ao preço atual "
            f"(limite de alerta: {thresholds['mo_price_alert_variation_pct']}%)."
        )

    if price_interval_bp > thresholds["mo_price_max_interval_bp"]:
        soft_alerts.append(
            f"[{side}] Price Interval ({price_interval_bp}bp) acima do máximo recomendado "
            f"({thresholds['mo_price_max_interval_bp']}bp)."
        )

    if use_amount:
        if initial_amount is not None and initial_amount > thresholds["mo_amount_max"]:
            soft_alerts.append(
                f"[{side}] Initial Amount ({initial_amount}) acima do máximo ({thresholds['mo_amount_max']})."
            )
        if amount_interval_pct is not None and amount_interval_pct > thresholds["mo_amount_max_interval_pct"]:
            soft_alerts.append(
                f"[{side}] Amount Interval ({amount_interval_pct}%) acima do máximo "
                f"({thresholds['mo_amount_max_interval_pct']}%)."
            )
    else:
        if initial_quantity is not None and initial_quantity > thresholds["mo_quantity_max"]:
            soft_alerts.append(
                f"[{side}] Initial Quantity ({initial_quantity}) acima do máximo ({thresholds['mo_quantity_max']})."
            )
        if quantity_interval_pct is not None and quantity_interval_pct > thresholds["mo_quantity_max_interval_pct"]:
            soft_alerts.append(
                f"[{side}] Quantity Interval ({quantity_interval_pct}%) acima do máximo "
                f"({thresholds['mo_quantity_max_interval_pct']}%)."
            )

    return {"hard_errors": hard_errors, "soft_alerts": soft_alerts}


# ===== Matching (New Orders vs T212 live state) =====

def match_new_orders_against_current(
    new_orders: List[Dict[str, Any]],
    current_orders: List[Dict[str, Any]],
    quantity_precision: int,
    price_precision: int = 2,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Matches generated New Orders against the CURRENT real T212 state
    (fetched fresh, not against any locally-pending edits in the
    Current Orders list — those are a separate, independent action).

    A current order "survives" (is left alone) if there's an unmatched new
    order with the same side + price (rounded to `price_precision`, the
    per-ISIN inferred decimal count — NOT hardcoded 2dp, since some ISINs
    use more/fewer decimals) + quantity (ISIN precision). Everything else
    in current_orders is cancelled; every unmatched new_order is created.

    Returns {"to_create": [...], "to_cancel": [...], "unchanged": [...]}.
    """
    to_create: List[Dict[str, Any]] = []
    unchanged: List[Dict[str, Any]] = []
    matched_current_ids = set()

    def _key(side: str, price: float, qty: float) -> tuple:
        return (side, round(price, price_precision), round(qty, quantity_precision))

    current_by_key: Dict[tuple, List[Dict[str, Any]]] = {}
    for co in current_orders:
        k = _key(co["side"], co["price"], co["quantity"])
        current_by_key.setdefault(k, []).append(co)

    for no in new_orders:
        k = _key(no["side"], no["price"], no["quantity"])
        candidates = [c for c in current_by_key.get(k, []) if c["t212_order_id"] not in matched_current_ids]
        if candidates:
            match = candidates[0]
            matched_current_ids.add(match["t212_order_id"])
            unchanged.append(match)
        else:
            to_create.append(no)

    to_cancel = [co for co in current_orders if co["t212_order_id"] not in matched_current_ids]

    return {"to_create": to_create, "to_cancel": to_cancel, "unchanged": unchanged}
