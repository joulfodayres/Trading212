# Documentation Directory

**Updated:** 2026-09-20  
**Active Phase:** 4 (Automation Engine) ✅ COMPLETE

---

## 📚 Current Documentation (Phase 4)

### Essential Guides
- **`../STATUS.md`** - Current project status & Phase 4 completion
- **`../README.md`** - Project overview & backlog
- **`../CLAUDE.md`** - Architecture & tech stack
- **`../BACKLOG.md`** - Phase 5 backlog (5 prioritized features)

### Phase 4 Implementation (Grid Trading Automation)
- **`../PHASE4_ARCHITECTURE.txt`** - Architectural decisions
- **`../PHASE4_IMPLEMENTATION_PLAN.md`** - Implementation guide
- **Backend Code:**
  - `backend/services/scheduler.py` - SchedulerService
  - `backend/services/automation_engine.py` - 3-phase cycle logic
  - `backend/services/t212_service.py` - T212 API wrapper
  - `backend/routes/automation.py` - Monitoring endpoints

### Trading 212 API Reference
- **`t212-api/API_ANALYSIS.md`** - Complete API endpoint reference
- **`t212-api/HISTORY_ORDERS_PARAMS.md`** - /history/orders parameters
- **`t212-api/INCREMENTAL_SYNC.md`** - Order history sync strategy
- **`t212-api/...`** - Other API documentation

---

## 🗂️ Folder Structure

```
docs/
├── README.md                    # ← This file
├── t212-api/                    # Trading 212 API analysis
│   ├── API_ANALYSIS.md
│   ├── HISTORY_ORDERS_PARAMS.md
│   ├── INCREMENTAL_SYNC.md
│   └── ...
└── _archive/                    # Old documentation
    ├── phase-2/                 # Backend & DB setup
    ├── phase-3/                 # UI & UX fixes
    └── sessions/                # Historical session reports
```

---

## 🔍 Quick Links

### Phase 4 Implementation (Grid Trading) ✅ COMPLETE
- Architecture: `../PHASE4_ARCHITECTURE.txt`
- Implementation: `../PHASE4_IMPLEMENTATION_PLAN.md`
- T212 API Reference: `t212-api/API_ANALYSIS.md`
- Status: `../STATUS.md` (see Phase 4 section)

### Phase 5 Backlog (Next Features)
- **`../BACKLOG.md`** - 5 prioritized features with timelines
- Priority 1: Global Automation Toggle (2-3h)
- Priority 2: Strategy Parameter Tables (4-6h)
- Priority 3: Automation Preview Dialog (3-4h)

### Architecture
- Read: `../CLAUDE.md`
- Database: Check `../db/supabase_schema.sql`
- Backend code: Check `../backend/routes/`

### Deployment
- Status: Check `../STATUS.md`
- Quick start: Check `../COMECA_AQUI.md`
- API docs: https://trading212-4ojx.onrender.com/docs
- Backend health: https://trading212-4ojx.onrender.com/health

### Scheduler & Automation (Phase 4 Specific)
- How it works: `../PHASE4_ARCHITECTURE.txt` (Q1-Q6)
- Lifecycle: `backend/main.py` (lifespan hooks)
- Monitoring: `backend/routes/automation.py`
- Performance: Cycle time ~9s (15s interval)

---

## 📝 File Types

- `API_*.md` - Trading 212 API documentation
- `INCREMENTAL_SYNC.md` - Phase 4 implementation guide
- `STRATEGY_*.md` - Strategy design documents
- `SIMPLIFY_TO_SINGLEUSER.md` - Database migration guide

---

## 🚀 Contributing

When adding new documentation:
1. Place in appropriate subfolder
2. Add link to this README.md
3. Update `../DOCUMENTATION_INDEX.md`
4. Commit with clear message

---

**For complete doc index, see `../DOCUMENTATION_INDEX.md`**
