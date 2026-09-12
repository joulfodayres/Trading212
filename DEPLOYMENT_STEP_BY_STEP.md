# 🚀 DEPLOYMENT STEP-BY-STEP - Trading 212 Bot

## PRÉ-REQUISITOS

- ✅ Repositório GitHub (privado)
- ✅ Conta Supabase
- ✅ Conta Render
- ✅ Código pronto para deploy

---

## PASSO 1: Push para GitHub

```bash
cd "C:\claude\401. Trading 212 Hub"

# Inicializar git (se não existir)
git init
git add .
git commit -m "Initial commit: Trading 212 Bot MVP"

# Adicionar remote
git remote add origin https://github.com/TU_USERNAME/trading212-bot.git

# Push para main
git branch -M main
git push -u origin main
```

**Verifica:** GitHub mostra o código? ✅

---

## PASSO 2: Setup Supabase (BD + Auth)

### 2.1 Criar Projeto Supabase

1. Vai a supabase.com → New Project
2. Nome: `trading212-bot`
3. Password: Guarda em local seguro
4. Região: Escolhe a mais próxima

### 2.2 Executar SQL Scripts

1. Supabase → SQL Editor
2. New Query
3. Copia o conteúdo de `db/supabase_schema.sql`
4. Executa

**Verifica:** Tabelas criadas? (users, isins, config, strategies, trades, logs)

### 2.3 Copiar Credenciais

1. Settings → API
2. Copia:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_KEY`
   - JWT Secret → `SUPABASE_JWT_SECRET`

**Guarda numa folha de papel ou gestor de senhas!**

---

## PASSO 3: Configurar Render (Backend)

### 3.1 Conectar GitHub ao Render

1. render.com → Dashboard
2. New → Web Service
3. Connect Repository
4. Autoriza GitHub
5. Seleciona `trading212-bot`

### 3.2 Configurar Backend Service

**Nome:** `trading212-bot-api`
**Build Command:** `pip install -r backend/requirements.txt`
**Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3.3 Adicionar Environment Variables

No Render, vai a Settings → Environment:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
T212_API_KEY=40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU
T212_API_SECRET=iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0
T212_ENVIRONMENT=demo
T212_BASE_URL=https://demo.trading212.com/api/v0
FASTAPI_ENV=production
FASTAPI_DEBUG=False
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENCRYPTION_KEY=mhRLQKMKc2d5fJ7pX8vN3qZ9wK1mL2nO3pR4sT5uV6w=
LOG_LEVEL=INFO
SCHEDULER_CHECK_INTERVAL=300
```

### 3.4 Deploy

Clica "Deploy" e aguarda (~5-10 min).

**Verifica:** URL do tipo `https://trading212-bot-api.onrender.com` ✅

---

## PASSO 4: Testar Backend (sem Frontend)

### 4.1 Health Check

Abre no browser:
```
https://trading212-bot-api.onrender.com/health
```

**Esperado:**
```json
{"status":"healthy"}
```

### 4.2 Swagger Docs

```
https://trading212-bot-api.onrender.com/docs
```

Deves ver todos os endpoints (ainda não implementados, mas estrutura existe).

---

## PASSO 5: Configurar Render (Frontend)

### 5.1 Criar novo Web Service no Render

1. New → Web Service
2. Connect Repository (mesmo repositório)
3. **Nome:** `trading212-bot-frontend`

### 5.2 Configurar Frontend Service

**Build Command:** 
```
cd frontend && npm install && npm run build
```

**Start Command:**
```
npm run serve
```

### 5.3 Adicionar Environment Variables

```
VITE_API_URL=https://trading212-bot-api.onrender.com/api
NODE_ENV=production
```

### 5.4 Deploy

Clica "Deploy" e aguarda (~10-15 min).

**Verifica:** URL do tipo `https://trading212-bot-frontend.onrender.com` ✅

---

## PASSO 6: Testar Tudo Junto

### 6.1 Frontend

Abre no browser:
```
https://trading212-bot-frontend.onrender.com
```

Deves ver:
- ✅ Login page
- ✅ Campo email
- ✅ Campo password
- ✅ Botão "Entrar"

### 6.2 Login (stub por enquanto)

- Preenche qualquer email/password
- Clica "Entrar"
- Deves ser direcionado para Dashboard

### 6.3 Dashboard

Deves ver:
- ✅ Sidebar com 3 menus
- ✅ Tabela de ISINs (mock data)
- ✅ Botão "Novo ISIN"
- ✅ Botão "Sair"

---

## PASSO 7: Configurar Domínio Custom (opcional)

Se quiseres um domínio tipo `trading212bot.com`:

1. Render → Settings → Custom Domain
2. Adiciona domínio
3. Aponta DNS para Render

**Ou:** Deixa o `.onrender.com` por enquanto.

---

## ✅ CHECKLIST FINAL

- [ ] Código em GitHub
- [ ] Supabase BD criada e configurada
- [ ] Backend rodando em Render
- [ ] `/health` endpoint funciona
- [ ] Frontend rodando em Render
- [ ] Login page carrega
- [ ] Dashboard carrega após login
- [ ] Sidebar navega entre views

---

## 🆘 TROUBLESHOOTING

### Backend não faz deploy?

Verifica:
```bash
# Localmente
cd backend
pip install -r requirements.txt
python main.py

# Se funciona localmente, o problema é:
# 1. Env vars faltando em Render
# 2. Python version incompatível
# 3. Erro de importação
```

### Frontend não carrega?

```bash
# Localmente
cd frontend
npm install
npm run build

# Se build falha, verificas:
# 1. npm install funciona?
# 2. Há erros TypeScript?
# 3. Faltam ficheiros?
```

### Erros de CORS?

Supabase pode bloquear requests. Adiciona em backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trading212-bot-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 PRÓXIMOS PASSOS APÓS DEPLOYMENT

1. **Implementar autenticação Supabase real**
   - Login/register com Supabase Auth
   - JWT tokens

2. **Conectar CRUD ISINs**
   - POST /isins
   - GET /isins
   - PUT /isins/{id}
   - DELETE /isins/{id}

3. **Integração T212 API**
   - Fetch dados quando adiciona ISIN
   - Atualizar em tempo real

4. **Estratégia Trading**
   - Scheduler
   - Grid Trading logic
   - Execute trades

---

## 🚀 PRONTO!

Quando terminares todos os passos, terás:

```
🌍 https://trading212-bot-frontend.onrender.com
   └─→ Browser acesso 24/7
       └─→ Conecta a API em Render
           └─→ API conecta a BD em Supabase
               └─→ Executa trades via T212 API
```

Sem nenhum ficheiro Python a correr localmente! ✅

---

**Começamos agora?** 🚀

Execute o Passo 1 (Push para GitHub) e avisa-me quando estiver pronto.
