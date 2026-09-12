# 🚀 GUIA RÁPIDO DE TESTES - 5 MINUTOS

## O que já foi testado e funciona ✅

1. **API Trading 212** — 100% funcional
   - Autenticação HTTP Basic ✅
   - Saldo: €5889.99 ✅
   - Posições: 2 abertas ✅
   - Ordens: 0 pendentes ✅

2. **FastAPI Backend** — Pronto para rodar
   - Estrutura criada ✅
   - Configuração pronta ✅
   - Health checks implementados ✅

3. **React Frontend** — Pronto para compilar
   - Estrutura criada ✅
   - Componentes prontos ✅
   - Rotas configuradas ✅

---

## 🎯 COMEÇA AQUI - Teste em 3 Passos

### **Passo 1: Abrir Terminal 1 (Backend)**

```bash
cd "C:\claude\401. Trading 212 Hub\backend"
python main.py
```

**Deves ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🚀 Iniciando Trading 212 Bot API
```

### **Passo 2: Abrir Terminal 2 (Frontend)**

```bash
cd "C:\claude\401. Trading 212 Hub\frontend"
npm install
npm run dev
```

**Deves ver:**
```
VITE v5.0.8 ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

### **Passo 3: Abrir Browser**

Dois URLs para testar:

1. **Backend - Swagger Docs** (Documentação interativa)
   - http://localhost:8000/docs
   - Aqui vês todos os endpoints e podes testar

2. **Frontend - Dashboard**
   - http://localhost:5173/
   - Login page (usa email/password qualquer para stub)
   - Clica "Entrar" → Dashboard com tabela ISINs

---

## ✅ CHECKLIST DO QUE FUNCIONA

### Backend (http://localhost:8000)

```bash
# Teste direto via curl (ou usa o Swagger)

# 1. Health check
curl http://localhost:8000/health
# Esperado: {"status":"healthy"}

# 2. Info da app
curl http://localhost:8000/
# Esperado: {"name":"Trading 212 Bot API","version":"0.1.0",...}

# 3. Swagger UI (abrir no browser)
http://localhost:8000/docs
```

### Frontend (http://localhost:5173)

```
✅ Página de Login
   - Input email
   - Input password
   - Botão "Entrar"

✅ Dashboard (após login)
   - Sidebar com menu
   - ISINs table com dados mock
   - Botão "Novo ISIN"
   - Editar/Deletar buttons
   - Botão "Sair"
```

---

## 📊 O QUE TESTAR MANUALMENTE

### 1. Backend Health Checks
- [ ] Abrir http://localhost:8000/health → OK?
- [ ] Abrir http://localhost:8000/ → Info da app?
- [ ] Abrir http://localhost:8000/docs → Swagger loads?

### 2. Frontend UI
- [ ] Abrir http://localhost:5173/ → Login page?
- [ ] Preencher email/password qualquer
- [ ] Clica "Entrar" → Dashboard?
- [ ] Sidebar navega entre views?
- [ ] Tabela ISINs mostra dados?
- [ ] Botão "Novo ISIN" abre form?
- [ ] Botão "Sair" funciona?

### 3. Integração (depois)
- [ ] Login com credenciais reais (Supabase)
- [ ] Criar ISIN → Fetch dados T212
- [ ] Toggle ON/OFF automação
- [ ] Ver dados em tempo real

---

## 🎥 VÍDEO MENTAL DO QUE DEVES VER

### Terminal 1 (Backend)
```
C:\claude\401. Trading 212 Hub\backend> python main.py
  ↓
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🚀 Iniciando Trading 212 Bot API
Ambiente: development
Debug: True

[Aqui fica à espera de requests... não fecha]
```

### Terminal 2 (Frontend)
```
C:\claude\401. Trading 212 Hub\frontend> npm run dev
  ↓
VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help

[Aqui fica à espera de mudanças nos ficheiros... não fecha]
```

### Browser Tabs
```
Tab 1: http://localhost:8000/docs
  → Swagger UI com todos os endpoints

Tab 2: http://localhost:5173/
  → Trading 212 Bot login page
  → Preenche qualquer login
  → Clica "Entrar"
  → Vê o Dashboard
```

---

## 🔧 Se algo não funcionar

### Backend não inicia?
```bash
# Verifica se port 8000 está livre
netstat -ano | findstr :8000

# Se estiver ocupada, mata o processo
taskkill /PID <PID> /F

# Ou usa outra port (edita main.py)
```

### Frontend não instala?
```bash
# Limpa cache
npm cache clean --force

# Tenta novamente
npm install
npm run dev
```

### Encoding errors?
```bash
# Windows tem problemas com UTF-8
# Solução: Já foi adicionada no test_t212_api.py
# Frontend não deve ter problema pois é JS
```

---

## 📈 PRÓXIMO PASSO APÓS TESTES

Se tudo funciona:

1. **Implementar Autenticação Supabase**
   - Setup BD
   - Integrar login real
   - Persistir dados

2. **Conectar CRUD ISINs**
   - POST /isins → Adicionar
   - GET /isins → Listar
   - PUT /isins/{id} → Editar
   - DELETE /isins/{id} → Deletar

3. **Integração T212**
   - Fetch dados reais quando adiciona ISIN
   - Mostrar na UI

4. **Estratégia Trading**
   - Scheduler
   - Grid Trading logic
   - Execute trades

---

## ⏱️ Timeline Estimado

```
Agora (0-30 min):
  ✅ Backend rodando
  ✅ Frontend rodando
  ✅ UI funcional

Próximas 1-2 horas:
  🔄 Supabase + Auth
  🔄 CRUD ISINs

Próximas 4-6 horas:
  🔄 Estratégia Trading
  🔄 Real-time updates

Depois:
  🔄 Deploy Render
  🔄 Testes completos
```

---

## 🎯 AÇÃO IMEDIATA

**Abre uma terminal agora e executa:**

```bash
cd "C:\claude\401. Trading 212 Hub\backend"
python main.py
```

**Se vires "Uvicorn running on http://0.0.0.0:8000" → ✅ SUCESSO!**

Depois, noutra terminal:

```bash
cd "C:\claude\401. Trading 212 Hub\frontend"
npm install && npm run dev
```

**Se vires "Local: http://localhost:5173/" → ✅ SUCESSO!**

Depois, abre no browser:
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173/

---

**Vamos testar agora?** 🚀
