# 📚 INDEX - Navegação de Documentação

**Sistema:** Trading 212 Bot MVP  
**Status:** ✅ Fase 2 Completo  
**Data:** 2026-09-15  

---

## 🚀 Começa Aqui

| Ficheiro | Descrição | Para Quem |
|----------|-----------|-----------|
| **README.md** | Overview rápido do projeto | Todos |
| **COMECA_AQUI.md** | Quick start + primeiros passos | Utilizadores novos |
| **CHECKLIST_FINAL.md** | Status completo e roadmap | Project managers |
| **CLAUDE.md** | Arquitetura técnica completa | Developers |

---

## 🏗️ Arquitetura & Design

### System Overview
| Ficheiro | Localização | Descrição |
|----------|-----------|-----------|
| CLAUDE.md - Stack Técnico | root | Tech stack: FastAPI, React, Supabase, Render |
| CLAUDE.md - Arquitetura | root | Diagrama fluxo de dados |
| CLAUDE.md - BD Schema | root | Estrutura completa Supabase |
| SESSION_CONTINUATION_SUMMARY.md | docs/ | Implementação detalhada Fase 2 |

### Database Documentation
| Ficheiro | O Quê |
|----------|-------|
| db/supabase_schema.sql | SQL para criar tabelas |
| CLAUDE.md - BD Section | Explicação de cada tabela |

---

## 💻 Development Guides

### Backend (Python/FastAPI)

| Path | Descrição | Conteúdo |
|------|----------|----------|
| backend/main.py | Entry point | FastAPI app, routers, CORS |
| backend/routes/auth.py | Autenticação | Login/Register/Logout/Verify |
| backend/routes/isins.py | CRUD ISINs | Create/Read/Update/Delete |
| backend/routes/config.py | Configuração | T212 credentials, strategy params |
| backend/api/trading212.py | T212 API | HTTP Basic Auth client |
| backend/config/settings.py | Environment | Pydantic settings + .env loader |
| backend/auth/crypto.py | Encriptação | Fernet para API keys |
| backend/auth/jwt.py | JWT tokens | Token creation/verification |
| backend/db/supabase_client.py | BD client | Lazy init + CRUD methods |

**Quick Start:**
```bash
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:8000
```

### Frontend (React/TypeScript)

| Path | Descrição | Conteúdo |
|------|----------|----------|
| frontend/src/pages/LoginPage.tsx | Login UI | Email/password form |
| frontend/src/pages/DashboardPage.tsx | Dashboard | Main UI + tabs |
| frontend/src/pages/ConfigPage.tsx | Config UI | T212 settings form |
| frontend/src/components/ISINTable.tsx | ISIN table | Listar ISINs |
| frontend/src/stores/authStore.ts | Auth state | Zustand store |
| frontend/src/api/client.ts | HTTP client | Axios + interceptors |

**Quick Start:**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## 🔐 Authentication & Security

| Ficheiro | Localização | Descrição |
|----------|-----------|----------|
| **Backend Auth** | backend/routes/auth.py | Login/Register/JWT |
| **Frontend Auth** | frontend/src/stores/authStore.ts | Zustand store |
| **JWT Testing** | docs/JWT_TESTING_GUIDE.md | Como testar endpoints |
| **CLAUDE.md - Segurança** | root | Security checklist |

---

## 📊 API Reference

### Endpoints Disponíveis

| Endpoint | Método | Descrição | Auth Required |
|----------|--------|-----------|----------------|
| `/` | GET | Health check | ❌ |
| `/health` | GET | Status | ❌ |
| `/api/auth/login` | POST | Fazer login | ❌ |
| `/api/auth/register` | POST | Registar conta | ❌ |
| `/api/auth/me` | GET | Dados utilizador | ✅ |
| `/api/auth/logout` | POST | Logout | ✅ |
| `/api/auth/verify-token` | POST | Verificar JWT | ✅ |
| `/api/isins` | GET | Listar ISINs | ✅ |
| `/api/isins` | POST | Criar ISIN | ✅ |
| `/api/isins/{id}` | GET | Detalhe ISIN | ✅ |
| `/api/isins/{id}` | PUT | Editar ISIN | ✅ |
| `/api/isins/{id}` | DELETE | Deletar ISIN | ✅ |
| `/api/isins/{id}/trades` | GET | Histórico trades | ✅ |
| `/api/isins/sync-from-trading212` | GET | Sync de posições | ✅ |
| `/api/config` | GET | Obter config | ✅ |
| `/api/config` | PUT | Guardar config | ✅ |
| `/api/config/test` | POST | Testar T212 API | ✅ |
| `/api/config/strategy-params` | GET | Obter params | ✅ |
| `/api/config/strategy-params` | PUT | Guardar params | ✅ |

**Documentação completa:** https://trading212-4ojx.onrender.com/docs (Swagger)

---

## 🚀 Deployment & Infrastructure

### Render Setup
| Ficheiro | Descrição |
|----------|-----------|
| CLAUDE.md - Deployment | Status, URLs, auto-deploy |
| COMECA_AQUI.md - Troubleshooting | Problemas e fixes |
| docs/DEPLOYMENT_STATUS.md | Status detalhado (archived) |

### URLs de Produção
```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com
Docs:     https://trading212-4ojx.onrender.com/docs
Health:   https://trading212-4ojx.onrender.com/health
```

### Environment Variables (Render Dashboard)
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| SUPABASE_URL | URL da BD | https://[].supabase.co |
| SUPABASE_KEY | Anon key | eyJhbGc... |
| SUPABASE_JWT_SECRET | JWT secret | ... |
| T212_API_KEY | Trading 212 key | ... |
| T212_API_SECRET | Trading 212 secret | ... |
| T212_ENVIRONMENT | demo ou live | demo |
| T212_BASE_URL | T212 base URL | https://demo.trading212.com/api/v0 |
| JWT_SECRET_KEY | JWT secret | cualquier-cosa |
| ENCRYPTION_KEY | Fernet key | base64-encoded |

**Guide detalhado:** docs/QUICK_FIX_GUIDE.md

---

## 🧪 Testing & Debugging

| Ficheiro | Localização | Descrição |
|----------|-----------|----------|
| TESTE_RESUMO.md | docs/ | Sumário de testes |
| TESTES.md | docs/ | Testes detalhados |
| VERIFICATION_CHECKLIST.md | docs/ | Checklist de validação |

### Local Testing
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
npm run dev

# API docs
http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

| Problema | Solução | Ficheiro |
|----------|---------|----------|
| Backend 404 | Verifica env vars em Render | COMECA_AQUI.md |
| Frontend 404 | VITE_API_URL sem /api | FIX_FINAL_DUPLICATE_API_PREFIX.md |
| Autenticação falha | Verifica JWT token | JWT_TESTING_GUIDE.md |
| Render deploy falha | Vê logs no Dashboard | COMECA_AQUI.md |

### Archived Troubleshooting Docs
| Ficheiro | Localização | Descrição |
|----------|-----------|----------|
| FIX_FINAL_DUPLICATE_API_PREFIX.md | _archive/_logs/ | /api/api bug fix |
| FIX_ROUTES_NOW_REGISTERED.md | _archive/_logs/ | Lazy init fix |
| FIX_SUPABASE_LAZY_INIT.md | _archive/_logs/ | Supabase init fix |
| SESSION_CONTINUATION_SUMMARY.md | docs/ | Histórico completo |

---

## 📚 Reference Documentation

### Project Status
| Ficheiro | Descrição |
|----------|-----------|
| CHECKLIST_FINAL.md | Status fase 2 + roadmap |
| SESSION_CONTINUATION_SUMMARY.md | Histórico implementação |
| RESUMO_PROBLEMA_SOLUCAO.md | Problemas encontrados/soluções |

### Tech Stack Reference
| Tecnologia | Documentação | Uso |
|------------|-----------|-----|
| FastAPI | https://fastapi.tiangolo.com | Backend |
| React | https://react.dev | Frontend |
| Supabase | https://supabase.com/docs | Database |
| Trading 212 API | https://docs.trading212.com/api | T212 integration |

---

## 🎯 Development Roadmap

### Fase 3: Automação (Próximo)
**Ficheiros a modificar:**
- backend/routes/config.py (encriptação real)
- backend/engine/scheduler.py (APScheduler)
- backend/engine/strategy.py (Grid Trading)
- frontend/src/pages/ConfigPage.tsx (UI real)

**Documentação a criar:**
- docs/AUTOMATION_GUIDE.md
- docs/GRID_TRADING.md

### Fase 4: Real-time Updates
**Ficheiros a modificar:**
- backend/websocket/ws.py (WebSocket)
- frontend/src/stores/ (WebSocket client)

---

## 📁 Estrutura de Ficheiros Explicada

```
Trading212/                    Root project
├── README.md                  Overview
├── COMECA_AQUI.md             Quick start
├── CLAUDE.md                  Arquitetura técnica
├── CHECKLIST_FINAL.md         Status + roadmap
├── INDEX.md                   Este ficheiro
├── .gitignore                 Git rules
├── render.yaml                Render config
│
├── backend/                   FastAPI app
│   ├── main.py               Entry point
│   ├── requirements.txt       Python deps
│   ├── .env.example          Template
│   ├── routes/               Endpoints
│   ├── db/                   Database
│   ├── api/                  External APIs
│   └── config/               Settings
│
├── frontend/                  React app
│   ├── index.html            HTML entry
│   ├── package.json          NPM deps
│   ├── vite.config.ts        Build config
│   ├── src/
│   │   ├── pages/            Page components
│   │   ├── components/       UI components
│   │   ├── stores/           Zustand state
│   │   └── api/              HTTP client
│   └── public/               Static assets
│
├── db/                        Database
│   └── supabase_schema.sql   SQL schema
│
├── docs/                      Documentation
│   ├── README.md             Docs overview
│   ├── api/                  API reference
│   ├── architecture/         Design docs
│   ├── deployment/           Deploy guides
│   └── *.md                  Various guides
│
└── _archive/                  Legacy files
    ├── _scripts/             Test scripts
    └── _logs/                Old docs
```

---

## 🔍 Quick Find Guide

**Procuro por...** → **Vê ficheiro...**

| Preciso saber... | Ficheiro |
|------------------|----------|
| Como começar | COMECA_AQUI.md |
| Status do projeto | CHECKLIST_FINAL.md |
| Arquitetura | CLAUDE.md |
| Como fazer deploy | docs/deployment/ |
| API endpoints | /docs (Swagger) |
| Problemas e fixes | FIX_*.md em _archive/ |
| Histórico de desenvolvimento | SESSION_CONTINUATION_SUMMARY.md |
| Autenticação | backend/routes/auth.py |
| ISIN CRUD | backend/routes/isins.py |
| Trading 212 integration | backend/api/trading212.py |
| Segurança | CLAUDE.md - Security section |
| Database | db/supabase_schema.sql |
| Frontend state | frontend/src/stores/authStore.ts |
| Errors e logging | backend/main.py |

---

## 🚀 Getting Started Paths

### Para Utilizador Novo
1. Lê **COMECA_AQUI.md**
2. Acede a https://trading212-1.onrender.com
3. Regista-te
4. Faz login

### Para Developer
1. Lê **CLAUDE.md** - Arquitetura
2. Clona repo: `git clone github.com/joulfodayres/Trading212`
3. Setup backend: `cd backend && pip install -r requirements.txt`
4. Setup frontend: `cd frontend && npm install`
5. Cria `.env` files com variáveis
6. Testa local: `python main.py` + `npm run dev`

### Para Project Manager
1. Lê **README.md** - Overview
2. Verifica **CHECKLIST_FINAL.md** - Status
3. Vê **CLAUDE.md** - Technical details
4. Roadmap em **CHECKLIST_FINAL.md** - Next steps

### Para DevOps / Deployment
1. Lê **COMECA_AQUI.md** - Troubleshooting
2. Verifica env vars em **QUICK_FIX_GUIDE.md**
3. Logs e status: **docs/deployment/**
4. HTTPS/SSL: Render automático

---

## 📞 Quick Reference Links

| Link | URL |
|------|-----|
| **Frontend Live** | https://trading212-1.onrender.com |
| **Backend Live** | https://trading212-4ojx.onrender.com |
| **API Docs** | https://trading212-4ojx.onrender.com/docs |
| **Health Check** | https://trading212-4ojx.onrender.com/health |
| **GitHub** | https://github.com/joulfodayres/Trading212 |
| **Supabase** | https://supabase.com (project: Trading212) |
| **Render** | https://render.com (dashboard) |

---

**Última atualização:** 2026-09-15 23:45 UTC  
**Versão:** Fase 2 Completa  
**Status:** ✅ Production Ready  

🚀 **Pronto para fase 3!**
