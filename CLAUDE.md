# Trading 212 Bot - MVP

**Projeto de automação de trading algorítmico integrado com a plataforma Trading 212 via API oficial.**

Status: **MVP EM PRODUÇÃO — DEMO + PROD LIVE** 🚀 (Phase 4 completa; Phase 5 em curso — auth, PROD environment, trading limits e SMTP alerts já implementados)

---

## 📋 Visão Geral

Sistema de trading automatizado hosted em cloud com dashboard web seguro e acessível via browser de qualquer lugar, sem necessidade de instalar software localmente.

**Objetivo:** Permitir automação de estratégias de trading (ex: Grid Trading) em contas DEMO/LIVE da Trading 212, com controle centralizado via dashboard web.

---

## 🏗️ Arquitetura

### **Stack Técnico**

| Componente | Tecnologia | Deployment |
|-----------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind CSS | Render (Static Site) |
| **Backend** | FastAPI + Python 3.14 + Uvicorn | Render (Python) |
| **Banco de Dados** | PostgreSQL (Supabase) | Supabase Cloud |
| **Autenticação** | Supabase Auth (JWT) | Supabase |
| **API Trading** | Trading 212 Official API (HTTP Basic Auth) | External (demo.trading212.com) |
| **Versão de Código** | Git | GitHub (joulfodayres/Trading212) |
| **Real-time** | WebSocket (preparado) | Render Backend |

### **Fluxo de Dados**

```
┌─────────────────────────────────────┐
│     BROWSER (qualquer lugar)        │
│  https://trading-212-automation-front-end.onrender.com  │
│                                     │
│  - Login (Supabase Auth)            │
│  - Dashboard com ISINs              │
│  - Tabela de posições               │
│  - Configuração de estratégias      │
│  - Gráficos em tempo real           │
└────────────────┬────────────────────┘
                 │ HTTPS (fetch/REST)
                 ▼
    ┌────────────────────────────┐
    │   BACKEND API (FastAPI)    │
    │ https://trading212-backend │
    │      Render (Python)       │
    │                            │
    │ - Autenticação JWT         │
    │ - CRUD ISINs               │
    │ - Integração T212 API      │
    │ - Scheduler (trades)       │
    │ - Estratégias              │
    └────────┬──────────┬────────┘
             │          │
       HTTPS │          │ HTTP/REST
             ▼          ▼
    ┌──────────────┐  ┌──────────────────────┐
    │  SUPABASE    │  │  TRADING 212 API     │
    │  PostgreSQL  │  │  https://demo...     │
    │              │  │  (HTTP Basic Auth)   │
    │ - users      │  │                      │
    │ - isins      │  │ - Fetch positions    │
    │ - config     │  │ - Get account info   │
    │ - trades     │  │ - Execute orders     │
    │ - logs       │  │ - Get instruments    │
    │ - strategies │  └──────────────────────┘
    └──────────────┘
```

---

## 📁 Estrutura do Projeto

```
Trading212/
├── README.md                           # Overview rápido
├── CLAUDE.md                           # Este ficheiro
├── DEPLOYMENT.md                       # Notas de deployment
├── DEPLOYMENT_STEP_BY_STEP.md         # Guia passo-a-passo
├── DEPLOYMENT_COMPLETE.txt            # Status final
├── RENDER_DEPLOYMENT_INSTRUCTIONS.txt # Setup Render
├── RENDER_FRONTEND_SETUP.txt          # Frontend Render
├── COMECA_AQUI.md                     # Quick start local
├── TESTES.md                          # Testes locais
├── TESTE_RESUMO.md                    # Sumário de testes
├── .gitignore                         # Git rules
├── render.yaml                        # Render config (não usado)
│
├── backend/                           # FastAPI Application
│   ├── main.py                        # Entry point FastAPI
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Template env vars
│   ├── .env                           # Production env (não commitado)
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                # Pydantic settings (env vars)
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── crypto.py                  # Encriptação Fernet (API keys)
│   │   └── jwt.py                     # JWT token management (TODO)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── trading212.py              # Cliente T212 API (HTTP Basic Auth)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py                      # SQLAlchemy models (users, isins, trades, etc)
│   │   └── schemas.py                 # Pydantic schemas (request/response validation)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                    # /auth endpoints (TODO)
│   │   ├── isins.py                   # /isins CRUD (TODO)
│   │   ├── config.py                  # /config endpoints (TODO)
│   │   ├── positions.py               # /positions (TODO)
│   │   └── orders.py                  # /orders endpoints (TODO)
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── scheduler.py               # APScheduler (corre a cada 15s) ✅
│   │   ├── automation_engine.py       # 3-phase automation cycle ✅
│   │   └── t212_service.py            # T212 API wrapper ✅
│   │
│   ├── services/                       # (NEW - Phase 4)
│   │   ├── __init__.py
│   │   ├── scheduler.py               # SchedulerService lifecycle ✅
│   │   ├── automation_engine.py       # AutomationEngine core logic ✅
│   │   └── t212_service.py            # T212 API helpers ✅
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── ws.py                      # WebSocket real-time updates (TODO)
│   │
│   ├── db/
│   │   └── __init__.py
│   │   └── migrations/                # Alembic (não usado, BD em Supabase)
│   │
│   └── test_t212_api.py              # Script de teste T212 API
│
├── frontend/                          # React Application
│   ├── index.html                    # HTML entry point
│   ├── package.json                  # npm dependencies + scripts
│   ├── tsconfig.json                 # TypeScript config
│   ├── tsconfig.node.json            # TS config para Vite
│   ├── vite.config.ts                # Vite build config
│   │
│   ├── src/
│   │   ├── main.tsx                  # React entry point
│   │   ├── App.tsx                   # Main app routing
│   │   ├── index.css                 # Global styles + Tailwind
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx         # Login form (stub)
│   │   │   ├── DashboardPage.tsx     # Main dashboard
│   │   │   ├── ISINDetailPage.tsx    # Detalhe ISIN (placeholder)
│   │   │   ├── ConfigPage.tsx        # Configuração (placeholder)
│   │   │   └── HistoryPage.tsx       # Histórico (placeholder)
│   │   │
│   │   ├── components/
│   │   │   ├── Sidebar.tsx           # Navigation sidebar
│   │   │   ├── ISINTable.tsx         # Tabela de ISINs (com mock data)
│   │   │   ├── ISINCard.tsx          # Card individual ISIN (placeholder)
│   │   │   ├── ToggleSwitch.tsx      # Toggle automation (placeholder)
│   │   │   └── ConfigForm.tsx        # Config form (placeholder)
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts             # Axios HTTP client
│   │   │   └── index.ts              # API endpoints wrapper
│   │   │
│   │   ├── stores/
│   │   │   └── authStore.ts          # Zustand auth store (mock)
│   │   │
│   │   └── pages/ (placeholder)
│   │       └── [outros ficheiros]
│   │
│   └── public/                        # Static assets
│
├── docker/
│   ├── Dockerfile.backend             # Docker image (production)
│   └── docker-compose.yml             # Compose (not used in cloud)
│
├── db/
│   ├── supabase_schema.sql            # SQL scripts para criar tabelas
│   └── migrations/                    # (não usado - BD em Supabase)
│
└── docs/
    ├── API.md                         # Documentação API (TODO)
    └── T212_API.md                    # Notas sobre T212 API
```

---

## 🚀 Deployment

### **Status Atual: ✅ LIVE EM PRODUÇÃO**

| Serviço | URL | Status | Tipo |
|---------|-----|--------|------|
| **Frontend** | https://trading-212-automation-front-end.onrender.com | ✅ Online | Static Site (React) |
| **Backend** | https://trading212-backend.onrender.com | ✅ Online | Python (FastAPI) |
| **BD** | supabase.com | ✅ Online | PostgreSQL |
| **GitHub** | github.com/joulfodayres/Trading212 | ✅ Online | Git |

### **Infraestrutura**

- **Frontend Hosting:** Render (Static Site — free; rewrite /* → /index.html)
- **Backend Hosting:** Render (Python Web Service)
- **BD Hosting:** Supabase (PostgreSQL Cloud)
- **Auth:** Supabase Auth (JWT)
- **DNS:** Render (*.onrender.com)
- **SSL/TLS:** Render (automático)

### **Auto-Deploy**

- Qualquer push para `main` no GitHub dispara auto-deploy
- Frontend: ~10-15 minutos (React build)
- Backend: ~5-10 minutos (pip install)
- BD: Sem rebuild necessário

---

## 📊 Banco de Dados (Supabase)

### **Tabelas**

#### **1. users**
```sql
id (UUID, PK)
email (VARCHAR, UNIQUE)
is_admin (BOOLEAN, default: false)
created_at (TIMESTAMP)
```
- **RLS:** Cada user vê apenas seus próprios dados
- **Índices:** idx_users_email

#### **2. isins**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
isin (VARCHAR)
ticker (VARCHAR)
name (VARCHAR)
currency (VARCHAR, default: 'EUR')
automation_enabled (BOOLEAN, default: false)
fields_json (JSONB)  -- Campos dinâmicos da API T212
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
UNIQUE(user_id, isin)
```
- **RLS:** User vê apenas seus ISINs
- **Índices:** idx_isins_user_id, idx_isins_isin

#### **3. config**
```sql
id (UUID, PK)
user_id (UUID, FK → users, UNIQUE)
t212_api_key_encrypted (VARCHAR)  -- Encriptado com Fernet
t212_api_secret_encrypted (VARCHAR)  -- Encriptado com Fernet
t212_environment (VARCHAR, default: 'demo')  -- 'demo' ou 'live'
strategy_params (JSONB)  -- Parâmetros da estratégia
updated_at (TIMESTAMP)
```
- **RLS:** User vê apenas sua config
- **Segurança:** API keys encriptadas com Fernet (chave em .env)

#### **4. strategies**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
name (VARCHAR)
type (VARCHAR, default: 'grid_trading')
params (JSONB)  -- Parâmetros específicos
created_at (TIMESTAMP)
```
- **RLS:** User vê apenas suas estratégias
- **Tipos:** grid_trading, rsi, sma_crossover (para expansão futura)

#### **5. trades**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
isin_id (UUID, FK → isins)
strategy_id (UUID, FK → strategies)
tipo (VARCHAR)  -- 'BUY' ou 'SELL'
quantidade (DECIMAL)
preco (DECIMAL)
comissao (DECIMAL, default: 0)
status (VARCHAR)  -- 'PENDING', 'EXECUTED', 'FAILED'
t212_order_id (VARCHAR)  -- Order ID da T212 API
created_at (TIMESTAMP)
executed_at (TIMESTAMP)
detalhes_json (JSONB)
```
- **RLS:** User vê apenas seus trades
- **Índices:** user_id, isin_id, status, created_at

#### **6. logs**
```sql
id (UUID, PK)
user_id (UUID, FK → users)
nivel (VARCHAR)  -- 'INFO', 'WARNING', 'ERROR', 'DEBUG'
mensagem (VARCHAR)
detalhes_json (JSONB)
created_at (TIMESTAMP)
```
- **RLS:** User vê apenas seus logs
- **Índices:** user_id, nivel, created_at

---

## 🔌 API Trading 212

### **Autenticação**

- **Tipo:** HTTP Basic Authentication
- **Formato:** `Authorization: Basic base64(API_KEY:API_SECRET)`
- **Ambientes:**
  - Demo: `https://demo.trading212.com/api/v0`
  - Live: `https://live.trading212.com/api/v0`

### **Endpoints Utilizados**

| Endpoint | Método | Rate Limit | Uso |
|----------|--------|-----------|-----|
| `/equity/account/summary` | GET | 1 req/5s | Fetch saldo |
| `/equity/positions` | GET | 1 req/1s | Posições abertas |
| `/equity/orders` | GET | 1 req/5s | Ordens pendentes |
| `/equity/orders/market` | POST | 50 req/1m | Colocar ordem |
| `/equity/orders/limit` | POST | 1 req/2s | Ordem limit |
| `/equity/orders/stop` | POST | 1 req/2s | Stop order |
| `/equity/orders/{id}` | DELETE | 50 req/1m | Cancelar ordem |
| `/equity/metadata/instruments` | GET | 1 req/50s | Lista de ISINs |
| `/equity/history/orders` | GET | 6 req/1m | Histórico |

### **Limitações**

- ✅ Apenas contas **Invest** ou **Stocks ISA**
- ✅ Ordens apenas em **moeda primária** da conta
- ✅ Sell = quantidade **negativa** (ex: `-10`)
- ✅ Max **50 ordens pendentes** por ticker
- ✅ Rate limits por account (não por API key)

### **Dados da Conta DEMO (Teste)**

```
API Key: 40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU
API Secret: iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0
Saldo: €5.889,99
Posições: 2 abertas
- Vanguard FTSE All-World: 14.84 @ €166.86
- SPDR S&P 500: 147.75 @ €16.37
```

---

## 🔑 Credenciais & Segurança

### **Supabase**
```
URL: https://[project-url].supabase.co
Anon Key: [anon-key-from-supabase]
JWT Secret: [jwt-secret-from-supabase]

Note: Credentials are stored in .env (not committed to git)
```

### **Trading 212 (DEMO)**
```
API Key: [api-key-from-t212-dashboard]
API Secret: [api-secret-from-t212-dashboard]
Environment: demo

Note: Credentials are stored in .env (not committed to git)
```

### **Environment Variables**
Credentials are stored in `.env` file (not committed) and loaded at runtime:
```
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_JWT_SECRET=...
T212_API_KEY=...
T212_API_SECRET=...
T212_ENVIRONMENT=demo
T212_BASE_URL=https://demo.trading212.com/api/v0
FASTAPI_ENV=production
FASTAPI_DEBUG=False
JWT_SECRET_KEY=trading212-bot-secret-key-change-later
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENCRYPTION_KEY=mhRLQKMKc2d5fJ7pX8vN3qZ9wK1mL2nO3pR4sT5uV6w=
LOG_LEVEL=INFO
```

### **Segurança**

- ✅ `.env` no `.gitignore` (nunca commitado)
- ✅ API keys T212 encriptadas com Fernet na BD
- ✅ JWT tokens via Supabase Auth
- ✅ CORS restringido (TODO: limitar a frontend URL)
- ✅ HTTPS automático em Render
- ✅ Row-Level Security (RLS) em todas as tabelas
- ✅ Passwords de API keys não expostas ao frontend

---

## 🧪 Utilizador de Teste

```
Email: teste@trading212.com
Senha: (qualquer coisa - login é stub)
Admin: true
ID: ab1036ff-937d-46e5-8f5b-bab07f1fb100
```

---

## 📌 Features Implementadas (MVP)

1. **Frontend**
   - ✅ Login page (stub - qualquer email/password)
   - ✅ Dashboard com sidebar
   - ✅ Navegação entre views (ISINs, Configuração, Histórico)
   - ✅ Tabela de ISINs (com mock data)
   - ✅ UI para Editar/Deletar ISINs (sem lógica)
   - ✅ UI para adicionar novo ISIN (sem lógica)
   - ✅ Botão logout
   - ✅ Responsivo com Tailwind CSS

2. **Backend**
   - ✅ Estrutura FastAPI
   - ✅ Health check endpoints (`/health`, `/`)
   - ✅ Cliente T212 API (HTTP Basic Auth)
   - ✅ Modelos SQLAlchemy (DB)
   - ✅ Schemas Pydantic (validation)
   - ✅ Encriptação Fernet (credenciais)
   - ✅ Logging
   - ✅ Settings via .env

3. **Infraestrutura**
   - ✅ GitHub setup
   - ✅ Render deployment (backend + frontend)
   - ✅ Supabase BD + Auth
   - ✅ HTTPS automático
   - ✅ Auto-deploy on git push

### 🔄 **Funcionalidades TODO (Próximas Fases)**

> ⚠️ Secção histórica do planeamento inicial. Muitos itens abaixo já foram concluídos entretanto —
> ver Item #20 (auth JWT em ~35 endpoints), Item #15 (PROD), Item #21 (SMTP) no `BACKLOG.md` e no `docs/KNOWLEDGE_BASE.md` para o estado real e atualizado.

1. **Autenticação Real** ✅ **CONCLUÍDO (Item #20)**
   - [x] Login/register com Supabase Auth
   - [x] JWT token validation no backend (~35 endpoints protegidos)
   - [x] Logout real
   - [ ] Password reset

2. **CRUD ISINs**
   - [ ] POST /isins → Adicionar ISIN (fetch T212 API)
   - [ ] GET /isins → Listar ISINs do user
   - [ ] PUT /isins/{id} → Editar ISIN
   - [ ] DELETE /isins/{id} → Deletar ISIN
   - [ ] Integração completa com Supabase

3. **Configuração**
   - [ ] POST /config → Guardar API Keys T212 (encriptadas)
   - [ ] GET /config → Recuperar config do user
   - [ ] PUT /config → Atualizar config
   - [ ] POST /config/test → Testar conexão T212

4. **Automação & Estratégias**
   - [ ] Scheduler (APScheduler - corre a cada 5 min)
   - [ ] Grid Trading strategy (compra em -1%, vende em +1%)
   - [ ] Executor de trades (chama T212 API)
   - [ ] Risk manager (stop-loss, max drawdown)
   - [ ] Toggle ON/OFF automação por ISIN

5. **Real-time Updates**
   - [ ] WebSocket para atualizações live
   - [ ] Preços em tempo real
   - [ ] Status de trades
   - [ ] Notificações

6. **Dashboard Avançado**
   - [ ] Gráficos (Recharts)
   - [ ] Detalhe de ISIN (info + gráfico)
   - [ ] Histórico de trades
   - [ ] P&L tracking
   - [ ] Alertas

---

## 🔍 Fluxo de Desenvolvimento

### **Fase 1: MVP Estrutura** ✅ COMPLETO
- ✅ GitHub setup
- ✅ Render deployment
- ✅ Supabase BD
- ✅ Frontend + Backend scaffolding
- ✅ T212 API integration

### **Fase 2: Autenticação** ✅ COMPLETO (Item #20)
- ✅ Supabase Auth no backend
- ✅ JWT validation em ~35 endpoints
- ✅ Frontend login real
- ✅ Logout real

### **Fase 3: CRUD ISINs**
- [ ] Endpoints implementados
- [ ] BD integration
- [ ] T212 API fetch
- [ ] Frontend conectado

### **Fase 4: Automação**
- [ ] Scheduler setup
- [ ] Strategy logic
- [ ] Trade execution
- [ ] Risk management

### **Fase 5: Polish**
- [ ] Real-time updates
- [ ] Gráficos
- [ ] Testes
- [ ] Docs

---

## 🎨 UI/UX Requirements

### **No Toast Notifications**
- ❌ **DO NOT** show success/error popup messages (toast notifications)
- ❌ No top-right corner notifications (e.g., "Scheduler interval updated successfully!")
- ✅ All actions should be **silent**
- ✅ Keep error handling and logging to console for debugging
- ✅ User can see UI state changes indicate success (e.g., value changed, button disabled → enabled)

**Implementation Notes:**
- Removed all `toast.success()` and `toast.error()` calls from frontend
- Errors are logged to browser console for debugging: `console.error('[ComponentName] Error message')`
- Success actions are logged to browser console: `console.log('[ComponentName] Success message')`
- Form validation errors are shown inline with form fields, not as toast popups

---

## 📦 Dependencies

### **Backend (Python)**
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.23
supabase>=2.3.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
cryptography>=41.0.0
httpx>=0.25.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
requests>=2.31.0
aiohttp>=3.9.0
websockets>=12.0
APScheduler>=3.10.0
```

### **Frontend (Node)**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.6.2",
  "zustand": "^4.4.2",
  "lucide-react": "^0.294.0"
}
```

---

## 🌐 URLs em Produção

Existem dois ambientes paralelos, DEMO e PROD (Item #15, setup completo em 2026-09-27):

```
DEMO frontend: https://trading-212-automation-front-end.onrender.com
DEMO backend:  https://trading212-backend.onrender.com
DEMO docs:     https://trading212-backend.onrender.com/docs

PROD frontend: https://trading212-frontend-real.onrender.com
PROD backend:  https://trading212-backend-prod.onrender.com
PROD docs:     https://trading212-backend-prod.onrender.com/docs

GitHub: https://github.com/joulfodayres/Trading212
```

**Nota de naming:** o serviço frontend de PROD chama-se `trading212-frontend-real` (não `-prod`) — nome escolhido intencionalmente, é assimétrico face ao backend `trading212-backend-prod` mas é o nome real em uso no Render.

**Separação DEMO/PROD:**
- Cada ambiente tem o seu próprio projeto Supabase (BD + Auth independentes) e a sua própria T212 API key (`T212_ENVIRONMENT=demo` vs `live`).
- Branch `main` → auto-deploy dos serviços DEMO. Branch `prod` → deploy manual (auto-deploy OFF por desenho) dos serviços PROD; `prod` recebe fast-forward merge de `main` depois de cada fix validado em DEMO.
- Banner visual no frontend indica sempre em que ambiente se está (DEMO vs PROD).
- Autenticação (JWT/Supabase Auth) é agora obrigatória em ~35 endpoints do backend (Item #20).
- Limites de trading, auto-disable pós-deploy, e alertas por email (SMTP) protegem a automação em ambos os ambientes (Item #15 Phase 1, Item #21).

---

## 🔧 Desenvolvimento Local (não recomendado)

Caso queiras testar localmente (opcional):

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (outra terminal)
cd frontend
npm install
npm run dev
```

---

## 📝 Conventions

### **Git**
- **Branch main:** Production-ready code
- **Auto-deploy:** On push to main
- **Commits:** "Fix/Feature: Description" + Co-Authored-By

### **Python**
- **UTF-8 encoding:** Suportado
- **Rate limiting:** Respeitar T212 API limits
- **Logging:** Info level em produção
- **Env vars:** Via .env (não commitado)

### **React**
- **TypeScript:** Strict mode
- **Components:** Functional, hooks-based
- **Styling:** Tailwind CSS
- **State:** Zustand (simple) ou Context (complex)

---

## 🐛 Troubleshooting

### **Backend não inicia**
```bash
# Verifica env vars
cat backend/.env

# Testa imports
python -c "from api.trading212 import Trading212Client"

# Checa requirements
pip install -r backend/requirements.txt
```

### **Frontend não compila**
```bash
# Limpa cache
npm cache clean --force
rm -rf node_modules dist

# Reinstala
npm install
npm run build
```

### **Render deploy falha**
- Verifica Build Command e Start Command
- Verifica Environment Variables
- Verifica GitHub sync
- Lê logs no Render Dashboard

---

## 📊 Métricas

### **Performance**
- **Frontend build:** ~5-10 min
- **Backend startup:** ~2-3 min
- **T212 API response:** ~500ms
- **DB query:** <100ms

### **Recursos**
- **Frontend size:** ~150KB (gzipped)
- **Backend RAM:** ~200MB
- **DB size:** <10MB (atual)

---

## 🎯 Roadmap

### **Fase 4: Automação Grid Trading** ✅ COMPLETO
- ✅ APScheduler integrado (ciclo de 15s)
- ✅ SchedulerService (lifecycle management)
- ✅ AutomationEngine (3-fase: setup → monitor → fill)
- ✅ T212Service (wrapper para API calls)
- ✅ Portfolio sync endpoint (POST /api/isins/sync)
- ✅ Automation monitoring endpoints
- ✅ Grid Trading strategy initial implementation

### **Fase 5: Features & Backlog** 🚧 PRÓXIMO (1-2 semanas)
- [ ] Global Automation Toggle (ON/OFF engine)
- [ ] Strategy Parameter Tables (UI editável)
- [ ] Automation Preview Dialog
- [ ] Upload Real T212 Data (CSV/Excel import)
- [ ] Charts & Statistics (equity curve, P&L)

### **Fase 6: Real-time & Polish**
- [ ] WebSocket real-time updates
- [ ] Advanced dashboard
- [ ] Automated testing suite
- [ ] Monitoring & alerts

### **Fase 7: Produção & Expansão**
- [ ] Live trading mode (com controlos)
- [ ] Mais estratégias (RSI, SMA, etc)
- [ ] Multiple account support
- [ ] Mobile app
- [ ] Backtesting engine

---

## 📚 Recursos

- **Trading 212 API Docs:** https://docs.trading212.com/api
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Supabase Docs:** https://supabase.com/docs
- **React Docs:** https://react.dev
- **Render Docs:** https://render.com/docs

---

## 📖 Documentação Interna (Phase 4)

### ✅ Phase 4 Implementation Complete
- **`PHASE4_ARCHITECTURE.txt`** - Decisões arquiteturais (APScheduler, lifespan, schema)
- **`PHASE4_IMPLEMENTATION_PLAN.md`** - Plano detalhado de implementação
- **Ficheiros de Código:**
  - `backend/services/scheduler.py` - SchedulerService
  - `backend/services/automation_engine.py` - AutomationEngine (3-fase)
  - `backend/services/t212_service.py` - T212 API wrapper
  - `backend/routes/automation.py` - Monitoring endpoints
  - `backend/models/db.py` - AppParameters model

### ⭐ Descobertas Importantes (Phase 4):

1. **APScheduler Embedded** - Sem serviço separado, integrado em FastAPI
2. **3-Phase Cycle** - Setup (initial trades) → Monitor (poll orders) → Fill (rebalance)
3. **15s Interval** - Ciclo completo executa em ~7-10s, deixa buffer de 5-8s
4. **Max Instances=1** - Previne overlapping cycles (thread-safety)
5. **Portfolio Sync** - POST /api/isins/sync sincroniza posições do T212

### 🔐 Autenticação T212:

- HTTP Basic Auth: `base64(API_KEY:API_SECRET)`
- Demo: `https://demo.trading212.com/api/v0`
- Live: `https://live.trading212.com/api/v0`

### ⚠️ Limitações Críticas:

- ❌ Sem webhooks (polling obrigatório)
- ❌ Sem filtro de data em /history/orders
- ❌ Máx 50 ordens pendentes por ticker
- ❌ Apenas contas Invest/Stocks ISA
- ✅ Todas as operações na moeda primária da conta
- ✅ Rate limits respeitados (polling a cada 15s é safe)

---

## 🛠️ Item #22: Manual Orders — "Gerir Ordens" (Completed — 2026-10-05)

Ecrã **manual, não automatizado** para gerir as ordens pendentes da T212 de um único ISIN.
Acede-se por um ícone na lista de ISINs (`ISINTable.tsx`).

⚠️ **Deliberadamente NÃO está sujeito aos limites de trading do Item #15/#19**
(`max_buy_order_value`, `max_sell_order_value`, `max_daily_spend`) — decisão de produto
explícita, por ser um caminho manual e deliberado, não automação. Tem a sua própria validação
independente (ver mais abaixo).

**Ficheiros principais:**
- `backend/routes/manual_orders.py` — endpoints
- `backend/services/manual_orders_service.py` — lógica de geração de séries + validação + matching
- `backend/utils/price_precision.py` — inferência de casas decimais do preço (ver abaixo)
- `frontend/src/pages/ManualOrdersPage.tsx` — ecrã
- `frontend/src/components/ManualOrdersConfigSection.tsx` — thresholds de validação na ConfigPage

**Dois modos (radio button, mutuamente exclusivos):**
1. **"Editar ordens existentes"** — lista "Current Orders": editar (preço/quantidade) ou cancelar
   uma ordem pendente. A T212 não tem endpoint de "editar ordem" — uma edição é sempre
   `DELETE` da ordem antiga + `POST` de uma nova (risco aceite: se o `DELETE` tiver sucesso e o
   `POST` falhar, fica-se sem a ordem).
2. **"Criar novas ordens via parâmetros"** (modo por omissão) — gera uma escada de ordens
   Sell/Buy a partir de parâmetros:
   - **Zona 1** — Initial Price + Price Interval (bp) + Acc (Y/N, composto ou não)
   - **Zona 2** — Amount (toggle Amount/Quantity)
   - **Zona 3** — Quantity (mutuamente exclusivo com a Zona 2)
   - **Zona 4** — Step + Multiplier: de `step` em `step` ordens (1-indexado), multiplica o
     Amount/Quantity dessa ordem (nunca o Preço) pelo `multiplier`, sem acumular entre ocorrências.
     `step=0` ou `multiplier=1` desativa (defaults)
   - **Zona 5** — Number of Orders
   - Botão **"APLICAR"** faz matching contra o estado real da T212 (não contra edições locais
     pendentes do modo 1): ordem igual (tipo+preço+quantidade) fica inalterada; o resto é
     cancelado/criado conforme necessário

**Validação (própria, independente dos limites de automação):** 7 parâmetros `mo_*` em
`app_parameters` (ver `db/manual_orders_validation_params.sql`), configuráveis na ConfigPage,
independentes por ambiente (DEMO/PROD). Só `mo_price_max_variation_pct` bloqueia (hard block);
as restantes 6 mostram um alerta único pedindo confirmação.

**Precisão de casas decimais do preço** — por ISIN, inferida a partir do texto bruto do JSON
devolvido pela T212 (`currentPrice`), porque a API nunca indica explicitamente quantas casas usa
e um `float` não distingue `166.80` de `166.8`. Conceito **separado** de `isins.quantity_precision`
(que é sobre a quantidade, não o preço) — não confundir os dois. Aplica-se também à lista
principal de ISINs (Current Price / Average Price).

**Últimos parâmetros usados** — gravados por ISIN (`isins.last_manual_order_params`, JSONB) a
cada "GERAR" com sucesso, e usados para pré-preencher o formulário na próxima visita —
**exceto** o Initial Price, que é sempre o preço de mercado atual no momento de abrir o ecrã
(nunca o valor gravado), para evitar disparar logo o hard block de variação de preço.

**Defaults atuais do formulário** (após ajustes finais): ecrã abre em "Criar novas ordens via
parâmetros"; Acc Price/Amount/Quantity = "N"; modo Quantity (não Amount); Amount/Quantity
Interval = 0; Step/Multiplier = 0/1 (desativado/sem efeito); Number of Orders = 3.

**Migrations (ficheiro apenas, correr manualmente no Supabase SQL Editor):**
- `db/manual_orders_validation_params.sql` — os 7 `mo_*` — confirmado corrido em DEMO e PROD
- `db/manual_orders_last_params.sql` (`isins.last_manual_order_params`) — **corrida manualmente
  pelo utilizador; confirmar antes de assumir que já está aplicada num ambiente específico**

**Efeito colateral — correção de schema drift:** ao construir esta feature descobriu-se que
`db/prod_setup_consolidated.sql` (script usado para recriar o schema de PROD do zero) estava
desatualizado face ao schema real em uso — faltavam várias colunas em `isins`
(`strategy_id`, `instrument_json`, `position_created_at`, campos `wi_*`, `quantity_precision`,
etc.) e tanto `isins` como `strategies` tinham uma coluna `user_id` pendente de antes da
simplificação para single-user. Reconciliado o ficheiro para refletir o schema real — relevante
para quem precisar de recriar um ambiente (DEMO/PROD) do zero no futuro.

---

## 🐛 Fix: Primeiro ciclo de automação no arranque (2026-10-05)

`services/scheduler.py` — `SchedulerService.start()` disparava o primeiro ciclo imediato no
arranque (`run_cycle_wrapper()`), que cria o seu **próprio event loop** com
`asyncio.new_event_loop()` + `run_until_complete()`. Isso só é seguro a correr na thread de
background do APScheduler (onde não há loop a correr). Mas `start()` já corre **dentro** do loop
principal do FastAPI (lifespan), por isso ao chamar `run_cycle_wrapper()` diretamente dava
`RuntimeError: Cannot run the event loop while another loop is running` em PROD logo no arranque.
**Fix:** `start()` passou a fazer `await self.automation_engine.run_cycle()` diretamente para o
primeiro ciclo (já está em contexto `async`), mantendo `run_cycle_wrapper()` inalterado para os
ciclos periódicos seguintes (esses sim correm na thread do APScheduler, onde o wrapper continua
correto).

**Item #23 (Manual Orders):** as listas "New Orders" e "Current Orders" no ecrã de Gestão de
Ordens passaram a mostrar o total de itens no título (ex: `New Orders (6)`).

**Item #24 (diagnosticado, não implementado):** incidente em PROD (2026-10-05, 08:37-08:38) —
health check do Render falhou por timeout (5s) "a correr o teu código" durante um "Aplicar" no
ecrã de Gestão de Ordens. Causa: `Trading212Client` (`backend/api/trading212.py`) usa `requests`
síncrono, e `_handle_rate_limit()` faz `time.sleep()` bloqueante quando a T212 sinaliza rate
limit — como as rotas (`manual_orders.py`) são `async def` mas chamam o cliente síncrono
diretamente (sem `await`/`asyncio.to_thread`), uma sequência de vários DELETE/POST no "Aplicar"
pode bloquear o **único worker Uvicorn** tempo suficiente para o health check do Render também
falhar — o Render marca a instância unhealthy e reinicia; o refresh automático do ecrã
(`GET /{isin}/screen`, chamado logo a seguir ao "Aplicar" ter respondido com sucesso) cai nessa
janela de reinício, sem resposta (nem cabeçalhos CORS, daí o erro de CORS "fantasma" no browser),
e sem nada nos logs da app (o pedido nunca chegou a ser processado). Solução escolhida (ver
`BACKLOG.md` Item #24 para alternativas consideradas e rejeitadas): `_handle_rate_limit()` passa
a **devolver** o tempo de espera em vez de dormir; as rotas `async` fazem
`await asyncio.sleep(wait_seconds)` entre chamadas sequenciais — espera o tempo exato indicado
pela T212 sem bloquear o event loop. O `AutomationEngine`/scheduler (thread separada do
APScheduler) mantém `time.sleep()` sem alterações, sem risco adicional aí.

---

## ✅ Checklist de Produção

- ✅ Código em GitHub
- ✅ Backend em Render (online)
- ✅ Frontend em Render (online)
- ✅ BD em Supabase (online)
- ✅ HTTPS automático
- ✅ Auto-deploy configurado
- ✅ Environment variables setup
- ✅ Testes básicos passados
- ✅ Documentação atualizada
- ✅ Phase 4 Automation Engine Live
- ✅ APScheduler running 24/7
- ✅ Autenticação JWT em ~35 endpoints (Item #20)
- ✅ Ambiente PROD separado (Supabase + backend + frontend próprios) (Item #15)
- ✅ Trading limits, auto-disable pós-deploy, alertas SMTP (Item #15/#21)
- ✅ Gestão manual de ordens pendentes por ISIN (Item #22 — fora dos limites de automação, por desenho)
- ✅ Fix: primeiro ciclo de automação no arranque já não crasha PROD (2026-10-05)
- ⏳ Item #24: espera de rate-limit T212 não-bloqueante (diagnosticado, não implementado)
- ⏳ Testes automatizados (Phase 5)
- ⏳ Monitoring avançado (Phase 6)
- ⏳ Backup strategy (Phase 6)

---

## 👨‍💻 Desenvolvimento

**Última atualização:** 2026-10-05
**Status:** DEMO + PROD ambos live; auth (Item #20), PROD environment (Item #15), SMTP alerts (Item #21), Manual Orders / Gerir Ordens (Item #22) concluídos; fix de arranque do scheduler em PROD + Item #23 (contagem de ordens) concluídos; Item #24 (rate-limit não-bloqueante) diagnosticado e documentado, por implementar
**Próximo focus:** Ver `docs/KNOWLEDGE_BASE.md` e `BACKLOG.md` para o estado atualizado do backlog

---

## 📞 Contacto & Suporte

Todas as credenciais e URLs estão guardadas em segurança.
Código versionado em GitHub.
Deployment automático em Render.

🚀 **Sistema pronto para expansão e novos features!**
