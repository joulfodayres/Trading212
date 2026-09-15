# 🔗 PLANO DE INTEGRAÇÃO FRONTEND-BACKEND

## Fase 3: Conectar Frontend ao Backend

Após backend ter autenticação + CRUD prontos, frontend precisa fazer:

---

## 1️⃣ **LoginPage.tsx** - Fazer login real

### Antes (Mock):
```typescript
const handleLogin = () => {
  // Aceita qualquer email/password
  setLoggedIn(true)
}
```

### Depois (Real):
```typescript
const handleLogin = async () => {
  try {
    const response = await apiClient.post('/api/auth/login', {
      email,
      password
    })
    
    // Guarda JWT no localStorage
    localStorage.setItem('token', response.data.access_token)
    
    // Interceptor em apiClient adiciona token aos headers
    // Redireciona a Dashboard
    navigate('/dashboard')
  } catch (error) {
    toast.error('Email ou password incorretos')
  }
}
```

**O que muda:**
- POST /api/auth/login com email + password
- Recebe JWT access_token
- Guarda em localStorage
- apiClient interceptor injeta token automaticamente

---

## 2️⃣ **ISINTable.tsx** - Listar ISINs reais

### Antes (Mock):
```typescript
const [isins] = useState([
  { id: '1', isin: 'IE00BK5BQT80', name: 'Vanguard', ... },
  { id: '2', isin: 'IE00B4L5Y983', name: 'SPDR', ... }
])
```

### Depois (Real):
```typescript
useEffect(() => {
  fetchIsins()
}, [])

const fetchIsins = async () => {
  try {
    const response = await apiClient.get('/api/isins')
    setIsins(response.data)  // Dados reais da BD!
  } catch (error) {
    if (error.response?.status === 401) {
      navigate('/login')  // Token expirado
    }
    toast.error('Erro ao carregar ISINs')
  }
}

const handleDelete = async (isinId) => {
  try {
    await apiClient.delete(`/api/isins/${isinId}`)
    setIsins(isins.filter(i => i.id !== isinId))
    toast.success('ISIN removido')
  } catch (error) {
    toast.error('Erro ao remover ISIN')
  }
}

const handleSync = async () => {
  try {
    const response = await apiClient.get('/api/isins/sync-from-trading212')
    setIsins(response.data.isins)
    toast.success(`Sincronizado ${response.data.synced_count} ISINs`)
  } catch (error) {
    toast.error('Erro ao sincronizar')
  }
}
```

**O que muda:**
- GET /api/isins na montagem da component
- DELETE /api/isins/{id} ao remover
- GET /api/isins/sync-from-trading212 ao sincronizar
- Dados vêm da BD, não hardcoded

---

## 3️⃣ **ConfigForm.tsx** - Guardar credenciais T212

### Antes (Mock):
```typescript
const handleSave = () => {
  toast.success('Config guardada')  // Não faz nada
}
```

### Depois (Real):
```typescript
const handleSave = async () => {
  try {
    await apiClient.put('/api/config', {
      t212_api_key: apiKey,
      t212_api_secret: apiSecret,
      t212_environment: environment
    })
    
    toast.success('Configuração guardada com sucesso!')
    setApiKey('')
    setApiSecret('')
  } catch (error) {
    toast.error('Erro ao guardar configuração')
  }
}

const handleTest = async () => {
  try {
    const response = await apiClient.post('/api/config/test', {
      t212_api_key: apiKey,
      t212_api_secret: apiSecret
    })
    
    setTestResult({ 
      success: true, 
      data: response.data 
    })
    toast.success('Conexão bem-sucedida!')
  } catch (error) {
    setTestResult({ 
      success: false, 
      error: error.response?.data?.detail 
    })
    toast.error('Erro ao testar conexão')
  }
}
```

**O que muda:**
- PUT /api/config com credenciais (encriptadas no backend)
- POST /api/config/test para validar
- Backend encripta credenciais com Fernet
- Só o user consegue ver suas próprias credenciais

---

## 4️⃣ **ISINDetailPage.tsx** - Detalhes reais

### Antes (Mock):
```typescript
setIsin({
  id: 'hardcoded',
  name: 'Vanguard',
  price: 166.86,
  ...
})
```

### Depois (Real):
```typescript
useEffect(() => {
  fetchIsinDetail()
}, [id])

const fetchIsinDetail = async () => {
  try {
    const response = await apiClient.get(`/api/isins/${id}`)
    setIsin(response.data)
    
    // Também fetch trades
    const tradesResponse = await apiClient.get(`/api/isins/${id}/trades`)
    setTrades(tradesResponse.data)
  } catch (error) {
    if (error.response?.status === 404) {
      toast.error('ISIN não encontrado')
    } else if (error.response?.status === 401) {
      navigate('/login')
    }
  }
}
```

**O que muda:**
- GET /api/isins/{id} retorna detalhe com P&L calculado
- GET /api/isins/{id}/trades retorna histórico
- Dados reais de BD + T212 API

---

## 5️⃣ **apiClient.ts** - Injetar JWT automaticamente

### Já Implementado:
```typescript
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

**Benefício:** Todas as chamadas usam token automaticamente!

---

## 📋 Checklist Implementação Frontend

```
Após backend estar pronto:

□ LoginPage.tsx - POST /api/auth/login
□ ISINTable.tsx - GET /api/isins + DELETE
□ ConfigForm.tsx - PUT/POST /api/config
□ ISINDetailPage.tsx - GET /api/isins/{id}
□ Testar fluxo completo (login → dashboard → config → sync)
□ Verificar console (F12) para erros
□ Teste em Render (https://trading212-1.onrender.com)
```

---

## 🚀 Timeline

1. ✅ Backend autentica + CRUD (implementação agora)
2. ⏳ Frontend conecta ao backend (após backend pronto)
3. ⏳ Testes end-to-end
4. ⏳ Deploy final
