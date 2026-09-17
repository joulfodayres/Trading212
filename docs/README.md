# Documentation Directory

**Updated:** 2026-09-17  
**Active Phase:** 3 (UI & Automation)

---

## 📚 Current Documentation (Phase 3)

### Essential Guides
- **`../STATUS.md`** - Current project status
- **`../README.md`** - Project overview
- **`../CLAUDE.md`** - Architecture & tech stack

### Trading 212 API (Phase 4 Reference)
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

### Phase 4 Implementation (Grid Trading)
- Start here: `t212-api/API_ANALYSIS.md`
- Implementation guide: `t212-api/INCREMENTAL_SYNC.md`
- Parameter reference: `t212-api/HISTORY_ORDERS_PARAMS.md`

### Architecture
- Read: `../CLAUDE.md`
- Database: Check `../db/supabase_schema.sql`
- Backend code: Check `../backend/routes/`

### Deployment
- Status: Check `../STATUS.md`
- Quick start: Check `../COMECA_AQUI.md`
- API docs: https://trading212-4ojx.onrender.com/docs

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
