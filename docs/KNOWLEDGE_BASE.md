# Trading 212 Bot - Knowledge Base

## 🎯 Project Overview

**Trading 212 Bot** é um sistema de automação de trading algorítmico integrado com a plataforma Trading 212 via API oficial.

**Status:** MVP em Produção (Phase 5 em desenvolvimento)

### Stack Técnico
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python 3.14 + Uvicorn
- **Database:** PostgreSQL (Supabase Cloud)
- **Auth:** Supabase Auth (JWT)
- **Trading API:** Trading 212 Official API (HTTP Basic Auth)
- **Deployment:** Render (frontend + backend) + Supabase (database)

### Arquitetura

```
┌─────────────────────────────────────────┐
│     BROWSER (qualquer lugar)            │
│  https://trading212-1.onrender.com      │
└────────────────┬────────────────────────┘
                 │ HTTPS
                 ▼
    ┌────────────────────────────┐
    │   BACKEND API (FastAPI)    │
    │ https://trading212-4ojx... │
    │      Render (Python)       │
    │                            │
    │ - Autenticação JWT         │
    │ - CRUD ISINs/Strategies    │
    │ - Integração T212 API      │
    │ - Scheduler (automação)    │
    └────────────┬──────────────┘
                 │ HTTP
                 ├─────────┬──────────────┐
                 ▼         ▼              ▼
         ┌────────────┐  ┌──────────────────────┐
         │  SUPABASE  │  │  TRADING 212 API     │
         │ PostgreSQL │  │  https://demo...     │
         │            │  │                      │
         │ - ISINs    │  │ - Fetch positions    │
         │ - Trades   │  │ - Execute orders     │
         │ - Config   │  │ - Get account info   │
         └────────────┘  └──────────────────────┘
```

---

## 📋 Phases Completed

### Phase 1-2: Foundation (Completed)
- ✅ GitHub setup & Render deployment
- ✅ Supabase PostgreSQL database
- ✅ Frontend scaffolding (React + TypeScript)
- ✅ Backend scaffolding (FastAPI)
- ✅ Trading 212 API client integration

### Phase 3: Authentication (Completed)
- ✅ Supabase Auth integration
- ✅ JWT token validation
- ✅ Login/logout flows
- ✅ Protected routes

### Phase 4: Automation Engine (Completed)
- ✅ APScheduler with BackgroundScheduler
- ✅ FastAPI lifespan context manager
- ✅ 3-phase automation cycle:
  1. **Setup Phase:** Create initial BUY/SELL pairs
  2. **Monitor Phase:** Poll T212 for order status
  3. **Rebalance Phase:** Handle fills and place new pairs
- ✅ SchedulerService (lifecycle management)
- ✅ AutomationEngine (3-phase logic)
- ✅ T212Service (API wrapper)
- ✅ Portfolio sync endpoint
- ✅ Global automation toggle

### Phase 5: Strategy Management (In Progress)
- ✅ Strategy CRUD (POST/PUT, no DELETE)
- ✅ Strategy parameters table (all 10 params)
- ✅ Strategy validation (requires pos -1, 0, 1)
- ✅ Frontend strategy editor
- ✅ Upload T212 data files (Reports — Activity Statement PDF import)
- ⏳ Charts & statistics dashboard
- ⏳ Knowledge Base

---

## 🗄️ Database Schema

### Tables

#### **isins** (Posições abertas)
```sql
- id (UUID, PK)
- isin (VARCHAR, UNIQUE)
- ticker (VARCHAR)
- name (VARCHAR)
- currency (VARCHAR, default: EUR)
- quantity (DOUBLE)
- current_price (DOUBLE)
- average_price_paid (DOUBLE)
- quantity_available_for_trading (DOUBLE)
- quantity_in_pies (DOUBLE)
- api_created_at (TIMESTAMP)
- position_created_at (TIMESTAMP)
- instrument_json (JSONB) - Complete instrument data
- automation_enabled (BOOLEAN, default: FALSE)
- initial_trade (BOOLEAN, default: FALSE)
- trades_balance (INTEGER, default: 0) - Grid level tracker
- strategy_id (UUID, FK → strategies)
- wi_currency, wi_current_value, wi_fx_impact, wi_total_cost, wi_unrealized_profit_loss (wallet impact)
- created_at, updated_at (TIMESTAMP)
```

#### **strategies** (Estratégias de trading)
```sql
- id (UUID, PK)
- name (VARCHAR)
- description (VARCHAR)
- initial_investment (DOUBLE) - EUR to invest per position
- enabled (BOOLEAN, default: FALSE)
- created_at, updated_at (TIMESTAMP)
```

#### **strategy_parameters** (Parâmetros por posição)
```sql
- id (UUID, PK)
- strategy_id (UUID, FK → strategies)
- pos (VARCHAR) - Position level: "-1", "0", "1", etc
- param1 to param10 (DOUBLE) - Configurable parameters
  * param1: Usually negative (buy discount %)
  * param2: Usually positive (sell premium %)
  * param3-10: Available for future use
- created_at, updated_at (TIMESTAMP)
```

#### **orders** (Histórico de ordens T212)
```sql
- id (UUID, PK)
- isin_id (UUID, FK → isins)
- t212_order_id (BIGINT)
- ticker, instrument_isin, instrument_name, instrument_currency (VARCHAR)
- side (VARCHAR: BUY/SELL)
- quantity, filled_quantity (DOUBLE)
- type (VARCHAR: MARKET/LIMIT/STOP/STOP_LIMIT)
- status (VARCHAR: NEW/CONFIRMED/FILLED/CANCELLED/etc)
- limit_price, stop_price (DOUBLE)
- time_in_force (VARCHAR: DAY/GOOD_TILL_CANCEL)
- automation_status (CHAR: W/E/C) - Watch/Executed/Cancelled
- related_order_id (UUID) - Link to paired BUY/SELL
- created_at, synced_at, updated_at (TIMESTAMP)
```

#### **app_parameters** (Configuração global)
```sql
- id (UUID, PK)
- scheduler_interval_seconds (INTEGER, default: 15)
- scheduler_enabled (BOOLEAN, default: TRUE)
- grid_trading_enabled (BOOLEAN, default: TRUE)
- max_positions_per_isin (INTEGER, default: 5)
- log_level (VARCHAR, default: INFO)
- created_at, updated_at (TIMESTAMP)
```

#### **Reports — Activity Statement import** (16 tables)
```sql
-- Control table
imported_files:
  - id (UUID, PK), file_name, file_hash (SHA-256, unique for dedup)
  - customer_id, customer_name, period_start, period_end, generated_at, pages
  - status (PENDING/IMPORTED/FAILED), imported_at, created_at, updated_at

-- 15 data tables (invest_*, cfd_*, crypto_*), each with:
  - id (UUID, PK), file_id (UUID, FK → imported_files ON DELETE CASCADE)
  - created_at, updated_at (TIMESTAMPTZ)
```
Full spec: `docs/REPORTS_FEATURE.md`, `reports/reports_schema.sql`, `reports/SECOES_PDF.md`.

---

### Strategies Management

#### **GET /api/v1/strategies**
Lista todas as estratégias com indicador de validade.
```json
Response: [
  {
    "id": "uuid",
    "name": "Grid Trading 1%",
    "description": "...",
    "initial_investment": 10.00,
    "enabled": false,
    "is_valid": true,  // Has params for -1, 0, 1
    "created_at": "2026-09-20T...",
    "updated_at": "2026-09-20T..."
  }
]
```

#### **GET /api/v1/strategies/{strategy_id}**
Obter estratégia com seus parâmetros.

#### **POST /api/v1/strategies**
Criar nova estratégia (sempre inicia disabled).
```json
Request: {
  "name": "Grid Trading 1%",
  "description": "...",
  "initial_investment": 10.00
}
```

#### **PUT /api/v1/strategies/{strategy_id}**
Atualizar estratégia. Ativa apenas se válida (tem pos -1, 0, 1).
```json
Request: {
  "name": "...",
  "enabled": true  // Will fail if not valid
}
```

### Strategy Parameters

#### **POST /api/v1/strategies/{strategy_id}/parameters**
Criar parâmetro para posição.
```json
Request: {
  "pos": "0",
  "param1": -0.1,
  "param2": 0.1,
  "param3": null,
  ...
  "param10": null
}
```

#### **PUT /api/v1/strategies/{strategy_id}/parameters/{param_id}**
Editar parâmetro.

#### **DELETE /api/v1/strategies/{strategy_id}/parameters/{param_id}**
Deletar parâmetro.

### ISINs Management

#### **GET /api/isins**
Listar ISINs com dados frescos da T212.

#### **POST /api/isins/sync**
Sincronizar carteira com T212 (atualiza todos os campos).
```json
Response: {
  "success": true,
  "synced": 5,
  "created": 1,
  "updated": 4,
  "errors": 0
}
```

#### **PUT /api/isins/{isin_id}/automation**
Ativar/desativar automação para ISIN.
```json
Request: {
  "automation_enabled": true,
  "strategy_id": "uuid"
}
```

### Automation Control

#### **GET /api/v1/automation/global-status**
Status global da automação.
```json
Response: {
  "grid_trading_enabled": true,
  "scheduler_running": true,
  "cycle_count": 42,
  "last_cycle_duration": 9.5
}
```

#### **PUT /api/v1/automation/enable**
Ativar automação global.

#### **PUT /api/v1/automation/disable**
Desativar automação global.

#### **GET /api/v1/automation/status**
Status detalhado do scheduler.

#### **PUT /api/v1/automation/config/interval**
Atualizar intervalo do scheduler (5-300s).
```json
Request: { "interval": 15 }
```

### Reports (Activity Statement Import)

#### **POST /api/reports/upload**
Upload one or more Activity Statement PDFs (multipart, `files` field). SHA-256 dedup (skips
duplicates), parses 15 tables, batch-inserts, returns per-table insertion summary.
```json
Response: {
  "files_processed": 1,
  "grand_total": { "invest_executed_trades": 71, ... },
  "grand_total_inserted": 314,
  "results": [ { "file_name": "...", "status": "imported", "total_inserted": 314, "inserted": {...} } ]
}
```

#### **GET /api/reports/files**
Lista de ficheiros processados (id, período, upload date, status).

#### **GET /api/reports/summary**
```json
Response: { "total_files": 3, "imported": 2, "failed": 1 }
```
Parser: `backend/services/report_parser.py` (PyMuPDF). See `docs/REPORTS_FEATURE.md`.

---

## 🧠 Automation Engine Logic

### 3-Phase Cycle (runs every 15 seconds)

#### **Phase 1: Initial Setup**
```
Para cada ISIN com initial_trade=TRUE:
  1. Carregar strategy e strategy_parameters (por trades_balance pos)
  2. Calcular preços: 
     - BUY: current_price * (1 + param1/100)
     - SELL: current_price * (1 + param2/100)
  3. Calcular quantidades: initial_investment / preço
  4. Colocar BUY limit order (qty positiva)
  5. Colocar SELL limit order (qty negativa)
  6. Linkar ordens com related_order_id
  7. Set initial_trade=FALSE
```

#### **Phase 2: Monitor Orders**
```
Para cada ordem com automation_status='W':
  1. Poll T212 /equity/orders/{id}
  2. Atualizar status e filled_quantity
  3. Se FILLED, set automation_status='E'
```

#### **Phase 3: Handle Fills & Rebalance**
```
Para cada ordem com status=FILLED e automation_status='E':
  1. Atualizar ISIN com posição da T212
  2. Ajustar trades_balance:
     - BUY fill: trades_balance -= 1
     - SELL fill: trades_balance += 1
  3. Cancelar related_order_id
  4. Carregar novos strategy_parameters (nova pos)
  5. Colocar novo BUY/SELL pair (novo grid level)
```

### Strategy Parameters Fallback Logic

Se pos exato não existir em strategy_parameters:
- **Positivo:** Usa máximo pos <= trades_balance
- **Negativo:** Usa mínimo pos >= trades_balance
- **Zero:** pos=0 é OBRIGATÓRIO (error se faltar)

Exemplo: Se tem params para pos=-1,0,1 mas trades_balance=3, usa params de pos=1.

---

## 🚀 Deployment

### Frontend (Render)
- URL: https://trading212-1.onrender.com
- Build: `npm run build`
- Start: `npm run preview`
- Auto-deploy on push to main

### Backend (Render)
- URL: https://trading212-4ojx.onrender.com
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0`
- Auto-deploy on push to main

### Database (Supabase)
- Cloud PostgreSQL
- Auto-backups enabled
- RLS policies on all tables

---

## 🔑 Key Concepts

### Grid Trading
Strategy que compra em desconto (-X%) e vende em premium (+X%), ajustando os níveis de preço conforme as execuções.

### trades_balance
Rastreador de qual nível de grid estamos. Começa em 0.
- BUY fill: -1 (move para preços mais baixos)
- SELL fill: +1 (move para preços mais altos)

### automation_status
- **W:** Watch (ordem pendente)
- **E:** Executed (ordem preenchida)
- **C:** Cancelled (ordem cancelada)

### is_valid (Strategy)
Strategy é válida se tem strategy_parameters para pos=-1, pos=0, e pos=1.
Só estratégias válidas podem ser ativadas.

---

## 📞 Support & Troubleshooting

### Common Issues

**"Strategy cannot be enabled"**
- Faltam parâmetros para pos -1, 0, ou 1
- Cria os parâmetros faltantes antes de ativar

**"Could not find column X"**
- Campo não existe na tabela
- Verifica schema SQL ou executa migrations

**"Rate limit atingido"**
- T212 API tem rate limits
- Scheduler espera automaticamente
- Ver logs para detalhes

**Orders não aparecem em monitorização**
- Verifica se automation_enabled=TRUE no ISIN
- Verifica se grid_trading_enabled=TRUE global
- Checa se strategy_id está correto

---

## 👨‍💻 Development

### Local Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (outro terminal)
cd frontend
npm install
npm run dev
```

### Key Files

**Backend:**
- `main.py` - FastAPI app + lifespan hooks
- `services/scheduler.py` - APScheduler lifecycle
- `services/automation_engine.py` - 3-phase logic
- `routes/strategies.py` - Strategy CRUD
- `routes/isins.py` - ISIN management
- `routes/automation.py` - Automation control

**Frontend:**
- `pages/DashboardPage.tsx` - Main layout
- `pages/StrategiesPage.tsx` - Strategy editor
- `components/ISINTable.tsx` - ISIN list
- `components/Sidebar.tsx` - Navigation + global toggle
- `hooks/useGlobalAutomation.ts` - Automation control
- `hooks/useAutomation.ts` - ISIN automation toggle

---

## 📚 Phase 5 Backlog

1. ✅ Strategy Management (DONE)
2. ✅ Upload T212 Data Files (DONE — Reports / Activity Statement PDF import)
3. ⏳ Charts & Statistics Dashboard
4. ✅ Global Automation Toggle (DONE)
5. ✅ Automation Dialog (DONE)
6. ⏳ Rename Render Projects
7. ⏳ Knowledge Base (THIS ONE)

---

**Last Updated:** 2026-09-21
**Status:** Phase 5 em desenvolvimento
