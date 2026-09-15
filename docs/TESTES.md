# 🧪 GUIA DE TESTES - Trading 212 Bot MVP

## Phase 1: Backend API

### Passo 1: Instalar Dependências

```bash
cd "C:\claude\401. Trading 212 Hub\backend"
pip install -r requirements.txt
```

**Esperado:** Sem erros, todas as bibliotecas instaladas.

---

### Passo 2: Testar Conexão T212 API

Antes de rodar o servidor FastAPI, testa direto:

```bash
cd "C:\claude\401. Trading 212 Hub\backend"
python test_t212_api.py
```

**Esperado:**
```
============================================================
🧪 TESTE DA API TRADING 212
============================================================

1️⃣  Inicializando cliente T212...
   ✅ Cliente criado com sucesso

2️⃣  Consultando saldo da conta...
   ✅ Saldo: €5889.99
      - Cash disponível: €994.88
      - Investido: €4895.11

3️⃣  Consultando posições abertas...
   ✅ Posições: 2
      - Vanguard FTSE All-World (Acc) (VWCEd_EQ)
        Quantidade: 14.8443008200 | Preço: €166.86
      - SPDR S&P 500 (Acc) (SPYLa_EQ)
        Quantidade: 147.7452249900 | Preço: €16.37

4️⃣  Consultando ordens pendentes...
   ✅ Ordens pendentes: 0

============================================================
✅ TODOS OS TESTES PASSARAM!
============================================================
```

---

### Passo 3: Rodar o Servidor FastAPI

```bash
cd "C:\claude\401. Trading 212 Hub\backend"
python main.py
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Testar endpoints:**

```bash
# Em outra terminal, testa estes URLs:

# 1. Health check
curl http://localhost:8000/health

# Esperado:
# {"status":"healthy"}

# 2. Root endpoint
curl http://localhost:8000/

# Esperado:
# {"name":"Trading 212 Bot API","version":"0.1.0","status":"running","environment":"development"}

# 3. Documentação interativa (abrir no browser)
http://localhost:8000/docs
```

---

## Phase 2: Frontend React

### Passo 1: Instalar Dependências

```bash
cd "C:\claude\401. Trading 212 Hub\frontend"
npm install
```

**Esperado:** Sem erros, node_modules criada.

---

### Passo 2: Rodar Dev Server

```bash
cd "C:\claude\401. Trading 212 Hub\frontend"
npm run dev
```

**Esperado:**
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Abrir no browser:** http://localhost:5173

---

## Phase 3: Integração Completa

### Teste Manual (sem backend funcional ainda)

1. Abre http://localhost:5173 no browser
2. Vês a página de login
3. Preenche qualquer email/password (stub)
4. Clica "Entrar"
5. Deves ver o Dashboard com:
   - Sidebar à esquerda
   - Tabela de ISINs
   - Botão "Novo ISIN"

### Teste de Funcionalidades UI

```
Dashboard:
  ✅ Sidebar com 3 menus (ISINs, Configuração, Histórico)
  ✅ Tabela de ISINs com dados (mock por enquanto)
  ✅ Botão "Novo ISIN" funcional (abre form)
  ✅ Editar/Deletar ISINs (UI only)
  ✅ Botão "Sair" funcional (limpa localStorage)
```

---

## Phase 4: Testar Integração Backend ↔ Frontend

Quando o backend estiver completo com endpoints:

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Testes manuais
curl -X GET http://localhost:8000/api/isins \
  -H "Authorization: Bearer TOKEN"
```

---

## 📋 Checklist de Testes

### Backend
- [ ] Dependências instaladas
- [ ] `.env` configurado corretamente
- [ ] API T212 responde (test_t212_api.py)
- [ ] FastAPI inicia sem erros
- [ ] Health check funciona (`/health`)
- [ ] Documentação Swagger abre (`/docs`)

### Frontend
- [ ] Dependências instaladas
- [ ] Dev server inicia
- [ ] Login page renderiza
- [ ] Dashboard renderiza após "login"
- [ ] Sidebar navega entre views
- [ ] Tabela ISINs exibe dados (mock)
- [ ] Botões funcionam (UI, sem API ainda)

### Integração
- [ ] Endpoints `/isins` implementados
- [ ] CRUD ISINs funciona
- [ ] Dados T212 carregam
- [ ] Automação toggle ON/OFF
- [ ] WebSocket real-time (depois)

---

## 🆘 Troubleshooting

### Python/pip issues
```bash
python --version  # Deve ser 3.11+
pip --version
pip install --upgrade pip
```

### Port já em uso
```bash
# Backend usa 8000, Frontend 5173
# Se estiver em uso:
# Windows: netstat -ano | findstr :8000
# Kill: taskkill /PID <PID> /F
```

### Erro de importação
```bash
# Certifica-te que estás na pasta correta
cd "C:\claude\401. Trading 212 Hub\backend"
python -c "from api.trading212 import Trading212Client; print('OK')"
```

---

## 🎯 Próximas Ações

1. ✅ Instalar dependências (em progresso)
2. ✅ Testar API T212
3. ✅ Rodar backend FastAPI
4. ✅ Rodar frontend React
5. 🔄 Implementar autenticação Supabase
6. 🔄 Conectar CRUD ISINs
7. 🔄 Implementar estratégia Grid Trading

---

**Começa agora!** 🚀
