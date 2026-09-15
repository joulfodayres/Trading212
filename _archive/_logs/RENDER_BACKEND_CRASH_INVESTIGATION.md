# 🚨 BACKEND AINDA EM CRASH - INSTRUÇÕES PARA INVESTIGAR

**Status:** Backend não responde nem a root endpoint  
**Provável Causa:** Deploy ainda em progresso OU erro no código

---

## 🔍 O QUE FAZER AGORA

### PASSO 1: Verificar Status do Render Dashboard

1. Vai a: **https://dashboard.render.com**
2. Clica em **"trading212-4ojx"** (Backend)
3. Vê o tab **"Deploys"**

**O que procurar:**

```
Status: "Building" (amarelo/laranja)
→ Significa: Deploy ainda em progresso
→ Ação: Aguarda mais 5-10 minutos

Status: "Live" (verde)
→ Significa: Deploy completo
→ Problema: Backend respondeu mas 404 nos endpoints
→ Ação: Ir para PASSO 2

Status: "Failed" (vermelho) ou não aparece
→ Significa: Deploy falhou
→ Ação: Ir para PASSO 3
```

---

### PASSO 2: Se Status é "Live" → Ver os Logs

1. Na página do Backend, clica na tab **"Logs"**
2. Scroll down para ver as últimas linhas
3. Procura por:

**Esperado (sucesso):**
```
Application startup complete
Uvicorn running on http://0.0.0.0:8000
[INFO] Iniciando Trading 212 Bot API
```

**Erro comum (Supabase credentials inválidas):**
```
ERROR - supabase.exceptions.AuthApiError
ERROR - Failed to initialize Supabase client
```

**Erro de módulo:**
```
ModuleNotFoundError: No module named 'supabase'
```

---

### PASSO 3: Se Deploy Falhou ou Crashed

Opção A: **Tentar Manual Deploy novamente**

1. Tab "Deploys"
2. Clica "Manual Deploy"
3. Aguarda 10 minutos

Opção B: **Se continua a falhar, faz um Redeploy forçado**

1. Tab "Settings" (gear icon)
2. Scroll até "Redeploy"
3. Clica "Redeploy latest commit"
4. Aguarda

---

## 📋 CHECKLIST PARA MIM AJUDAR

Para que eu possa diagnosticar melhor, copia desta página:

**1. Status do Deploy:**
```
[ ] Building (ainda está a compilar)
[ ] Live (pronto mas com erro)
[ ] Failed (falhou)
[ ] Não sei
```

**2. Se é "Live", copia as últimas linhas dos logs (aquelas que dizem ERROR ou algo vermelho)**

**3. Se é "Building", que tempo leva? (ex: 2 minutos, 5 minutos, mais de 10...)**

---

## ⏳ TIMELINE ESPERADA

```
0 min:    Commit pushed para GitHub
0-1 min:  Render deteta e começa auto-deploy
1-5 min:  Building (downloading deps, etc)
5-10 min: Starting (iniciando FastAPI)
10-15 min: Live (completo!)
```

Se passou 15 minutos e ainda está "Building" → algo está errado.

---

## 🎯 PRÓXIMAS AÇÕES

**Enquanto isso, faz isto:**

1. Abre Render Dashboard
2. Vai a trading212-4ojx
3. Ver se está "Building" ou "Live"
4. Se "Live": Vê os logs (copia erro se houver)
5. Relança comigo com essas informações

---

**Aguardando teu feedback! 💪**
