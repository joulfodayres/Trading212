# Quantity Precision Flow - Verification

## Problem Fixed
**Double-rounding (or triple-rounding) was occurring for QUANTITIES, and unnecessary rounding for PRICES:**

### Before Fix:
```
QUANTITIES:
1. AutomationEngine rounds to quantity_precision (ex: 2)
   0.5777 → round(0.5777, 2) = 0.58

2. T212Service rounds to 3 decimals
   0.58 → round(0.58, 3) = 0.58 (OK in this case, but wrong in principle)

3. Trading212Client rounds to 3 decimals AGAIN
   0.58 → round(0.58, 3) = 0.58

PRICES:
1. AutomationEngine rounds to 3 decimals
   17.326656 → round(17.326656, 3) = 17.327

2. T212Service rounds to 3 decimals
   17.327 → round(17.327, 3) = 17.327 (no change)

3. Trading212Client rounds to 3 decimals AGAIN
   17.327 → round(17.327, 3) = 17.327 (no change)

Problems: 
- Quantities: Re-rounding breaks precision adaptation when quantity_precision != 3
- Prices: Unnecessary rounding destroys precision from calculations
```

### After Fix:
```
QUANTITIES:
1. AutomationEngine loads ISIN.quantity_precision
   quantity_precision = 2 (or whatever is stored)

2. AutomationEngine rounds quantity to that precision
   0.5777 → round(0.5777, 2) = 0.58

3. AutomationEngine calls _place_order_with_precision_retry()
   - Passes: quantity=0.58

4. T212Service receives and passes as-is
   - No rounding: 0.58 → 0.58

5. Trading212Client receives and passes as-is
   - No rounding: 0.58 → 0.58

6. T212 API receives: {"quantity": 0.58, ...}  ✅ CORRECT!

PRICES:
1. AutomationEngine calculates price
   17.326656 (full precision)

2. AutomationEngine passes as-is (NO rounding)
   17.326656 → 17.326656

3. T212Service passes as-is (NO rounding)
   17.326656 → 17.326656

4. Trading212Client passes as-is (NO rounding)
   17.326656 → 17.326656

5. T212 API receives: {"limitPrice": 17.326656, ...}  ✅ CORRECT!
   (API will handle precision internally)
```

## Files Fixed

### 1. `backend/services/automation_engine.py`
**Functions:** `_phase_1_setup_isin()`, `_phase_3_place_new_pair()`

**Before:**
```python
buy_price_rounded = round(buy_price, 3)      # ← WRONG: unnecessary rounding
sell_price_rounded = round(sell_price, 3)
# ...
await self._place_order_with_precision_retry(
    limit_price=buy_price_rounded,  # ← sends rounded price
)
```

**After:**
```python
# Prices are NOT rounded - sent as-is with full precision
# No price rounding variables created
# ...
await self._place_order_with_precision_retry(
    limit_price=buy_price,  # ← sends as-is, full precision
)
```

**Why:** Prices should be sent with maximum precision. Let T212 API handle any rounding if needed.

### 2. `backend/services/t212_service.py`
**Functions:** `place_buy_limit_order()`, `place_sell_limit_order()`

**Before:**
```python
limit_price_rounded = round(limit_price, 3)  # ← WRONG: re-rounds!
# ...
response = self.client.place_limit_order(
    limit_price=limit_price_rounded,  # ← sends rounded price
)
```

**After:**
```python
# Both quantity and limit_price are already properly formatted by AutomationEngine
# Pass them as-is without any modifications
# No rounding variables created
response = self.client.place_limit_order(
    quantity=quantity,      # ← as-is, pre-rounded to quantity_precision
    limit_price=limit_price # ← as-is, full precision
)
```

**Why:** Quantity has already been rounded to ISIN's quantity_precision by AutomationEngine.
Price should maintain full precision from calculation. No re-rounding needed.

### 3. `backend/api/trading212.py`
**Function:** `place_limit_order()`

**Before:**
```python
quantity_rounded = round(quantity, 3)     # ← WRONG: re-rounds quantity!
limit_price_rounded = round(limit_price, 3)  # ← WRONG: re-rounds price!
payload = {
    "quantity": quantity_rounded,
    "limitPrice": limit_price_rounded,
}
```

**After:**
```python
# Use quantity and limit_price as-is - they're already properly formatted by caller
# No rounding happens here
payload = {
    "quantity": quantity,      # ← as-is
    "limitPrice": limit_price, # ← as-is
}
```

**Why:** Values arrive pre-formatted from T212Service. Trading212Client is a pass-through.

## Flow Diagram (After Fix)

```
AutomationEngine._phase_1_setup_isin()
  ↓
  Load: ISIN.quantity_precision = 2 (example)
  Calculate: buy_quantity = 0.5777, buy_price = 17.326656
  ↓
  Round only quantity: round(0.5777, 2) = 0.58
  Keep price as-is: 17.326656 (full precision)
  ↓
AutomationEngine._place_order_with_precision_retry()
  ↓
  Call: T212Service.place_buy_limit_order(qty=0.58, price=17.326656)
  ↓
T212Service.place_buy_limit_order()
  ↓
  # Does NOT modify quantity or price
  Call: Trading212Client.place_limit_order(qty=0.58, price=17.326656)
  ↓
Trading212Client.place_limit_order()
  ↓
  # Does NOT modify quantity or price
  POST to T212 API: {"quantity": 0.58, "limitPrice": 17.326656, ...}
  ↓
T212 API returns:
  - 200 OK: Order created successfully with full precision
  - 400: {"error": "invalid quantity precision 1"}
        ↑ AutomationEngine catches this, extracts 1, updates ISIN, retries
```

## Retry Logic (Still Works Correctly)

When T212 API returns `"invalid quantity precision X"` error:

1. `_place_order_with_precision_retry()` detects it
2. Extracts X from error message (e.g., "invalid quantity precision 2" → 2)
3. Updates ISIN in database: `quantity_precision = 2`
4. Rounds quantity to X: `round(0.58, 2) = 0.58` (no change in this example)
5. Retries the order with rounded quantity (price unchanged)
6. If succeeds: returns response
7. If fails again: returns None
8. **Next cycle** will use the updated quantity_precision from ISIN

## Testing

To verify this works:

### Test 1: Default Precision (3)
```
1. Create ISIN with quantity_precision=3 (default)
2. Add to automation
3. Run cycle: Should place order with quantity rounded to 3 decimals
4. Price should have full precision from calculation
5. Check order in T212: Should see precision-3 quantity and full-precision price
```

### Test 2: Adaptive Precision with Full Price Precision
```
1. Create ISIN with quantity_precision=3 (default)
2. T212 API actually requires precision=2 for this ticker
3. Run cycle: 
   - AutomationEngine sends qty with 2 decimals (as-is)
   - AutomationEngine sends price with full precision (as-is)
4. T212 API returns: "invalid quantity precision 2"
5. AutomationEngine catches error, updates ISIN: quantity_precision=2
6. AutomationEngine retries: Sends qty with 2 decimals, price with full precision
7. T212 API accepts it (200 OK)
8. Check ISIN in database: quantity_precision should now be 2
9. Next cycle: Will automatically use precision=2 (no more errors)
```

### Test 3: Verify No Double-Rounding of Quantities
```
Use the test_limit_order_gui.py to test:
1. Send quantity with 4 decimals to T212 API (via GUI)
2. If T212 accepts it: Good, no re-rounding happening
3. If T212 rejects with "invalid quantity precision X": 
   - Means we're sending X decimals (correct behavior)
   - Means we're NOT re-rounding to 3 before sending
```

### Test 4: Verify Full Price Precision
```
1. Calculate a price: 17.326656666...
2. AutomationEngine should pass to API as-is
3. T212 API receives full precision (not rounded to 3)
4. Check order details in T212: Price should have full precision, not rounded
```

## Code Quality Notes

- ✅ AutomationEngine is the single source of truth for quantity rounding
- ✅ Prices are never rounded (full precision maintained)
- ✅ T212Service and Trading212Client are pure pass-through (no manipulation)
- ✅ Precision adaptation logic is isolated in `_place_order_with_precision_retry()`
- ✅ No data corruption from multiple levels of rounding
- ✅ Clear docstrings explain the contract between layers
- ✅ Each layer trusts that its inputs are correctly formatted by the caller

## Summary

The fix ensures that:
1. **Quantity rounding happens exactly once**, at the AutomationEngine level, respecting each ISIN's unique `quantity_precision` requirement
2. **Prices are sent with full precision**, no rounding applied, allowing T212 API to handle precision as needed
3. The retry logic can safely extract the correct precision from API errors and update the database without worrying about downstream re-rounding interfering

