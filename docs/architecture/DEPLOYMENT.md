# 🚀 GUIA DE DEPLOYMENT - Trading 212 Bot MVP

## Pré-requisitos

- ✅ Conta Supabase
- ✅ Conta Render
- ✅ Repositório GitHub
- ✅ Código pronto

---

## FASE 1: Preparar Código para Production

### 1.1 Atualizar .env.example com valores reais

(Será preenchido depois com credenciais)

### 1.2 Criar `.gitignore` (se não existe)

```
.env
.env.local
__pycache__/
*.pyc
node_modules/
.vite/
dist/
build/
.DS_Store
*.log
```

### 1.3 Criar `render.yaml` (config de deployment)

Este ficheiro diz ao Render como compilar e rodar o projeto.

---

## FASE 2: Setup Supabase (BD + Auth)

### 2.1 Criar Tabelas na BD

SQL scripts para executar no Supabase SQL Editor.

### 2.2 Gerar Credenciais

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_JWT_SECRET`

---

## FASE 3: Deploy Backend (Render)

### 3.1 Conectar GitHub → Render

1. Vai a render.com → New Web Service
2. Conecta o repositório GitHub
3. Configura variáveis de ambiente
4. Deploy automático

### 3.2 Backend URL

`https://trading212-bot-api.onrender.com`

---

## FASE 4: Deploy Frontend (Render)

### 4.1 Build React

```bash
npm run build
```

Cria pasta `dist/` com ficheiros estáticos.

### 4.2 Deploy em Render (Static Site)

Ou usar o mesmo Render Web Service com nginx.

---

## PRÓXIMOS PASSOS

1. Push código para GitHub
2. Executar SQL scripts em Supabase
3. Configurar Render
4. Aceder via browser

---

**Começamos?** 🚀
