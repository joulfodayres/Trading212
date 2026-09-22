# 🚀 Trading 212 Bot - Quick Start (5 min)

## What is this?

**Trading 212 Bot** is an **automated algorithmic trading platform** that runs in the cloud. It lets you:
- ✅ Create **Grid Trading strategies** (buy at price - 1%, sell at price + 1%)
- ✅ Manage multiple **ISINs** (stocks/ETFs) simultaneously
- ✅ Monitor automation **24/7** via web dashboard
- ✅ Control via **browser from anywhere** (no software to install)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| 🎨 **Frontend** | React 18 + TypeScript + Tailwind CSS |
| ⚙️ **Backend** | FastAPI + Python 3.14 |
| 💾 **Database** | PostgreSQL (Supabase Cloud) |
| 🔐 **Auth** | Supabase Auth (JWT) |
| 🚀 **Hosting** | Render (auto-deploy from GitHub) |
| 📈 **Trading API** | Trading 212 Official API (HTTP Basic Auth) |

## Architecture

```
Browser (You)
    ↓ HTTPS
    ↓
Frontend (React) ← → Backend (FastAPI)
    ↓
    ↓ ← → Supabase (PostgreSQL + Auth)
    ↓
    ↓ ← → Trading 212 API (demo/live)
```

## Current Status

✅ **Phase 4 Complete** - Automation Engine running 24/7
- 3-phase cycle: Setup → Monitor → Fill/Rebalance
- 15s interval between cycles
- Grid trading strategy operational
- Order status tracking (W/E/P/X)

📊 **Phase 5 Progress** - 60% Complete (6 of 12 items)
- ✅ Strategy management UI + Parameters CRUD
- ✅ Global automation toggle
- ✅ Database cleanup on sync
- ⏳ TODO: Smart validation messages, rename Render projects, upload T212 data, charts

## Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://trading212-1.onrender.com |
| **Backend API** | https://trading212-4ojx.onrender.com |
| **API Docs** | https://trading212-4ojx.onrender.com/docs |

## Key Concepts

### 1. **ISINs** - Securities you own
- Stock or ETF (e.g., AAPL, VWRL)
- Each has quantity, current price, automation status
- Can enable "Grid Trading" on each ISIN

### 2. **Strategies** - Trading rules
- Define positions (-1, 0, +1) = (sell, hold, buy)
- Set parameters (price adjustments, investment amounts)
- Attached to ISINs to automate trading

### 3. **Grid Trading** - The automation
- **Phase 1 (Setup):** Create initial BUY and SELL orders
- **Phase 2 (Monitor):** Check if orders filled
- **Phase 3 (Rebalance):** Create new pair when one side fills
- **Repeat:** Every 15 seconds, 24/7

### 4. **Orders** - Trade records
- W = Watch (pending execution)
- E = Executed (filled on T212)
- P = Processed (automation handled it)
- X = Error (something went wrong)

## Getting Started (First Time)

### Step 1: Add ISINs to Portfolio
1. Go to **Dashboard** tab
2. Click **"+ Add ISIN"** button
3. Enter ISIN code (e.g., "GB00B4L5Y983" for VWRL)
4. Quantities auto-sync from T212
5. Click **"Sync Portfolio"** to fetch latest

### Step 2: Create Strategy
1. Go to **Strategies** tab
2. Click **"+ New Strategy"** button
3. Enter strategy name (e.g., "Grid ±1% on VWRL")
4. Leave status "Enabled"
5. Click **"Save"**

### Step 3: Add Parameters
1. From strategy detail, click **"Edit Parameters"**
2. Add 3 rows (positions -1, 0, +1):
   - **Position -1:** SELL above market price (param1 = +2%, param3 = amount to sell)
   - **Position 0:** HOLD (no orders)
   - **Position +1:** BUY below market price (param2 = -1%, param4 = amount to buy)
3. Save each parameter

### Step 4: Enable Automation
1. Go to **Dashboard**
2. Click **"Enable Grid Trading"** in sidebar
3. Confirm in dialog
4. Select strategy for each ISIN you want to automate
5. Watch it go! 🚀

## Monitoring

**Dashboard shows:**
- 📊 Total portfolio value
- 📈 All ISINs with quantities and prices
- 🟢 Automation status (active/inactive)
- ⏱️ Scheduler interval (check every N seconds)

**Logs are available at:**
- Backend: `https://trading212-4ojx.onrender.com/logs` (coming soon)
- Console: Browser DevTools → Console tab

## Common Tasks

### Check if automation is working
1. Set `Log Level` to **MEDIUM** in Config
2. Click **"Run Cycle Once"** button
3. Check browser console: `console.log('[...]')`
4. Check Render backend logs: Render Dashboard → Backend service → Logs

### Pause/Resume automation
1. Sidebar: toggle **Global Automation** ON/OFF
2. Or disable specific ISINs individually
3. Existing orders stay open (you can close manually on T212)

### See detailed logs
1. Go to **Config** tab
2. Set **Log Level** to MEDIUM
3. Automation will log all DB/API interactions
4. View in database table `logs` (admin only)

### Sync with T212
1. Go to **Dashboard**
2. Click **"Sync Portfolio"** button
3. Backend fetches latest positions from T212
4. Adds new ISINs, updates quantities
5. **Deletes ISINs no longer in your T212 account**

## Key Files

**Frontend:**
- `frontend/src/pages/DashboardPage.tsx` — Main dashboard
- `frontend/src/pages/StrategiesPage.tsx` — Strategy management
- `frontend/src/components/ISINTable.tsx` — Portfolio table

**Backend:**
- `backend/main.py` — FastAPI entry point
- `backend/services/automation_engine.py` — 3-phase cycle logic
- `backend/routes/isins.py` — Portfolio endpoints
- `backend/routes/automation.py` — Automation control

**Database:**
- Tables: `users`, `isins`, `strategies`, `strategy_parameters`, `orders`, `config`, `logs`
- Hosted on Supabase (PostgreSQL)

## Troubleshooting

**Q: Dashboard shows "Connecting..." forever**
- A: Check backend health: `curl https://trading212-4ojx.onrender.com/health`
- Render services may be starting (5-10 min boot time)

**Q: Orders not executing**
- A: Check automation enabled + strategy assigned
- Verify T212 account has funds for orders
- Check backend logs: `Log Level = MEDIUM`

**Q: Can't login**
- A: Use any email + password (login is stub for MVP)
- Auth will be real in Phase 6

**Q: Strategy parameters won't save**
- A: All 3 positions (-1, 0, +1) must be present
- Make sure `param1` and `param2` are filled

## Next Steps

👉 **Read full docs:** `docs/` folder
👉 **See API endpoints:** `docs/API_ENDPOINTS.md`
👉 **Understand automation:** `docs/AUTOMATION_FLOW.md`
👉 **Check backlog:** `BACKLOG.md` (Phase 5 TODO items)

---

**Status:** ✅ MVP Ready for Production
**Latest commit:** Phase 4 complete + Phase 5 (60% progress)
**Next:** Phase 5 remaining items + real auth + charts

