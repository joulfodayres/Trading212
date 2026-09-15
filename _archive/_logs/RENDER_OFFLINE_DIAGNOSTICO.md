# 🚨 RENDER DEPLOYMENT - PROBLEMA IDENTIFICADO

**Data:** 2026-09-15  
**Status:** Backend offline - Solução encontrada  
**Ação necessária:** Configurar environment variables no Render Dashboard

---

## 📍 O PROBLEMA

**Ambos os serviços estão offline porque o backend não inicializa.**

```
Render Dashboard → trading212-4ojx (Backend)
Status: Live (aparenta estar online)
Real Status: CRASHED (não responde)

Razão: Settings valida 9 environment variables ao iniciar
Problema: Nenhuma delas foi configurada em Render
Resultado: Backend falha com "8 validation errors"
```

---

## 🔍 COMO DESCOBRI

1. Session anterior tinha agentes de teste
2. Ambos os agentes receberam timeout (600s)
3. Backend nunca respondeu (HTTP 000)
4. Executei diagnóstico local
5. Encontrei: .env local tem tudo, mas Render runtime não tem nada

```
Local (.env): 17 variáveis OK
Render (runtime): 0 variáveis carregadas
Backend startup: FALHA
```

---

## ✅ SOLUÇÃO PASSO-A-PASSO

### PASSO 1: Abrir Render Dashboard

```
1. Browser: https://dashboard.render.com
2. Login com a tua conta
3. Clica em "trading212-4ojx" (Backend)
```

### PASSO 2: Environment Variables

```
Na página do serviço, clica em "Environment" (lado esquerdo)
```

Verás algo como:

```
Environment
┌─────────────────────────────────┐
│ Add Environment Variable        │
│ Key: [_________________]        │
│ Value: [_________________]      │
│ Add                             │
└─────────────────────────────────┘

Current variables:
(lista vazia ou sem as nossas)
```

### PASSO 3: Adicionar as 9 Variáveis Críticas

**Copia cada linha abaixo e cola no Render:**

```
SUPABASE_URL
https://gocvyhizqggqaxryuplu.supabase.co

---

SUPABASE_KEY
sb_publishable_283LZ_pvCLRaxYLaikfA7w_h4oSLVCW

---

SUPABASE_JWT_SECRET
sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4

---

T212_API_KEY
40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU

---

T212_API_SECRET
iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0

---

T212_ENVIRONMENT
demo

---

T212_BASE_URL
https://demo.trading212.com/api/v0

---

JWT_SECRET_KEY
trading212-bot-secret-key-change-in-production

---

ENCRYPTION_KEY
YZXbxF3a-y2HQUXprACQ0lSkhW8imYBJ1D1hYcsL61Y=
```

**Instruções de input:**

1. Click em "Add Environment Variable"
2. **Key:** SUPABASE_URL
3. **Value:** https://gocvyhizqggqaxryuplu.supabase.co
4. Click "Save" (ou "Add")
5. Repete para cada variável

### PASSO 4: Salvar e Redeploy

Depois de adicionar todos:

```
1. Clica em "Manual Deploy" ou "Redeploy" (botão azul)
2. Aguarda 5-10 minutos (watch os logs)
3. Status muda para "Live" quando completo
```

### PASSO 5: Verificar se ficou online

```
URL: https://trading212-4ojx.onrender.com
Resposta esperada:

{
  "name": "Trading 212 Bot API",
  "version": "0.1.0",
  "status": "running",
  "environment": "production"
}
```

Se vir isto ✅ = Backend ficou online!

---

## 🎯 Próximos Passos Após Fix

### Quando Backend ficar online:

1. **Frontend já funciona** (porque consegue fazer API calls)
2. **Endpoints estarão disponíveis:**
   - POST /api/auth/login
   - POST /api/auth/register
   - GET /api/isins
   - etc.
3. **Swagger UI funciona:**
   - https://trading212-4ojx.onrender.com/docs

### Teste rápido:

```bash
# Testar login
curl -X POST https://trading212-4ojx.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@trading212.com","password":"password123"}'

# Deve retornar: { access_token, token_type, user_id, email, message }
```

---

## 📋 Checklist de Confirmação

Depois de configurar Render:

- [ ] Adicionar 9 variáveis no Render Dashboard
- [ ] Cliqar "Manual Deploy"
- [ ] Aguardar 5-10 minutos
- [ ] Status muda de "Building" → "Live"
- [ ] Visitar https://trading212-4ojx.onrender.com
- [ ] Ver JSON com "status": "running"
- [ ] Visitar Frontend: https://trading212-1.onrender.com
- [ ] Login funciona (deveria conectar ao backend real agora)

---

## 🚨 Se Continuar Falhando

Se após Manual Deploy ainda ver erro:

### Verificar Logs

1. Render Dashboard → trading212-4ojx
2. Clica em "Logs" (lado esquerdo, ou scroll down)
3. Procura por linhas vermelhas de erro
4. Exemplos de erros comuns:

```
ERROR - ValidationError - Field required
→ Uma das variáveis está mal copiada

ERROR - supabase.exceptions.AuthApiError
→ Credentials do Supabase estão errados

ERROR - ConnectionError
→ Rede está bloqueada (improvável em Render)

ERROR - Port 8000 already in use
→ Redeploy não killing o processo anterior
  → Solução: "Cancel Deploy" + "Redeploy"
```

### Solução Última Resort

Se nada funcionar:

```
1. Render Dashboard → trading212-4ojx
2. Clica em "Settings" (gear icon)
3. Scroll down → "Delete Service"
4. Re-criar o serviço (lê DEPLOYMENT_STEP_BY_STEP.md)
```

---

## ℹ️ Por Que Isto Aconteceu

### Contexto

1. **Code foi commitado para GitHub** ✅
   - Mas `.env` está no `.gitignore` ✅ (segurança)

2. **Render auto-deploy foi acionado** ✅
   - Backend code foi atualizado
   - Mas `render.yaml` estava vazio (não configurado)

3. **Render tentou iniciar o backend** ⚠️
   - Sem environment variables definidas
   - FastAPI/Pydantic falha validation
   - Processo crashes

4. **Resultado:** Backend offline ❌

### Como Evitar no Futuro

1. **NUNCA** commitar `.env` para GitHub ✅ (já fazemos isto)
2. **SEMPRE** adicionar env vars via Render Dashboard (ou `render.yaml`)
3. **Verificar** que backend inicia: `POST /health` deve retornar 200

---

## 📌 Ficheiros Relevantes

- `backend/.env` - Credenciais (local only, não commitado)
- `backend/config/settings.py` - Define quais variáveis são obrigatórias
- `backend/main.py` - Ponto de entrada do FastAPI
- `RENDER_FIX_OFFLINE_ISSUE.md` - Este documento

---

**Criado:** 2026-09-15 22:30 UTC  
**Status:** Blocker identificado + Solução documentada  
**Próxima ação:** User configurar env vars em Render Dashboard
