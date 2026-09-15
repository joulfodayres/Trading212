# 📚 Documentação - Trading 212 Bot

## Estrutura de Pastas

```
docs/
├── api/                      # API Documentation (Autenticação, Endpoints)
│   ├── AUTH_JWT_IMPLEMENTATION.md
│   ├── JWT_TESTING_GUIDE.md
│   └── README_JWT_AUTHENTICATION.md
│
├── frontend/                 # Frontend Integration & Setup
│   ├── FRONTEND_JWT_INTEGRATION.md
│   ├── FRONTEND_BACKEND_INTEGRATION.md
│   └── INTEGRACAO_FRONTEND.md
│
├── architecture/             # System Design & Architecture
│   ├── DEPLOYMENT.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── IMPLEMENTATION_COMPLETE.txt
│   └── IMPLEMENTATION_CHECKLIST.txt
│
├── deployment/               # Deployment & Production Setup
│   ├── DEPLOYMENT_COMPLETE.txt
│   ├── DEPLOYMENT_STEP_BY_STEP.md
│   ├── RENDER_DEPLOYMENT_INSTRUCTIONS.txt
│   └── RENDER_FRONTEND_SETUP.txt
│
└── guides/                   # Guides & References
    └── ROADMAP_FINAL.md
```

---

## 📖 Como Usar Esta Documentação

### **Para Entender a Arquitetura:**
1. Lê: `docs/architecture/IMPLEMENTATION_SUMMARY.md`
2. Depois: `../CLAUDE.md` (no root)

### **Para Implementar Auth:**
1. Lê: `docs/api/README_JWT_AUTHENTICATION.md` (quick start)
2. Depois: `docs/api/AUTH_JWT_IMPLEMENTATION.md` (technical details)

### **Para Integrar Frontend:**
1. Lê: `docs/frontend/FRONTEND_JWT_INTEGRATION.md`
2. Depois: `docs/frontend/FRONTEND_BACKEND_INTEGRATION.md` (complete guide)

### **Para Fazer Deploy:**
1. Lê: `docs/deployment/DEPLOYMENT_STEP_BY_STEP.md`
2. Depois: `docs/deployment/RENDER_DEPLOYMENT_INSTRUCTIONS.txt`

### **Para Testar:**
1. Lê: `docs/api/JWT_TESTING_GUIDE.md`

### **Para Futuro Roadmap:**
- Lê: `docs/guides/ROADMAP_FINAL.md`

---

## ✅ Ficheiros Principais no Root

| Ficheiro | Propósito |
|----------|-----------|
| **CLAUDE.md** | Instruções principais do projeto |
| **README.md** | Overview do repositório |
| **CHECKLIST_FINAL.md** | Checklist completo de funcionalidades |
| **COMECA_AQUI.md** | Quick start local development |
| **TESTES.md** | Guia de testes |

---

## 📦 Pastas do Projeto

```
Trading212/
├── backend/                  # FastAPI + Python
│   ├── routes/               # Endpoints (auth, isins, config)
│   ├── db/                   # Database client (Supabase)
│   ├── api/                  # T212 API integration
│   ├── auth/                 # Autenticação & Criptografia
│   ├── config/               # Settings
│   ├── models/               # Data models
│   └── main.py               # FastAPI app entry point
│
├── frontend/                 # React + TypeScript
│   ├── src/
│   │   ├── pages/            # Pages (Login, Register, Dashboard)
│   │   ├── components/       # Reusable components
│   │   ├── stores/           # Zustand state
│   │   ├── api/              # HTTP client
│   │   └── index.css         # Global styles
│   └── tailwind.config.ts    # Tailwind config
│
├── db/                       # Database setup
│   ├── supabase_schema.sql   # Table definitions
│   └── create_test_user.sql  # Test user setup
│
├── docs/                     # Documentation (THIS FOLDER)
│   ├── api/                  # API docs
│   ├── frontend/             # Frontend docs
│   ├── architecture/         # Architecture docs
│   ├── deployment/           # Deployment docs
│   └── guides/               # Reference guides
│
└── .github/                  # GitHub workflows
    └── workflows/            # CI/CD
```

---

## 🚀 Quick Links

- **Frontend:** https://trading212-1.onrender.com
- **Backend API:** https://trading212-4ojx.onrender.com
- **Swagger UI:** https://trading212-4ojx.onrender.com/docs
- **GitHub:** https://github.com/joulfodayres/Trading212

---

## 📞 Getting Help

- **Architecture questions?** → Lê `docs/architecture/`
- **Auth issues?** → Lê `docs/api/`
- **Frontend problems?** → Lê `docs/frontend/`
- **Deployment stuck?** → Lê `docs/deployment/`
- **General questions?** → Lê `CLAUDE.md` no root

---

**Last Updated:** 2026-09-15  
**Status:** MVP Production Ready (90% complete)
