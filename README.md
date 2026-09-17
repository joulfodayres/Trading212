# Trading 212 Bot - MVP

**Status:** ✅ **Phase 3 Complete - Moving to Phase 4** 🚀  
**Last Update:** 2026-09-17  
**Version:** 0.3.0

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

### Essential Reading
| Document | Purpose |
|----------|---------|
| **`STATUS.md`** | Current project status & timeline |
| **`CLAUDE.md`** | Architecture, database schema, tech stack |
| **`COMECA_AQUI.md`** | Quick start & troubleshooting |

### Detailed Guides
| Document | Topic |
|----------|-------|
| **`docs/README.md`** | Documentation index |
| **`docs/t212-api/`** | Trading 212 API analysis (Phase 4) |

---

## ✅ What Works Now (Phase 3)

### Core Features
- ✅ Live ISINs data from Trading 212 API
- ✅ Dashboard with real-time positions
- ✅ Automation toggle (enable/disable per ISIN)
- ✅ Strategy selection dialog
- ✅ Audit trail for all changes
- ✅ Modal dialog (Trading 212 style UI)

### Technical
- ✅ Backend: FastAPI with 25+ endpoints
- ✅ Frontend: React 18 + TypeScript
- ✅ Database: PostgreSQL (Supabase)
- ✅ Auth: JWT tokens
- ✅ Deployment: Auto-deploy on git push
- ✅ Encryption: API keys encrypted
- ✅ Logging: Full audit trail

---

## 🚧 Next Phase (Phase 4: Grid Trading)

Priority tasks to implement automation:

1. **OrderHistoryManager**
   - Incremental sync of order history
   - Validate ordering assumptions
   - Handle pagination

2. **APScheduler Setup**
   - Polling every 5 seconds
   - Monitor positions
   - Check strategy triggers

3. **Grid Trading Logic**
   - Buy at -1% below average
   - Sell at +1% above average
   - Risk management (max position, stop-loss)

4. **Validation**
   - Test with real data (DEMO account)
   - Verify order history ordering
   - Rate limit handling

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

- ✅ Upgraded modal to Trading 212 style design
- ✅ Removed toast notifications
- ✅ Simplified to single-user (no user_id)
- ✅ Fixed automation toggle bugs
- ✅ Implemented strategy selection

See **`STATUS.md`** for full timeline.

---

## 🎯 Next Steps

1. Implement Grid Trading strategy
2. Setup APScheduler polling
3. Test with real data
4. Deploy to live (with controls)

---

**Version:** 0.3.0 (MVP Phase 3)  
**Updated:** 2026-09-17  
**Status:** ✅ Functional | 🚧 Advancing to Phase 4

For detailed status, see **`STATUS.md`**.

