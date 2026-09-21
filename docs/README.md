# Trading 212 Bot - Knowledge Base Index

## 📚 Documentation Overview

This Knowledge Base contains comprehensive documentation for the Trading 212 Bot project. Below is a guide to each document.

### 1. **KNOWLEDGE_BASE.md** - Start Here! 🎯
**Overview and Project Guide**
- Project status and tech stack
- High-level architecture diagram
- Phases completed (1-5)
- Database schema for all tables
- API endpoints by category
- 3-phase automation engine logic
- Key concepts (Grid Trading, trades_balance, etc.)

**Use when:** You need a general overview or want to understand how everything fits together.

---

### 2. **API_REFERENCE.md** - For API Integration
**Complete API Documentation**
- Base URLs (production + local)
- Authentication headers
- All endpoints grouped by feature:
  - Strategies management (CRUD + parameters)
  - ISINs management (sync, automation)
  - Automation control (enable/disable, status)
- Request/response examples for every endpoint
- Error handling and status codes
- Rate limiting info
- Complete flow example (create strategy → enable automation)

**Use when:** Building frontend, testing with curl/Postman, or integrating with API.

**Examples:**
```bash
# List strategies
GET /api/v1/strategies

# Create strategy
POST /api/v1/strategies
{
  "name": "Grid Trading 1%",
  "initial_investment": 10.0
}

# Enable automation
PUT /api/v1/automation/enable
```

---

### 3. **CODE_EXAMPLES.md** - For Developers
**Real Code Snippets**
- Frontend examples:
  - API client setup (axios + interceptors)
  - Creating strategies with React hooks
  - Portfolio sync and automation setup
  - useGlobalAutomation hook example
  - Strategy selection component

- Backend examples:
  - Automation engine 3-phase cycle (complete code)
  - Strategy validation logic
  - Portfolio sync endpoint
  - Database operations

- Database examples:
  - Creating app_parameters
  - Setting up strategies and parameters
  - Linking ISINs to strategies
  - Creating and linking orders

**Use when:** Need to understand implementation details or copy/adapt code.

---

### 4. **DEVELOPMENT.md** - For Local Development
**Setup, Structure, and Workflows**
- Local setup instructions (backend + frontend)
- Project folder structure with descriptions
- Environment variables template
- Running tests (backend + frontend)
- Git workflow (branches, commits, PRs)
- Deployment process (Render auto-deploy)
- Debugging techniques
- Common issues and quick fixes
- Performance optimization tips
- Security checklist

**Use when:** Setting up local environment, making changes, or preparing to deploy.

**Quick start:**
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

---

### 5. **TROUBLESHOOTING.md** - For Problem-Solving
**Common Issues and Solutions**
- Startup issues (backend won't start, port conflicts, etc.)
- Authentication errors
- Database issues (missing columns, RLS policies)
- Automation engine problems (scheduler not running, orders not placed)
- T212 API errors (401, 429, 400)
- Frontend issues (page blank, API 404s)
- Render deployment issues
- Performance debugging
- Getting help resources

**Use when:** Something isn't working and you need to fix it.

**Example:**
```
Error: "Strategy cannot be enabled"
Solution:
1. Missing parameters for pos -1, 0, or 1
2. Go to Strategies page → select strategy
3. Add missing parameters → try again
```

---

### 6. **QUICK_REFERENCE.md** - For Quick Lookups
**Cheat Sheet and Quick Facts**
- Project URLs (frontend, backend, GitHub, Supabase)
- Local development URLs
- Key database tables (isins, strategies, orders, etc.)
- Common API endpoints summary
- Environment variables checklist
- 3-phase automation explained briefly
- Important concepts (trades_balance, is_valid, etc.)
- Common tasks with curl examples
- File locations
- Deployment checklist
- Phase 5 backlog status
- Quick command reference
- Test account credentials

**Use when:** Need to quickly find a URL, table name, endpoint, or command.

---

### 7. **REPORTS_FEATURE.md** - Activity Statement Import
**Reports Feature Documentation**
- PDF structure parsed (15 tables across Invest / CFD / Crypto)
- `imported_files` control table + 15 data tables schema
- Endpoints: POST /api/reports/upload, GET /api/reports/files, GET /api/reports/summary
- PyMuPDF parser (`report_parser.py`) logic + validation counts
- Frontend Reports page (sidebar item, upload, summary, processed-files list)

**Use when:** Working on the Reports / PDF import feature.

---

## 📖 How to Use This Knowledge Base

### For Different Roles:

**🎯 Project Manager / Stakeholder**
1. Read: KNOWLEDGE_BASE.md → Overview + Phases sections
2. Skim: QUICK_REFERENCE.md → Phase 5 backlog status

**👨‍💻 Backend Developer**
1. Read: DEVELOPMENT.md → Local setup + Project structure
2. Reference: API_REFERENCE.md + CODE_EXAMPLES.md
3. Debug: TROUBLESHOOTING.md when issues arise

**🎨 Frontend Developer**
1. Read: DEVELOPMENT.md → Frontend setup
2. Reference: API_REFERENCE.md for endpoints
3. Copy: CODE_EXAMPLES.md → Frontend examples
4. Use: QUICK_REFERENCE.md for API URLs

**🐛 Debugger / DevOps**
1. Start: TROUBLESHOOTING.md for your issue
2. Check: Logs in DEVELOPMENT.md → Debugging section
3. Reference: QUICK_REFERENCE.md for commands
4. Deep dive: KNOWLEDGE_BASE.md or CODE_EXAMPLES.md

---

## 🚀 Quick Navigation

### Find specific information:

**"How do I...?"**
- Start a local server? → DEVELOPMENT.md
- Create a strategy? → CODE_EXAMPLES.md or API_REFERENCE.md
- Fix an error? → TROUBLESHOOTING.md
- Deploy changes? → DEVELOPMENT.md → Deployment section
- Understand how Grid Trading works? → KNOWLEDGE_BASE.md → Automation Engine Logic

**"Where is...?"**
- The API documentation? → API_REFERENCE.md
- Strategy CRUD code? → CODE_EXAMPLES.md → Backend examples
- Frontend code examples? → CODE_EXAMPLES.md → Frontend examples
- The database schema? → KNOWLEDGE_BASE.md → Database Schema section
- Deployment instructions? → DEVELOPMENT.md → Deployment section

**"What is...?"**
- trades_balance? → KNOWLEDGE_BASE.md → Key Concepts
- is_valid? → QUICK_REFERENCE.md → Important Concepts
- automation_status? → QUICK_REFERENCE.md → Important Concepts
- The scheduler interval? → KNOWLEDGE_BASE.md → app_parameters table

---

## 📋 Phase 5 Status

| Item | Status | Documentation |
|------|--------|----------------|
| 1. Strategy Management | ✅ DONE | CODE_EXAMPLES.md, API_REFERENCE.md |
| 2. Upload T212 Data Files | ⏳ TODO | N/A |
| 3. Charts & Statistics | ⏳ TODO | N/A |
| 4. Global Automation Toggle | ✅ DONE | API_REFERENCE.md |
| 5. Automation Dialog | ✅ DONE | CODE_EXAMPLES.md |
| 6. Rename Render Projects | ⏳ TODO | DEVELOPMENT.md → Deployment |
| 7. Knowledge Base | ✅ DONE | THIS FILE + 5 other docs |

---

## 📞 Quick Links

- **Frontend:** https://trading212-1.onrender.com
- **Backend API:** https://trading212-4ojx.onrender.com
- **API Docs (Swagger):** https://trading212-4ojx.onrender.com/docs
- **GitHub:** https://github.com/joulfodayres/Trading212
- **Supabase Dashboard:** https://app.supabase.com

---

## 🎓 Learning Path

### Beginner (New to project)
1. KNOWLEDGE_BASE.md (Overview + Architecture)
2. QUICK_REFERENCE.md (Quick facts)
3. DEVELOPMENT.md (Local setup)

### Intermediate (Ready to code)
1. DEVELOPMENT.md (Project structure)
2. API_REFERENCE.md (API structure)
3. CODE_EXAMPLES.md (Real examples)

### Advanced (Deep dive)
1. CODE_EXAMPLES.md (Backend logic)
2. KNOWLEDGE_BASE.md (3-phase engine)
3. TROUBLESHOOTING.md (Edge cases)

---

## 📝 How to Update This Knowledge Base

All docs are in `/docs/` folder:
```
docs/
├── KNOWLEDGE_BASE.md      # Main overview
├── API_REFERENCE.md       # API documentation
├── CODE_EXAMPLES.md       # Code snippets
├── DEVELOPMENT.md         # Development guide
├── TROUBLESHOOTING.md     # Problem-solving
└── QUICK_REFERENCE.md     # Quick lookup
```

When you make changes:
1. Update relevant documentation file
2. Update QUICK_REFERENCE.md if needed
3. Commit with message: `docs: Update [topic]`

---

## 🤝 Contributing

If you find:
- **Missing information:** Add it to the relevant doc
- **Outdated content:** Update it immediately
- **Unclear explanation:** Rewrite for clarity
- **New endpoints/features:** Document in API_REFERENCE.md

Keep docs in sync with code!

---

**Last Updated:** 2026-09-21
**Total Documentation:** 3,000+ lines across 7 documents
**Status:** Complete and production-ready
