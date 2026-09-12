# 🤖 Trading 212 Bot - MVP

Projeto de automação de trading algorítmico com integração **Trading 212 API**.

---

## 🚀 Setup Rápido

### **1. Backend (Python FastAPI)**

```bash
cd backend

# Criar .env a partir do template
cp .env.example .env

# Editar .env com tuas credenciais
# - SUPABASE_URL, SUPABASE_KEY
# - T212_API_KEY, T212_API_SECRET
# - JWT_SECRET_KEY
# - ENCRYPTION_KEY (gerar com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

Backend estará em: `http://localhost:8000`

### **2. Frontend (React + Vite)**

```bash
cd frontend

# Instalar dependências
npm install

# Executar dev server
npm run dev
```

Frontend estará em: `http://localhost:5173`

---

## 📋 Credenciais de Teste

**Trading 212 DEMO:**
- API Key ID: `40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU`
- API Secret: `iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0`
- Environment: `demo`

---

## 🏗️ Estrutura

```
401. Trading 212 Hub/
├── backend/           # FastAPI
├── frontend/          # React
├── docker/            # Docker compose
└── docs/              # Documentação
```

---

## 📝 Próximas Etapas

- [ ] Integração completa Supabase
- [ ] Implementar autenticação JWT
- [ ] CRUD de ISINs com API T212
- [ ] Estratégia Grid Trading
- [ ] Real-time updates (WebSocket)
- [ ] Deploy em Render

---

## 🔐 Segurança

- API Keys encriptadas com Fernet
- JWT tokens via Supabase Auth
- CORS restringido em produção
- Rate limiting respectado

---

**Status:** MVP em desenvolvimento 🚀
