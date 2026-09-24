# 📋 Trading 212 Bot - Backlog (Phase 5)

## ✅ Completed (Phase 5)

### 1. ✅ Strategy Management UI + Parameters CRUD
**Status:** DONE (Commit `4bf858f`)
**What was done:**
- ✅ List view: name, description, status only
- ✅ Detail view: edit name, description, status, investment, timestamps
- ✅ Parameter editing: separate view accessible from detail
- ✅ Full CRUD for parameters (pos, param1-param10)
- ✅ Strategy validation (requires pos -1, 0, 1)
- ✅ Status bug fixed (enabled now shows correctly 🟢/🔴)

---

### 2. ✅ Global Automation Toggle
**Status:** DONE (Commit `84d32ff`)
**What was done:**
- ✅ Sidebar toggle for ON/OFF automation
- ✅ Confirmation dialog before enable/disable
- ✅ Status indicator (🟢 Active / 🔴 Inactive)
- ✅ Auto-refresh every 30s
- ✅ Backend endpoints: PUT /api/v1/automation/enable/disable

---

### 3. ✅ Automation Dialog with Strategy Selection
**Status:** DONE (Commit `9f2d7a2`)
**What was done:**
- ✅ Dialog to select strategy + confirm automation
- ✅ Edit mode for ISINs with automation already enabled
- ✅ Shows strategy info before enabling
- ✅ Removed initial_investment from ISIN dialog (belongs in strategy)

---

### 4. ✅ ConfigPage Refactor
**Status:** DONE (Commit `7d1f08d`)
**What was done:**
- ✅ Removed "Estratégia" tab
- ✅ Removed "Gestão de Risco" tab
- ✅ Renamed "Trading 212" → "Geral"
- ✅ Added scheduler interval editor (5-300s)
- ✅ Save/update via PUT /api/v1/automation/config/interval

---

### 5. ✅ Frontend Translation to English
**Status:** DONE (Commit `1374333`)
**What was done:**
- ✅ All pages translated (StrategiesPage, ConfigPage, DashboardPage, etc)
- ✅ All components translated (Sidebar, ISINTable, etc)
- ✅ All buttons, labels, placeholders in English
- ✅ Maintained code structure and functionality

---

### 6. ✅ Database Cleanup
**Status:** DONE (Commit `6b7fbbb`)
**What was done:**
- ✅ Removed unused `max_positions_per_isin` column
- ✅ Removed unused `log_level` column
- ✅ Simplified app_parameters schema
- ✅ Created migration script for Supabase

---

### 7. ✅ Knowledge Base + Documentation
**Status:** DONE (Commits `40b0458`, `6b8f638`, `c244880`, `51b592e`, `67afc6a`)
**What was done:**
- ✅ 7 comprehensive documentation files (2,947 lines)
- ✅ KNOWLEDGE_BASE.md - Project overview
- ✅ API_REFERENCE.md - All 14 endpoints documented
- ✅ CODE_EXAMPLES.md - 25+ code snippets
- ✅ DEVELOPMENT.md - Setup & workflows
- ✅ TROUBLESHOOTING.md - Issue solving
- ✅ QUICK_REFERENCE.md - Quick lookup
- ✅ README.md - Navigation guide
- ✅ HOW_TO_UPLOAD_KNOWLEDGE_BASE.md - Upload instructions

---

## ⏳ TODO (Phase 5 - Remaining)

### Item #12: Enhanced Login Security & Authentication (NEW)
**Estimated:** 6-8 hours
**Priority:** HIGH (Security-critical)
**Scope:** Single-user app (personal trading account). Protect: (a) T212 API access (critical), (b) Supabase data (important)

**Functional Design (Brainstormed & Finalized):**

#### Login Flow
- Email + Password (Supabase Auth — already integrated ✅)
- **MFA/TOTP mandatory** (Google Authenticator, Authy, etc.)
- No registo público (account created manually, once)
- Remove dev backdoor (`teste@trading212.com` entry point)

#### Brute Force Protection
- **Atraso progressivo por IP** (NOT account lockout):
  - 1ª falha: 0s | 2ª: 2s | 3ª: 4s | 4ª: 8s ... (exponencial)
  - Configurable teto: `LOGIN_DELAY_MAX_MINUTES` (env var, default 15 min)
  - Reset after successful login
  - Advantage: blocks attackers without blocking legitimate user if on same IP
  
#### Trusted Devices
- Mark browser/device as "trusted" after successful login + MFA
- Configurable duration: `TRUSTED_DEVICE_DAYS` (env var, default 30)
- Value 0 = always ask for MFA (option for maximum security)
- Trusted devices skip atraso progression on this IP

#### Session Management
- JWT token: strong secret (not hardcoded), 24h expiration
- Refresh token: to extend sessions without re-entering password
- Logout button: invalidates token immediately
- **Killswitch** endpoint: terminate all active sessions (emergency)
- Token storage: `httpOnly` cookie (not `localStorage` — protects vs XSS)

#### Logging & Alerts
- Log all login attempts (successful + failed): IP, email, timestamp, device
- After 5 failed attempts on same IP: send email alert to user
- Alert includes: timestamp, IP origin, attempts count
- User can then act (change password, terminate all sessions, etc.)

#### Environment Variables (Configurable)
```
LOGIN_DELAY_MAX_MINUTES=15        # Teto do atraso (1-60)
TRUSTED_DEVICE_DAYS=30            # Duração do "trusted" (0-90, 0=always MFA)
JWT_SECRET_KEY=<strong-random>    # NEVER in docs, only in .env
JWT_EXPIRATION_HOURS=24           # Token validity
FASTAPI_ENV=production            # Remove dev mode bypass
```

#### DEMO vs PROD
- Same login rules in both environments
- Separate passwords: demo_user@trading212.com vs prod_user@trading212.com (or single email, different password)
- Separate MFA: different Authenticator entries for each environment
- Each environment has its own JWT secret (via separate .env files)
- Allows testing security mechanisms in DEMO before trusting PROD

#### Deliverables
- ✅ Remove public registration + dev backdoor
- ✅ Implement MFA/TOTP (Supabase Auth native support)
- ✅ Atraso progressivo por IP with configurable max
- ✅ Trusted devices (cookie-based tracking)
- ✅ Revogable sessions + killswitch endpoint
- ✅ Strong JWT secret + short expiry + refresh token
- ✅ Login attempt logging + email alerts
- ✅ httpOnly cookie storage (no localStorage)
- ✅ Environment variables for all tuning
- ✅ Same rules DEMO/PROD, independent credentials

#### Dependencies
- [ ] Supabase Auth native TOTP support (already available ✅)
- [ ] Backend logging table for login attempts
- [ ] Email service for alerts (Supabase email or SendGrid)
- [ ] Device fingerprinting/tracking (browser cookies)
- [ ] Refresh token mechanism in JWT flow

#### Testing Checklist (DEMO first, then replicate in PROD)
- [ ] MFA required: can't login without code from phone
- [ ] Atraso progressivo: 5 wrong attempts slow down the 6th
- [ ] Trusted device: after 1st successful login+MFA, 2nd login skips code
- [ ] Killswitch: logout all sessions works from any device
- [ ] Email alert: received after 5 failed attempts
- [ ] IP isolation: same IP blocked doesn't block different IP
- [ ] JWT secret strong: verify not in docs, random in .env

**Impact:** Secure the door to your trading account. MFA + atraso block brute-force. Single-user design simplifies (no lockout DoS risk). Testable in DEMO first.

---

### Item #13: Dynamic Grid Strategy - Variable Delta Intervals (NEW)
**Estimated:** 8-10 hours
**Priority:** MEDIUM (Feature enhancement)
**Description:**
- Implement new strategy type: "Dynamic Grid" with varying BUY/SELL deltas
- Current grid: Fixed delta every cycle (e.g., always buy at -1%, always sell at +2%)
- New feature: **Adjust delta every N days** based on market conditions
  - Example: Week 1 buy at -0.5%, sell at +1.5% (tight grid, more trades)
  - Example: Week 2 buy at -1%, sell at +2% (normal grid)
  - Example: Week 3 buy at -2%, sell at +3% (wide grid, fewer trades)
- Support multiple delta "schedules" per strategy
- Allow user to define: delta values, time intervals (days), cycling pattern

**Current State (Fixed Grid):**
```
Strategy: Grid ±1% on VWRL
Position -1: SELL @ +2% (fixed)
Position +1: BUY @ -1% (fixed)
↓
Every cycle uses SAME deltas
↓
No adaptation to market volatility
```

**Proposed State (Dynamic Grid):**
```
Strategy: Dynamic Grid on VWRL
Schedule A (Days 1-7): BUY @ -0.5%, SELL @ +1.5%
Schedule B (Days 8-14): BUY @ -1%, SELL @ +2%
Schedule C (Days 15-21): BUY @ -2%, SELL @ +3%
↓
Cycle 1-168 cycles: Use Schedule A
Cycle 169-336: Use Schedule B
Cycle 337+: Use Schedule C
↓
Adapts to market conditions over time
```

**Detailed Requirements:**

1. **Database Changes:**
   - Add column `strategy_type` to strategies table (grid_trading vs dynamic_grid)
   - Create new table `strategy_delta_schedules`:
     ```
     id (UUID, PK)
     strategy_id (UUID, FK → strategies)
     schedule_name (VARCHAR) — e.g., "Tight", "Normal", "Wide"
     day_start (INT) — Which day this schedule starts (1-indexed)
     day_end (INT) — Which day this schedule ends
     param1_delta (DECIMAL) — Delta % for SELL (position -1)
     param2_delta (DECIMAL) — Delta % for BUY (position +1)
     created_at (TIMESTAMP)
     ```

2. **UI Changes (Frontend):**
   - Strategy creation: Radio buttons: "Fixed Grid" vs "Dynamic Grid"
   - If "Dynamic Grid" selected:
     - Input: "Cycle interval in days" (e.g., 7 days per schedule)
     - Table to add multiple delta schedules:
       - Schedule name (Tight, Normal, Wide, etc)
       - Day range (1-7, 8-14, etc)
       - BUY delta % and SELL delta %
       - Add/Remove/Edit rows
   - Parameter section: Shows current active schedule based on elapsed days
   - Automation preview: Shows schedule that will be used next

3. **AutomationEngine Changes (Backend):**
   - New method: `_get_current_delta_schedule(strategy)`:
     - Calculate days elapsed since strategy creation
     - Determine which schedule is active based on day_start/day_end
     - Return current delta values
   - Modify Phase 1 (Setup):
     - Instead of using fixed param1/param2
     - Call `_get_current_delta_schedule()` to get current deltas
     - Use those for order price calculation
   - Add logging: Track which schedule is active each cycle

4. **Grid Trading Strategy Enhancement:**
   - Current fixed grid: 0% complexity, always same prices
   - New dynamic grid: Adds market adaptation capability
   - Helps capture different market regimes:
     - Low volatility weeks: tight delta (more frequent trades, smaller profits)
     - High volatility weeks: wide delta (fewer trades, larger profits per trade)

5. **Example Use Cases:**
   - **Volatility Adapting Grid:**
     ```
     Week 1: Tight (±1%) - Capture sideways market
     Week 2: Normal (±2%) - Standard market
     Week 3: Wide (±5%) - Prepare for volatility
     Repeat 3-week cycle
     ```
   - **Profit Taking Grid:**
     ```
     Month 1: Tight (±0.5%) - Quick profits, short hold times
     Month 2: Normal (±1.5%) - Balanced
     Month 3: Wide (±3%) - Let winners run longer
     ```
   - **Cost Averaging Grid:**
     ```
     Week 1: Wide (buy/sell far apart) - Initial positions
     Week 2-3: Tighter - Average into position
     Week 4+: Wide again - Unwind position
     ```

**Deliverables:**
- ✅ New strategy type: "Dynamic Grid"
- ✅ Delta schedule management UI (CRUD)
- ✅ Backend logic to calculate current schedule
- ✅ AutomationEngine integration (Phase 1 uses dynamic deltas)
- ✅ Audit trail: Track which schedule was active for each order
- ✅ Example strategy templates (3-4 pre-built patterns)

**Dependencies:**
- [ ] Database schema update + migration
- [ ] New API endpoints: CRUD delta schedules
- [ ] Frontend: Strategy type selector + schedule table
- [ ] Backend: Schedule calculation logic
- [ ] Testing: Verify correct schedule selection over multiple days

**Testing Scenarios:**
1. Create dynamic grid with 7-day schedules
2. Run automation for 21 cycles (simulating 3 weeks)
3. Verify orders use different deltas each week
4. Check audit trail shows correct schedules were applied
5. Verify UI shows current + next schedule

**Impact:**
- Opens new trading strategy possibilities (market adaptation)
- Enables sophisticated grid strategies (not just fixed)
- Allows experimentation with different delta patterns
- Foundation for future: AI-powered delta optimization

---

### Item #14: Dashboard Analytics & Statistics Widgets (NEW)
**Estimated:** 10-12 hours
**Priority:** HIGH (Core dashboard feature)
**Description:**
- Add real-time analytics widgets to main dashboard
- Track automation performance metrics over time
- Enable time-period filtering (day/week/month/year)
- Provide insights into trading activity and profitability

**Widget #1: Automated Orders Executed**
- Count of orders automatically executed by automation engine
- Filter by time period: Today | Week | Month | Year
- Break down by: ISIN, Strategy, BUY vs SELL
- Displays:
  - Total orders: 24
  - BUY orders: 12 (50%)
  - SELL orders: 12 (50%)
  - Success rate: 100% (24/24 executed without errors)
  - Failed orders: 0

**Widget #2: P&L (Profit & Loss)**
- Calculate realized P&L from executed trades
- Filter by time period: Today | Week | Month | Year
- Display:
  - Total P&L: €125.50
  - P&L %: +2.3%
  - Winning trades: 18
  - Losing trades: 6
  - Win rate: 75%
  - Avg profit per win: €7.50
  - Avg loss per loss: €-4.20
- Show trend: 📈 (up), 📉 (down), ➡️ (flat)

**Widget #3: Automation Cycles Executed**
- Count of complete automation cycles (Phase 1→2→3)
- Filter by time period: Today | Week | Month | Year
- Display:
  - Total cycles: 96 (every 15s for 24h)
  - Successful cycles: 95 (98.96%)
  - Failed cycles: 1 (1.04%)
  - Avg cycle duration: 8.5s
  - Fastest cycle: 6.2s
  - Slowest cycle: 12.1s

**Data Model Changes:**

1. **New Table: `cycle_executions`** (for tracking cycles)
   ```
   id (UUID, PK)
   user_id (UUID, FK → users)
   cycle_number (INT)
   started_at (TIMESTAMP)
   completed_at (TIMESTAMP)
   duration_ms (INT)
   phase_1_duration (INT)  -- time for Phase 1
   phase_2_duration (INT)  -- time for Phase 2
   phase_3_duration (INT)  -- time for Phase 3
   orders_processed (INT)  -- how many orders in this cycle
   status (VARCHAR)  -- SUCCESS, PARTIAL, ERROR
   details_json (JSONB)  -- Error details if failed
   ```

2. **New Table: `trade_executions`** (for P&L calculation)
   ```
   id (UUID, PK)
   user_id (UUID, FK → users)
   order_id (UUID, FK → orders)
   isin_id (UUID, FK → isins)
   type (VARCHAR)  -- BUY, SELL
   entry_price (DECIMAL)
   entry_quantity (DECIMAL)
   entry_timestamp (TIMESTAMP)
   exit_price (DECIMAL)  -- populated when pair closes
   exit_quantity (DECIMAL)
   exit_timestamp (TIMESTAMP)
   pnl_gross (DECIMAL)  -- (exit_price - entry_price) * quantity
   pnl_net (DECIMAL)  -- gross - fees/commissions
   pnl_percent (DECIMAL)  -- pnl_net / (entry_price * quantity)
   fees_paid (DECIMAL)
   status (VARCHAR)  -- OPEN, CLOSED, CANCELLED
   ```

3. **Enhancements to `orders` table:**
   - Add `cycle_execution_id` (link to cycle_executions)
   - Add `entry_timestamp`, `exit_timestamp` (precise timing)
   - Add `fees` column (commission/spread)

4. **Query Examples:**
   ```sql
   -- Orders executed today
   SELECT COUNT(*) FROM orders 
   WHERE user_id = 'user' AND status IN ('P', 'E')
   AND DATE(executed_at) = CURDATE();

   -- P&L for this month
   SELECT 
     SUM((exit_price - entry_price) * quantity) as pnl,
     COUNT(*) as trade_count,
     SUM(CASE WHEN pnl_net > 0 THEN 1 ELSE 0 END) as winners,
     SUM(CASE WHEN pnl_net <= 0 THEN 1 ELSE 0 END) as losers
   FROM trade_executions
   WHERE user_id = 'user' AND status = 'CLOSED'
   AND MONTH(exit_timestamp) = MONTH(NOW());

   -- Cycles executed this week
   SELECT COUNT(*) FROM cycle_executions
   WHERE user_id = 'user'
   AND completed_at >= NOW() - INTERVAL 7 DAY
   AND status = 'SUCCESS';
   ```

**Frontend Implementation:**

1. **Dashboard Layout Changes:**
   - Add new section below portfolio table: "Automation Performance"
   - 3-column grid of metric cards:
     - [Orders Card] | [P&L Card] | [Cycles Card]
   - Each card has:
     - Title + big number (e.g., "24 Orders")
     - Sparkline chart (trend over time)
     - Time filter buttons: [Today] [Week] [Month] [Year]
     - Secondary metrics below
     - Color coding: 🟢 green if positive, 🔴 red if negative

2. **Component: `MetricCard.tsx`**
   ```
   Props:
   - title: string
   - value: number
   - unit: string (optional)
   - trend: 'up' | 'down' | 'flat'
   - secondaryMetrics: {label, value}[]
   - selectedPeriod: 'day' | 'week' | 'month' | 'year'
   - onPeriodChange: (period) => void
   - isLoading: boolean
   - sparklineData: [timestamp, value][]
   ```

3. **Hook: `useAutomationMetrics.ts`**
   ```
   - Fetches metrics from backend
   - Caches results (refresh every 30s)
   - Handles time period changes
   - Returns loading/error states
   ```

4. **New Endpoints:**
   - `GET /api/v1/metrics/orders?period=day|week|month|year`
   - `GET /api/v1/metrics/pnl?period=day|week|month|year`
   - `GET /api/v1/metrics/cycles?period=day|week|month|year`
   - Each returns:
     ```json
     {
       "value": 24,
       "trend": "up",
       "breakdowns": {...},
       "sparkline": [[timestamp, value], ...]
     }
     ```

**Backend Implementation:**

1. **New Service: `MetricsService`** (`backend/services/metrics_service.py`)
   ```python
   class MetricsService:
     async def get_orders_executed(period: str) -> dict
     async def get_pnl(period: str) -> dict
     async def get_cycles_executed(period: str) -> dict
     async def calculate_pnl_pair(buy_order, sell_order) -> dict
   ```

2. **New Routes: `backend/routes/metrics.py`**
   ```python
   @router.get("/metrics/orders")
   @router.get("/metrics/pnl")
   @router.get("/metrics/cycles")
   ```

3. **AutomationEngine Integration:**
   - After each cycle, log to `cycle_executions` table
   - When orders pair completes, calculate P&L and log to `trade_executions`
   - Track cycle duration + phase durations

**Testing:**

1. Unit tests for P&L calculations
2. Integration tests for metrics endpoints
3. Frontend tests for metric card rendering + period changes
4. E2E: Run automation, verify metrics update correctly

**Example Dashboard with Metrics:**
```
┌─ Trading 212 Bot Dashboard ─────────────────────────────────┐
│                                                              │
│ [Portfolio Table with ISINs]                                │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ISIN | Qty | Price | Automation | Strategy             │  │
│ │ VWRL | 10  | €50   | 🟢 ON      | Grid ±1%            │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ Automation Performance (Week) ──────────────────────────┐ │
│ ├──────────┬──────────────┬───────────────────────────────┤ │
│ │ Orders   │ P&L          │ Cycles                        │ │
│ │ Executed │ (Auto)       │ Executed                      │ │
│ ├──────────┼──────────────┼───────────────────────────────┤ │
│ │ 📊 145   │ 📈 €2,345.67 │ ⚙️ 672                       │ │
│ │ +12% WoW │ +8.5% trend  │ 99.1% success rate           │ │
│ │          │              │                               │ │
│ │ BUY: 73  │ Wins: 124    │ Avg cycle: 8.3s              │ │
│ │ SELL: 72 │ Losses: 21   │ Fastest: 6.1s                │ │
│ │          │ Win rate:86% │ Slowest: 12.5s               │ │
│ │ [T][W][M][Y] │ [T][W][M][Y] │ [T][W][M][Y]            │ │
│ └──────────┴──────────────┴───────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Deliverables:**
- ✅ 3 new metric widgets on dashboard
- ✅ Time period filtering (Day/Week/Month/Year)
- ✅ P&L calculation engine
- ✅ Cycle execution tracking
- ✅ Backend metrics endpoints
- ✅ Frontend components + responsive design
- ✅ Real-time updates every 30s
- ✅ Historical sparkline charts

**Dependencies:**
- [ ] Database schema changes (3 new/enhanced tables)
- [ ] Cycle execution logging in AutomationEngine
- [ ] P&L calculation logic
- [ ] Recharts for sparklines (already included)
- [ ] Backend metrics service + routes
- [ ] Frontend metric card components

**Impact:**
- Provides visibility into automation performance
- Enables data-driven strategy refinement
- Builds confidence in automation (show it's working)
- Critical for production dashboard (users need metrics)
- Foundation for alerts, notifications, advanced analytics

---

### Item #10: Cybersecurity Testing & Penetration Testing
**Estimated:** 8-12 hours
**Description:**
- Comprehensive security audit of the entire application
- Penetration testing (try to break in, escalate privileges, steal data)
- Vulnerability scanning (OWASP Top 10, dependency check)
- Authentication/authorization testing
- API endpoint security (rate limiting, input validation, SQL injection, XSS)
- Data encryption at rest & in transit
- Credential management (API keys, JWT tokens, passwords)
- CORS and CSRF protection
- Access control validation (user can't see other user's data)
- Dependency vulnerability scan

**Deliverable:**
- Security audit report with findings, severity levels, and remediation steps
- List of vulnerabilities found and fixed
- Security recommendations for production

**Dependencies:**
- [ ] Use OWASP testing guide as reference
- [ ] Test authentication bypass attempts
- [ ] Test authorization bypass attempts
- [ ] Fuzz API endpoints with invalid inputs
- [ ] Check API key exposure in logs/responses
- [ ] Verify HTTPS on all endpoints
- [ ] Check database query parameterization (prevent SQL injection)
- [ ] Check input sanitization (prevent XSS, command injection)

**Impact:** Identify and fix security holes before production use, build confidence in data safety

---

### Item #11: Architecture Analysis & Improvement Recommendations
**Estimated:** 6-8 hours
**Description:**
- Critical analysis of current solution architecture
- Document current design decisions and their trade-offs
- Identify bottlenecks, redundancies, and inefficiencies
- Compare with industry best practices
- Propose improvements with justification
- Estimate effort and impact of each improvement

**Analysis Areas:**
- Frontend architecture (state management, component structure, performance)
- Backend architecture (monolithic vs microservices, API design, database schema)
- Database design (normalization, indexes, query optimization)
- Deployment architecture (Render single instance, no load balancing)
- Error handling and logging strategy
- Testing coverage (unit, integration, E2E tests)
- API design (REST conventions, versioning, documentation)
- Real-time features (WebSocket readiness)
- Scalability (how to handle 10x, 100x growth)
- Code organization and maintainability

**Deliverable:**
- Architecture review document with findings and recommendations
- Priority matrix: High impact / Low effort improvements
- Proposal for Phase 6+ roadmap based on analysis

**Impact:** Understand system strengths/weaknesses, plan next evolution of platform

---

### Item #8: Strategy Parameters - Edit Line in List
**Estimated:** 2-3 hours
**Description:**
- Parameters List view: allow editing a row in-place (currently only allows delete)
- Click on a parameter row (pos, param1-param10) to edit values
- Save changes without leaving the list view
- Show confirmation/error messages

**Dependencies:**
- [ ] Frontend: ParametersTable.tsx - add edit mode (click → inline editing)
- [ ] Frontend: Modal/inline form for editing a single parameter
- [ ] Backend: Parameter already has PUT endpoint via strategy routes

**Impact:** Better UX for parameter management, avoid need to delete + re-add

---

### Item #9: Strategy Parameters - Smart "Missing Parameters" Message
**Estimated:** 1-2 hours
**Description:**
- When returning to Strategy Details page from Parameters List, check if pos -1, 0, 1 are all present
- **Show** "Missing parameters (-1, 0, 1)" message only if any are missing
- **Hide** the message if all three positions exist in database
- Message should be dynamic based on actual database state

**Dependencies:**
- [ ] Frontend: StrategyDetailPage.tsx - call endpoint to verify parameters on mount
- [ ] Backend: GET `/api/v1/strategies/{id}/parameters/status` (or enhance existing GET)
- [ ] Validate: all three pos values (-1, 0, 1) exist for the strategy

**Impact:** Cleaner UI, accurate validation feedback, less visual clutter

---

### Item #2: Upload T212 Data Files
**Estimated:** 6-8 hours
**Status:** ✅ DONE
**Description:**
- Endpoint to upload CSV/Excel from T212 exports
- Parser for trade history, positions, accounts
- Import ISINs + history to database
- Data validation (valid ISINs, numeric values, correct dates)
- User feedback (X ISINs imported, Y errors, Z warnings)

**Dependencies:**
- ✅ Backend: POST `/api/v1/upload/t212-data` (file upload)
- ✅ Backend: CSV parser + validator
- ✅ Frontend: Upload form with drag-and-drop
- ✅ Database: Verify if new history table needed

**Impact:** Start with real data instead of mock data

---

### Item #15: Production Environment Setup - Real Money API (NEW)
**Estimated:** 4-6 hours
**Priority:** HIGH (Pre-production infrastructure)

#### ✅ Decisions from brainstorming (2026-09-24) — these supersede the original description below
- **Isolation:** separate Supabase project for PROD; independent credentials (own account, password, MFA entry, JWT/encryption secrets)
- **Code flow:** `main` → DEMO (auto-deploy); `prod` branch → PROD (auto-deploy off, manual deploy); promotion = merge `main` → `prod`; never commit directly to `prod`
- **SQL:** run scripts manually in PROD before promoting code (tracking deferred to Item #18)
- **Limits** (in `app_parameters`, editable per parameter in UI, independent values per environment):
  - Max value per BUY order; max value per SELL order (checked before placing)
  - Max daily spend = executed BUYs − executed SELLs with positive P&L (full sell value), since 00:00 Europe/Lisbon. Values from T212 `fill.walletImpact.netValue` (EUR) and `realisedProfitLoss`
  - Any limit hit → whole automation stops, pending orders stay on T212, resume only manually (also next day)
  - Dashboard shows consumption vs max
  - Deferred to Item #19: orders/day, per-ISIN exposure, price deviation, daily loss, reinforced confirmation to raise limits. No absolute ceiling, no protected stock, no simulation mode
- **Automation starts OFF after a deploy that changes code** (compare `RENDER_GIT_COMMIT` with stored value) — same in DEMO and PROD
- **Backend: exactly 1 instance, no autoscaling** (embedded scheduler → 2 instances = duplicate orders)
- **Alerts:** critical alerts first, on in DEMO and PROD, each toggleable in UI (JSON column `alert_settings` in `app_parameters`); requires SMTP config on Render
- **T212 environment: single source of truth = `T212_ENVIRONMENT` env var.** Remove the non-functional credentials card in UI, `PUT /config`, `config.t212_environment`, `T212_BASE_URL`; replace with a read-only status panel
- **Red permanent banner in PROD** ("PRODUÇÃO — DINHEIRO REAL"), driven by backend-reported environment
- **T212 API keys:** new keys for DEMO and PROD, IP-restricted (Render outbound ranges + home IP), minimum permissions; revoke old keys; remove T212 keys, `ENCRYPTION_KEY` and `JWT_SECRET_KEY` values from `CLAUDE.md`
- **Only LIMIT orders** (confirmed: engine only calls `place_limit_order`)
- **Go-live:** current MVP, automation off at start, 1 ISIN, low limits, raise gradually
- **Execution:** Phase 1 (code, tested in DEMO) delivered in one go; Phases 2-4 (PROD infra, IP-restricted keys, go-live) discussed after Phase 1 is validated

#### ✅ Phase 1 delivered (commit `52b11c4`, 2026-09-24) — pending DEMO validation
- Trading limits (max buy/sell order, max daily spend) + consumption bar on dashboard
- Automation auto-disables after a code deploy (RENDER_GIT_COMMIT check)
- Alerts: order rejected, invalid credentials, cycle errors, auto-disabled, MFA disabled, killswitch — all toggleable in UI
- T212 environment cleanup: removed the non-functional credentials card, single source of truth (T212_ENVIRONMENT), read-only status panel
- **Before deploying:** run `db/trading_limits_and_alerts.sql` in Supabase first
- **Not yet done:** SMTP not configured on Render — alerts currently only log, don't email (needed to actually test the alert flows end-to-end)

**Original description:**
- Create separate Render environment for PROD (currently on DEMO)
- Switch from T212 DEMO API (sandbox) to REAL MONEY API
- Set up production database (separate Supabase instance or database)
- Configure environment variables for PROD (API keys, URLs, etc)
- Implement safety controls and warnings for live trading
- Set up monitoring, alerting, and backup procedures
- Document PROD deployment checklist

**Current State (DEMO Only):**
```
Environment: DEMO
API Endpoint: https://demo.trading212.com/api/v0
Account: Sandbox with €5,889.99 (play money)
Frontend: https://trading-212-automation-front-end.onrender.com (single env)
Backend: https://trading212-4ojx.onrender.com (single env)
Database: Supabase (single instance)
```

**Proposed State (DEMO + PROD):**
```
DEMO Environment:
  - API: https://demo.trading212.com/api/v0 (sandbox)
  - Frontend: https://trading-212-automation-front-end.onrender.com
  - Backend: https://trading212-4ojx.onrender.com
  - Database: Supabase demo instance
  - Purpose: Testing, development, user onboarding

PROD Environment (NEW):
  - API: https://live.trading212.com/api/v0 (real money)
  - Frontend: https://trading212-prod.onrender.com (NEW)
  - Backend: https://trading212-prod-api.onrender.com (NEW)
  - Database: Supabase prod instance (NEW)
  - Purpose: Real trading with real funds
```

**Implementation Details:**

1. **Render Setup:**
   - Create new Render projects:
     - `trading212-prod` (frontend)
     - `trading212-prod-api` (backend)
   - Copy configurations from existing services
   - Set separate environment variables
   - Enable auto-deploy from same GitHub repo (different branch or tags)

2. **Supabase Setup:**
   - Create new production Supabase project (or dedicated database)
   - Run migrations to create all tables
   - Set up separate user accounts for PROD
   - Configure Row-Level Security (RLS) for production
   - Set up automated backups

3. **Environment Variables (PROD):**
   ```
   ENVIRONMENT=production
   T212_API_KEY=[real-money-api-key]
   T212_API_SECRET=[real-money-api-secret]
   T212_ENVIRONMENT=live  (instead of demo)
   T212_BASE_URL=https://live.trading212.com/api/v0
   SUPABASE_URL=[prod-supabase-url]
   SUPABASE_KEY=[prod-supabase-key]
   SUPABASE_JWT_SECRET=[prod-jwt-secret]
   FASTAPI_ENV=production
   FASTAPI_DEBUG=False  (critical for security)
   ```

4. **Safety Controls & Warnings:**
   - Add "PRODUCTION MODE" warning banner on frontend (red/bold)
   - Disable or restrict certain features (test mode only)
   - Add account verification step before enabling automation
   - Implement max position size limits (safety circuit breaker)
   - Add manual approval workflow for large orders
   - Rate limiting on critical endpoints
   - Disable demo/sandbox mode warnings in PROD

5. **Frontend Indicators:**
   - Environment badge: "DEMO" (blue) vs "PRODUCTION" (red)
   - Warning message: "⚠️ LIVE TRADING - REAL MONEY AT RISK"
   - Show account type clearly (Demo vs Live)
   - Different color scheme or styling for PROD

6. **Backend Safeguards:**
   - Verify T212_ENVIRONMENT=live before executing trades
   - Log all trades with "PRODUCTION" marker
   - Alert system for unusual activity
   - Killswitch endpoint: emergency stop all automation
   - Daily/weekly spending limits
   - Position size limits per ISIN

7. **Monitoring & Alerting:**
   - Set up error monitoring (Sentry or similar)
   - Email alerts for:
     - Automation errors
     - Large trades (>€1000)
     - Failed orders
     - Account balance changes
   - Dashboard: real-time performance metrics
   - Audit trail: all trades logged

8. **Backup & Disaster Recovery:**
   - Automated Supabase backups (daily)
   - Database export to cloud storage
   - Order/trade history export
   - Disaster recovery plan documented

9. **Deployment Checklist:**
   ```
   ✅ Create Render services (frontend + backend)
   ✅ Create Supabase project
   ✅ Set environment variables
   ✅ Run database migrations
   ✅ Test API connectivity (live.trading212.com)
   ✅ Test authentication (real API keys)
   ✅ Implement safety controls
   ✅ Set up monitoring
   ✅ Document runbook
   ✅ Load test (ensure stability)
   ✅ Security audit (before going live)
   ✅ User acceptance testing (UAT)
   ✅ Go-live procedure
   ```

10. **Branching Strategy:**
    - `main` → DEMO deployment (current)
    - `prod` → PRODUCTION deployment (new)
    - Merge from `main` to `prod` only after testing
    - Separate CI/CD pipelines for each

**Dependencies:**
- [ ] Real Trading 212 API account (live credentials)
- [ ] Production Supabase instance
- [ ] Render services setup (2 new services)
- [ ] Environment configuration management
- [ ] Safety controls implementation
- [ ] Monitoring setup (Sentry or similar)
- [ ] Documentation + runbook

**Deliverables:**
- ✅ Separate DEMO and PROD environments
- ✅ PROD frontend + backend on Render
- ✅ PROD database on Supabase
- ✅ Safety controls + warnings
- ✅ Monitoring + alerting system
- ✅ Deployment runbook
- ✅ Disaster recovery plan

**Testing:**
- Test automation in PROD with small positions
- Verify P&L calculations with real data
- Test error handling + killswitch
- Verify all safety limits work
- Audit trail completeness

**Risk Mitigation:**
- Start with small account balance
- Use strict position size limits
- Daily spending caps
- Manual approval for large trades
- 24/7 monitoring initially
- Documented kill procedures

**Impact:**
- ✅ Enable real money trading (major milestone)
- ✅ Production-ready infrastructure
- ✅ Professional-grade monitoring
- ✅ Safety mechanisms in place
- ✅ Ready for wider user adoption

**Timeline:**
- Week 1: Infrastructure setup (Render, Supabase)
- Week 2: Safety controls + monitoring
- Week 3: Testing + UAT
- Week 4: Go-live procedure

---

### Item #3: Charts & Statistics Dashboard
**Estimated:** 8-10 hours
**Description:**
- Statistics dashboard: total P&L, gain%, volatility, etc
- Charts (Recharts):
  - Equity curve (Portfolio value over time)
  - Win/Loss ratio
  - Monthly returns
  - Drawdown analysis
  - ISINs performance comparison
- Trade history table (executed trades)
- Filters by date, ISIN, strategy

**Dependencies:**
- [ ] Frontend: Charts with Recharts
- [ ] Backend: Endpoints for statistical calculations
- [ ] Data: Trade/position history in database

**Impact:** Full visibility of performance, enables visual backtesting

---

### Item #6: Rename Render Projects (Quick Win)
**Estimated:** 0.5 hours
**Description:**
- Rename frontend service: `trading212-1` → `trading212-frontend`
- Rename backend service: `trading212-4ojx` → `trading212-backend`
- Update documentation links
- Update .env URLs

**Impact:** Better naming convention, easier management

---

## 📊 Progress Summary

**Phase 5:** 60% Complete (6 of 12 items)

| Item | Status | Commits |
|------|--------|---------|
| 1. Strategy Management | ✅ DONE | `4bf858f`, `08cc493`, `da97bbe` |
| 4. Global Toggle | ✅ DONE | `84d32ff` |
| 5. Automation Dialog | ✅ DONE | `9f2d7a2` |
| 7. Knowledge Base | ✅ DONE | Multiple |
| 8. Parameters Edit Row | ✅ DONE | `f10d0d0` |
| (ISIN Cleanup) | ✅ DONE | `3d342c3` |
| (Documentation Reorganization) | ✅ DONE | `3b6e12e` |
| 2. Upload T212 Data | ✅ DONE | - |
| 9. Smart Missing Msg | ⏳ TODO | - |
| 6. Rename Render | ⏳ TODO | - |
| **12. Enhanced Login Security** | ⏳ TODO | - |
| **13. Dynamic Grid Strategy** | ⏳ TODO | - |
| **14. Dashboard Analytics** | ⏳ TODO | - |
| **15. Production Environment (PROD)** | ⏳ TODO | - |
| 3. Charts & Stats | ⏳ TODO | - |
| 10. Cybersecurity Testing | ⏳ TODO | - |
| 11. Architecture Analysis | ⏳ TODO | - |

**Completed this session:**
- 10 commits
- 500+ lines of UI refactor
- 3,500+ lines of documentation
- Full frontend translation to English
- Database cleanup

**Time invested:** ~20-25 hours of development

---

## 🎯 Recommended Next Steps

### High Impact / Low Effort (Quick Wins)
1. **Item #9:** Smart "Missing Parameters" Message (1-2h) - Quick validation fix
2. **Item #6:** Rename Render (0.5h) - Quick win

### High Impact / Medium Effort (Security & User Features)
3. **Item #12:** Enhanced Login Security (6-8h) - Prevent brute force, rate limiting, real auth
4. **Item #13:** Dynamic Grid Strategy (8-10h) - Variable BUY/SELL deltas by day
5. **Item #2:** Upload T212 Data (6-8h) - Enable real data workflow ✅ DONE

### High Impact / High Effort (Core Features & Strategic)
6. **Item #14:** Dashboard Analytics & Metrics (10-12h) - Orders, P&L, cycles tracking
7. **Item #15:** Production Environment Setup - PROD (4-6h) - **NEW** - Real money API integration (CRITICAL before live trading)
8. **Item #3:** Charts & Stats (8-10h) - Advanced performance analytics
9. **Item #11:** Architecture Analysis (6-8h) - Understand strengths/weaknesses
10. **Item #10:** Cybersecurity Testing (8-12h) - Security audit + penetration testing

**Suggested workflow:**
- Quick wins first (#9, #6) — 2-3 hours, polish
- Then security (#12) — 6-8 hours, HIGH priority
- Then new features (#13, #14) — 18-22 hours, visible on dashboard
- Then PRODUCTION setup (#15) — 4-6 hours, CRITICAL for live trading
- Then strategic reviews + advanced features (#11, #10, #3)

---

## 📈 Overall Project Status

**MVP Status:** ✅ PRODUCTION READY
- Frontend: ✅ Fully translated, all pages working
- Backend: ✅ Automation engine running (Phase 4 complete)
- Database: ✅ Cleaned up, optimized
- Documentation: ✅ Comprehensive knowledge base created
- Deployment: ✅ Auto-deploy to Render on git push

**Ready for:** Live demo, user testing, real data import

---

## 🖥️ Infrastructure / Environment (Outside Backlog)

### Cloud Workstation Setup
**Status:** ⏳ TODO (Strategic, not urgent)
**Description:**
- Set up a personal cloud computer (VPS/cloud VM) accessible from anywhere
- Replace current laptop-based development workflow
- Allows development from any device/browser without laptop dependency
- Enables 24/7 automation testing (AutomationEngine can run continuously)

**Considerations:**
- [ ] Choose provider (AWS EC2, DigitalOcean, Hetzner, Azure VM, etc)
- [ ] Install development environment (Python 3.14, Node, git, VSCode-server, etc)
- [ ] Set up persistent storage for code/data
- [ ] Configure SSH access + security
- [ ] Cost monitoring (for continuous 24/7 operation)

**Impact:** Development independence from laptop, 24/7 bot operation, backup dev environment

---

### Item #16: Scheduler Time Window - Parametrize Operating Hours (NEW)
**Estimated:** 2-3 hours
**Priority:** MEDIUM (Operational tuning)
**Description:** Allow user to configure a time window during which AutomationEngine should operate (e.g., 9:00-17:00 market hours). Outside this window, scheduler runs but skips cycle execution. Useful for:
- Trading during market hours only (avoid off-hours volatility)
- Reduce server load outside trading hours
- Adapt to different market opening times (US, UK, EU markets)
- Manual control over when money is at risk

**Design:**

#### Database Schema:
Add two columns to `app_parameters` table:
```sql
scheduler_time_window_start VARCHAR DEFAULT '00:00'  -- HH:MM format (e.g., "09:00")
scheduler_time_window_end VARCHAR DEFAULT '23:59'    -- HH:MM format (e.g., "17:00")
-- Note: If start > end (e.g., "22:00"-"06:00"), wraps around midnight
```

#### Frontend Changes:
- **ConfigPage.tsx** → Add new section "Scheduler Time Window"
  - Two time pickers: "Start time" (HH:MM) and "End time" (HH:MM)
  - Show current setting: "Active hours: 09:00 - 17:00"
  - Show next window: "Next execution: at 09:00 tomorrow"
  - Show if currently inside/outside window: "🟢 WITHIN window" or "🔴 OUTSIDE window"
  - Save button: `PUT /api/v1/automation/config/time-window`
  - Display example: "During market hours: 9 AM to 5 PM"

- **Sidebar.tsx** → Add visual indicator
  - Show status: "🟢 Active (within window)" or "⏸️ Paused (outside window)"
  - Tooltip: "Scheduler will resume at 09:00"

#### Backend Changes:
- **`backend/models/schemas.py`**
  - Add `scheduler_time_window_start`, `scheduler_time_window_end` to `AppParametersResponse`
  - Add validation: must be valid HH:MM format, must be different (or same for 24/7)

- **`backend/routes/automation.py`**
  - Add new endpoint: `PUT /api/v1/automation/config/time-window`
  - Request: `{"start": "09:00", "end": "17:00"}`
  - Response: Updated config + next execution time

- **`backend/services/automation_engine.py`**
  - Add method: `_is_within_time_window()` → bool
    - Compare current time with `scheduler_time_window_start/end`
    - Handle midnight wrap: if start > end (e.g., 22:00-06:00), consider current time in window if > start OR < end
  - Modify `run_cycle()`:
    - At start, check `if not _is_within_time_window(): return`
    - Skip cycle without error (just log and return)
  - Log: "[Scheduler] ⏸️ Outside time window (09:00-17:00), skipping cycle"

#### Example Usage:
```
User sets: Start 09:00, End 17:00
Scheduler runs every 15s (always)

9:00 AM:
  ✅ Cycle 1 executes (within window)
  ✅ Cycle 2 executes (within window)

5:01 PM:
  ⏸️ Cycle skipped (outside window)
  ⏸️ Cycle skipped (outside window)
  
Next day at 9:00 AM:
  ✅ Cycle resumes
```

#### Edge Cases:
1. **Overnight wrap** (e.g., start 22:00, end 06:00):
   - 21:00: Outside (before 22:00)
   - 23:00: Inside (after 22:00, before midnight)
   - 00:30: Inside (after midnight, before 06:00)
   - 07:00: Outside (after 06:00, before 22:00)

2. **Window disabled** (set to "00:00"-"23:59"):
   - Scheduler always active (24/7)

3. **Single-minute window** (e.g., "09:00"-"09:01"):
   - Only cycles at exactly 09:00-09:00:59
   - Next execution at 09:00 next day

#### Testing Checklist:
- [ ] Set window to 09:00-17:00
- [ ] Verify cycles execute during 9 AM-5 PM
- [ ] Verify cycles skip outside 9 AM-5 PM
- [ ] Test midnight wrap: 22:00-06:00
- [ ] Verify log messages show window status
- [ ] Sidebar shows correct indicator (🟢 Active / ⏸️ Paused)
- [ ] Change window, verify new time takes effect immediately
- [ ] Set to 24/7 (00:00-23:59), verify always active

#### Deliverables:
- ✅ Two time picker fields in ConfigPage
- ✅ Time window validation (HH:MM format)
- ✅ Backend endpoint to save/retrieve window
- ✅ AutomationEngine respects window (skip cycles outside)
- ✅ Logging for window status
- ✅ Sidebar indicator
- ✅ Next execution time display

#### Dependencies:
- [ ] Time picker component (or use HTML5 `<input type="time">`)
- [ ] Time zone handling (assume server timezone = user timezone for now)
- [ ] Database migration to add columns

#### Impact:**
- ✅ Reduce unnecessary cycles outside trading hours
- ✅ Lower server costs (skip 16+ hours/day if only 9-17)
- ✅ User control over when automation is active
- ✅ Foundation for multi-timezone support (future)
- ✅ Better operational awareness (visual indicator)

#### Future Enhancements:
- Support multiple time windows per week (e.g., different hours Mon-Fri vs Sat-Sun)
- Time zone configuration (currently assumes server timezone)
- Market calendar integration (auto-detect market holidays)
- Event-based scheduling (trigger before/after market open/close)

---

### Item #17: Same-Domain Architecture - Eliminate Cross-Origin Cookie Dependency (NEW)
**Estimated:** 3-5 hours
**Priority:** LOW (Defense-in-depth hardening, not a fix for a known exploit)
**Context:** Discovered while fixing Item #12 (Enhanced Login Security). Frontend (`trading-212-automation-front-end.onrender.com`) and backend (`trading212-4ojx.onrender.com`) live on different Render subdomains, which are different origins as far as the browser is concerned.

**Description:**
The session cookie currently requires `SameSite=None` (see commit `3a8c43c`) because it's sent cross-site between the two origins — `SameSite=Lax`/`Strict` would make the browser silently drop the cookie on every `axios`/`fetch` call, breaking login entirely (this is exactly the bug that got fixed). `SameSite=None` is safe today because CORS is locked to an explicit origin allowlist (`FRONTEND_URL` only, no wildcard) and every state-changing endpoint uses JSON bodies, which forces a CORS preflight that blocks unauthorized origins before the request is even sent.

That said, `SameSite=None` still removes a **browser-level** defense layer and makes the app depend entirely on **one** remaining layer (CORS config) instead of two independent layers. If serving frontend and backend under the *same* domain (e.g., `trading212.app` for the SPA, `trading212.app/api/*` proxied to the backend), the browser would once again treat every request as same-site, and `SameSite=Lax` (or even `Strict`) could be restored — giving back CSRF protection at the browser level, independent of any CORS misconfiguration.

**Options to achieve same-domain:**
1. **Reverse proxy on Render** — front both services behind a single custom domain, path-based routing (`/api/*` → backend, everything else → frontend static site)
2. **Custom domain + path rewriting** — buy a domain, configure DNS + a proxy layer (e.g., Render's rewrite rules, or a lightweight edge proxy like Cloudflare Workers) to route `/api/*` to the backend service while serving the SPA from the same host
3. **Merge into one service** — serve the built React static files directly from the FastAPI backend (`StaticFiles` mount), eliminating the second Render service entirely

**Trade-offs:**
- Requires a custom domain (currently using free `*.onrender.com` subdomains)
- Option 3 (merge into one service) is the simplest but couples frontend release cadence to backend deploys
- Options 1-2 keep services independent but add a proxy layer to maintain
- Not urgent: current CORS-based protection is sound for this app's actual attack surface (verified no state-mutating GET endpoints exist in active routes)

**Deliverables:**
- [ ] Decide on approach (reverse proxy vs merged service vs custom domain + rewrite)
- [ ] Acquire/configure custom domain if needed
- [ ] Update CORS + cookie `SameSite` back to `Lax` (or `Strict`) once same-origin is confirmed
- [ ] Update `FRONTEND_URL` / CORS origins accordingly
- [ ] Verify login flow works end-to-end after the domain change
- [ ] Update `CLAUDE.md` URLs section

**Impact:** Restores browser-level CSRF protection as a second independent layer (defense-in-depth), removing reliance on CORS configuration alone. Not fixing a known vulnerability — current setup is sound — this is a hardening item for when a custom domain is set up anyway (e.g., alongside Item #15 PROD setup).

---

### Item #18: Database Migration Tracking (NEW)
**Estimated:** 2-3 hours
**Priority:** LOW (becomes more valuable as DEMO and PROD schemas need to stay in sync)
**Context:** Raised during Item #15 (DEMO/PROD) brainstorming. Decision for now: run SQL scripts manually in PROD before promoting code. This item hardens that later.

**Description:**
- Number every schema change (`db/migrations/001_...sql`, `002_...sql`, ...)
- New table `schema_migrations` records which scripts ran in each database — shows at a glance what's missing in PROD
- Backend checks the expected schema version at startup; if it doesn't match, it starts with automation blocked and sends an alert, instead of failing mid-trading-cycle
- Write migrations backward-compatible (add columns with defaults; never drop a column in the same step the code stops using it), so "SQL first, code after" is always safe

---

### Item #19: Additional Trading Safety Limits + Reinforced Confirmation (NEW)
**Estimated:** 4-6 hours
**Priority:** MEDIUM (after Item #15 is live)
**Context:** Item #15 starts with only two limits (max value per order, max daily spend on executed orders). These were discussed and deferred.

**Additional limits:**
| Limit | Protects against |
|---|---|
| Max orders per day | A bug placing orders in a loop — each under the per-order max, hundreds in total |
| Max exposure per ISIN | Concentrating too much money in a single asset |
| Max price deviation (e.g. ±5% vs last price) | Bad API data generating orders at absurd prices |
| Max daily loss | Runaway losses (depends on Item #14 P&L tracking) |

**Reinforced confirmation to raise limits:**
- Raising any limit requires password or MFA code re-entry; lowering stays free
- Rationale: if someone hijacks a session, raising the limits is the first thing they'd do
- Log every limit change (old value, new value, timestamp) + send a security alert

---

**Last Updated:** 2026-09-24
**Status:** Phase 5: 60% complete (8 of 18 items) + 8 NEW items (#12-#19)
**Recent:** Item #18 (Migration Tracking) ✅ ADDED | Item #19 (Extra Safety Limits) ✅ ADDED
