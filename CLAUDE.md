# Trading 212 Bot - MVP

Projeto de automação de trading algorítmico integrado com a plataforma **Trading 212** via API oficial.

---

## Visão Geral

Sistema de trading automatizado com dashboard web seguro. Funcionalidades MVP:

1. ✅ Tabela de ISINs gerenciável (admin only)
2. ✅ Extração de dados via API T212
3. ✅ Ecran de detalhe por ISIN (máxima informação disponível)
4. ✅ Gráficos (quando disponível na API T212)
5. ✅ Configuração de parâmetros técnicos (API Keys, URLs)
6. ✅ Toggle ON/OFF de automação por ISIN
7. ✅ Estratégia Grid Trading (compra/vende em função de % de variação)

---

## Stack Técnico

| Componente | Tecnologia |
|------------|-----------|
| **Backend** | FastAPI + Python 3.11+ |
| **BD** | Supabase (PostgreSQL) |
| **Frontend** | React 18 + TypeScript + Vite |
| **Auth** | Supabase Auth (JWT) |
| **Hosting** | Render (backend) + Vercel/Render (frontend) |
| **API Trading** | Trading 212 Official API (HTTP Basic Auth) |
| **Real-time** | WebSocket ou polling (5s) |

---

## Estrutura de Pastas

```
401. Trading 212 Hub/
├── CLAUDE.md                    # Este ficheiro
├── backend/
│   ├── main.py                  # Entrada FastAPI
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   └── settings.py          # Variáveis de ambiente
│   ├── auth/
│   │   ├── routes.py            # /auth/login, /auth/register
│   │   ├── jwt.py               # JWT token management
│   │   └── crypto.py            # Encriptação API Keys
│   ├── api/
│   │   └── trading212.py        # Cliente T212 API
│   ├── models/
│   │   ├── db.py                # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── isins.py             # /isins CRUD
│   │   ├── config.py            # /config (parâmetros técnicos)
│   │   ├── automation.py        # /automation/toggle
│   │   ├── positions.py         # /positions (dados T212)
│   │   └── orders.py            # /orders (histórico)
│   ├── engine/
│   │   ├── scheduler.py         # Corre checks periódicos
│   │   ├── strategy.py          # Lógica de estratégia
│   │   └── executor.py          # Executa trades
│   ├── websocket/
│   │   └── ws.py                # WebSocket para real-time
│   └── db/
│       └── migrations/          # Alembic (se necessário)
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ISINDetailPage.tsx
│   │   │   ├── ConfigPage.tsx
│   │   │   └── HistoryPage.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ISINTable.tsx
│   │   │   ├── ISINCard.tsx
│   │   │   ├── ToggleSwitch.tsx
│   │   │   └── ConfigForm.tsx
│   │   └── api/
│   │       ├── auth.ts
│   │       ├── isins.ts
│   │       └── config.ts
│   └── public/
├── docker/
│   ├── Dockerfile.backend
│   └── docker-compose.yml
└── docs/
    ├── API.md                   # Documentação da API interna
    └── T212_API.md              # Notas sobre T212 API
```

---

## Modelo de Dados (Supabase)

### **Tabela: users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### **Tabela: isins**
```sql
CREATE TABLE isins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  isin VARCHAR NOT NULL,
  ticker VARCHAR,
  name VARCHAR,
  currency VARCHAR DEFAULT 'EUR',
  automation_enabled BOOLEAN DEFAULT FALSE,
  fields_json JSONB,  -- Campos dinâmicos da API T212
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, isin)
);
```

### **Tabela: config**
```sql
CREATE TABLE config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  t212_api_key_encrypted VARCHAR,
  t212_api_secret_encrypted VARCHAR,
  t212_environment VARCHAR DEFAULT 'demo',  -- 'demo' ou 'live'
  strategy_params JSONB,  -- Parâmetros da estratégia
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);
```

### **Tabela: strategies**
```sql
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  type VARCHAR DEFAULT 'grid_trading',  -- Tipo de estratégia
  params JSONB,  -- Parâmetros específicos
  created_at TIMESTAMP DEFAULT NOW()
);
```

### **Tabela: trades**
```sql
CREATE TABLE trades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id),
  tipo VARCHAR,  -- 'BUY' ou 'SELL'
  quantidade DECIMAL,
  preco DECIMAL,
  comissao DECIMAL DEFAULT 0,
  status VARCHAR,  -- 'PENDING', 'EXECUTED', 'FAILED'
  t212_order_id VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  executed_at TIMESTAMP,
  detalhes_json JSONB
);
```

### **Tabela: logs**
```sql
CREATE TABLE logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  nivel VARCHAR,  -- 'INFO', 'WARNING', 'ERROR'
  mensagem VARCHAR,
  detalhes_json JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints (Backend)

### **Auth**
- `POST /api/auth/register` — Registar nova conta
- `POST /api/auth/login` — Login
- `POST /api/auth/refresh` — Refresh JWT token

### **ISINs**
- `GET /api/isins` — Listar todos os ISINs do user
- `POST /api/isins` — Adicionar novo ISIN (admin)
- `GET /api/isins/{id}` — Detalhes de um ISIN
- `PUT /api/isins/{id}` — Editar ISIN (admin)
- `DELETE /api/isins/{id}` — Eliminar ISIN (admin)
- `GET /api/isins/{id}/details` — Dados em tempo real da API T212

### **Configuração**
- `GET /api/config` — Ver configuração atual
- `PUT /api/config` — Atualizar parâmetros técnicos (API Keys, etc)
- `POST /api/config/test` — Testar conexão T212

### **Automação**
- `PUT /api/isins/{id}/automation/toggle` — Ligar/desligar automação

### **Histórico**
- `GET /api/trades` — Histórico de trades
- `GET /api/logs` — Logs do sistema

---

## Estratégia Grid Trading (MVP)

### **Funcionamento:**
1. User adiciona ISIN à tabela
2. Bot executa compra inicial com quantidade X
3. Liga-se automação (ON)
4. Scheduler verifica a cada 5 minutos:
   - Se preço subiu Y% → Vende X unidades (lucro)
   - Se preço desceu Y% → Compra X unidades (acumula)

### **Parâmetros Configuráveis:**
```json
{
  "buy_threshold_percent": 1.0,      // Descida de 1% compra
  "sell_threshold_percent": 1.0,     // Subida de 1% vende
  "buy_quantity_percent": 50,        // Compra 50% da qtd inicial
  "sell_quantity_percent": 50,       // Vende 50% da qtd inicial
  "initial_quantity": 10,            // Quantidade inicial
  "check_interval_seconds": 300      // 5 minutos
}
```

---

## Trading 212 API - Notas Importantes

### **Autenticação:**
- HTTP Basic Auth: `-u "API_KEY:API_SECRET"`
- Ambientes: `https://demo.trading212.com/api/v0` ou `https://live.trading212.com/api/v0`

### **Endpoints Principais:**
- `GET /equity/account/summary` — Saldo
- `GET /equity/positions` — Posições abertas
- `GET /equity/orders` — Ordens pendentes
- `POST /equity/orders/market` — Ordem de mercado
- `DELETE /equity/orders/{id}` — Cancelar ordem
- `GET /equity/metadata/instruments` — Lista de instrumentos

### **Rate Limits:**
- Account summary: 1 req/5s
- Positions: 1 req/1s
- Instruments: 1 req/50s
- Market orders: 50 req/1m
- Limit orders: 1 req/2s

### **Limitações:**
- ✅ Apenas contas "Invest" ou "Stocks ISA"
- ✅ Moeda primária da conta
- ✅ Sell = quantidade negativa

---

## Implementação - Próximas Etapas

### **Fase 1: Setup Base** ✅ (Agora)
- [ ] Criar estrutura de pastas
- [ ] Configurar backend (FastAPI, requirements.txt)
- [ ] Criar .env.example
- [ ] Setup Supabase BD (tabelas)
- [ ] Criar modelos SQLAlchemy

### **Fase 2: Auth & Config** (Depois)
- [ ] Login/register Supabase
- [ ] Configuração de API Keys T212
- [ ] Encriptação de credenciais

### **Fase 3: CRUD ISINs** (Depois)
- [ ] Listar ISINs
- [ ] Adicionar ISIN (fetch da API T212)
- [ ] Editar/Deletar ISIN
- [ ] Página de detalhe de ISIN

### **Fase 4: Automação** (Depois)
- [ ] Scheduler (corre a cada 5 min)
- [ ] Estratégia Grid Trading
- [ ] Executor de trades
- [ ] Toggle ON/OFF por ISIN

### **Fase 5: Frontend** (Depois)
- [ ] Sidebar + Dashboard
- [ ] Tabela de ISINs
- [ ] Detalhe ISIN
- [ ] Configuração de parâmetros
- [ ] Real-time updates (WebSocket)

---

## Desenvolvimento

### **Backend (Python)**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### **Frontend (React)**
```bash
cd frontend
npm install
npm run dev
```

### **Deployment (Render)**
- Backend: FastAPI dockerfile → Render
- Frontend: React build → Vercel ou Render static

---

## Notas

- **Credenciais**: As API Keys T212 são encriptadas com Fernet (cryptography lib)
- **JWT Tokens**: Gerados pelo Supabase Auth, validados em cada request
- **Rate Limiting**: Respeitar limites T212 com delays entre requests
- **Ambiente**: DEMO por defeito (pode trocar para LIVE depois)

---

**Status:** Em desenvolvimento 🚀
