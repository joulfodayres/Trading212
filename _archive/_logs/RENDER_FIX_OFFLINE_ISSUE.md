# 🔴 PROBLEMA CRÍTICO: RENDER BACKEND & FRONTEND OFFLINE

## Status: Backend não inicia por falta de environment variables

---

## 📊 Diagnóstico

Ambos os serviços em Render (Backend e Frontend) estão **OFFLINE** porque:

### Backend (trading212-4ojx.onrender.com)
- **Problema:** Render **NÃO TEM os environment variables definidos**
- **Causa:** O ficheiro `.env` está no `.gitignore` (correto), mas Render não foi configurado
- **Resultado:** Settings valida ao iniciar e falha com 8 validation errors
- **Status:** Crashed / não responde

### Frontend (trading212-1.onrender.com)  
- **Problema:** Dependência do Backend (API calls falham)
- **Resultado:** Frontend carrega mas sem dados
- **Status:** Online mas não funcional

---

## 🔧 SOLUÇÃO: Configurar Render Environment Variables

### Passo 1: Ir ao Render Dashboard

1. Acede a: https://dashboard.render.com
2. Clica em **"trading212-4ojx"** (Backend)
3. Clica na aba **"Environment"**

### Passo 2: Adicionar as 9 variáveis obrigatórias

Copia e cola cada uma:

#### SUPABASE (Copiar de .env)
```
SUPABASE_URL=https://gocvyhizqggqaxryuplu.supabase.co
SUPABASE_KEY=sb_publishable_283LZ_pvCLRaxYLaikfA7w_h4oSLVCW
SUPABASE_JWT_SECRET=sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4
```

#### TRADING 212 (DEMO)
```
T212_API_KEY=40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU
T212_API_SECRET=iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0
T212_ENVIRONMENT=demo
T212_BASE_URL=https://demo.trading212.com/api/v0
```

#### JWT & ENCRYPTION
```
JWT_SECRET_KEY=trading212-bot-secret-key-change-in-production
ENCRYPTION_KEY=YZXbxF3a-y2HQUXprACQ0lSkhW8imYBJ1D1hYcsL61Y=
```

### Passo 3: Salvar e Redeploy

1. Clica em **"Save"** (Render guarda automaticamente)
2. Vai a **"Deploys"**
3. Clica em **"Manual Deploy"**
4. Aguarda 5-10 minutos

### Passo 4: Verificar se ficou online

1. Vai a: https://trading212-4ojx.onrender.com
2. Deve aparecer:
```json
{
  "name": "Trading 212 Bot API",
  "version": "0.1.0",
  "status": "running",
  "environment": "production"
}
```

---

## 📝 Notas Importantes

### ⚠️ Segurança
- **NUNCA** commitar `.env` para GitHub (está no `.gitignore` ✓)
- **SEMPRE** adicionar credentials via Render Dashboard (env vars)
- **Secrets sensíveis** precisam de rotação periodicamente

### 🔄 Process
1. Render reads environment variables
2. Backend loads settings.py
3. FastAPI starts on port 8000
4. All routes become available

### 🐛 Se ainda não funcionar
1. Verifica os logs: Render Dashboard → trading212-4ojx → "Logs"
2. Procura por erro vermelho 🔴
3. Se vires erro, copia a mensagem e relancia

---

## ✅ Confirmação de Sucesso

Quando ficar online:

1. **Backend responde:**
   ```bash
   curl https://trading212-4ojx.onrender.com
   ```
   → Deve retornar JSON com status "running"

2. **Swagger UI funciona:**
   ```
   https://trading212-4ojx.onrender.com/docs
   ```

3. **Frontend consegue fazer API calls**

---

**Última atualização:** 2026-09-15  
**Status:** Blocker found - Solution documented
**Ação necessária:** Configurar Render env vars
