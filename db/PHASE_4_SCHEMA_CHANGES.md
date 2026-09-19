# 📊 Phase 4 - Schema Changes Summary

**Data:** 2026-09-19  
**Objetivo:** Preparar BD para Grid Trading Automation  
**Status:** 📝 SQL pronto para aplicar

---

## ✅ Alterações Planeadas

### 1️⃣ Tabela `isins` - Adicionar 16 colunas

Campos que vêm **da API T212** (atualizados via polling):

| Coluna | Tipo | Propósito | Origem |
|--------|------|----------|--------|
| `api_created_at` | TIMESTAMP | Quando a posição foi aberta (API T212) | GET /positions |
| `initial_trade` | BOOLEAN | Flag de primeira operação | GET /positions |
| `trades_balance` | INTEGER | Saldo de trades (pode ser negativo) | GET /positions |
| `average_price_paid` | DOUBLE | Preço médio pago | GET /positions |
| `current_price` | DOUBLE | Preço atual do instrumento | GET /positions |
| `quantity` | DOUBLE | Total de shares | GET /positions |
| `quantity_available_for_trading` | DOUBLE | Shares disponíveis | GET /positions |
| `quantity_in_pies` | DOUBLE | Shares em Pies | GET /positions |
| `wi_currency` | VARCHAR | Moeda do wallet impact | GET /positions |
| `wi_current_value` | DOUBLE | Valor de mercado atual | GET /positions |
| `wi_fx_impact` | DOUBLE | Impacto de câmbio | GET /positions |
| `wi_total_cost` | DOUBLE | Custo total investido | GET /positions |
| `wi_unrealized_profit_loss` | DOUBLE | P&L não realizado | GET /positions |

**Nota:** 
- `created_at` já existe (timestamp local de criação do registo)
- `api_created_at` é novo (timestamp da API T212)
- Colunas existentes `ticker`, `name`, `currency` mantêm-se

---

### 2️⃣ Tabela `strategies` - Adicionar 1 coluna

| Coluna | Tipo | Propósito |
|--------|------|----------|
| `initial_investment` | DOUBLE | Valor em EUR que user investiu na estratégia |

---

### 3️⃣ Tabela `orders` - **NOVA**

Rastreia todas as ordens colocadas via T212 API.

**Campos da Order (API T212):**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | PK local |
| `isin_id` | UUID | FK → isins (identifica o instrumento) |
| `t212_order_id` | BIGINT | ID único da ordem na T212 |
| `ticker` | VARCHAR | Ex: AAPL_US_EQ |
| `instrument_isin` | VARCHAR | ISIN do instrumento |
| `instrument_name` | VARCHAR | Nome do instrumento |
| `instrument_currency` | VARCHAR | Moeda do instrumento |
| `side` | VARCHAR | BUY ou SELL |
| `quantity` | DOUBLE | Quantidade solicitada |
| `filled_quantity` | DOUBLE | Quantidade preenchida |
| `type` | VARCHAR | MARKET, LIMIT, STOP, STOP_LIMIT |
| `status` | VARCHAR | NEW, CONFIRMED, FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED, UNCONFIRMED |
| `created_at` | TIMESTAMP | Quando a ordem foi criada na T212 |
| `limit_price` | DOUBLE | Preço limite (opcional) |
| `stop_price` | DOUBLE | Preço stop (opcional) |
| `time_in_force` | VARCHAR | DAY ou GOOD_TILL_CANCEL |
| `initiated_from` | VARCHAR | API, WEB, ANDROID, IOS, SYSTEM, AUTOINVEST |

**Campos de Automação (Local):**

| Coluna | Tipo | Valores | Descrição |
|--------|------|--------|-----------|
| `automation_status` | CHAR(1) | W, E, C | **W**=Watch (pendente), **E**=Executed, **C**=Canceled |
| `related_order_id` | UUID | FK → orders | Ordem relacionada (BUY ↔ SELL pair) |
| `synced_at` | TIMESTAMP | | Quando foi sincronizada da API |
| `updated_at` | TIMESTAMP | | Última atualização local |

**Indices (Performance):**
- `t212_order_id` - Buscar por ID T212
- `isin_id` - Encontrar ordens de um instrumento
- `status` - Filtrar por status
- `automation_status` - Encontrar ordens "Watch"
- `created_at` - Ordenar temporalmente

---

## 🔗 Relacionamentos

### Antes (Phase 3)
```
users
  ├─ isins
  ├─ strategies
  ├─ trades
  └─ logs
```

### Depois (Phase 4)
```
users
  ├─ isins
  │   └─ orders (NEW!)
  │       └─ related_order_id (BUY ↔ SELL)
  ├─ strategies
  ├─ trades (antigo, pode ser removido)
  └─ logs
```

**Mudança:** Tabela `orders` substitui parcialmente `trades` com dados da API T212.

---

## 📋 Checklist de Implementação

### Fase 1: Aplicar SQL ✅
- [ ] Executar `phase_4_schema_changes.sql` no Supabase
- [ ] Verificar que todas as colunas/tabelas foram criadas
- [ ] Testar query básica em Supabase Query Editor

### Fase 2: Atualizar Backend 🔄
- [ ] `backend/models/db.py` - Adicionar SQLAlchemy models
  - [ ] Adicionar colunas ao modelo `Isin`
  - [ ] Adicionar coluna ao modelo `Strategy`
  - [ ] Criar novo modelo `Order`

- [ ] `backend/models/schemas.py` - Atualizar Pydantic schemas
  - [ ] Expandir `IsinSchema` com novos campos
  - [ ] Expandir `StrategySchema`
  - [ ] Criar `OrderSchema` + `OrderCreateSchema`

- [ ] `backend/routes/` - Adicionar endpoints
  - [ ] `GET /orders` - Listar todas as ordens
  - [ ] `GET /orders/{order_id}` - Detalhe de uma ordem
  - [ ] `POST /orders` - Criar ordem (interno)
  - [ ] `PUT /orders/{order_id}` - Atualizar status

### Fase 3: Implementar OrderHistoryManager 🚀
- [ ] `backend/engine/order_manager.py` - Sincronização incremental
  - [ ] Fetch de `/equity/orders` (pendentes)
  - [ ] Fetch de `/equity/history/orders` (executadas)
  - [ ] Reconciliation (detectar mudanças)
  - [ ] Atualizar BD com novos status

### Fase 4: Implementar Grid Trading 🎯
- [ ] `backend/engine/strategy.py` - Lógica de trading
- [ ] `backend/engine/scheduler.py` - APScheduler setup
- [ ] Testes com conta DEMO

---

## 🛡️ Validações & Constraints

### SQL-level
- ✅ `side` ∈ {BUY, SELL}
- ✅ `type` ∈ {MARKET, LIMIT, STOP, STOP_LIMIT}
- ✅ `automation_status` ∈ {W, E, C}
- ✅ `status` ∈ {NEW, CONFIRMED, FILLED, ...}
- ✅ `time_in_force` ∈ {DAY, GOOD_TILL_CANCEL}
- ✅ `id` ≠ `related_order_id` (diferente)

### App-level (Python/Backend)
- `related_order_id` side oposto (BUY ↔ SELL)
- `filled_quantity` ≤ `quantity`
- Datas lógicas (`created_at` ≤ `synced_at`)

---

## 📌 Notas Importantes

1. **Single-user mode:** RLS policies mantêm-se para compatibilidade futura
2. **related_order_id:** Sempre 1 BUY + 1 SELL (validado em app-level)
3. **Campos opcionais:** `limit_price`, `stop_price`, `wi_currency` podem ser NULL
4. **Indices:** Criados para evitar full-table scans
5. **Comentários SQL:** Adicionados para documentação do esquema

---

## 🚀 Próximos Passos

1. **Aplicar SQL no Supabase:**
   ```
   Supabase Dashboard → SQL Editor → Copiar & Executar phase_4_schema_changes.sql
   ```

2. **Depois de executar:**
   - Verificar que tabelas existem
   - Testar RLS policies (opcional em single-user)
   - Fazer backup

3. **Continuar em:** `backend/models/db.py`

---

**Status:** 📝 SQL Pronto  
**Criado:** 2026-09-19  
**Próximo:** Aplicar no Supabase e atualizar Python models
