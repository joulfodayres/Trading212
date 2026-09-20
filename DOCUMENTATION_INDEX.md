# Documentation Index

**Updated:** 2026-09-20  
**Phase:** 4 (Automation Engine) ✅ COMPLETE

---

## 📖 Start Here

| Document | Duration | Purpose |
|----------|----------|---------|
| **README.md** | 2 min | Project overview & quick links |
| **STATUS.md** | 5 min | Current phase status & timeline |
| **COMECA_AQUI.md** | 10 min | Quick start + troubleshooting |

---

## 🏗️ Architecture & Design

| Document | Topic |
|----------|-------|
| **CLAUDE.md** | Complete architecture, database schema, API stack |
| **docs/ARCHITECTURE.md** | System design & components (if exists) |

---

## 🎯 Phase Documentation

### Phase 4 (Complete): Grid Trading Automation ✅
- ✅ APScheduler setup (embedded in FastAPI)
- ✅ SchedulerService lifecycle management
- ✅ AutomationEngine 3-phase cycle
- ✅ T212Service API wrapper
- ✅ Portfolio sync endpoint
- ✅ Automation monitoring

**Files:**
- `PHASE4_ARCHITECTURE.txt` - Architectural decisions
- `PHASE4_IMPLEMENTATION_PLAN.md` - Implementation guide
- `STATUS.md` - Phase 4 status (see section)
- `backend/services/scheduler.py`
- `backend/services/automation_engine.py`
- `backend/services/t212_service.py`
- `backend/routes/automation.py`

### Phase 5 (Next): Features & Backlog 🚧
- [ ] Global Automation Toggle
- [ ] Strategy Parameter Tables
- [ ] Automation Preview Dialog
- [ ] Upload Real T212 Data
- [ ] Charts & Statistics

**Files:**
- `BACKLOG.md` - 5 prioritized features with timelines

---

## 📚 Complete File List

### Root Level
```
├── README.md                    # Project overview
├── STATUS.md                    # Current status & timeline
├── CLAUDE.md                    # Architecture guide
├── COMECA_AQUI.md              # Quick start
├── render.yaml                  # Render deployment config
└── .gitignore                   # Git ignore rules
```

### Backend (`backend/`)
```
├── main.py                      # FastAPI entry point (with lifespan)
├── requirements.txt             # Python dependencies
├── config/settings.py           # Environment settings
├── auth/crypto.py              # Encryption (Fernet)
├── api/trading212.py           # T212 API client
├── models/db.py                # Database models
├── models/schemas.py           # Pydantic schemas
├── routes/                     # API endpoints
│   ├── auth.py
│   ├── isins.py
│   ├── config.py
│   ├── positions.py
│   ├── orders.py
│   └── automation.py          # ✅ NEW (Phase 4)
├── services/                   # ✅ NEW (Phase 4)
│   ├── scheduler.py           # SchedulerService
│   ├── automation_engine.py   # AutomationEngine
│   └── t212_service.py        # T212 wrapper
├── db/supabase_client.py       # Supabase wrapper
└── engine/                     # (Legacy, see services/)
```

### Frontend (`frontend/`)
```
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Router
│   ├── pages/                   # Page components
│   ├── components/              # Reusable components
│   ├── api/client.ts            # API client
│   ├── stores/authStore.ts      # Zustand state
│   └── hooks/useAutomation.ts   # Custom hooks
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### Database (`db/`)
```
├── supabase_schema.sql          # Table definitions
├── simplify_to_singleuser.sql  # Single-user migration
├── app_parameters_table.sql    # ✅ NEW (Phase 4)
└── migrations/                 # (Not used - Supabase manages schema)

### Documentation (`docs/`)
```
├── README.md                    # Docs index (updated Phase 4)
├── t212-api/                    # Trading 212 API analysis
│   ├── API_ANALYSIS.md
│   ├── HISTORY_ORDERS_PARAMS.md
│   ├── INCREMENTAL_SYNC.md
│   └── ... (more API docs)
└── _archive/                    # Old documentation
```

### Root Documentation
```
├── README.md                           # ✅ Updated
├── STATUS.md                           # ✅ Updated (Phase 4)
├── CLAUDE.md                           # ✅ Updated (Phase 4)
├── BACKLOG.md                          # ✅ NEW (Phase 5 priorities)
├── DOCUMENTATION_INDEX.md              # ← This file
├── PHASE4_ARCHITECTURE.txt             # ✅ NEW (Decisions)
├── PHASE4_IMPLEMENTATION_PLAN.md       # ✅ NEW (Guide)
├── COMECA_AQUI.md                      # Quick start
├── render.yaml                         # Render config
└── .gitignore                          # Git rules

---

## 🔗 Cross-References

### By Task

**I want to...**

- **Add a new API endpoint:**
  1. Read `CLAUDE.md` (architecture section)
  2. Check `backend/routes/*.py` for patterns
  3. Add schema in `backend/models/schemas.py`
  4. Add route in `backend/routes/*.py`

- **Fix a frontend bug:**
  1. Check `frontend/src/components/` for the component
  2. Review `frontend/src/hooks/` for state logic
  3. Test locally with `npm run dev`

- **Understand T212 API:**
  1. Read `docs/t212-api/API_ANALYSIS.md`
  2. Check `backend/api/trading212.py` for implementation
  3. Review `docs/t212-api/HISTORY_ORDERS_PARAMS.md` for specific endpoints

- **Understand the Scheduler:**
  1. Read `PHASE4_ARCHITECTURE.txt` (questions 1-6)
  2. Check `backend/services/scheduler.py` (SchedulerService)
  3. Review `backend/services/automation_engine.py` (3-phase cycle)
  4. Test: `GET /api/v1/automation/status`

- **Deploy a change:**
  1. Commit to `main` branch
  2. GitHub auto-triggers Render
  3. Check logs in Render dashboard
  4. Verify at https://trading212-1.onrender.com

- **Debug database issues:**
  1. Visit Supabase dashboard
  2. Check RLS policies
  3. Run queries in Query Editor
  4. Review table schemas

- **Implement Phase 5 feature:**
  1. Check `BACKLOG.md` for detailed requirements
  2. Create branch: `feature/phase5-xyz`
  3. Update backend, frontend, database as needed
  4. Test locally before deploying
  5. Create PR with reference to backlog item
  4. Setup APScheduler in `backend/engine/scheduler.py`

---

## 🗂️ Archived Documentation

Older docs moved to `_archive/`:
- Phase 1 (Setup) - `_archive/phase-1/`
- Phase 2 (Backend & DB) - `_archive/phase-2/`
- Session reports - `_archive/sessions/`
- Old implementation guides - `_archive/guides/`

---

## 📝 Document Types

### Technical Docs
- `CLAUDE.md` - Architecture, schema, tech stack
- `docs/t212-api/*.md` - API analysis & implementation

### Quick Guides
- `README.md` - Overview
- `COMECA_AQUI.md` - Quick start
- `STATUS.md` - Timeline & progress

### Administrative
- `docs/DEPLOYMENT.md` - Deployment procedures
- `docs/SECURITY.md` - Security checklist
- `docs/CONTRIBUTING.md` - Contribution guide (if created)

---

## 🔍 Search by Topic

### Authentication
- `CLAUDE.md` → Auth section
- `backend/routes/auth.py`
- `backend/auth/` folder

### Database
- `CLAUDE.md` → Database schema section
- `db/supabase_schema.sql`
- `backend/models/db.py`

### Trading 212 API
- `docs/t212-api/API_ANALYSIS.md` (complete reference)
- `backend/api/trading212.py` (Python implementation)
- `CLAUDE.md` → T212 API section

### Frontend Components
- `frontend/src/components/` - All components
- `frontend/src/hooks/useAutomation.ts` - Custom hooks
- `frontend/src/pages/` - Page templates

### Deployment
- `render.yaml` - Render config
- `CLAUDE.md` → Deployment section
- `docs/DEPLOYMENT.md` - Procedures (if exists)

---

## 📊 Document Map

```
README.md (overview)
    ↓
STATUS.md (current phase)
    ↓
COMECA_AQUI.md (quick start)
    ↓
CLAUDE.md (deep dive)
    ├─→ backend/routes/ (API implementation)
    ├─→ backend/models/ (schemas & DB)
    ├─→ frontend/src/ (React components)
    └─→ db/supabase_schema.sql (database)
    
docs/t212-api/ (Trading 212 API details)
    ├─→ API_ANALYSIS.md (all endpoints)
    ├─→ INCREMENTAL_SYNC.md (Phase 4)
    └─→ HISTORY_ORDERS_PARAMS.md (endpoint reference)

_archive/ (old docs & cancelled features)
```

---

## 🔄 How to Update Docs

1. **After implementing a feature:**
   - Update `STATUS.md` with completion
   - Add example/guide in `docs/`

2. **After fixing a bug:**
   - Document solution in relevant guide
   - Add to troubleshooting section

3. **Before deploying:**
   - Verify `STATUS.md` is current
   - Confirm `README.md` links are valid

4. **When archiving old work:**
   - Move to `_archive/` folder
   - Keep reference in this index

---

## ✅ Documentation Checklist

Current status:
- ✅ README.md - Up to date
- ✅ STATUS.md - Current
- ✅ CLAUDE.md - Architecture guide
- ✅ COMECA_AQUI.md - Quick start
- ✅ docs/t212-api/ - Phase 4 reference
- ⏳ docs/PHASE_4_GUIDE.md - To create (Phase 4 implementation)
- ⏳ docs/CONTRIBUTING.md - To create
- ⏳ docs/SECURITY.md - To create

---

**This index is the authoritative guide to all documentation.**

If a document is not listed here, it's either archived or deprecated.

**Last Updated:** 2026-09-17
