# Quantity Precision Flow - Verification

## Problem Fixed
**Double-rounding (or triple-rounding) was occurring:**

### Before Fix:
```
1. AutomationEngine rounds to quantity_precision (ex: 2)
   0.5777 → round(0.5777, 2) = 0.58

2. T212Service rounds to 3 decimals
   0.58 → round(0.58, 3) = 0.58 (OK in this case, but wrong in principle)

3. Trading212Client rounds to 3 decimals AGAIN
   0.58 → round(0.58, 3) = 0.58

Problem: If ISIN had quantity_precision=4, AutomationEngine would send 0.5777,
then T212Service AND Trading212Client would both round it to 3, breaking the logic.
```

### After Fix:
```
1. AutomationEngine loads ISIN.quantity_precision
   quantity_precision = 2 (or whatever is stored)

2. AutomationEngine rounds quantity to that precision
   0.5777 → round(0.5777, 2) = 0.58

3. AutomationEngine rounds price to 3 decimals
   17.326656 → round(17.326656, 3) = 17.327

4. AutomationEngine calls _place_order_with_precision_retry()
   - Passes: quantity=0.58, limit_price=17.327, initial_precision=2

5. _place_order_with_precision_retry() calls T212Service
   - Passes: quantity=0.58, limit_price=17.327 (NO re-rounding)

6. T212Service calls Trading212Client
   - Passes: quantity=0.58, limit_price=17.327 (NO re-rounding)

7. Trading212Client posts to T212 API
   - Sends: {"quantity": 0.58, "limitPrice": 17.327, ...} (AS-IS)

Result: Quantity preserves AutomationEngine's rounding to quantity_precision!
```

## Files Fixed

### 1. `backend/services/t212_service.py`
**Functions:** `place_buy_limit_order()`, `place_sell_limit_order()`

**Before:**
```python
quantity_rounded = round(quantity, 3)  # ← WRONG: re-rounds!
limit_price_rounded = round(limit_price, 3)
```

**After:**
```python
# Quantity is already rounded by AutomationEngine - use as-is
# Only ensure limit_price is properly formatted
limit_price_rounded = round(limit_price, 3)
# quantity passed as-is
```

**Why:** Quantity has already been rounded to ISIN's quantity_precision by AutomationEngine.
Re-rounding would break the precision adaptation logic.

### 2. `backend/api/trading212.py`
**Function:** `place_limit_order()`

**Before:**
```python
quantity_rounded = round(quantity, 3)  # ← WRONG: re-rounds!
limit_price_rounded = round(limit_price, 3)
payload = {..., "quantity": quantity_rounded, ...}
```

**After:**
```python
# Use quantity and limit_price as-is - they're already properly rounded by caller
payload = {..., "quantity": quantity, "limitPrice": limit_price, ...}
```

**Why:** Quantity arrives pre-rounded from T212Service (which got it from AutomationEngine).
Trading212Client should NOT re-round it.

## Flow Diagram (After Fix)

```
AutomationEngine._phase_1_setup_isin()
  ↓
  Load: ISIN.quantity_precision = 2 (example)
  Calculate: buy_quantity = 0.5777
  Round: round(0.5777, 2) = 0.58
  ↓
AutomationEngine._place_order_with_precision_retry()
  ↓
  Call: T212Service.place_buy_limit_order(qty=0.58, ...)
  ↓
T212Service.place_buy_limit_order()
  ↓
  # Does NOT re-round quantity
  Call: Trading212Client.place_limit_order(qty=0.58, ...)
  ↓
Trading212Client.place_limit_order()
  ↓
  # Does NOT re-round quantity
  POST to T212 API: {"quantity": 0.58, ...}
  ↓
T212 API returns:
  - 200 OK: Order created successfully
  - 400: {"error": "invalid quantity precision 1"}
        ↑ AutomationEngine catches this, extracts 1, updates ISIN, retries
```

## Retry Logic (Still Works Correctly)

When T212 API returns `"invalid quantity precision X"` error:

1. `_place_order_with_precision_retry()` detects it
2. Extracts X from error message (e.g., "invalid quantity precision 2" → 2)
3. Updates ISIN in database: `quantity_precision = 2`
4. Rounds quantity to X: `round(0.58, 2) = 0.58` (no change in this example)
5. Retries the order with rounded quantity
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
4. Check order in T212: Should see precision-3 quantity
```

### Test 2: Adaptive Precision
```
1. Create ISIN with quantity_precision=3 (default)
2. T212 API actually requires precision=2 for this ticker
3. Run cycle: AutomationEngine sends qty with 3 decimals
4. T212 API returns: "invalid quantity precision 2"
5. AutomationEngine catches error, updates ISIN: quantity_precision=2
6. AutomationEngine retries: Sends qty with 2 decimals
7. T212 API accepts it (200 OK)
8. Check ISIN in database: quantity_precision should now be 2
9. Next cycle: Will automatically use precision=2 (no more errors)
```

### Test 3: Verify No Double-Rounding
```
Use the test_limit_order_gui.py to test:
1. Send quantity with 4 decimals to T212 API (via GUI)
2. If T212 accepts it: Good, no re-rounding happening
3. If T212 rejects with "invalid quantity precision X": 
   - Means we're sending X decimals (correct behavior)
   - Means we're NOT re-rounding to 3 before sending
```

## Code Quality Notes

- ✅ AutomationEngine is the single source of truth for rounding
- ✅ T212Service and Trading212Client are pure pass-through (no manipulation)
- ✅ Precision adaptation logic is isolated in `_place_order_with_precision_retry()`
- ✅ No data corruption from multiple levels of rounding
- ✅ Clear docstrings explain the contract between layers
- ✅ Each layer trusts that its inputs are correctly formatted by the caller

## Summary

The fix ensures that quantity rounding happens **exactly once**, at the AutomationEngine level,
respecting each ISIN's unique `quantity_precision` requirement. The retry logic can safely
extract the correct precision from API errors and update the database without worrying
about downstream re-rounding interfering.
