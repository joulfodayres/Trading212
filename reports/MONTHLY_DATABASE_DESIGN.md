# Trading 212 Monthly Reports - Database Design

## 🎯 Objetivo

Armazenar **TODA** a informação dos relatórios mensais da Trading 212 de forma estruturada, auditável e facilmente consultável.

**Escopo:** Apenas relatórios mensais (Activity Statement de 1 a 31 dias de período)

---

## 📊 Estrutura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    REPORT_FILES                             │
│  (Controlo de ficheiros importados com UUID único)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ BALANCE_SUMMARY  │  │  TRANSACTIONS   │  │ OPEN_POSITIONS
│                  │  │                 │  │
│ • Opening bal    │  │ • BUY/SELL      │  │ • ISIN
│ • Closing bal    │  │ • DIVIDEND      │  │ • Quantity
│ • Deposits       │  │ • DEPOSIT/WITHDRAW│ • Market Value
│ • Withdrawals    │  │ • INTEREST      │  │
└──────────────────┘  │ • FEES          │  └──────────────┘
                      │                 │
                      └─────────────────┘

        ┌──────────────────────┬──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────────┐      ┌──────────────┐      ┌──────────────┐
   │  DIVIDENDS  │      │ CASH_MOVEMENTS│     │ FEES_CHARGES │
   │             │      │               │      │              │
   │ • ex_date   │      │ • DEPOSIT     │      │ • TRADING_COMM
   │ • payment   │      │ • WITHDRAWAL  │      │ • PLATFORM_FEE
   │ • amount    │      │ • INTEREST    │      │ • CUSTODY_FEE
   │ • per_share │      │ • FEE         │      │              │
   └─────────────┘      └──────────────┘      └──────────────┘

        ┌──────────────────────────────────────┐
        │                                      │
        ▼                                      ▼
   ┌─────────────────┐              ┌──────────────────┐
   │  METADATA       │              │  IMPORT_LOG      │
   │                 │              │                  │
   │ • Page count    │              │ • Status         │
   │ • Validation    │              │ • Records count  │
   │ • Discrepancies │              │ • Timestamps     │
   │ • Notes         │              │ • Error message  │
   └─────────────────┘              └──────────────────┘
```

---

## 📋 Tabelas Detalhadas

### 1. **REPORT_FILES** (Raiz)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único do ficheiro
filename                | VARCHAR     | Nome do ficheiro (UNIQUE)
file_hash               | VARCHAR     | SHA256 para detetar duplicatas
file_size_bytes         | INT         | Tamanho do ficheiro
period_start            | DATE        | Data inicial do período (ex: 2026-06-01)
period_end              | DATE        | Data final do período (ex: 2026-06-30)
account_holder_name     | VARCHAR     | Nome do titular da conta
account_number          | VARCHAR     | Número da conta
account_type            | VARCHAR     | Tipo: Invest, ISA, etc
total_transactions      | INT         | Contador de transações importadas
total_positions         | INT         | Contador de posições importadas
import_status           | VARCHAR     | pending|processing|completed|error
error_message           | TEXT        | Mensagem de erro (se houver)
created_at              | TIMESTAMP   | Quando foi registado
updated_at              | TIMESTAMP   | Última atualização
imported_by             | VARCHAR     | Utilizador/sistema que importou
import_completed_at     | TIMESTAMP   | Quando completou a importação
```

**Índices:**
- `idx_report_files_period` → (period_start, period_end)
- `idx_report_files_status` → (import_status)
- `idx_report_files_created` → (created_at)

---

### 2. **MONTHLY_BALANCE_SUMMARY** (1:1 com REPORT_FILES)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro (UNIQUE)
opening_balance         | DECIMAL     | Saldo no 1º dia do mês
closing_balance         | DECIMAL     | Saldo no último dia do mês
total_deposits          | DECIMAL     | Soma de todos os depósitos
total_withdrawals       | DECIMAL     | Soma de todos os levantamentos
total_interest_earned   | DECIMAL     | Juros creditados no cash
total_trading_fees      | DECIMAL     | Comissões de negociação
total_charges           | DECIMAL     | Outras taxas/charges
total_positions_value   | DECIMAL     | Valor total do portfolio
total_cash_in_account   | DECIMAL     | Cash disponível (não em posições)
currency                | VARCHAR     | EUR, GBP, etc
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

---

### 3. **MONTHLY_TRANSACTIONS** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
transaction_date        | DATE        | Data da transação
transaction_seq         | INT         | Seq se múltiplas no mesmo dia
transaction_type        | VARCHAR     | BUY|SELL|DIVIDEND|DEPOSIT|WITHDRAWAL|...
order_id                | VARCHAR     | ID do T212
settlement_date         | DATE        | Data de liquidação
isin                    | VARCHAR     | ISIN (NULL para cash)
ticker                  | VARCHAR     | Ticker
instrument_name         | VARCHAR     | Nome do instrumento
quantity                | DECIMAL     | Quantidade (fracionária)
unit_price              | DECIMAL     | Preço unitário
gross_amount            | DECIMAL     | Valor bruto (qty × price)
fees_charged            | DECIMAL     | Comissões/taxas
net_amount              | DECIMAL     | Valor líquido (gross - fees)
currency                | VARCHAR     | EUR, GBP, etc
notes                   | TEXT        | Notas adicionais
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

**Índices:**
- `idx_transactions_report` → (report_file_id)
- `idx_transactions_date` → (transaction_date)
- `idx_transactions_type` → (transaction_type)
- `idx_transactions_isin` → (isin)
- `idx_transactions_order_id` → (order_id)

---

### 4. **MONTHLY_OPEN_POSITIONS** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
position_date           | DATE        | Data do snapshot (= period_end)
isin                    | VARCHAR     | ISIN (NOT NULL, UNIQUE per report+isin)
ticker                  | VARCHAR     | Ticker
instrument_name         | VARCHAR     | Nome do instrumento
quantity                | DECIMAL     | Quantidade detida
market_price_per_unit   | DECIMAL     | Preço de mercado por unidade
total_market_value      | DECIMAL     | quantity × market_price_per_unit
currency                | VARCHAR     | EUR, GBP, etc
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

**Índices:**
- `idx_open_positions_report` → (report_file_id)
- `idx_open_positions_date` → (position_date)
- `idx_open_positions_isin` → (isin)
- `UNIQUE idx_open_positions_unique` → (report_file_id, isin)

---

### 5. **MONTHLY_DIVIDENDS** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
ex_date                 | DATE        | Data ex-dividend
payment_date            | DATE        | Data que foi creditado
isin                    | VARCHAR     | ISIN da ação
ticker                  | VARCHAR     | Ticker
instrument_name         | VARCHAR     | Nome do instrumento
shares_held             | DECIMAL     | Quantidade que gerou dividendo
dividend_per_share      | DECIMAL     | Dividendo por ação
total_dividend_amount   | DECIMAL     | Total bruto
withholding_tax         | DECIMAL     | Imposto retido (se houver)
net_dividend            | DECIMAL     | total - withholding_tax
currency                | VARCHAR     | EUR, GBP, etc
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

---

### 6. **MONTHLY_CASH_MOVEMENTS** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
movement_date           | DATE        | Data do movimento
movement_type           | VARCHAR     | DEPOSIT|WITHDRAWAL|INTEREST|FEE
amount                  | DECIMAL     | + entrada, - saída
description             | VARCHAR     | Descrição
reference               | VARCHAR     | Ref bancária ou T212 ID
currency                | VARCHAR     | EUR, GBP, etc
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

---

### 7. **MONTHLY_FEES_CHARGES** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
charge_date             | DATE        | Data da taxa
fee_type                | VARCHAR     | TRADING_COMMISSION|PLATFORM_FEE|...
isin                    | VARCHAR     | ISIN (NULL se taxa geral)
ticker                  | VARCHAR     | Ticker (NULL se taxa geral)
instrument_name         | VARCHAR     | Nome (NULL se taxa geral)
amount                  | DECIMAL     | Valor da taxa (sempre positivo)
description             | VARCHAR     | Descrição
currency                | VARCHAR     | EUR, GBP, etc
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

---

### 8. **MONTHLY_METADATA** (1:1)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência (UNIQUE)
pdf_page_count          | INT         | Número de páginas do PDF
pdf_generated_date      | TIMESTAMP   | Quando foi gerado
pdf_parsing_notes       | TEXT        | Notas de parsing
is_validated            | BOOLEAN     | Passou na validação?
validation_errors       | TEXT        | Erros encontrados
has_discrepancies       | BOOLEAN     | Há discrepâncias?
discrepancy_notes       | TEXT        | Detalhes das discrepâncias
general_notes           | TEXT        | Notas gerais
created_at              | TIMESTAMP   | Criado em
updated_at              | TIMESTAMP   | Atualizado em
```

---

### 9. **MONTHLY_IMPORT_LOG** (1:N)
```
Coluna                  | Tipo        | Descrição
─────────────────────────────────────────────────────────
id                      | UUID PK     | Identificador único
report_file_id          | UUID FK     | Referência ao ficheiro
import_start_time       | TIMESTAMP   | Quando começou
import_end_time         | TIMESTAMP   | Quando terminou
status                  | VARCHAR     | started|completed|failed|partial
transactions_imported   | INT         | Nº de transações inseridas
transactions_skipped    | INT         | Nº de transações ignoradas
positions_imported      | INT         | Nº de posições inseridas
dividends_imported      | INT         | Nº de dividendos inseridos
cash_movements_imported | INT         | Nº de movimentos cash inseridos
fees_imported           | INT         | Nº de taxas inseridas
error_message           | TEXT        | Mensagem de erro (se houver)
error_stack_trace       | TEXT        | Stack trace (se houver)
duration_seconds        | DECIMAL     | Tempo total em segundos
import_notes            | TEXT        | Notas adicionais
```

---

## 🔑 Relacionamentos e Constraints

### Foreign Keys
```
report_files (PK: id)
    ├─ monthly_balance_summary (FK: report_file_id → id, 1:1, CASCADE)
    ├─ monthly_transactions (FK: report_file_id → id, 1:N, CASCADE)
    ├─ monthly_open_positions (FK: report_file_id → id, 1:N, CASCADE)
    ├─ monthly_dividends (FK: report_file_id → id, 1:N, CASCADE)
    ├─ monthly_cash_movements (FK: report_file_id → id, 1:N, CASCADE)
    ├─ monthly_fees_charges (FK: report_file_id → id, 1:N, CASCADE)
    ├─ monthly_metadata (FK: report_file_id → id, 1:1, CASCADE)
    └─ monthly_import_log (FK: report_file_id → id, 1:N, CASCADE)
```

**ON DELETE CASCADE:** Se um ficheiro for eliminado, todos os seus dados também.

---

## 📊 Views Criadas

### 1. `v_monthly_transactions_summary`
Resume transações por tipo, com contagem, inflows/outflows e taxas.

```sql
SELECT report_file_id, filename, transaction_type, count, 
       total_inflow, total_outflow, total_fees
FROM v_monthly_transactions_summary;
```

### 2. `v_monthly_portfolio_final`
Portfolio final (posições no fim do período).

```sql
SELECT * FROM v_monthly_portfolio_final
ORDER BY total_market_value DESC;
```

### 3. `v_monthly_dividends_summary`
Resumo de dividendos (bruto, impostos, líquido).

```sql
SELECT * FROM v_monthly_dividends_summary;
```

### 4. `v_monthly_realized_pnl`
Vendas realizadas no período (base para calcular P&L).

```sql
SELECT * FROM v_monthly_realized_pnl;
```

---

## 💾 Estimativa de Crescimento

Para 1 mês de atividade típica:

| Tabela | Registos Típicos | Tamanho |
|--------|------------------|---------|
| report_files | 1 | <1 KB |
| monthly_balance_summary | 1 | 1 KB |
| monthly_transactions | 20-100 | 50 KB |
| monthly_open_positions | 5-50 | 10 KB |
| monthly_dividends | 0-10 | 5 KB |
| monthly_cash_movements | 5-20 | 10 KB |
| monthly_fees_charges | 1-10 | 5 KB |
| monthly_metadata | 1 | <1 KB |
| monthly_import_log | 1 | 1 KB |
| **TOTAL** | **~35-250** | **~85 KB** |

**Crescimento Anual:** ~1 MB (12 relatórios mensais)

---

## 🔐 Auditoria Completa

Cada tabela tem:
- ✅ `created_at` - Timestamp de criação
- ✅ `updated_at` - Timestamp de última alteração
- ✅ `report_file_id` - Rastreabilidade 100%

Além disso:
- ✅ `report_files.file_hash` - Detetar duplicatas
- ✅ `monthly_import_log` - Histórico de importações
- ✅ `monthly_metadata` - Validação e discrepâncias

---

## ✅ Exemplos de Queries Úteis

### Obter Todas as Transações de um Mês
```sql
SELECT *
FROM monthly_transactions
WHERE report_file_id = 'uuid-do-ficheiro'
ORDER BY transaction_date DESC;
```

### Portfolio Final (Posições Abertas)
```sql
SELECT isin, instrument_name, quantity, total_market_value
FROM monthly_open_positions
WHERE report_file_id = 'uuid-do-ficheiro'
ORDER BY total_market_value DESC;
```

### Total de Transações por Tipo
```sql
SELECT transaction_type, COUNT(*) as total
FROM monthly_transactions
WHERE report_file_id = 'uuid-do-ficheiro'
GROUP BY transaction_type;
```

### Dividendos Recebidos no Mês
```sql
SELECT isin, instrument_name, total_dividend_amount, withholding_tax, net_dividend
FROM monthly_dividends
WHERE report_file_id = 'uuid-do-ficheiro'
ORDER BY payment_date DESC;
```

### Resumo de Movimentos de Cash
```sql
SELECT movement_type, SUM(amount) as total_amount, COUNT(*) as count
FROM monthly_cash_movements
WHERE report_file_id = 'uuid-do-ficheiro'
GROUP BY movement_type;
```

### Saldo do Período
```sql
SELECT opening_balance, closing_balance, 
       (closing_balance - opening_balance) as net_change,
       total_deposits, total_withdrawals
FROM monthly_balance_summary
WHERE report_file_id = 'uuid-do-ficheiro';
```

---

## 📝 Checklist de Implementação

- [x] ✅ Schema SQL criado
- [x] ✅ Documentação completa
- [ ] ⏳ Deploy em Supabase
- [ ] ⏳ Implementar parser PDF → SQL INSERT
- [ ] ⏳ Validação de dados importados
- [ ] ⏳ Testes com 3 ficheiros mensais
- [ ] ⏳ API endpoints para consultas
- [ ] ⏳ Dashboard de visualização

