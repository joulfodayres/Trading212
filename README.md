# Trading 212 Bot - MVP

**Status:** ✅ **Phase 4 Complete - Automation Engine Live** 🚀  
**Last Update:** 2026-09-20  
**Version:** 0.4.0

Automação de trading algorítmico integrada com Trading 212 API, acessível via browser de qualquer lugar.

---

## ⚡ Quick Start

### 🌐 Access Online (Production)
```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com
API Docs: https://trading212-4ojx.onrender.com/docs
```

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
**👉 Open [`docs/index.html`](docs/index.html) in your browser for the complete documentation system**

- Beautiful, searchable documentation hub
- 7 main sections (Getting Started, Architecture, API, Development, Deployment, Knowledge Base, Troubleshooting)
- Real-time search (Cmd/Ctrl+K)
- Dark mode support
- Mobile-responsive design
- Learning paths for different roles

### Essential Reading
| Document | Purpose |
|----------|---------|
| **`docs/index.html`** | 🎯 **Main documentation hub** (start here!) |
| **`docs/KNOWLEDGE_BASE.md`** | Complete project overview + architecture |
| **`docs/DEVELOPMENT.md`** | Local setup & development workflow |
| **`docs/API_REFERENCE.md`** | Complete API endpoint documentation |
| **`STATUS.md`** | Current project status & timeline |
| **`CLAUDE.md`** | Architecture, database schema, tech stack |
| **`COMECA_AQUI.md`** | Quick start & troubleshooting |

### Detailed Guides
| Document | Topic |
|----------|-------|
| **`docs/DOCUMENTATION_STRUCTURE.md`** | How documentation is organized |
| **`docs/TROUBLESHOOTING.md`** | Common issues & solutions |
| **`docs/CODE_EXAMPLES.md`** | Real code snippets |
| **`docs/QUICK_REFERENCE.md`** | Quick lookup cheat sheet |
| **`docs/t212-api/`** | Trading 212 API analysis (Phase 4) |

---

## ✅ What Works Now (Phase 4)

### Core Features
- ✅ **Live ISINs data** from Trading 212 API
- ✅ **Dashboard with real-time positions**
- ✅ **Automation toggle** (enable/disable per ISIN)
- ✅ **Strategy selection dialog**
- ✅ **Audit trail** for all changes
- ✅ **Modal dialog** (Trading 212 style UI)
- ✅ **APScheduler automation engine** (15s interval)
- ✅ **Portfolio sync endpoint** (POST /api/isins/sync)
- ✅ **3-phase automation cycle** (setup → monitor → fill handling)
- ✅ **Grid Trading strategy** (initial implementation)

### Technical
- ✅ Backend: FastAPI with 30+ endpoints
- ✅ Frontend: React 18 + TypeScript
- ✅ Database: PostgreSQL (Supabase)
- ✅ Auth: JWT tokens
- ✅ Deployment: Auto-deploy on git push
- ✅ Encryption: API keys encrypted
- ✅ Logging: Full audit trail + automation logs
- ✅ **APScheduler:** Background automation running 24/7
- ✅ **SchedulerService:** Lifecycle management
- ✅ **AutomationEngine:** 3-phase strategy execution

---

## 🚧 Next Phase (Phase 5: Features & Polish)

Priority backlog items (5 items):

1. **🎚️ Global Automation Toggle** (Low complexity, 2-3h)
   - ON/OFF button in header for engine control
   - Status visual indicator
   - Confirmation dialog

2. **🎛️ Strategy Parameter Tables** (Medium complexity, 4-6h)
   - Editable UI for grid parameters per position
   - CRUD endpoints for strategy_parameters
   - Real-time validation

3. **📁 Upload Real T212 Data** (High complexity, 6-8h)
   - CSV/Excel import from Trading 212
   - Parser + validator
   - Batch ISIN + history import

4. **📊 Charts & Statistics** (High complexity, 8-10h)
   - Equity curve, P&L, drawdown graphs
   - Performance metrics
   - Trade history table

5. **💬 Automation Preview Dialog** (Medium complexity, 3-4h)
   - Show strategy details before activation
   - Parameter summary
   - Confirmation step

See **`BACKLOG.md`** for full details.

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

- **Frontend:** https://trading212-1.onrender.com
- **Backend:** https://trading212-4ojx.onrender.com
- **API Docs:** https://trading212-4ojx.onrender.com/docs
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
curl https://trading212-4ojx.onrender.com/health
```

### View API docs
```
https://trading212-4ojx.onrender.com/docs
```

---

## 🔐 Security

- ✅ JWT authentication (24h expiration)
- ✅ Encrypted API keys (Fernet)
- ✅ HTTPS/TLS automatic
- ✅ CORS configured
- ✅ Database RLS policies
- ✅ Passwords hashed
- ⏳ TODO: Rate limiting on endpoints

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

1. ✅ Phase 4: Grid Trading Automation Engine (DONE)
2. 🚧 Phase 5: Backlog Features (Global ON/OFF, Parameter UI, Data Import, Charts)
3. Phase 6: Real-time WebSocket updates
4. Phase 7: Live trading mode

For detailed status, see **`STATUS.md`**.

---

**Version:** 0.4.0 (MVP Phase 4 - Automation Engine)  
**Updated:** 2026-09-20  
**Status:** ✅ Functional | 🚧 Phase 5 Backlog Ready

