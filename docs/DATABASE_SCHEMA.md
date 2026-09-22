# 💾 Database Schema

## Overview

8 core tables in Supabase PostgreSQL:

```
users (1:N) → isins (1:N) → orders
users (1:N) → users ← strategies (1:N) → strategy_parameters
users (1:N) → config
users (1:N) → logs
users (1:N) → app_parameters (1:1 per user)
```

---

## Tables

### 1. **users**
User accounts (authentication + base entity)

```sql
id (UUID, PK)
email (VARCHAR, UNIQUE)
is_admin (BOOLEAN, default: false)
created_at (TIMESTAMP, auto)
```

**RLS:** Each user sees only themselves
**Indexes:** idx_users_email

**Notes:**
- Currently allows any email/password (stub auth)
- Real Supabase Auth JWT will be integrated in Phase 6

---

### 2. **isins**
Securities/assets owned (stocks, ETFs)

```sql
id (UUID, PK)
user_id (UUID, FK → users)
isin (VARCHAR)
ticker (VARCHAR)
name (VARCHAR)
currency (VARCHAR, default: 'EUR')
quantity (DECIMAL)
current_price (DECIMAL)
automation_enabled (BOOLEAN, default: false)
strategy_id (UUID, FK → strategies) [nullable]
quantity_precision (INT, default: 2)  -- decimals for quantity
fields_json (JSONB)  -- Extra T212 API fields
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

UNIQUE(user_id, isin)
```

**RLS:** User sees only their ISINs
**Indexes:** idx_isins_user_id, idx_isins_isin

**Key Fields:**
- `isin` — Standard identifier (e.g., "GB00B4L5Y983")
- `ticker` — Stock ticker (e.g., "VWRL")
- `automation_enabled` — Grid trading active?
- `strategy_id` — Which strategy to use
- `quantity_precision` — Decimal places for T212 API calls
- `fields_json` — Cached T212 API response fields

---

### 3. **strategies**
Trading strategies (define grid parameters)

```sql
id (UUID, PK)
user_id (UUID, FK → users)
name (VARCHAR)
description (VARCHAR)
type (VARCHAR, default: 'grid_trading')  -- grid_trading, rsi, sma_crossover (future)
status (VARCHAR, default: 'enabled')  -- enabled, disabled, paused
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

UNIQUE(user_id, name)
```

**RLS:** User sees only their strategies
**Indexes:** idx_strategies_user_id

**Key Fields:**
- `name` — User-friendly strategy name
- `type` — Currently only 'grid_trading', but extensible
- `status` — Can be disabled without deleting

**Related:** strategy_parameters (1:N relationship)

---

### 4. **strategy_parameters**
Grid trading parameters per position

```sql
id (UUID, PK)
strategy_id (UUID, FK → strategies)
pos (INT, PK/composite)  -- -1 (sell), 0 (hold), +1 (buy)
param1 (DECIMAL)  -- Price adjustment % for position (pos -1 uses param1, pos +1 uses param2)
param2 (DECIMAL)  -- Price adjustment % for position +1 (buy below)
param3 (DECIMAL)  -- Investment/quantity for position -1 (sell)
param4 (DECIMAL)  -- Investment/quantity for position +1 (buy)
param5 to param10 (DECIMAL)  -- Future use
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

PRIMARY KEY(strategy_id, pos)  -- One param per position per strategy
```

**RLS:** Access via strategy (inherited from strategies table)
**Indexes:** idx_strategy_parameters_strategy_id

**Key Concepts:**
- **Position -1 (Sell):** param1 = price adj %, param3 = qty to sell
- **Position 0 (Hold):** No orders
- **Position +1 (Buy):** param2 = price adj %, param4 = qty to buy

**Validation:**
- All strategies must have pos -1, 0, +1 (3 rows per strategy)
- pos values must be exactly -1, 0, 1

**Example:**
```
Strategy "Grid ±1% on VWRL":
  pos: -1, param1: +2.0, param3: 10.0  (Sell 10 @ +2% above market)
  pos:  0, param2:  0.0, param4:  0.0  (Hold)
  pos: +1, param2: -1.0, param4: 10.0  (Buy 10 @ -1% below market)
```

---

### 5. **orders**
Trade order records (BUY/SELL attempts)

```sql
id (UUID, PK)
user_id (UUID, FK → users)
isin_id (UUID, FK → isins)
strategy_id (UUID, FK → strategies)
t212_order_id (VARCHAR)  -- Order ID from T212 API
type (VARCHAR)  -- 'BUY' or 'SELL'
quantity (DECIMAL)
price (DECIMAL)
status (VARCHAR)  -- W (Watch), E (Executed), P (Processed), X (Error), C (Cancelled)
automation_status (VARCHAR) [NEW for Phase 3]  -- Tracks processing state
related_order_id (UUID)  -- Link BUY ↔ SELL in a pair
trades_balance (INT)  -- Counter: how many buys ahead of sells
filled_quantity (DECIMAL)  -- Actual qty filled (if status = E/P)
filled_price (DECIMAL)  -- Actual price filled
commission (DECIMAL)
created_at (TIMESTAMP)
executed_at (TIMESTAMP)  -- When T212 filled it
updated_at (TIMESTAMP)
details_json (JSONB)  -- Extra data (error messages, T212 response, etc)
```

**RLS:** User sees only their orders
**Indexes:** idx_orders_user_id, idx_orders_isin_id, idx_orders_status, idx_orders_created_at

**Key Fields:**
- `status` — Main state (W/E/P/X/C)
- `related_order_id` — Links BUY and SELL in a grid pair
- `trades_balance` — Counter (updated when fills processed)
- `filled_quantity` / `filled_price` — Actual execution data from T212
- `details_json` — Error messages, T212 API responses, etc

**Status Flow:**
```
W (Watch) → E (Executed on T212) → P (Processed by automation) or X (Error)
                                   ↓
                           (or) C (Cancelled)
```

---

### 6. **config**
User trading configuration

```sql
id (UUID, PK)
user_id (UUID, FK → users, UNIQUE)
t212_api_key_encrypted (VARCHAR)  -- Fernet encrypted
t212_api_secret_encrypted (VARCHAR)  -- Fernet encrypted
t212_environment (VARCHAR, default: 'demo')  -- 'demo' or 'live'
updated_at (TIMESTAMP)
```

**RLS:** User sees only their config
**Security:**
- API keys encrypted with Fernet (key in .env)
- Never exposed to frontend
- Only decrypted for T212 API calls

**Key Fields:**
- `t212_environment` — Which T212 server to use (demo for testing)

---

### 7. **logs**
Audit trail and debugging (optional)

```sql
id (UUID, PK)
user_id (UUID, FK → users)
nivel (VARCHAR)  -- INFO, WARNING, ERROR, DEBUG
mensagem (VARCHAR)
detalhes_json (JSONB)
created_at (TIMESTAMP)
```

**RLS:** User sees only their logs
**Indexes:** idx_logs_user_id, idx_logs_nivel, idx_logs_created_at

**When Used:**
- Only if `app_parameters.log_level` = 'MEDIUM' (or higher)
- AutomationEngine logs all DB/API interactions
- Helps with debugging issues

**Example Entry:**
```json
{
  "id": "abc123",
  "user_id": "user456",
  "nivel": "INFO",
  "mensagem": "✅ VWRL BUY order filled",
  "detalhes_json": {
    "isin": "GB00B4L5Y983",
    "qty_filled": 10.5,
    "price_filled": 49.05,
    "t212_order_id": "12345"
  },
  "created_at": "2026-09-22T14:30:45Z"
}
```

---

### 8. **app_parameters**
Global application settings (per-user)

```sql
id (UUID, PK)
user_id (UUID, FK → users, UNIQUE)
scheduler_interval_seconds (INT, default: 15)  -- 5-300 range
automation_enabled (BOOLEAN, default: false)  -- Global ON/OFF for engine
log_level (VARCHAR, default: 'OFF')  -- OFF, LOW, MEDIUM, HIGH
updated_at (TIMESTAMP)
```

**RLS:** User sees only their app parameters
**Special:** One row per user (singleton pattern)

**Key Fields:**
- `scheduler_interval_seconds` — How often to run automation cycle (5-300)
- `automation_enabled` — Global enable/disable for entire engine
- `log_level` — Control logging verbosity (for debugging)

**Constraints:**
- `scheduler_interval_seconds` must be 5-300
- `log_level` must be one of: OFF, LOW, MEDIUM, HIGH

---

## Relationships

```sql
users
  ├─ (1:N) → isins
  │           ├─ strategy_id (FK → strategies)
  │           └─ (1:N) → orders
  │               ├─ isin_id (FK ← ISIN)
  │               ├─ strategy_id (FK ← strategies)
  │               └─ related_order_id (FK ← orders)
  │
  ├─ (1:N) → strategies
  │           └─ (1:N) → strategy_parameters
  │               └─ pos (composite key)
  │
  ├─ (1:1) → config
  ├─ (1:1) → app_parameters
  └─ (1:N) → logs
```

---

## Key Constraints

### Foreign Keys
- `isins.user_id` → `users.id` (ON DELETE CASCADE)
- `isins.strategy_id` → `strategies.id` (ON DELETE SET NULL)
- `orders.user_id` → `users.id` (ON DELETE CASCADE)
- `orders.isin_id` → `isins.id` (ON DELETE CASCADE)
- `orders.strategy_id` → `strategies.id` (ON DELETE SET NULL)
- `strategy_parameters.strategy_id` → `strategies.id` (ON DELETE CASCADE)
- `strategies.user_id` → `users.id` (ON DELETE CASCADE)
- `config.user_id` → `users.id` (ON DELETE CASCADE, UNIQUE)
- `app_parameters.user_id` → `users.id` (ON DELETE CASCADE, UNIQUE)
- `logs.user_id` → `users.id` (ON DELETE CASCADE)

### Unique Constraints
- `users.email`
- `isins` (user_id, isin) — Can't have duplicate ISIN per user
- `strategies` (user_id, name) — Can't have duplicate strategy name per user
- `strategy_parameters` PRIMARY KEY (strategy_id, pos) — One param set per position
- `config.user_id` — One config per user
- `app_parameters.user_id` — One app_params per user

### Check Constraints
- `orders.automation_status` IN ('W', 'E', 'P', 'X', 'C')
- `app_parameters.scheduler_interval_seconds` BETWEEN 5 AND 300
- `app_parameters.log_level` IN ('OFF', 'LOW', 'MEDIUM', 'HIGH')
- `config.t212_environment` IN ('demo', 'live')

---

## Indexes

For performance:

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);

-- ISINs
CREATE INDEX idx_isins_user_id ON isins(user_id);
CREATE INDEX idx_isins_isin ON isins(isin);

-- Strategies
CREATE INDEX idx_strategies_user_id ON strategies(user_id);

-- Strategy Parameters
CREATE INDEX idx_strategy_parameters_strategy_id ON strategy_parameters(strategy_id);

-- Orders
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_isin_id ON orders(isin_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- Logs
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_nivel ON logs(nivel);
CREATE INDEX idx_logs_created_at ON logs(created_at DESC);
```

---

## Data Flow Examples

### Add ISIN and Enable Automation

```
1. User goes to Dashboard, clicks "Add ISIN"
   ↓
2. Frontend: POST /api/v1/isins
   ├─ Create row: isins (isin, ticker, name, quantity, current_price)
   └─ automation_enabled = false (default)
   ↓
3. User selects a strategy and enables automation
   ↓
4. Frontend: PUT /api/v1/isins/{id}
   ├─ Update: strategy_id = selected_strategy_id
   └─ Update: automation_enabled = true
   ↓
5. Next automation cycle (Phase 1)
   ├─ AutomationEngine reads isins where automation_enabled = true
   ├─ Fetches strategy_parameters for strategy_id
   ├─ Creates BUY + SELL orders via T212 API
   ├─ Inserts to orders table (status = 'W')
   └─ Cycle continues
```

### Order Execution Flow

```
Phase 1: Create order
  ↓
orders: status = 'W', type = 'BUY', qty = 10, price = 49
  ↓
Phase 2: T212 fills order
  ↓
orders: status = 'E', filled_qty = 10, filled_price = 49.05
  ↓
Phase 3: Automation processes fill
  ├─ Cancel sibling SELL (if not filled)
  ├─ Update ISIN position (quantity, price)
  ├─ Create new BUY + SELL pair
  └─ orders: status = 'P' (success) or 'X' (error)
```

### Logging Flow

```
app_parameters.log_level = 'OFF' (default)
  → No logging
  ↓
User sets: app_parameters.log_level = 'MEDIUM'
  ↓
Next automation cycle:
  ├─ Phase 1: Logs "Creating grid for VWRL"
  ├─ Phase 2: Logs "Order filled at €49.05"
  └─ Phase 3: Logs "Placing rebalance order"
  ↓
All entries stored in: logs table
```

---

## Queries

### Common Queries

**Find all active ISINs for a user:**
```sql
SELECT * FROM isins 
WHERE user_id = 'user-id' AND automation_enabled = true;
```

**Get all pending orders:**
```sql
SELECT * FROM orders 
WHERE user_id = 'user-id' AND status = 'W'
ORDER BY created_at DESC;
```

**Find filled orders waiting for rebalance:**
```sql
SELECT * FROM orders 
WHERE user_id = 'user-id' AND status = 'E'
ORDER BY created_at ASC;
```

**Get strategy with all parameters:**
```sql
SELECT s.*, sp.pos, sp.param1, sp.param2, sp.param3, sp.param4
FROM strategies s
LEFT JOIN strategy_parameters sp ON s.id = sp.strategy_id
WHERE s.user_id = 'user-id' AND s.id = 'strategy-id'
ORDER BY sp.pos;
```

**Check automation status:**
```sql
SELECT * FROM app_parameters WHERE user_id = 'user-id';
```

**Recent error logs:**
```sql
SELECT * FROM logs
WHERE user_id = 'user-id' AND nivel = 'ERROR'
ORDER BY created_at DESC
LIMIT 10;
```

---

## Performance Notes

- All tables have user_id + proper indexes
- Row-Level Security (RLS) enabled (users see only their own data)
- Typical query response: <100ms
- Order table grows ~1 row per ISIN per cycle (manageable at scale)
- Logs table only populated if log_level=MEDIUM (optional)

---

**Last Updated:** 2026-09-22
**Version:** Phase 4 (Automation Live)
**Next:** Phase 5 enhancements + real auth integration

