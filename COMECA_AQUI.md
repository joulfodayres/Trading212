# 🚀 COMEÇA AQUI - Quick Start

**Status:** ✅ Sistema ao vivo e operacional

---

## 🎯 Objetivo

Sistema de trading automatizado integrado com Trading 212, acessível via browser de qualquer lugar.

---

## ✅ O que já funciona (Fase 2)

✅ **Autenticação Real**
- Registar nova conta (Firebase/Supabase)
- Fazer login com email/password
- JWT token de 24 horas
- Logout e sessão

✅ **CRUD ISINs** (Experimental)
- Adicionar ISIN
- Listar ISINs do utilizador
- Editar ISIN (nome, automação)
- Deletar ISIN

✅ **Infraestrutura**
- Backend em Render (Python/FastAPI)
- Frontend em Render (React)
- BD Supabase (PostgreSQL + RLS)
- HTTPS automático

---

## 🔑 Como usar

### Passo 1: Aceder ao Sistema

```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com/docs
```

### Passo 2: Registar Conta

1. Clica em **"Sign Up"**
2. Entra email + password (mínimo 6 caracteres)
3. Confirma password
4. Clica **Register**
5. ✅ Conta criada em Supabase

### Passo 3: Fazer Login

1. Clica em **Login**
2. Entra email + password (a mesma da conta)
3. ✅ JWT token guardado em localStorage (24h)

### Passo 4: Dashboard

- Vês a sidebar com navigation
- Tabs: ISINs, Configuração, Histórico
- Por enquanto, dados mock

---

## 🧪 Testar com API

### Health Check
```bash
curl https://trading212-4ojx.onrender.com/health
# → {"status": "healthy"}
```

### Login
```bash
curl -X POST https://trading212-4ojx.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"seu-email@example.com","password":"sua-password"}'
# → {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...", "token_type": "bearer"}
```

### Listar ISINs
```bash
curl https://trading212-4ojx.onrender.com/api/isins \
  -H "Authorization: Bearer <seu-token>"
# → [{"id": "...", "isin": "...", ...}]
```

---

## 📁 Estrutura de Ficheiros

```
Trading212/
├── backend/            # FastAPI (Python)
│   ├── main.py        # Entry point
│   ├── routes/        # /auth, /isins, /config
│   ├── db/            # Supabase client
│   ├── api/           # Trading 212 client
│   └── config/        # Settings & env vars
│
├── frontend/          # React (TypeScript)
│   ├── src/pages/    # Login, Dashboard, etc
│   ├── src/components/ # UI components
│   ├── src/stores/    # Zustand auth store
│   └── src/api/       # Axios client
│
├── docs/              # Documentação
├── _archive/          # Scripts antigos
└── db/               # SQL schemas
```

---

## 🔧 Configuração Render (Env Vars)

Se deploy falhar, verifica se todas estas 9 variáveis estão em **Render Dashboard → Environment**:

```
1. SUPABASE_URL=https://[project].supabase.co
2. SUPABASE_KEY=[anon-key]
3. SUPABASE_JWT_SECRET=[jwt-secret]
4. T212_API_KEY=[api-key]
5. T212_API_SECRET=[api-secret]
6. T212_ENVIRONMENT=demo
7. T212_BASE_URL=https://demo.trading212.com/api/v0
8. JWT_SECRET_KEY=[qualquer-coisa]
9. ENCRYPTION_KEY=[base64-encoded-key]
```

---

## 🚨 Troubleshooting

### Problema: Backend 404 (endpoints não encontrados)
- **Causa:** Env vars não carregadas em Render
- **Fix:** Verifica em Render Dashboard se as 9 variáveis estão lá

### Problema: Frontend retorna 404 em Register
- **Causa:** Frontend env var estava `https://...com/api` (duplica /api)
- **Fix:** Deve ser `https://...com` (sem /api - Axios adiciona)

### Problema: Render não mostra novo código
- **Causa:** Cache em produção
- **Fix:** Força rebuild com git push ou redeploy manual

---

## 📚 Documentação Completa

Ver:
- **INDEX.md** - Índice com descrição de todos os ficheiros
- **docs/README.md** - Arquivos e guias detalhados
- **docs/api/** - Guia de endpoints
- **CLAUDE.md** - Arquitetura técnica completa

---

## 🎯 Próximas Fases

### Fase 3: Automação (Próximo Sprint)
- [ ] Configurar T212 credentials (encriptado)
- [ ] Conectar Dashboard com real data
- [ ] Grid Trading scheduler (APScheduler)
- [ ] Trade execution

### Fase 4: Polish
- [ ] Real-time updates (WebSocket)
- [ ] Gráficos (Recharts)
- [ ] Histórico de trades
- [ ] Alertas

---

## 👨‍💻 Development Local (Optional)

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python main.py
# → Running on http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
# → Running on http://localhost:5173
```

---

## 📊 Status Atual

| Item | Status |
|------|--------|
| Frontend Online | ✅ |
| Backend Online | ✅ |
| Autenticação | ✅ |
| BD Supabase | ✅ |
| CRUD ISINs | ✅ |
| Automação | ⏳ Próximo |
| Real-time | ⏳ Próximo |
| Gráficos | ⏳ Próximo |

---

## 🔐 Segurança

- ✅ JWT tokens (24h expiration)
- ✅ Row-Level Security (Supabase)
- ✅ API keys encriptados com Fernet
- ✅ HTTPS automático
- ✅ CORS configurado
- ✅ Passwords hashed com bcrypt

---

**Última atualização:** 2026-09-15
**Desenvolvedor:** Trading 212 Bot
**Próxima sesão:** Fase 3 Automação

🚀 Pronto para expandir!
