# 🔄 Automation Flow - How Grid Trading Works

## Overview

Grid Trading is a **3-phase cycle** that repeats every 15 seconds, 24/7.

```
┌─────────────────────────────────────────────────────┐
│        PHASE 1: SETUP (First time only)             │
│  - For each ISIN with automation enabled:           │
│    - Read strategy parameters                       │
│    - Create BUY order (quantity, price - adj%)      │
│    - Create SELL order (quantity, price + adj%)     │
│    - Mark both with status = W (Watch)              │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│       PHASE 2: MONITOR (Every 15 seconds)           │
│  - Poll T212 API for order status                   │
│  - If order filled:                                 │
│    - Update status: W → E (Executed)                │
│    - Record fill details (qty, price, timestamp)    │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│   PHASE 3: REBALANCE (When E orders detected)       │
│  - For each filled order:                           │
│    - Update ISIN position (quantity, price)         │
│    - Adjust trades_balance counter                  │
│    - Place new order pair (opposite positions)      │
│    - Mark as P (Processed) on success               │
└─────────────────────────────────────────────────────┘
                         ↓
                    (Repeat)
```

---

## Detailed Flow

### PHASE 1: Setup (Initial Grid)

**When:** First time automation is enabled on an ISIN

**What Happens:**
1. AutomationEngine wakes up (scheduler every 15s)
2. Reads all ISINs with `automation_enabled = true`
3. For each ISIN without pending orders:
   - Fetch strategy parameters (pos -1, 0, +1)
   - Read current position from T212 (quantity, current price)
   - **Position -1:** Create **SELL** order
     - Price = current_price + param1 (e.g., +2%)
     - Qty = strategy.param3 (e.g., 10 shares)
   - **Position 0:** Skip (no order)
   - **Position +1:** Create **BUY** order
     - Price = current_price - param2 (e.g., -1%)
     - Qty = strategy.param4 (e.g., 10 shares)
4. Call T212 API: `POST /equity/orders/limit` (BUY + SELL)
5. Save order record in DB:
   - `status = 'W'` (Watch — pending execution)
   - `type = 'BUY'` or `'SELL'`
   - `related_order_id` = link BUY ↔ SELL

**Example:**
```
ISIN: VWRL (currently 10 @ €50 = €500)
Strategy: Buy at -1%, Sell at +2%, Qty 5 each

→ Create BUY order:  5 @ €49.50   (current €50 - 1%)
→ Create SELL order: 5 @ €51.00   (current €50 + 2%)
```

### PHASE 2: Monitor (Poll Order Status)

**When:** Every 15 seconds (continuous)

**What Happens:**
1. Poll T212 API: `GET /equity/orders`
2. For each order in our DB with status 'W':
   - Check if it appears in T212 response as "filled"
   - If YES:
     - Update DB: `status = 'E'` (Executed)
     - Record: filled quantity, fill price, timestamp
3. Continue to next cycle

**No action taken yet** — just monitoring.

### PHASE 3: Rebalance (Handle Fills)

**When:** Next cycle after an order fills (detected in Phase 2)

**What Happens:**

#### Case 1: **Isolated Fill** (Only one side of pair filled)

Example: BUY order filled, SELL still waiting

1. **Update ISIN Position:**
   - Fetch fresh position from T212
   - Update DB: quantity, current price, cost basis
   
2. **Cancel Pending Sibling:**
   - Find linked SELL order (via `related_order_id`)
   - Call T212 API: `DELETE /equity/orders/{order_id}`
   - Mark cancelled order as status 'X' (Error/Cancelled)

3. **Adjust Balance Counter:**
   - If BUY filled: `trades_balance -= 1`  (now we're -1 from target)
   - If SELL filled: `trades_balance += 1` (now we're +1 from target)

4. **Place New Pair:**
   - Recalculate prices based on current market price + strategy params
   - Create new BUY + SELL at new grid level
   - Status 'W' (Watch)

5. **Mark Success:**
   - Original filled order: status = 'P' (Processed)

**Example:**
```
Scenario: BUY @ €49.50 fills, SELL @ €51 still waiting

→ Cancel SELL order on T212
→ Update ISIN: now 15 @ €49.50 (was 10 @ €50)
→ trades_balance = -1 (bought, now below target)
→ Recalculate prices: Current €49.50
   - New SELL @ €50.45 (€49.50 + 2%)
   - New BUY @ €48.50 (€49.50 - 1%)
→ Create new orders
→ Mark original BUY as 'P' (Processed)
```

#### Case 2: **Complete Pair** (Both sides filled between cycles)

Example: Both BUY and SELL executed since last check

1. **Recognize the Pair:**
   - Check if both `order.id` and `order.related_order_id` are in filled list
   - Flag as "complete pair"

2. **Update ISIN Position:**
   - Fetch fresh position from T212
   - Update DB: quantity, current price
   
3. **No Balance Adjustment:**
   - BUY -1 + SELL +1 = 0
   - `trades_balance` stays unchanged
   - **No cancellation needed** (both already filled)

4. **Place New Pair:**
   - Same as isolated case: recalculate prices, create new BUY+SELL at same grid
   - Status 'W'

5. **Mark Success:**
   - Both orders: status = 'P' (Processed)

**Example:**
```
Scenario: Both BUY @ €49.50 AND SELL @ €51 filled

→ No cancellation (both already done)
→ trades_balance unchanged (0 net change)
→ Update ISIN: still 10 @ (weighted average) ≈ €50.25
→ Recalculate prices (based on actual fill prices):
   - New SELL @ €51.26 
   - New BUY @ €49.76
→ Create new orders at same grid level
→ Mark both orders as 'P' (Processed)
```

---

## Order Status Lifecycle

```
                    ┌─── P ───┐
                    │         │
                    ↓         ↓
(Not created) → W → E → C
     (Pending)   (Exec) (Cancel)

       Processed↑  Error↑
            (P)    (X)
```

**Statuses:**
- **W** = Watch (order placed, waiting for execution on T212)
- **E** = Executed (order filled on T212, not yet processed by automation)
- **P** = Processed (automation handled the fill, created rebalance pair)
- **X** = Error (something went wrong, manual review needed)
- **C** = Cancelled (by automation when sibling filled first)

**Transitions:**
- W → E (Phase 2: T212 notifies execution)
- E → P (Phase 3: automation processed and created rebalance)
- E → X (Phase 3: exception during processing)
- W → C (Phase 3: cancellation of sibling)

---

## Configuration

### Strategy Parameters

Each strategy has parameters per position:

| Position | Meaning | Example Params |
|----------|---------|-----------------|
| **-1** (Sell) | Orders **above** market | param1 = +2%, param3 = qty 10 |
| **0** (Hold) | No orders | param2 = 0%, param4 = 0 |
| **+1** (Buy) | Orders **below** market | param2 = -1%, param4 = qty 10 |

### Scheduler Configuration

**Cycle Interval:** Configurable (5-300 seconds, default 15s)
- Can adjust in Config tab
- Changes take effect next cycle
- Does NOT affect running orders

**Log Level:** Controls how much detail is logged
- `OFF` — No logging (default)
- `LOW` — Basic operation only
- `MEDIUM` — All DB/API interactions (for debugging)
- `HIGH` — Reserved for future

---

## Example: Full Cycle Timeline

```
T+0s:   Cycle starts
        ├─ Phase 1: Check ISINs, find VWRL automation_enabled
        ├─ Create BUY @ €49 (10 qty)
        ├─ Create SELL @ €51 (10 qty)
        └─ Status: W (Watch)

T+1s to T+14s:  (Waiting for T212 execution)
        └─ T212 market executes trades
           BUY fills @ €49.05
           SELL still open

T+15s:  Next cycle starts
        ├─ Phase 2: Poll T212
        ├─ BUY filled (€49.05) → Update status: W → E
        ├─ SELL still pending
        └─ Mark for Phase 3 processing

T+30s:  Next cycle starts
        ├─ Phase 3: Handle filled orders
        ├─ Isolated fill detected (BUY only)
        ├─ Cancel pending SELL
        ├─ Update ISIN: 15 qty @ €49.05
        ├─ trades_balance = -1
        ├─ Create new BUY @ €48.05 (€49.05 - 1%)
        ├─ Create new SELL @ €50.05 (€49.05 + 2%)
        ├─ Mark original BUY: status = P (Processed)
        └─ Status: W (new pair watching)

T+31s to T+44s: (Waiting for execution)

T+45s:  Cycle continues...
        └─ (Repeat: monitor → rebalance → new orders)
```

---

## Key Concepts

### trades_balance Counter
Tracks how many "BUY fills ahead of SELL fills" have occurred.
- `trades_balance = 0` → balanced (equal buys and sells)
- `trades_balance = -1` → we're below target (need to sell)
- `trades_balance = +1` → we're above target (need to buy)

When rebalancing:
- **Isolated BUY fill:** `trades_balance -= 1` (go more negative)
- **Isolated SELL fill:** `trades_balance += 1` (go more positive)
- **Complete pair:** No change (equal buy + sell)

### related_order_id
Links BUY and SELL orders in a pair:
- When placing pair: BUY.related_order_id = SELL.id
- When pair fills: Can identify which orders belong together
- Used for cancelling sibling when one fills

### Quantity Precision
T212 API requires quantities with exact decimal places per ISIN:
- VWRL: 2 decimals (10.50 shares)
- AAPL: 0 decimals (10 shares)
- MSFT: 2 decimals (5.75 shares)

AutomationEngine:
1. Tries to place order with calculated qty
2. If "invalid quantity precision" error → retry with adjusted decimal places
3. Stores correct precision in cache for next time

---

## Performance & Limits

### Scheduler
- **Interval:** 15 seconds (configurable)
- **Execution time:** 7-10 seconds per cycle
- **Overlap prevention:** Max 1 concurrent instance (thread-safe)
- **Uptime:** 24/7 (auto-restart if crashes)

### T212 API Rate Limits
- 1 req/second for most endpoints
- 50 reqs/minute for order execution
- **Strategy:** Respectful polling (not hammering API)

### Database
- Order records: ~1 per ISIN per cycle (grows slowly)
- Logs: Only if log_level = MEDIUM (optional)
- Performance: <100ms per query

---

## Monitoring & Debugging

### Check if Automation is Running
1. Go to Config tab
2. Set Log Level to **MEDIUM**
3. Click **"Run Cycle Once"** in sidebar
4. Open browser console (F12)
5. Look for logs: `[AutomationEngine]`, `[Phase 1]`, etc.

### View Full Logs (Database)
```sql
-- Check recent logs (if log_level = MEDIUM)
SELECT * FROM logs 
WHERE user_id = (SELECT id FROM users WHERE email = 'your@email.com')
ORDER BY created_at DESC 
LIMIT 50;

-- Check orders status
SELECT id, type, status, isin_id, created_at 
FROM orders 
ORDER BY created_at DESC 
LIMIT 20;
```

### Common Issues

**Q: Orders created but never fill**
- Check T212 account manually — order might be there but at wrong price
- Verify T212 price vs strategy price calculation
- Check market hours (markets may be closed)

**Q: "Phase 3 errors" (status X)**
- Check backend logs: `Log Level = MEDIUM`
- May be quantity precision issue → see `DECIMAL_PLACES_TESTER_README.md`

**Q: Same price orders not updating**
- Grid might have converged (new price = old price)
- Normal behavior, orders stay at same price until market moves

---

**Last Updated:** 2026-09-22
**Version:** Phase 4 Complete (Automation Live)
**Next:** Phase 5 items + enhanced monitoring

