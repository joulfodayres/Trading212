# Trading 212 Bot - Quick Reference

## Project URLs

| Component | URL |
|-----------|-----|
| Frontend | https://trading212-1.onrender.com |
| Backend API | https://trading212-4ojx.onrender.com |
| API Docs | https://trading212-4ojx.onrender.com/docs |
| GitHub | https://github.com/joulfodayres/Trading212 |
| Supabase | https://app.supabase.com (login required) |

## Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**URLs:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Key Database Tables

### isins
- Portfolio positions from T212
- Fields: ticker, quantity, current_price, automation_enabled, strategy_id
- Related: strategies (via strategy_id), orders (via id)

### strategies
- Grid trading configurations
- Fields: name, initial_investment, enabled, is_valid
- Related: strategy_parameters (1:many), isins (1:many)

### strategy_parameters
- Grid levels for each strategy
- Fields: pos (position level), param1-param10 (parameters)
- Required for automation: pos must include -1, 0, 1

### orders
- Order history and monitoring
- Fields: t212_order_id, side, status, automation_status
- automation_status: W (watch), E (executed), C (cancelled)

### app_parameters
- Global app configuration
- Singleton table (only one row)
- Fields: scheduler_interval_seconds, grid_trading_enabled

## Key API Endpoints

```bash
# Strategies
GET    /api/v1/strategies              # List all
POST   /api/v1/strategies              # Create
PUT    /api/v1/strategies/{id}         # Update
POST   /api/v1/strategies/{id}/parameters      # Add parameter
DELETE /api/v1/strategies/{id}/parameters/{pid}  # Remove parameter

# ISINs
GET    /api/isins                      # List
POST   /api/isins/sync                 # Sync from T212
PUT    /api/isins/{id}/automation      # Enable/disable automation

# Automation
GET    /api/v1/automation/global-status        # Status
PUT    /api/v1/automation/enable               # Enable
PUT    /api/v1/automation/disable              # Disable
GET    /api/v1/automation/status               # Detailed status
PUT    /api/v1/automation/config/interval      # Set interval
```

## Environment Variables

**Backend (.env):**
```
SUPABASE_URL=
SUPABASE_KEY=
T212_API_KEY=
T212_API_SECRET=
T212_ENVIRONMENT=demo
ENCRYPTION_KEY=
JWT_SECRET_KEY=
LOG_LEVEL=INFO
```

**Frontend (.env.local):**
```
VITE_API_URL=http://localhost:8000
```

## Automation Engine - 3 Phases

1. **Phase 1: Initial Setup**
   - Create BUY/SELL pairs at current price ± param1/param2 %
   - Quantity = initial_investment / buy_price

2. **Phase 2: Monitor**
   - Poll T212 for order status
   - Mark filled orders

3. **Phase 3: Handle Fills**
   - Adjust trades_balance (BUY: -1, SELL: +1)
   - Cancel related order
   - Place new pair at new grid level

Runs every 15 seconds (configurable in app_parameters.scheduler_interval_seconds).

## Important Concepts

**trades_balance:** Grid level tracker
- Starts at 0
- BUY fill → -1 (lower prices)
- SELL fill → +1 (higher prices)
- Used to select strategy_parameters

**is_valid:** Strategy validity indicator
- True if has parameters for pos -1, 0, 1
- Required to enable strategy
- Checked automatically before enabling

**automation_status:** Order tracking status
- **W**: Watch (pending)
- **E**: Executed (filled)
- **C**: Cancelled

**initial_trade:** Flag for Phase 1
- True → create initial BUY/SELL pair
- False → skip Phase 1

## Git Workflow

```bash
# Feature development
git checkout -b feature/my-feature
# ... make changes ...
git commit -m "feat: Add new feature"
git push origin feature/my-feature

# Create PR on GitHub

# After merge to main
# Auto-deployment to Render (10-15 min)
```

## Common Tasks

### Enable Automation for an ISIN

```bash
# 1. Get strategy ID
curl http://localhost:8000/api/v1/strategies | grep id

# 2. Get ISIN ID
curl http://localhost:8000/api/isins | grep id

# 3. Enable automation
curl -X PUT http://localhost:8000/api/isins/<isin-id>/automation \
  -H "Content-Type: application/json" \
  -d '{"automation_enabled": true, "strategy_id": "<strategy-id>"}'

# 4. Enable global automation
curl -X PUT http://localhost:8000/api/v1/automation/enable
```

### Create a Strategy

```bash
# 1. Create strategy
curl -X POST http://localhost:8000/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grid 1%",
    "description": "...",
    "initial_investment": 10.0
  }'

# Response contains: strategy_id

# 2. Add parameters
curl -X POST http://localhost:8000/api/v1/strategies/<strategy-id>/parameters \
  -H "Content-Type: application/json" \
  -d '{"pos": "-1", "param1": -1.0, "param2": 1.0}'

# 3. Repeat for pos 0 and pos 1

# 4. Enable
curl -X PUT http://localhost:8000/api/v1/strategies/<strategy-id> \
  -d '{"enabled": true}'
```

### Debug Automation Issues

```bash
# Check if scheduler running
curl http://localhost:8000/api/v1/automation/status

# Check strategy is valid
curl http://localhost:8000/api/v1/strategies/<id> | grep is_valid

# Check ISIN has strategy
curl http://localhost:8000/api/isins | grep strategy_id

# Check if global automation on
curl http://localhost:8000/api/v1/automation/global-status

# View logs (local)
tail -f backend.log

# View logs (Render)
# Navigate to: https://dashboard.render.com → Services → Backend → Logs
```

## File Locations

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI entry point |
| `backend/services/automation_engine.py` | 3-phase logic |
| `backend/routes/strategies.py` | Strategy CRUD |
| `backend/routes/isins.py` | ISIN management |
| `frontend/src/pages/StrategiesPage.tsx` | Strategy UI |
| `frontend/src/components/Sidebar.tsx` | Navigation + global toggle |
| `db/supabase_client.py` | Database connection |

## Deployment Checklist

Before pushing to main:
- ✅ Run tests locally
- ✅ Check for console errors (frontend)
- ✅ Verify database connection
- ✅ Test API endpoints with Postman/curl
- ✅ Update .env variables (Render dashboard)
- ✅ Verify git history is clean

After deploy:
- ✅ Check Render logs (should see ✅ messages)
- ✅ Test frontend at https://trading212-1.onrender.com
- ✅ Test API at https://trading212-4ojx.onrender.com/docs
- ✅ Check database (Supabase dashboard)

## Phase 5 Backlog

| Item | Status | Files |
|------|--------|-------|
| 1. Strategy Management | ✅ DONE | StrategiesPage.tsx, routes/strategies.py |
| 2. Upload T212 Data | ⏳ TODO | TBD |
| 3. Charts & Stats | ⏳ TODO | TBD |
| 4. Global Automation Toggle | ✅ DONE | Sidebar.tsx, routes/automation.py |
| 5. Automation Dialog | ✅ DONE | AutomationBottomSheet.tsx |
| 6. Rename Render Projects | ⏳ TODO | Render dashboard |
| 7. Knowledge Base | ✅ DONE | docs/ folder |

## Support Resources

- **API Docs:** http://localhost:8000/docs (swagger)
- **GitHub Issues:** https://github.com/joulfodayres/Trading212/issues
- **Render Logs:** https://dashboard.render.com
- **Supabase Docs:** https://supabase.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

## Quick Command Reference

```bash
# Database
# Connect to Supabase SQL editor: https://supabase.com → SQL Editor

# Backend
cd backend
python -m pytest                  # Run tests
python -m black .                # Format code
LOG_LEVEL=DEBUG uvicorn main:app # Debug mode

# Frontend
cd frontend
npm run build                     # Production build
npm run preview                   # Preview build
npm run type-check               # TypeScript check

# Git
git log --oneline                # View commits
git diff HEAD~1                  # View latest changes
git status                       # Check status
git reset --hard                 # Discard changes (careful!)
```

## Test Account (Supabase)

```
Email: teste@trading212.com
Password: (any)
User ID: ab1036ff-937d-46e5-8f5b-bab07f1fb100
```

## Test Account (Trading 212)

```
API Key: 40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU
API Secret: iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0
Balance: €5,889.99
Environment: demo
```

⚠️ **Never commit credentials to GitHub!**

---

**Last Updated:** 2026-09-20
**Quick Reference for Trading 212 Bot**
