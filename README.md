# Trading 212 Bot - MVP

**Status:** ✅ **DEMO + PROD Live** 🚀 — Auth (Item #20), PROD environment (Item #15), SMTP alerts (Item #21) all shipped
**Last Update:** 2026-09-27

Algorithmic trading platform with automated Grid Trading strategy. Built with React + FastAPI, hosted on Render + Supabase.

---

## ⚡ Quick Start

### 🌐 Access Online (Production)
```
DEMO Frontend: https://trading-212-automation-front-end.onrender.com
DEMO Backend:  https://trading212-backend.onrender.com
DEMO API Docs: https://trading212-backend.onrender.com/docs

PROD Frontend: https://trading212-frontend-real.onrender.com
PROD Backend:  https://trading212-backend-prod.onrender.com
PROD API Docs: https://trading212-backend-prod.onrender.com/docs
```
See `docs/KNOWLEDGE_BASE.md` for the full DEMO/PROD split (separate Supabase projects, `main` vs `prod` git branches, manual-only deploy on PROD).

### 💻 Development (Local)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# → Edit .env with your credentials
python main.py  # http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

---

## 📚 Documentation

### 🎯 **Start Here: Documentation Hub**
👉 **Open [`docs/index.html`](docs/index.html)** in your browser

Beautiful, interactive documentation hub with:
- 📖 7 main documentation sections
- 🔍 Quick navigation to all guides
- ⚡ Getting started (5 min) + Quick Start guide
- 🏗️ Architecture deep dives (Automation, Database, API)
- 🛠️ Development setup + Deployment guide
- 📋 Backlog & Roadmap
- 🧠 Knowledge Base + Code Examples

### Quick Links to Key Documents

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **`docs/QUICK_START.md`** | 5-minute intro (what is this, how to use) | 5 min ⚡ |
| **`docs/PHASE_5_STATUS.md`** | Current progress, what's done, what's next | 10 min |
| **`docs/AUTOMATION_FLOW.md`** | How the 3-phase grid trading cycle works | 15 min 🔄 |
| **`docs/DATABASE_SCHEMA.md`** | All tables, relationships, constraints | 10 min 💾 |
| **`CLAUDE.md`** | Project overview, architecture, conventions | 20 min 🏗️ |
| **`BACKLOG.md`** | Next features, effort estimates, priorities | 10 min 📋 |

### Additional References
- **`docs/API_REFERENCE.md`** — All 14 REST endpoints
- **`docs/CODE_EXAMPLES.md`** — 25+ code snippets
- **`docs/DEVELOPMENT.md`** — Local setup & development
- **`docs/DEPLOYMENT_NOTES.md`** — Production deployment
- **`docs/TROUBLESHOOTING.md`** — Common issues & fixes
- **`docs/KNOWLEDGE_BASE.md`** — Full knowledge base
- **`docs/QUICK_REFERENCE.md`** — One-page cheat sheet

---

## ✅ What Works Now (Phase 4 Complete)

### Core Automation
- ✅ **3-Phase Grid Trading Cycle** (Phase 1: Setup, Phase 2: Monitor, Phase 3: Rebalance)
- ✅ **APScheduler Engine** running 24/7 every 15 seconds
- ✅ **Order Management** (BUY/SELL pairs, watch, execute, process, handle errors)
- ✅ **Strategy Parameters** (position-based: -1 sell, 0 hold, +1 buy)
- ✅ **Automation Control** (enable/disable per ISIN, global toggle)
- ✅ **Portfolio Sync** (fetch latest positions from T212)
- ✅ **Complete Pair Handling** (when both grid legs fill between cycles)

### Features
- ✅ **Live Dashboard** (real-time ISIN positions from T212)
- ✅ **Strategy Management** (CRUD strategies + parameters)
- ✅ **Automation Dialog** (select strategy before enabling)
- ✅ **Configuration UI** (scheduler interval, log level)
- ✅ **Parameters Editor** (inline editing with validation)
- ✅ **Database Cleanup** (remove orphaned ISINs on sync)
- ✅ **Order Tracking** (status: W/E/P/X/C)

### Infrastructure
- ✅ **FastAPI Backend** with 14+ REST endpoints
- ✅ **React 18 Frontend** with TypeScript
- ✅ **PostgreSQL Database** (Supabase) — separate DEMO and PROD projects
- ✅ **Auto-Deploy** from GitHub to Render (DEMO only; PROD is manual-deploy by design)
- ✅ **HTTPS/TLS** on all endpoints
- ✅ **JWT Authentication** enforced on ~35 backend endpoints + API key encryption
- ✅ **Trading safety limits**, auto-disable-after-deploy, and SMTP email alerts
- ✅ **Full Audit Trail** + conditional logging

---

## 🚧 Next Phase (Phase 5: Features & Polish)

**Progress:** 60% Complete (6 of 12 items done)

### ✅ Completed Phase 5 Items
1. ✅ Strategy Management UI + Parameters CRUD
2. ✅ Global Automation Toggle
3. ✅ Automation Dialog with Strategy Selection
4. ✅ ConfigPage Refactor
5. ✅ Frontend Translation to English
6. ✅ Parameters Inline Editing (fixed bugs)

### ⏳ TODO Phase 5 Items
1. **Smart "Missing Parameters" Message** (1.5h) — Show validation warning only if needed
2. **Rename Render Projects** (0.5h) — Better naming convention
3. **Upload T212 Data** (7h) — CSV/Excel import
4. **Charts & Statistics** (9h) — Equity curve, P&L, performance
5. **Cybersecurity Testing** (10h) — Security audit + penetration testing
6. **Architecture Review** (7h) — Design analysis + improvement recommendations

See **`BACKLOG.md`** for full details and time estimates.

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind |
| **Backend** | FastAPI + Python 3.14 |
| **Database** | PostgreSQL (Supabase) |
| **Auth** | JWT (Supabase Auth) |
| **Trading API** | Trading 212 Official API |
| **Hosting** | Render.com |

---

## 🔗 Useful Links

- **DEMO Frontend:** https://trading-212-automation-front-end.onrender.com
- **DEMO Backend:** https://trading212-backend.onrender.com
- **PROD Frontend:** https://trading212-frontend-real.onrender.com
- **PROD Backend:** https://trading212-backend-prod.onrender.com
- **GitHub:** https://github.com/joulfodayres/Trading212
- **Supabase:** https://supabase.com

---

## 🚀 Deployment

Fully automated:
- Push to `main` on GitHub
- Render auto-builds and deploys
- Frontend: ~10-15 min
- Backend: ~5-10 min

---

## 📁 Project Structure

```
Trading212/
├── STATUS.md           ← Current status
├── README.md           ← This file
├── CLAUDE.md           ← Architecture guide
├── COMECA_AQUI.md      ← Quick start
│
├── backend/            # FastAPI
├── frontend/           # React + TypeScript
├── db/                 # SQL schemas
├── docs/               # Developer docs
└── _archive/           # Old files
```

---

## 🧪 Quick Test

### Health check
```bash
curl https://trading212-backend.onrender.com/health
```

### View API docs
```
https://trading212-backend.onrender.com/docs
```

---

## 🔐 Security

- ✅ JWT authentication enforced on ~35 endpoints (24h expiration)
- ✅ Encrypted API keys (Fernet)
- ✅ HTTPS/TLS automatic
- ✅ CORS configured
- ✅ Database RLS policies
- ✅ Passwords hashed
- ✅ SMTP email alerts for automation events
- ⏳ TODO: restrict T212 LIVE API key by IP (T212's UI did not support pasting the Render IP list — open follow-up)

---

## 📞 Common Issues

**Frontend not updating after deploy:**
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

**Backend 500 error:**
Check logs in Render dashboard and environment variables.

**Database connection failed:**
Verify SUPABASE_URL and SUPABASE_KEY in .env

---

## 📝 Recent Changes

- ✅ **Phase 4 Complete:** APScheduler automation engine implemented
  - SchedulerService lifecycle management
  - AutomationEngine with 3-phase cycle
  - T212Service wrapper for API calls
  - Background automation running every 15s
  
- ✅ **Portfolio Sync Endpoint:** POST /api/isins/sync
  - Fetches positions from Trading 212 API
  - Updates ISIN database with latest data
  - Used by frontend for real-time updates
  
- ✅ Upgraded modal to Trading 212 style design
- ✅ Removed toast notifications
- ✅ Simplified to single-user (no user_id)
- ✅ Fixed automation toggle bugs
- ✅ Implemented strategy selection

See **`STATUS.md`** for full timeline.

---

## 🎯 Next Steps

1. ✅ **Phase 4:** Grid Trading Automation Engine (DONE ✅)
2. 🚧 **Phase 5:** Backlog Features (60% complete)
   - Quick wins (#9, #6): 2-3 hours
   - Features (#2, #3): 16 hours
   - Strategic (#11, #10): 17 hours
3. 🔮 **Phase 6:** Production Polish (Real auth, WebSockets, monitoring)
4. 🚀 **Phase 7:** Expansion (Live mode, more strategies, mobile)

### Immediate Priorities
- [ ] Item #9: Smart validation messages (1.5h)
- [ ] Item #6: Rename Render projects (0.5h)
- [ ] SQL: Fix `automation_status` CHECK constraint (for P/X states)

---

**Version:** 0.6.0-beta (DEMO + PROD both live; auth, trading safety, SMTP alerts shipped)
**Updated:** 2026-09-27
**Status:** ✅ Production Ready | 🟢 DEMO + PROD Live | 🔐 Auth Enforced

