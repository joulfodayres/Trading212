# Trading 212 Bot - MVP

**Status:** ✅ **Fase 2 Completa - Produção** 🚀  
**Último Update:** 2026-09-15

Automação de trading algorítmico integrada com Trading 212 API, acessível via browser de qualquer lugar.

---

## ⚡ Quick Start

### Aceder ao Sistema (Online)
```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com/docs
```

1. Clica em **Sign Up** para registar conta
2. Faz login com email/password
3. Vê dashboard com ISINs (dados mock por enquanto)

### Setup Local (Desenvolvimento)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# → Edita .env com tuas credenciais
python main.py  # http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

---

## 📚 Documentação

### 🔴 Ler Primeiro (Phase 4 - API Analysis)
| Ficheiro | Descrição |
|----------|-----------|
| **`docs/QUICK_REFERENCE_PHASE4.md`** | ⭐ Quick start (2 min) |
| **`docs/PHASE_4_SUMMARY.md`** | 📋 Resumo executivo |
| **`docs/t212-api/ORDERING_WARNING.md`** | ⚠️ CRÍTICO validar |

### 📖 Documentação Completa
| Ficheiro | Descrição |
|----------|-----------|
| **`COMECA_AQUI.md`** | Quick start + troubleshooting |
| **`CLAUDE.md`** | Arquitetura técnica + BD schema |
| **`docs/README.md`** | Índice completo de docs |
| **`docs/DOCUMENTATION_INDEX.md`** | Índice detalhado |

### 🔵 Phase 4 - T212 API (Detailed Analysis)
| Ficheiro | Descrição |
|----------|-----------|
| **`docs/t212-api/API_ANALYSIS.md`** | Análise de todos endpoints |
| **`docs/t212-api/HISTORY_ORDERS_PARAMS.md`** | Parâmetros com exemplos |
| **`docs/t212-api/HISTORY_ORDERS_NO_DATE_FILTER.md`** | Limitações e workarounds |
| **`docs/t212-api/INCREMENTAL_SYNC.md`** | Algoritmo + código Python |
| **`docs/t212-api/ORDER_HISTORY_BY_ID.md`** | Acesso a histórico |

### 📦 Documentação Anterior (Archive)
| Localização | Descrição |
|------------|-----------|
| **`docs/_archive/phase-2/`** | Auth, CRUD, Deployment |
| **`docs/_archive/phase-3/`** | Login fixes, ISIN updates |
| **`docs/_archive/sessions/`** | Session reports |

---

## ✅ O que já funciona (Fase 3 - Atual)

- ✅ Autenticação real (Email/Password → JWT)
- ✅ Dashboard com dados LIVE de T212 API
- ✅ Tabela ISINs com sincronização automática
- ✅ CRUD ISINs (Create, Read, Update, Delete)
- ✅ Backend online em Render (FastAPI)
- ✅ Frontend online em Render (React)
- ✅ Database Supabase (PostgreSQL + RLS)
- ✅ 25+ endpoints API funcionais
- ✅ Row-Level Security (cada user vê só seus dados)
- ✅ Toggle automação por ISIN
- ✅ T212 API Integration (polling de posições)
- ✅ Análise completa de T212 API (documentada)

### 🔄 Em Desenvolvimento (Phase 4 Próximo)
- ⏳ APScheduler (monitoramento a cada 5s)
- ⏳ Grid Trading Logic (+1%/-1%)
- ⏳ Sincronização incremental de histórico
- ⏳ Real-time updates (WebSocket)
- ⏳ Execução automática de trades

---

## 📊 Tech Stack

| Componente | Tecnologia |
|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite + Tailwind |
| **Backend** | FastAPI + Python 3.14 + Uvicorn |
| **Database** | PostgreSQL (Supabase) + RLS |
| **Auth** | Supabase Auth (JWT) |
| **Hosting** | Render (Cloud) |
| **Version Control** | GitHub |

---

## 🚀 Deployment

Ambos os serviços estão online e auto-deploy ativo:

- **Frontend:** https://trading212-1.onrender.com
- **Backend:** https://trading212-4ojx.onrender.com
- **API Docs:** https://trading212-4ojx.onrender.com/docs

Qualquer push para `main` no GitHub dispara auto-deploy.

---

## 🎯 Próximas Fases

### Fase 4: Grid Trading Automation (Próximo)
- [ ] Implementar OrderHistoryManager
- [ ] Setup APScheduler (polling a cada 5s)
- [ ] Grid Trading strategy (+1% vender, -1% comprar)
- [ ] Trade execution via T212 API
- [ ] Testes de ordenação de /history/orders

### Fase 5: Polish & Production
- [ ] Real-time updates (WebSocket)
- [ ] Dashboard avançado (gráficos)
- [ ] Testes automatizados
- [ ] Monitoring e alertas
- [ ] Deploy em Live (com risco controlado)

### 🔍 Validação Crítica Pendente
- ⏳ Confirmar ordenação DESC de /history/orders (implícita, não documentada)
- ⏳ Testar rate limits na prática
- ⏳ Validar incremental sync com dados reais
- [ ] Gráficos (Recharts)
- [ ] Histórico de trades
- [ ] Alertas

---

## 📁 Estrutura de Ficheiros

```
Trading212/
├── README.md              # Este ficheiro
├── COMECA_AQUI.md         # Quick start
├── CHECKLIST_FINAL.md     # Status
├── INDEX.md               # Índice docs
├── CLAUDE.md              # Arquitetura
├── DOCUMENTATION.html     # Navegador HTML
│
├── backend/               # FastAPI Python
├── frontend/              # React TypeScript
├── db/                    # SQL schemas
├── docs/                  # Developer documentation
├── _archive/              # Scripts antigos
│   ├── _scripts/
│   └── _logs/
│
└── [Config files]         # .gitignore, render.yaml, etc
```

Ver **INDEX.md** ou **DOCUMENTATION.html** para navegação completa.

---

## 🔐 Segurança

- ✅ JWT tokens (24h expiration)
- ✅ Row-Level Security ativa
- ✅ Passwords hashed (bcrypt)
- ✅ API keys encriptados (Fernet)
- ✅ HTTPS automático (Render)
- ✅ CORS configurado
- ✅ .env não commitado

---

## 🧪 Testing

Testar endpoints localmente:

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'

# Listar ISINs (com JWT token)
curl http://localhost:8000/api/isins \
  -H "Authorization: Bearer <token>"
```

API Docs interativa: http://localhost:8000/docs (Swagger)

---

## 📞 Links Úteis

- **Frontend:** https://trading212-1.onrender.com
- **Backend:** https://trading212-4ojx.onrender.com
- **API Docs:** https://trading212-4ojx.onrender.com/docs
- **GitHub:** https://github.com/joulfodayres/Trading212
- **Supabase:** https://supabase.com (project: Trading212)

---

## 📝 Notas

- **Sistema de utilizador único:** Apenas tu usas este sistema
- **Modo:** Development/Testing (pode expandir para live)
- **Deployment:** Render auto-deploy on git push
- **Ambiente T212:** DEMO (pode mudar para LIVE depois)

---

🚀 **Pronto para Fase 3 - Automação!**

Para questões, ver documentação em **COMECA_AQUI.md** ou **INDEX.md**.
