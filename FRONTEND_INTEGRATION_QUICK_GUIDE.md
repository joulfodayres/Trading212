# Frontend-Backend Integration - Quick Reference 🚀

**Última atualização:** 2026-09-15
**Status:** ✅ Completo e pronto para testar

---

## 📋 What Was Done

Transformação completa: **Mock Data → Real HTTP API Calls**

### Componentes Modificados:
| Componente | Mudanças | Endpoints |
|-----------|----------|-----------|
| **LoginPage** | ✅ Integrado com authStore | POST /auth/login |
| **RegisterPage** | ✨ **NOVO** | POST /auth/register |
| **ISINTable** | ✅ CRUD completo | GET, POST, DELETE, PUT (sync, toggle) |
| **ISINDetailPage** | ✅ Carrega dados reais | GET /isins/{id}, GET /trades |
| **ConfigForm** | ✅ Credenciais + teste | PUT /config, POST /test |
| **API Client** | ✅ JWT interceptor | Bearer token automático |
| **AuthStore** | ✅ Resposta JSON corrigida | Login + Register reais |
| **Routing** | ✅ RegisterPage adicionada | /register path |

---

## 🔌 API Integration Checklist

### ✅ Autenticação
- [x] POST /api/auth/login
- [x] POST /api/auth/register
- [x] JWT token em localStorage
- [x] Authorization header automático
- [x] 401 handling → logout + redirect

### ✅ ISINs
- [x] GET /api/isins (lista todos)
- [x] POST /api/isins (criar novo)
- [x] GET /api/isins/{id} (detalhe)
- [x] PUT /api/isins/{id}/automation/toggle
- [x] DELETE /api/isins/{id}
- [x] GET /api/isins/{id}/trades
- [x] GET /api/isins/sync-from-trading212

### ✅ Config
- [x] PUT /api/config (guardar credenciais)
- [x] POST /api/config/test (testar conexão)

---

## 🧪 Teste Rápido (2 minutos)

```bash
# Terminal 1: Backend
cd backend && python main.py
# Esperar por "Application startup complete"

# Terminal 2: Frontend
cd frontend && npm run dev
# Abrir http://localhost:5173
```

### Fluxo Teste:
```
1. Clicar "Criar conta" → /register
2. Email: test@test.com
3. Password: 123456
4. Confirmar: 123456
5. ✅ Deve fazer POST /api/auth/register
6. ✅ Deve ir para /dashboard
7. ✅ Deve aparecer "Olá, test@test.com"
```

---

## 🔑 Key Changes

### 1️⃣ API Client (frontend/src/api/client.ts)
```diff
- baseURL: API_BASE
+ baseURL: `${API_BASE}/api`
```
**Resultado:** Todos os requests vão para `http://localhost:8000/api/...`

### 2️⃣ JWT Interceptor
```typescript
// AUTOMÁTICO em cada request
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3️⃣ AuthStore (authStore.ts)
```diff
- Mock login
+ Real: POST /api/auth/login
```

### 4️⃣ RegisterPage (NOVO)
```typescript
import RegisterPage from './pages/RegisterPage'
// Criado do zero com validações
```

### 5️⃣ ISINTable (ISINTable.tsx)
```diff
- handleAdd: TODO
+ handleAdd: POST /isins (REAL)
+ handleDelete: DELETE /isins/{id} (NOVO)
+ handleToggle: PUT /isins/{id}/automation/toggle (REAL)
+ handleSync: GET /isins/sync-from-trading212 (REAL)
```

---

## ⚡ Error Handling

Todos os endpoints têm:

```typescript
try {
  // Chamar API
  const response = await apiClient.get('/endpoint')
  // Sucesso
  toast.success('Message')
  setState(response.data)
} catch (error: any) {
  // Erro
  const message = error?.response?.data?.detail || 'Erro genérico'
  toast.error(message)
  console.error('Error:', error)
}
```

---

## 📱 Response Formats

### Login/Register
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "user_id": "ab1036ff-937d-46e5-8f5b-bab07f1fb100",
  "email": "user@example.com",
  "message": "Login realizado com sucesso"
}
```

### ISINs List
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "isin": "IE00BK5BQT80",
    "ticker": "VWRX",
    "name": "Vanguard FTSE All-World",
    "currency": "EUR",
    "automation_enabled": false,
    "pnl": 100.50,
    "pnl_percent": 4.1
  }
]
```

### Toggle Automation Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "automation_enabled": true,
  "message": "Automação ativada"
}
```

---

## 🚀 Deployment Ready

### Frontend
```bash
# Production build
npm run build
# Output: frontend/dist/
# Render deploy automático
```

### Backend
```bash
# Production ready
python main.py
# Render deploy automático via push main
```

### URLs Produção
```
Frontend: https://trading212-1.onrender.com
Backend:  https://trading212-4ojx.onrender.com
```

---

## 🔐 JWT Security

### Como funciona:
1. User faz login com email + password
2. Backend retorna JWT token (24h válido)
3. Frontend guarda em localStorage
4. CADA request: `Authorization: Bearer {token}`
5. Backend verifica JWT
6. Se expirado/inválido → 401
7. Frontend: logout + redirect /login

### Teste JWT:
```bash
# Ver token no browser console
localStorage.getItem('token')

# Copiar token aqui para verificar:
https://jwt.io
# Deve mostrar: { user_id, email, exp, iat }
```

---

## 📊 Componente Diagram

```
LoginPage (real)
    ↓ POST /auth/login
    ↓ Guarda JWT
    ↓
AuthStore (login realizado)
    ↓ Redirect /dashboard
    ↓
DashboardPage
    ├─→ ISINTable
    │   ├─ GET /isins (lista)
    │   ├─ POST /isins (criar)
    │   ├─ DELETE /isins/{id} (deletar)
    │   ├─ PUT /automation/toggle
    │   └─ GET /sync-from-trading212
    │
    ├─→ ConfigForm
    │   ├─ PUT /config
    │   └─ POST /config/test
    │
    └─→ ISINDetailPage
        ├─ GET /isins/{id}
        └─ GET /isins/{id}/trades

RegisterPage (novo)
    ↓ POST /auth/register
    ↓ Auto-login
    ↓ Redirect /dashboard
```

---

## 🐛 Troubleshooting

### Problema: CORS error
```
Solution: Backend deve aceitar frontend URL
Verificar: CORS configurado em FastAPI
```

### Problema: 401 Unauthorized
```
Causa: Token expirado ou inválido
Solution: Fazer novo login (logout + redirect automático)
```

### Problema: ISINTable vazio
```
Causa: Nenhum ISIN sincronizado
Solution: 
1. Clicar "Sincronizar Carteira"
2. Ou: POST novo ISIN manualmente
```

### Problema: Config test retorna erro
```
Causa: Credenciais T212 inválidas/ausentes
Solution:
1. Verificar API Key + Secret em T212 settings
2. Testar em T212 dashboard primeiro
```

---

## ✨ Features Implementadas

| Feature | Status | Componente |
|---------|--------|-----------|
| Login Real | ✅ | LoginPage |
| Register Real | ✅ | RegisterPage (NOVO) |
| JWT Token | ✅ | AuthStore |
| ISIN List | ✅ | ISINTable |
| Add ISIN | ✅ | ISINTable |
| Delete ISIN | ✅ | ISINTable |
| Toggle Automação | ✅ | ISINTable |
| Sync Carteira | ✅ | ISINTable |
| ISIN Details | ✅ | ISINDetailPage |
| Trades History | ✅ | ISINDetailPage |
| Config Credenciais | ✅ | ConfigForm |
| Test Config | ✅ | ConfigForm |

---

## 🎯 Next Steps

1. **Testar Localhost**
   - [ ] Start backend + frontend
   - [ ] Register nova conta
   - [ ] Login
   - [ ] ISIN CRUD
   - [ ] Config test

2. **Deploy Render**
   - [ ] Push para main
   - [ ] Auto-deploy (5-15min)
   - [ ] Testar URLs produção

3. **Melhorias Futuras**
   - [ ] Refresh token (24h expiry)
   - [ ] Real T212 API data
   - [ ] Websocket real-time
   - [ ] Gráficos com Recharts
   - [ ] Testes E2E

---

## 📞 Support

Se tiver dúvidas:
- Ver logs no browser DevTools (Console + Network)
- Ver logs backend (terminal onde python main.py corre)
- Verificar `.env` vars
- Testar endpoints com Postman/Insomnia

**Status:** 🟢 Ready to Go! 🚀
