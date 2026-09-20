# Trading 212 Bot - Development Guide

## Local Setup

### Prerequisites
- Python 3.14+
- Node.js 18+
- PostgreSQL (or use Supabase)
- Git

### Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your values:
# - SUPABASE_URL
# - SUPABASE_KEY
# - T212_API_KEY
# - T212_API_SECRET
# - etc

# Run migrations (if any)
# alembic upgrade head

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## Project Structure

### Backend (`backend/`)

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
│
├── config/
│   └── settings.py           # Pydantic settings (reads .env)
│
├── db/
│   ├── supabase_client.py    # Supabase connection
│   └── migrations/           # Alembic migrations (not used - BD in cloud)
│
├── models/
│   ├── db.py                 # SQLAlchemy models
│   └── schemas.py            # Pydantic schemas
│
├── routes/
│   ├── auth.py               # Authentication endpoints
│   ├── isins.py              # ISIN CRUD
│   ├── config.py             # Configuration
│   ├── automation.py         # Automation control
│   └── strategies.py         # Strategy management
│
├── services/
│   ├── scheduler.py          # APScheduler lifecycle
│   ├── automation_engine.py  # 3-phase automation logic
│   └── t212_service.py       # T212 API wrapper
│
├── api/
│   └── trading212.py         # Trading212Client HTTP wrapper
│
└── tests/
    └── test_t212_api.py      # API integration tests
```

### Frontend (`frontend/`)

```
frontend/
├── index.html                 # HTML entry point
├── package.json              # npm dependencies
├── vite.config.ts            # Vite build config
├── tsconfig.json             # TypeScript config
│
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Main app routing
│   ├── index.css             # Global styles + Tailwind
│   │
│   ├── pages/
│   │   ├── LoginPage.tsx     # Login
│   │   ├── DashboardPage.tsx # Main dashboard
│   │   ├── StrategiesPage.tsx # Strategy management
│   │   ├── ConfigPage.tsx    # Configuration
│   │   └── HistoryPage.tsx   # Trade history
│   │
│   ├── components/
│   │   ├── Sidebar.tsx       # Navigation + global toggle
│   │   ├── ISINTable.tsx     # ISIN list
│   │   ├── AutomationBottomSheet.tsx # Dialog
│   │   └── ui/               # Reusable components
│   │
│   ├── api/
│   │   ├── client.ts         # Axios instance
│   │   └── index.ts          # API wrappers
│   │
│   ├── hooks/
│   │   ├── useAutomation.ts      # ISIN automation toggle
│   │   └── useGlobalAutomation.ts # Global automation control
│   │
│   └── stores/
│       └── authStore.ts      # Zustand auth store
```

---

## Environment Variables

### Backend (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Trading 212
T212_API_KEY=your-api-key
T212_API_SECRET=your-api-secret
T212_ENVIRONMENT=demo  # or 'live'
T212_BASE_URL=https://demo.trading212.com/api/v0

# FastAPI
FASTAPI_ENV=development  # or 'production'
FASTAPI_DEBUG=True
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Encryption (Fernet key)
ENCRYPTION_KEY=mhRLQKMKc2d5fJ7pX8vN3qZ9wK1mL2nO3pR4sT5uV6w=

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Trading 212 Bot
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_t212_api.py::test_login
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# E2E tests (if configured)
npm run test:e2e
```

---

## Git Workflow

### Branching Strategy

- `main` - Production-ready code (auto-deploys to Render)
- `develop` - Development branch (merge before release)
- `feature/*` - Feature branches (branch off develop)
- `bugfix/*` - Bug fixes (branch off main)

### Commit Messages

```
feat: Add strategy CRUD endpoints
fix: Handle missing position fields
docs: Update API reference
refactor: Simplify automation logic
test: Add strategy validation tests
chore: Update dependencies
```

### Creating a Pull Request

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git commit -m "feat: Add new feature"

# Push to GitHub
git push origin feature/my-feature

# Create PR on GitHub
gh pr create --title "Add new feature" --body "Description"
```

---

## Deployment

### Frontend Deployment (Render)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy: Update frontend"
   git push origin main
   ```

2. **Render Auto-Deploy:**
   - Render watches main branch
   - Builds with: `npm run build`
   - Serves from: `dist/`
   - Takes ~10-15 minutes

3. **Preview URL:** https://trading212-1.onrender.com

### Backend Deployment (Render)

1. **Same GitHub push triggers backend**
2. **Render builds with:** `pip install -r requirements.txt`
3. **Runs:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Takes ~5-10 minutes**

5. **Preview URL:** https://trading212-4ojx.onrender.com

### Database (Supabase)

Database is cloud-based, no deployment needed:
- Schema: Update SQL directly in Supabase dashboard
- Migrations: Manual (or use Alembic locally, but not sync'd to cloud)
- Backups: Automatic daily

---

## Debugging

### Backend Debugging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload

# Check scheduler status
curl http://localhost:8000/api/v1/automation/status

# Check database connection
python -c "from db.supabase_client import get_db; print(get_db())"

# View logs (Render dashboard)
# - Click on backend service
# - View "Logs" tab
```

### Frontend Debugging

```bash
# Browser console (F12)
# - Network tab: Check API calls
# - Console: Check JavaScript errors
# - Application: Check localStorage

# React DevTools browser extension
# - Component tree
# - Props inspection
# - State tracking

# VS Code Debugger
# - Add breakpoints
# - F5 to start debugging
```

### Common Issues

**"Could not connect to database"**
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Verify Supabase project is online
- Check network connectivity

**"Rate limit reached (429)"**
- T212 API has rate limits
- Backend handles automatically with exponential backoff
- Check logs for retry attempts

**"Strategy cannot be enabled"**
- Missing parameters for pos -1, 0, or 1
- Check strategy_parameters table
- Add missing parameters before enabling

**"Automation not running"**
- Check if grid_trading_enabled in app_parameters is true
- Check scheduler status: GET /api/v1/automation/status
- Check backend logs for errors

---

## Performance Optimization

### Backend

```python
# Use connection pooling
# Already configured in Supabase client

# Cache strategy parameters
# Cache for 5 minutes to avoid repeated DB queries

# Batch database operations
# Update multiple ISINs in single transaction

# Use indexes
# Already created on: isins(isin), isins(user_id), orders(isin_id)
```

### Frontend

```typescript
// Code splitting
const StrategiesPage = lazy(() => import('./pages/StrategiesPage'))

// Memoization
const MemoizedISINTable = memo(ISINTable)

// Lazy image loading
<img loading="lazy" src={url} />

// API response caching
// Use React Query or SWR for automatic caching
```

---

## Security Checklist

- ✅ API keys encrypted in database (Fernet)
- ✅ JWT tokens for authentication
- ✅ CORS restricted (set allowed origins in production)
- ✅ HTTPS enforced (Render automatic)
- ✅ SQL injection protected (SQLAlchemy ORM)
- ✅ CSRF protection (TODO: Add if needed)
- ✅ Rate limiting (T212 API limits respected)
- ✅ Input validation (Pydantic schemas)
- ⏳ Add API key rotation (TODO)
- ⏳ Add audit logging (TODO)
- ⏳ Add 2FA support (TODO)

---

## Phase 5 Progress

### Completed ✅
1. Strategy Management (CRUD + validation)
2. Global Automation Toggle
3. Automation Dialog for ISINs

### In Progress 🔄
4. Knowledge Base (THIS FILE)

### Todo ⏳
5. Upload T212 Data Files
6. Charts & Statistics Dashboard
7. Rename Render Projects

---

## Useful Commands

```bash
# Database
# Export data
pg_dump -U postgres -d mydb > backup.sql

# Import data
psql -U postgres -d mydb < backup.sql

# Frontend
npm run build      # Production build
npm run preview    # Preview production build locally
npm run type-check # TypeScript validation

# Backend
python -m pytest   # Run tests
python -m black .  # Format code
python -m pylint . # Lint code

# Git
git log --oneline                  # View commits
git diff main develop              # Compare branches
git cherry-pick <commit>           # Apply commit from another branch
git rebase main                    # Rebase onto main
git force-push                     # Force push (use carefully!)
```

---

**Last Updated:** 2026-09-20
**Status:** Development guide complete
