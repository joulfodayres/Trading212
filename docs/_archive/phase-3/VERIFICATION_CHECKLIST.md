# ✅ CHECKLIST - RENDER FIX VERIFICATION

**Data:** 2026-09-15  
**Objetivo:** Verificar que Backend ficou online após configurar env vars  
**Tempo estimado:** 20 minutos total (5 config + 10 deploy + 5 testes)

---

## PHASE 1: CONFIGURAÇÃO (5 minutos)

- [ ] Abrir Render Dashboard: https://dashboard.render.com
- [ ] Clique em "trading212-4ojx" (Backend service)
- [ ] Vai a "Environment" (no menu lateral esquerdo)
- [ ] Clique em "Add Environment Variable"
- [ ] Adiciona a primeira variável:
  - [ ] Key: SUPABASE_URL
  - [ ] Value: https://gocvyhizqggqaxryuplu.supabase.co
  - [ ] Clique "Save" ou "Add"
- [ ] Repete para as restantes 8 variáveis (ver QUICK_FIX_GUIDE.md)
- [ ] Verifica que todas 9 aparecem na lista "Current variables"

---

## PHASE 2: DEPLOYMENT (10-15 minutos)

- [ ] Na página do serviço, clique em "Manual Deploy"
- [ ] Confirma (se aparecer popup)
- [ ] Status muda para "Building" (yellow/orange)
- [ ] Aguarda... (típico 5-10 minutos)
- [ ] Logs começam a aparecer (Render → Logs)
- [ ] Procura por "Server started on" ou "Uvicorn running on"
- [ ] Status muda para "Live" (green)
- [ ] Anota o timestamp quando ficou "Live"

---

## PHASE 3: TESTES (5 minutos)

### Test 3.1: Root Endpoint
- [ ] Abre browser: https://trading212-4ojx.onrender.com
- [ ] Espera resposta JSON:
  ```json
  {
    "name": "Trading 212 Bot API",
    "version": "0.1.0",
    "status": "running",
    "environment": "production"
  }
  ```
- [ ] Se vir isto: ✅ SUCESSO - Backend online!
- [ ] Se não vir, vai para TROUBLESHOOTING

### Test 3.2: Swagger UI
- [ ] Abre browser: https://trading212-4ojx.onrender.com/docs
- [ ] Deveria ver interface interativa com todos os endpoints
- [ ] Se vir isto: ✅ API documentation online!

### Test 3.3: Frontend Connection
- [ ] Abre browser: https://trading212-1.onrender.com
- [ ] Clique em "Login" ou "Register"
- [ ] Insira email: teste@trading212.com
- [ ] Insira password: qualquer coisa
- [ ] Clique "Login"
- [ ] Se: ✅ Redireciona para Dashboard = Sucesso!
- [ ] Se: ❌ Erro de conexão = Backend ainda não responde

### Test 3.4: API Call (Optional)
```bash
# Terminal/PowerShell
curl -X POST https://trading212-4ojx.onrender.com/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"teste@trading212.com","password":"password123"}'

# Esperado: Resposta com access_token ou error message
# (qualquer resposta = backend respondeu ✓)
```

---

## ✅ SUCCESS CRITERIA

Marcar como **COMPLETO** se:

- [ ] Render status = "Live" (green)
- [ ] https://trading212-4ojx.onrender.com retorna JSON
- [ ] Swagger UI acessível
- [ ] Frontend consegue fazer login (ou tenta)
- [ ] **Nenhum erro HTTP 000 ou timeout**

---

## ❌ TROUBLESHOOTING

Se algo falhar:

### Problem: Status ainda é "Building" após 15 minutos
```
Ação: Espera mais 5 minutos (máximo 20 min total)
Se continuar: 
  1. Clique "Cancel Deploy"
  2. Clique "Manual Deploy" novamente
  3. Se ainda não funcionar → Lê logs
```

### Problem: Status é "Live" mas não responde (HTTP 000)
```
Ação: Verifica os Logs
  1. Render → trading212-4ojx → Logs (scroll down)
  2. Procura por linhas vermelhas de erro
  3. Exemplos:
     - "ValidationError" → Variável mal copiada
     - "AuthApiError" → Supabase credentials erradas
     - "Connection refused" → Rede bloqueada (improvável)
```

### Problem: Vejo erro "port 8000 already in use"
```
Ação: Render precisa matar processo anterior
  1. Clique "Cancel Deploy"
  2. Aguarda 2 minutos
  3. Clique "Manual Deploy"
  4. Repete deploy
```

### Problem: Vejo erro sobre variável mal formatada
```
Ação: Verifica se copiou exatamente
  1. Render → trading212-4ojx → Environment
  2. Revê cada variável (especialmente SUPABASE_KEY e SECRET)
  3. Se tiver erro de cópia (espaço extra, etc):
     - Delete e re-adiciona
     - Manual Deploy novamente
```

---

## 📊 LOG DIAGNOSTICS

Se não funcionar, copia as últimas linhas do log e procura:

```
✅ SUCESSO (esperar isto):
- "Application startup complete"
- "Uvicorn running on"
- "Server started"

❌ ERRO (procura isto):
- "ValidationError" (env var falta ou inválida)
- "Authentication failed" (Supabase credenciais erradas)
- "Connection refused" (não consegue conectar BD)
- "Module not found" (dependência em falta)
```

---

## 📈 DEPOIS DE SUCESSO

Quando Backend ficar **ONLINE**:

1. **Próxima fase:** Testes de endpoints
   - Arquivo: `TESTES.md` ou `docs/api/JWT_TESTING_GUIDE.md`

2. **Depois:** Automação (Grid Trading)
   - Arquivo: `docs/guides/ROADMAP_FINAL.md`

3. **Depois:** Real-time updates
   - Arquivo: `CLAUDE.md` (Fase 5 no roadmap)

---

## 📝 NOTAS

- Render usa cache. Se ainda vir erro antigo após 20 min, algo está mal.
- Env vars aplicam-se apenas a novos deploys (não afeta código existente).
- Se precisar mudar variáveis depois: Render → Environment → Edit → Manual Deploy.
- .env local NÃO afeta Render (correto, está em .gitignore).

---

## 🎯 CONCLUSÃO

| Passo | Status | Tempo |
|-------|--------|-------|
| Configurar 9 vars | [ ] | 5 min |
| Manual Deploy | [ ] | 10 min |
| Testes | [ ] | 5 min |
| **TOTAL** | [ ] | **20 min** |

**Target:** Backend online em 20 minutos ✅

---

**Criado:** 2026-09-15 23:00 UTC  
**Versão:** 1.0  
**Status:** Pronto para usar
