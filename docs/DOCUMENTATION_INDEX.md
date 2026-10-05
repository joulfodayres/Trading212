# 📑 Índice Completo da Documentação - Trading 212 Bot

**Data Atualização:** 2026-09-27
**Status:** 🟢 DEMO + PROD Live — ver `docs/KNOWLEDGE_BASE.md` para o estado atual do projeto

> ⚠️ **Nota de manutenção:** este índice ficou desatualizado durante várias sessões (os caminhos
> abaixo tinham sido movidos de `docs/T212_*.md` para `docs/t212-api/*.md` sem que este ficheiro
> fosse corrigido). Os caminhos foram corrigidos em 2026-09-27. Se voltar a ficar stale, considere
> este ficheiro dispensável — a fonte de verdade é sempre `docs/KNOWLEDGE_BASE.md` + `BACKLOG.md`.

---

## 📚 Documentação por Tópico

### 🔴 CRÍTICO - Ler Primeiro

1. **`docs/KNOWLEDGE_BASE.md`** ⭐⭐⭐
   - Documento principal, usado como Knowledge Base do Claude.ai Project
   - Arquitetura atual (DEMO vs PROD), schema da BD, endpoints, automação
   - Sempre a fonte de verdade mais atualizada

2. **`docs/t212-api/API_ANALYSIS.md`** ⭐⭐⭐
   - Análise completa de todos os endpoints da T212
   - Rate limits, autenticação, limitações
   - Estrutura de resposta de cada endpoint

3. **`docs/t212-api/ORDERING_WARNING.md`** ⚠️
   - Assunção sobre ordenação DESC em `/history/orders`
   - Riscos de assumir ordem de resultados

---

### 🔵 Endpoints Específicos da T212

4. **`docs/t212-api/ORDER_HISTORY_BY_ID.md`**
   - Aceder a histórico de ordem específica por ID
   - GET /orders/{id} vs GET /history/orders

5. **`docs/t212-api/HISTORY_ORDERS_PARAMS.md`**
   - Parâmetros de GET /history/orders (`limit`, `cursor`, `ticker`)

6. **`docs/t212-api/HISTORY_ORDERS_NO_DATE_FILTER.md`**
   - Limitação: sem filtro de data em `/history/orders`
   - Comparação com `/history/transactions`

7. **`docs/t212-api/INCREMENTAL_SYNC.md`**
   - Como funciona o incremental sync, algoritmo passo-a-passo

8. **`docs/t212-api/api.yaml`**
   - Especificação OpenAPI da T212 API (referência bruta)

---

### 📋 Documentação da Aplicação

9. **`README.md`** — Overview do projeto, quick start, URLs DEMO/PROD
10. **`CLAUDE.md`** (raiz) — Instruções para Claude Code: stack, estrutura, convenções
11. **`BACKLOG.md`** (raiz) — Backlog completo, itens concluídos e em aberto, estimativas

---

### 🚀 Deployment

12. **`docs/DEVELOPMENT.md`** — Setup local & desenvolvimento
13. Ver `docs/KNOWLEDGE_BASE.md` seção "🚀 Deployment" para os 4 serviços Render (DEMO + PROD) e o
    fluxo de branches `main`/`prod`

---

### 🗄️ Referência adicional (podem estar desatualizados face à KB)

- `docs/API_REFERENCE.md`, `docs/CODE_EXAMPLES.md`, `docs/DATABASE_SCHEMA.md`,
  `docs/AUTOMATION_FLOW.md`, `docs/AUTOMATION_ENDPOINTS.md`, `docs/TROUBLESHOOTING.md`,
  `docs/QUICK_REFERENCE.md`, `docs/QUICK_START.md`, `docs/REPORTS_FEATURE.md`
- Ficheiros históricos de sessões passadas (não atualizar, apenas consultar):
  `docs/CHANGELOG.md`, `docs/CHANGELOG_2026_09_17.md`, `docs/PHASE_4_SUMMARY.md`,
  `docs/PHASE_5_STATUS.md`, `docs/PHASE5_ITEM7_SUMMARY.md`, `docs/QUICK_REFERENCE_PHASE4.md`,
  `docs/CLEANUP_PLAN.md`, `docs/SIMPLIFY_TO_SINGLEUSER.md`, `docs/STRATEGY_TABLES_*.md`

---

## 🔑 Conceitos-Chave

- T212 API é **REST-based, polling-only** (sem webhooks)
- Rate limits são **por account**, não por API key
- Autenticação: **HTTP Basic Auth** (T212) + **JWT/Supabase Auth** (app, ~35 endpoints protegidos)
- `/history/orders` tem paginação cursor-based, máximo 50 items/página
- `/history/transactions` tem parâmetro `time` (filtro de data); `/history/orders` não tem
- Dois ambientes de aplicação, DEMO e PROD, cada um com a sua própria API key T212
  (`demo.trading212.com` vs `live.trading212.com`) — ver `docs/KNOWLEDGE_BASE.md`

---

**Última Atualização:** 2026-10-05
**Status:** Caminhos corrigidos; índice alinhado com `docs/t212-api/`; ver `docs/KNOWLEDGE_BASE.md` para o Item #22 (Manual Orders / "Gerir Ordens")
