# 📑 Índice Completo da Documentação - Trading 212 Bot

**Data Atualização:** 2026-09-17  
**Status:** 🟢 Phase 4 - Análise Completa da T212 API

---

## 📚 Documentação por Tópico

### 🔴 CRÍTICO - Ler Primeiro

1. **`docs/T212_API_ANALYSIS.md`** ⭐⭐⭐
   - Análise completa de todos os endpoints
   - Rate limits, autenticação, limitações
   - Estrutura de resposta de cada endpoint
   - Resumo executivo para Grid Trading

2. **`docs/T212_ORDERING_ASSUMPTION_WARNING.md`** ⚠️
   - **IMPORTANTE:** Assunção não confirmada sobre ordenação DESC
   - Riscos de assumir ordem de resultados
   - Estratégias seguras vs. rápidas
   - **AÇÃO:** Validar na prática antes de usar em produção

---

### 🔵 Endpoints Específicos

3. **`docs/T212_ORDER_HISTORY_BY_ID.md`**
   - Aceder a histórico de ordem específica por ID
   - GET /orders/{id} vs GET /history/orders
   - Como detectar execução de ordem
   - Workflows recomendados

4. **`docs/T212_HISTORY_ORDERS_PARAMS.md`**
   - Parâmetros de GET /history/orders
   - `limit`, `cursor`, `ticker` - detalhado
   - Exemplos Python prontos para usar
   - Armadilhas comuns

5. **`docs/T212_HISTORY_ORDERS_NO_DATE_FILTER.md`**
   - **Limitação:** Sem filtro de data em /history/orders
   - Comparação: /history/orders vs /history/transactions
   - Estratégias alternativas (BD local recomendado)
   - Impacto no design da aplicação

---

### 🟢 Estratégias de Sincronização

6. **`docs/T212_INCREMENTAL_SYNC_HOW_IT_WORKS.md`**
   - Como funciona incremental sync
   - Algoritmo passo-a-passo
   - Implementação em Python
   - Casos edge e tratamento de erros
   - Integração com APScheduler

7. **`docs/T212_ORDERING_VERIFICATION_RESULTS.md`** (TBD)
   - Testes práticos na API Demo
   - Confirmação: DESC vs ASC vs outro
   - Recomendações finais
   - Data: A fazer quando houver tempo

---

### 📋 Documentação da Aplicação

8. **`README.md`**
   - Overview do projeto
   - Quick start
   - Architecture high-level

9. **`CLAUDE.md`** (este arquivo - instruções para Claude Code)
   - Stack técnico
   - Estrutura do projeto
   - Convenções
   - Dependencies

10. **`COMECA_AQUI.md`**
    - Guia de início rápido
    - Setup local (opcional)
    - Variáveis de ambiente

---

### 🚀 Deployment

11. **`DEPLOYMENT.md`**
    - Notas de deployment
    - Status atual em Render

12. **`RENDER_DEPLOYMENT_INSTRUCTIONS.txt`**
    - Setup Render passo-a-passo

---

## 🔑 Conceitos-Chave Aprendidos

### ✅ Confirmado na Documentação:

- ✅ T212 API é **REST-based, polling-only** (sem webhooks)
- ✅ Rate limits são **por account**, não por API key
- ✅ Autenticação: **HTTP Basic Auth**
- ✅ `/history/orders` retorna com **cursor-based pagination**
- ✅ Máximo **50 items por página**
- ✅ `/history/transactions` TEM parâmetro `time` (filtro de data)

### ❌ NÃO Confirmado:

- ❌ Ordenação de `/history/orders` é **DESC** (implícito no exemplo, não documentado!)
- ❌ Todos os endpoints em `/history/` têm **filtro de data**

### ⚠️ Validação Pendente:

- ❓ Confirmar ordenação DESC na prática
- ❓ Testar com múltiplas ordens

---

## 📊 Endpoints Principais

| Endpoint | Rate Limit | Uso | Documentado? |
|----------|-----------|-----|-------------|
| GET `/equity/account/summary` | 1 req/5s | Saldo | ✅ |
| GET `/equity/positions` | 1 req/1s | Posições | ✅ |
| GET `/equity/orders` | 1 req/5s | Ordens pendentes | ✅ |
| POST `/equity/orders/market` | 50 req/1m | Colocar ordem | ✅ |
| POST `/equity/orders/limit` | 1 req/2s | Limite order | ✅ |
| POST `/equity/orders/stop` | 1 req/2s | Stop order | ✅ |
| POST `/equity/orders/stop_limit` | 1 req/2s | Stop-limit | ✅ |
| DELETE `/equity/orders/{id}` | 50 req/1m | Cancelar | ✅ |
| GET `/equity/history/orders` | 6 req/1m | Histórico | ✅ |
| GET `/equity/history/transactions` | 6 req/1m | Transações | ✅ |
| GET `/equity/metadata/instruments` | 1 req/50s | Catálogo | ✅ |

---

## 🎯 Arquitetura Phase 4 (Grid Trading)

```
┌─ APScheduler (5s interval)
│  ├─ GET /positions (1 req/1s) ✅ RÁPIDO
│  ├─ GET /orders (1 req/5s) ✅ RÁPIDO
│  └─ Grid Trading Logic
│
├─ Incremental Sync (1x/dia)
│  ├─ GET /history/orders (6 req/1m) 🐢 LENTO
│  └─ Guardar em BD local
│
└─ BD Local (Supabase)
   └─ Query histórico (⚡ SUPER RÁPIDO)
```

---

## ⚙️ Configuração Necessária

### Backend `.env`:

```
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_JWT_SECRET=...
T212_API_KEY=...
T212_API_SECRET=...
T212_ENVIRONMENT=demo
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Supabase Tables:

- `order_history` - Histórico sincronizado de ordens
  - `t212_order_id` (PK)
  - `ticker`
  - `side` (BUY/SELL)
  - `quantity`
  - `price`
  - `filled_at`
  - `pnl`

- `sync_log` - Checkpoint para incremental sync
  - `last_order_id`
  - `last_order_date`
  - `sync_time`

---

## 🚀 Próximas Ações

### Curto Prazo:
1. [ ] Implementar `OrderHistoryManager` (versão Safe)
2. [ ] Criar tabela `order_history` em Supabase
3. [ ] Setup APScheduler para sync diário
4. [ ] Implementar Grid Trading logic

### Validação:
5. [ ] Testar ordenação de `/history/orders` na prática
6. [ ] Atualizar `T212_ORDERING_VERIFICATION_RESULTS.md`
7. [ ] Escolher estratégia final (Fast vs Safe)

### Produção:
8. [ ] Testes automatizados
9. [ ] Monitoring
10. [ ] Deploy em Live (com cuidado!)

---

## 📞 Documentação de Referência Rápida

**Para Grid Trading:**
- Buscar: `docs/T212_API_ANALYSIS.md` → seção "🎯 Fluxo Grid Trading"

**Para Sincronização:**
- Buscar: `docs/T212_INCREMENTAL_SYNC_HOW_IT_WORKS.md` → código Python

**Para Troubleshooting:**
- Buscar: `docs/T212_ORDERING_ASSUMPTION_WARNING.md` → armadilhas

**Para Implementação:**
- Buscar: `docs/T212_HISTORY_ORDERS_PARAMS.md` → exemplos Python

---

## 🔗 Ligações Internas

- API Analysis → Todos os endpoints
- Order History by ID → Como buscar ordem executada
- History Orders Params → Detalhe de parâmetros
- Incremental Sync → Implementação
- Ordering Warning → ⚠️ Ler antes de confiar em DESC

---

**Última Atualização:** 2026-09-17  
**Próxima Revisão:** Após testes práticos de ordenação  
**Status:** 🟢 Documentação Completa (validação pendente)
