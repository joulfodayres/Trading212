# Phase 4 - Automation Engine Implementation Plan

**Status:** Ready for Implementation  
**Date:** 2026-09-20  
**Location:** Scheduler runs on Render backend (same container as Uvicorn)

---

## 📋 Implementation Order

### **Step 1: Database Schema**
- [ ] Create `app_parameters` table (SQL already ready)
- [ ] Add `AppParameters` model to SQLAlchemy

### **Step 2: Core Services**
- [ ] Create `SchedulerService` (manages APScheduler lifecycle)
- [ ] Create `AutomationEngine` (3-phase logic)
- [ ] Create `T212Service` (API wrapper for orders, positions)

### **Step 3: Integration**
- [ ] Add lifespan hooks to `main.py`
- [ ] Update `requirements.txt` with APScheduler
- [ ] Add new imports to models

### **Step 4: API Routes**
- [ ] GET `/api/v1/automation/status` (monitor scheduler)
- [ ] PUT `/api/v1/automation/config/interval` (change scheduler interval)
- [ ] GET `/api/v1/automation/logs` (view recent logs)

### **Step 5: Testing & Deployment**
- [ ] Local testing with debug endpoints
- [ ] Deploy to Render (auto-deploy via git push)
- [ ] Monitor logs for 1 hour

---

## 📁 Files to Create/Modify

```
backend/
├── main.py                          [MODIFY] Add lifespan
├── requirements.txt                 [MODIFY] Add apscheduler
│
├── models/
│   ├── db.py                        [MODIFY] Add AppParameters model
│   └── schemas.py                   [MODIFY] Add AppParametersSchema
│
├── services/                        [NEW FOLDER]
│   ├── __init__.py
│   ├── scheduler.py                 [NEW] SchedulerService
│   ├── automation_engine.py         [NEW] AutomationEngine (3-phase logic)
│   └── t212_service.py              [NEW] T212 API helpers
│
└── routes/
    └── automation.py                [NEW] Status, config, logs endpoints

db/
└── app_parameters_table.sql         [EXISTS] Ready to apply
```

---

## 🔧 Implementation Details

### **Phase 1: Database Schema**

**File:** `db/app_parameters_table.sql` (already created)

Need to:
1. Execute SQL in Supabase
2. Add `AppParameters` SQLAlchemy model
3. Add `AppParametersSchema` Pydantic schema

---

### **Phase 2: SchedulerService**

```python
# backend/services/scheduler.py

Key responsibilities:
- Load scheduler interval from BD at startup
- Start/stop APScheduler
- Add automation_cycle job
- Allow runtime interval updates
- Log scheduler events
- Handle errors gracefully
```

---

### **Phase 3: AutomationEngine**

```python
# backend/services/automation_engine.py

Three phases per cycle:

Phase 1: Initial Setup
├─ SELECT isins WHERE initial_trade=TRUE AND automation_enabled=TRUE
├─ For each ISIN:
│  ├─ Load strategy + strategy_parameters (by trades_balance)
│  ├─ Place BUY limit order (positive qty)
│  ├─ Place SELL limit order (negative qty)
│  ├─ Save both with related_order_id linking
│  └─ Set initial_trade=FALSE

Phase 2: Monitor Orders
├─ SELECT orders WHERE automation_status='W'
├─ For each order:
│  ├─ Poll T212 API for status
│  ├─ Update local DB with T212 response
│  └─ If FILLED → set automation_status='E'

Phase 3: Handle Fills
├─ For each FILLED order:
│  ├─ If BUY:
│  │  ├─ Update ISIN with position data
│  │  ├─ trades_balance -= 1
│  │  ├─ Cancel related SELL order
│  │  └─ Place new BUY/SELL pair
│  │
│  └─ If SELL:
│     ├─ Update ISIN with position data
│     ├─ trades_balance += 1
│     ├─ Cancel related BUY order
│     └─ Place new BUY/SELL pair
```

---

### **Phase 4: T212Service**

Wrapper around `api/trading212.py`:

```python
# backend/services/t212_service.py

Methods needed:
- place_buy_limit_order(ticker, quantity, limit_price)
- place_sell_limit_order(ticker, quantity, limit_price)
- get_pending_order(order_id) → Order details
- cancel_order(order_id)
- get_position(ticker) → Position details
- Error handling + logging
```

---

### **Phase 5: FastAPI Integration**

```python
# backend/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    - Create DB session
    - Create AutomationEngine
    - Create SchedulerService
    - Call scheduler.start()
    
    yield  # App running
    
    # SHUTDOWN
    - Call scheduler.stop()
    - Close DB session

app = FastAPI(lifespan=lifespan)
```

---

### **Phase 6: API Routes**

```python
# backend/routes/automation.py

GET /api/v1/automation/status
  → Returns scheduler status, cycle count, last cycle time

PUT /api/v1/automation/config/interval
  → Update scheduler interval (requires int >= 5)

GET /api/v1/automation/logs
  → Returns last 50 log entries from BD

GET /api/v1/automation/orders/watch
  → Returns all orders with status='W' (Watch)
```

---

## 🎯 Execution Strategy

### **Day 1: Skeleton**
- Create services folder structure
- Add SQLAlchemy model for AppParameters
- Add Pydantic schemas
- Basic SchedulerService (start/stop only)
- Update main.py with lifespan

### **Day 2: Phase 1 & 2**
- Implement AutomationEngine Phase 1 (initial setup)
- Implement AutomationEngine Phase 2 (monitor orders)
- T212Service basic methods
- Local testing

### **Day 3: Phase 3 & Polish**
- Implement AutomationEngine Phase 3 (handle fills)
- Complete T212Service
- Add error handling & logging
- API routes for monitoring

### **Day 4: Testing & Deploy**
- Manual testing locally
- Test SQL execution
- Deploy to Render
- Monitor in production

---

## ⚠️ Critical Implementation Notes

1. **Database Transactions:**
   - Use `with db_session.begin()` for atomic operations
   - Always rollback on error
   - Avoid dirty reads with proper isolation level

2. **T212 Rate Limits:**
   - GET /positions: 1 req/1s
   - GET /orders: 1 req/5s
   - POST /orders: 50 req/1m
   - Respect these in all cycles

3. **Error Handling:**
   - Log ALL errors but continue to next ISIN/order
   - No retries yet (Phase 5)
   - No order cancellations on error (Phase 5)

4. **Concurrency:**
   - Use `max_instances=1` to prevent overlapping cycles
   - Use DB locks (`with_for_update()`) where needed
   - Thread-safe logging

5. **Monitoring:**
   - Log every cycle start/end
   - Log every phase completion
   - Log every error
   - API endpoint to check health

---

## 📊 Expected Behavior

```
Cycle Timeline (15s interval):

t=0s:   Cycle #1 starts
├─ Phase 1: Setup (2s) - Create initial pairs
├─ Phase 2: Monitor (5s) - Poll existing orders
└─ Phase 3: Rebalance (2s) - Handle fills

t=9s:   Cycle #1 complete
        ↓ Wait 6 seconds

t=15s:  Cycle #2 starts
├─ Phase 1: Setup (2s)
├─ Phase 2: Monitor (5s)
└─ Phase 3: Rebalance (2s)

t=24s:  Cycle #2 complete
        ↓ Wait 6 seconds

t=30s:  Cycle #3 starts
...
```

---

## ✅ Success Criteria

- [ ] Scheduler starts without errors
- [ ] Scheduler runs every 15 seconds
- [ ] Cycles complete in <15s
- [ ] No overlapping cycles (max_instances=1)
- [ ] Frontend requests not blocked
- [ ] All orders properly tracked in BD
- [ ] Logs show all phases completing
- [ ] API endpoints work correctly
- [ ] Deployment successful
- [ ] No errors in Render logs (1 hour observation)

---

## 🚀 Ready to Start?

Confirm and I'll begin with Step 1: Database Schema
