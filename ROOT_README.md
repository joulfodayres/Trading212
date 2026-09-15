# Trading 212 Bot - MVP (Production Ready)

**Status:** ✅ **LIVE IN PRODUCTION** (Phase 2 Complete)

---

## 🚀 Quick Start

```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com/docs
```

**Login with your account (created during registration)**

---

## 📁 Folder Structure

```
Trading212/
├── backend/                    # FastAPI Backend (Python)
├── frontend/                   # React Frontend (TypeScript)
├── db/                        # Database schemas
├── docs/                      # Developer documentation
├── _archive/                  # Legacy scripts & logs
│   ├── _scripts/             # Setup & test scripts (internal)
│   └── _logs/                # Old diagnostics & fixes
└── [Root files]              # Essential files only
```

### Root Files Only:
- **README.md** - This file
- **CLAUDE.md** - Technical documentation
- **INDEX.md** - Documentation navigation
- **CHECKLIST_FINAL.md** - Feature status
- **COMECA_AQUI.md** - Quick start guide
- **.gitignore, render.yaml, etc.** - Configuration

---

## 📚 Documentation

Start here: **[INDEX.md](./INDEX.md)** or **[docs/README.md](./docs/README.md)**

Key documents:
- 🏗️ **Architecture:** `docs/architecture/`
- 🔌 **API Guide:** `docs/api/`
- 💻 **Frontend:** `docs/frontend/`
- 🚀 **Deployment:** `docs/deployment/`

---

## 🎯 Features Implemented

✅ **Phase 1: Infrastructure**
- GitHub + Render + Supabase setup
- Frontend/Backend scaffolding

✅ **Phase 2: Authentication & CRUD**
- JWT login/register (Supabase Auth)
- ISIN CRUD endpoints
- Frontend real API integration
- User isolation (RLS)

⏳ **Phase 3: Automation (Next)**
- Grid Trading strategy
- APScheduler integration
- Trade execution

---

## 🔑 How It Works

1. **You Register** → Account created in Supabase
2. **You Login** → JWT token for 24h
3. **You Add ISINs** → Monitored positions from Trading 212
4. **You Configure** → T212 credentials (encrypted)
5. **Automation Runs** → Bot executes Grid Trading (Phase 3)

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind |
| **Backend** | FastAPI + Python 3.14 + Uvicorn |
| **Database** | PostgreSQL (Supabase) + RLS |
| **Auth** | Supabase Auth (JWT) |
| **Hosting** | Render (Cloud) |
| **Version Control** | GitHub |

---

## 🛠️ For Developers

### Local Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables
See `backend/.env.example` and `frontend/.env.production`

### Testing
- Auth: `docs/api/JWT_TESTING_GUIDE.md`
- CRUD: Use Frontend or API docs at `/docs`

---

## 📞 Support

- **Status:** Check `CHECKLIST_FINAL.md`
- **Troubleshooting:** See `docs/deployment/`
- **Architecture questions:** Read `docs/architecture/IMPLEMENTATION_SUMMARY.md`

---

## 📄 Current Session Status

Last update: **2026-09-15 23:45 UTC**

✅ **Complete:**
- Environment variables configured in Render
- Backend lazy initialization (Supabase, T212 clients)
- Frontend API URL fixed (removed duplicate `/api`)
- Login/Register working
- JWT authentication functional
- RLS policies active

🎯 **Next (Phase 3):**
- ISIN CRUD integration with real user
- T212 credentials encryption
- Grid Trading automation
- Dashboard with real data

---

**User:** Only YOU use this system  
**Mode:** Development/Testing  
**Deployment:** Render (auto-deploy on git push)

🚀 Ready to continue tomorrow!
