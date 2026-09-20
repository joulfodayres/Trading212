# Resumo: Estrutura da Base de Dados T212 Reports

## 🎯 Objetivo
Armazenar **TODA** a informação dos relatórios da Trading 212 (Anual, Mensal, Por Intervalo) de forma estruturada, rastreável e auditável.

---

## 📦 Componentes Principais

### **1. Tabela Raiz: REPORT_FILES**
```
┌──────────────────────────────────────────────────┐
│ REPORT_FILES (Ficheiros Importados)              │
├──────────────────────────────────────────────────┤
│ • id (UUID) - Identificador único do ficheiro   │
│ • filename (VARCHAR) - Nome do ficheiro          │
│ • file_hash (VARCHAR) - SHA256 para detetar dup │
│ • report_type - 'annual' | 'monthly' | 'interval'
│ • period_start, period_end - Datas do período   │
│ • account_holder_name - Nome do titular         │
│ • account_number, account_type - Info da conta  │
│ • total_transactions - Contador de transações   │
│ • created_at, updated_at - Timestamps           │
│ • import_status - pending|processing|processed  │
└──────────────────────────────────────────────────┘
```

---

## 🌳 Estrutura Hierárquica

```
                    REPORT_FILES
                   /      |      \
                  /       |       \
                 /        |        \
    ┌───────────┴─────┬──┴──┬──────┴──────────────┐
    │                 │     │                     │
    ▼                 ▼     ▼                     ▼
BALANCE_     TRANSACTIONS POSITIONS          DIVIDENDS
SUMMARY      (compra/      (portfolio       (rendimentos)
(saldos)     venda/dep/    snapshot)
             lev/comiss)

    │                 │     │                     │
    └────────┬────────┼─────┼──────┬──────────────┘
             │        │     │      │
             ▼        ▼     ▼      ▼
         CASH_      COSTS  REALIZED_    CORPORATE_
         MOVEMENTS  (taxas  PNL         ACTIONS
         (dep/lev)  comiss) (gains/     (splits)
                            losses)

         │
         └─ TAX_SUMMARY (apenas Anual)
         └─ METADATA
         └─ IMPORT_LOG
         └─ VALIDATION_CHECKS
```

---

## 📊 As 12 Tabelas Criadas

| # | Tabela | Tipo | Cardinalidade | Descrição |
|---|--------|------|---------------|-----------|
| 1 | **REPORT_FILES** | Raiz | - | Metadados do ficheiro importado |
| 2 | **REPORT_BALANCE_SUMMARY** | 1:1 | Um saldo por ficheiro | Resumo de saldo (início + fim + movimentos) |
| 3 | **REPORT_TRANSACTIONS** | 1:N | Múltiplas transações | Todas as compras, vendas, dividendos, etc |
| 4 | **REPORT_POSITIONS** | 1:N | Posições no fim de período | Portfolio snapshot (ISIN + quantidade + valores) |
| 5 | **REPORT_DIVIDENDS** | 1:N | Dividendos recebidos | Rendimentos de ações |
| 6 | **REPORT_CASH_MOVEMENTS** | 1:N | Movimentos de cash | Depósitos, levantamentos, juros |
| 7 | **REPORT_COSTS** | 1:N | Custos e comissões | Taxas, comissões de negociação, impostos |
| 8 | **REPORT_REALIZED_PNL** | 1:N | Ganhos/perdas realizadas | P&L de cada venda |
| 9 | **REPORT_CORPORATE_ACTIONS** | 1:N | Ações corporativas | Stock splits, mergers, etc |
| 10 | **REPORT_TAX_SUMMARY** | 1:1 | Info fiscal anual | Gains, losses, carryforward (apenas Anual) |
| 11 | **REPORT_METADATA** | 1:1 | Metadata técnica | Pages, encoding, avisos de extração |
| 12 | **REPORT_IMPORT_LOG** | 1:N | Log de importação | Histórico de quando foi importado |
| 13 | **REPORT_VALIDATION_CHECKS** | 1:N | Validações | Verificação de integridade dos dados |

---

## 🔑 Convenções Utilizadas

### ✅ Cada Tabela Tem:
- **`id` (UUID)** - Primary Key único e imutável
- **`report_file_id` (UUID, FK)** - Referência ao ficheiro de origem
- **`created_at` (TIMESTAMP)** - Quando foi criado
- **`updated_at` (TIMESTAMP)** - Quando foi atualizado pela última vez

### ✅ Rastreabilidade 100%
Cada registo sabe:
1. De qual ficheiro veio (`report_file_id`)
2. Quando foi criado/alterado (`created_at`, `updated_at`)
3. Qual é a sua identidade única (`id`)

### ✅ Integridade Referencial
- Todas as FKs com `ON DELETE CASCADE`
- Se um ficheiro for apagado, todos os seus dados também
- Impossível ter dados órfãos

---

## 📈 Relação Entre Tabelas

```
REPORT_FILES (1)
    ├─→ (1:1) REPORT_BALANCE_SUMMARY
    │         └─ beginning_balance: €1000
    │         └─ ending_balance: €1250
    │         └─ net_cash_flow: -€0
    │         └─ net_pnl: €250
    │
    ├─→ (1:N) REPORT_TRANSACTIONS
    │         ├─ 2025-01-05 BUY VANGUARD 10 @ €150 = €1500
    │         ├─ 2025-02-10 DIVIDEND VANGUARD €10
    │         └─ 2025-03-15 SELL VANGUARD 5 @ €160 = €800
    │
    ├─→ (1:N) REPORT_POSITIONS
    │         └─ 2025-12-31 VANGUARD (ISIN...) 5 units @ €170 = €850
    │
    ├─→ (1:N) REPORT_REALIZED_PNL
    │         └─ Venda de 5 VANGUARD: €50 ganho (5%)
    │
    ├─→ (1:N) REPORT_COSTS
    │         ├─ 2025-01-05 COMMISSION €2.50
    │         └─ 2025-03-15 COMMISSION €1.50
    │
    ├─→ (1:N) REPORT_CASH_MOVEMENTS
    │         ├─ DEPOSIT €5000
    │         └─ INTEREST €25
    │
    ├─→ (1:1) REPORT_TAX_SUMMARY (apenas se Anual)
    │         ├─ total_realized_gains: €50
    │         ├─ total_dividend_income: €10
    │         └─ total_withholding_tax: €0
    │
    ├─→ (1:1) REPORT_METADATA
    │         ├─ page_count: 42
    │         └─ extraction_warnings: "None"
    │
    ├─→ (1:N) REPORT_IMPORT_LOG
    │         └─ 2026-09-20 14:30:00 COMPLETED 127 registos em 2.5s
    │
    └─→ (1:N) REPORT_VALIDATION_CHECKS
              ├─ balance_reconciliation: PASSED
              └─ transaction_count: PASSED
```

---

## 💾 Tipos de Dados Utilizados

| Tipo | Uso | Exemplos |
|------|-----|----------|
| **UUID** | IDs e FKs | id, report_file_id |
| **VARCHAR** | Textos curtos | filename, isin, ticker, currency |
| **TEXT** | Textos longos | description, notes, error_message |
| **DATE** | Datas | transaction_date, period_start |
| **TIMESTAMP** | Data + hora | created_at, updated_at, import_timestamp |
| **DECIMAL(15,2)** | Valores monetários | amounts, prices, balances |
| **DECIMAL(15,8)** | Quantidades (fracionárias) | quantity, fractional shares |
| **DECIMAL(8,2)** | Percentagens | unrealised_pnl_percentage, gain_loss_percentage |
| **INT** | Contadores | page_count, transaction_count, records_imported |
| **BOOLEAN** | Flags | has_discrepancies, passed |

---

## 🎯 Casos de Uso Principais

### ✅ Caso 1: Importar um novo Relatório PDF
```
1. Upload PDF
2. Parse PDF → Extract data
3. INSERT INTO report_files (cria UUID: abc-123)
4. INSERT INTO report_balance_summary (reference: abc-123)
5. INSERT INTO report_transactions (500 registos, cada um: abc-123)
6. INSERT INTO report_positions (reference: abc-123)
7. ... resto das tabelas
8. INSERT INTO report_import_log (status: COMPLETED)
9. ✅ Relatório Importado!
```

### ✅ Caso 2: Obter Portfolio Atual (Posições)
```sql
SELECT isin, instrument_name, quantity, total_market_value, unrealised_pnl
FROM report_positions
WHERE report_file_id = (
    SELECT id FROM report_files
    ORDER BY period_end DESC
    LIMIT 1
);
```

### ✅ Caso 3: Calcular P&L Anual
```sql
SELECT
    tax_year,
    total_realized_gains,
    total_realized_losses,
    (total_realized_gains - total_realized_losses) as net_pnl
FROM report_tax_summary
WHERE tax_year = 2025;
```

### ✅ Caso 4: Rastrear Transações Específicas
```sql
SELECT transaction_date, transaction_type, isin, quantity, net_amount
FROM report_transactions
WHERE isin = 'IE00B4L5Y983'  -- VANGUARD FTSE ALL-WORLD
ORDER BY transaction_date;
```

---

## 🔍 Índices para Performance

Criados automaticamente em:
- `report_files.period_start, period_end` - Queries por período
- `report_files.report_type` - Filtrar Anual/Mensal
- `report_transactions.transaction_date` - Queries por data
- `report_transactions.isin` - Lookup de instrumento
- `report_positions.position_date, isin` - Portfolio por data
- Todas as FKs (`report_file_id`) - Queries rápidas

---

## 📋 Checklist de Implementação

- [x] ✅ Schema SQL criado (`T212_REPORTS_DB_SCHEMA.sql`)
- [x] ✅ Documentação criada (`DATABASE_DESIGN_DOCUMENTATION.md`)
- [ ] ⏳ Criar tabelas em Supabase
- [ ] ⏳ Implementar parser PDF → SQL
- [ ] ⏳ Testar com os 3 PDFs fornecidos
- [ ] ⏳ Criar API endpoints
- [ ] ⏳ Criar dashboard

---

## 📚 Ficheiros Criados

| Ficheiro | Descrição |
|----------|-----------|
| `T212_REPORTS_DB_SCHEMA.sql` | Schema completo com todas as 13 tabelas |
| `DATABASE_DESIGN_DOCUMENTATION.md` | Documentação detalhada (ERD, queries, etc) |
| `REPORTS_ANALYSIS.md` | Análise inicial dos 3 tipos de relatórios |

---

## 🚀 Próximos Passos

1. **Deploy Schema** → Criar tabelas em Supabase
2. **Parser PDF** → Implementar extração de dados dos PDFs
3. **Validação** → Adicionar checks de integridade
4. **API** → Criar endpoints para consultar dados
5. **Dashboard** → Visualizar dados importados

