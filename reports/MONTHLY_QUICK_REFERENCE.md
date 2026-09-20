# Quick Reference - Trading 212 Monthly Reports Database

## 📋 Resumo Executivo

Uma estrutura de base de dados **limpa e focada** para armazenar relatórios mensais da Trading 212.

- ✅ **9 tabelas** (não 13)
- ✅ **Focadas exclusivamente** em dados mensais
- ✅ **Rastreabilidade 100%** via UUID do ficheiro
- ✅ **Auditoria completa** com created_at/updated_at
- ✅ **Views úteis** para queries rápidas
- ✅ **Crescimento controlado** (~1 MB/ano)

---

## 🏗️ As 9 Tabelas

| # | Tabela | Tipo | Cardinalidade | Dados |
|---|--------|------|---------------|-------|
| 1 | **REPORT_FILES** | Raiz | - | Metadados do ficheiro + status importação |
| 2 | **MONTHLY_BALANCE_SUMMARY** | 1:1 | Um por ficheiro | Saldo abertura/fecho, depósitos, levantamentos |
| 3 | **MONTHLY_TRANSACTIONS** | 1:N | Múltiplas | BUY, SELL, DIVIDEND, DEPOSIT, WITHDRAWAL, etc |
| 4 | **MONTHLY_OPEN_POSITIONS** | 1:N | Múltiplas | Portfolio snapshot (ISIN + Qty + Market Value) |
| 5 | **MONTHLY_DIVIDENDS** | 1:N | 0 ou mais | Dividendos recebidos + withholding tax |
| 6 | **MONTHLY_CASH_MOVEMENTS** | 1:N | Múltiplas | DEPOSIT, WITHDRAWAL, INTEREST, FEE |
| 7 | **MONTHLY_FEES_CHARGES** | 1:N | 0 ou mais | Comissões e taxas detalhadas |
| 8 | **MONTHLY_METADATA** | 1:1 | Um por ficheiro | Info técnica, validação, discrepâncias |
| 9 | **MONTHLY_IMPORT_LOG** | 1:N | Histórico | Status importação, contadores, erros |

---

## 🔑 Coluna Padrão em Cada Tabela

```sql
id                  UUID PRIMARY KEY     -- Identificador único
report_file_id      UUID NOT NULL FK     -- Sempre presente (rastreabilidade)
created_at          TIMESTAMP NOT NULL   -- Quando foi criado
updated_at          TIMESTAMP NOT NULL   -- Última alteração
```

---

## 💾 Ficheiros Criados

| Ficheiro | Conteúdo |
|----------|----------|
| **MONTHLY_REPORTS_DB_SCHEMA.sql** | SQL completo - copiar e executar em Supabase |
| **MONTHLY_DATABASE_DESIGN.md** | Documentação detalhada de cada tabela + exemplos queries |
| **MONTHLY_DATABASE_DIAGRAM.md** | Diagramas ER (Mermaid + ASCII) + cardinalidades |
| **MONTHLY_DATABASE_QUICK_REFERENCE.md** | Este ficheiro |

---

## 🎯 Como Usar

### 1️⃣ Deploy Schema
```bash
# Copiar T212_REPORTS_DB_SCHEMA.sql inteiro
# Colar em Supabase SQL Editor
# Executar (vai criar as 9 tabelas + índices + views)
```

### 2️⃣ Importar um Relatório Mensal
```
1. Parse PDF → Extract dados
2. INSERT INTO report_files (cria UUID)
3. INSERT INTO monthly_balance_summary
4. INSERT INTO monthly_transactions (N registos)
5. INSERT INTO monthly_open_positions (N registos)
6. INSERT INTO monthly_dividends (0-N registos)
7. INSERT INTO monthly_cash_movements (N registos)
8. INSERT INTO monthly_fees_charges (0-N registos)
9. INSERT INTO monthly_metadata
10. INSERT INTO monthly_import_log
11. UPDATE report_files SET import_status = 'completed'
```

### 3️⃣ Consultar Dados
```sql
-- Portfolio Atual
SELECT * FROM v_monthly_portfolio_final 
WHERE report_file_id = 'uuid'
ORDER BY total_market_value DESC;

-- Resumo Transações
SELECT * FROM v_monthly_transactions_summary
WHERE report_file_id = 'uuid';

-- Dividendos
SELECT * FROM v_monthly_dividends_summary
WHERE report_file_id = 'uuid';
```

---

## 📊 Estrutura Simplificada

```
REPORT_FILES (raiz com UUID)
    ↓
    ├─ BALANCE_SUMMARY (saldo mês)
    ├─ TRANSACTIONS (47 compras/vendas/dividendos)
    ├─ OPEN_POSITIONS (8 ativos no portfolio)
    ├─ DIVIDENDS (dividendos recebidos)
    ├─ CASH_MOVEMENTS (depósitos/levantamentos)
    ├─ FEES_CHARGES (comissões/taxas)
    ├─ METADATA (info técnica)
    └─ IMPORT_LOG (histórico importação)
```

---

## ✅ Exemplo Real: Junho 2026

```
Ficheiro: Activity-Statement-2026-06-01-2026-06-30.pdf

report_files
  id: abc-123-def
  filename: Activity-Statement-2026-06-01-2026-06-30.pdf
  period: 2026-06-01 a 2026-06-30
  status: completed
  total_transactions: 47
  total_positions: 8

monthly_balance_summary
  opening_balance: €5000.00
  closing_balance: €5250.75
  deposits: €1000.00
  withdrawals: €500.00
  interest: €12.50
  fees: €75.00

monthly_transactions (47 registos)
  BUY Vanguard 10 @ €150
  SELL Berkshire 2 @ €300
  DIVIDEND Vanguard €25
  DEPOSIT €500
  WITHDRAWAL €100
  ...

monthly_open_positions (8 registos)
  IE00B4L5Y983 Vanguard 14.840 @ €166.22 = €2,467.42
  US0846707026 Berkshire 0.100 @ €318.90 = €31.89
  ...

monthly_dividends (3 registos)
  Vanguard 10 shares × €2.50 = €25.00
  ...

monthly_cash_movements
  DEPOSIT €500
  INTEREST €12.50
  WITHDRAWAL €100

monthly_fees_charges
  TRADING_COMMISSION €2.50 (Vanguard compra)
  TRADING_COMMISSION €1.50 (Berkshire venda)
  ...
```

---

## 🔍 Queries Comuns

### Obter Saldo do Mês
```sql
SELECT opening_balance, closing_balance, 
       (closing_balance - opening_balance) as net_change
FROM monthly_balance_summary
WHERE report_file_id = 'abc-123-def';
```

### Contar Transações por Tipo
```sql
SELECT transaction_type, COUNT(*) as total
FROM monthly_transactions
WHERE report_file_id = 'abc-123-def'
GROUP BY transaction_type;
```

### Total de Dividendos
```sql
SELECT SUM(total_dividend_amount) as total_gross,
       SUM(withholding_tax) as total_tax,
       SUM(net_dividend) as total_net
FROM monthly_dividends
WHERE report_file_id = 'abc-123-def';
```

### Movimentos de Cash por Tipo
```sql
SELECT movement_type, SUM(amount) as total
FROM monthly_cash_movements
WHERE report_file_id = 'abc-123-def'
GROUP BY movement_type;
```

### Total de Taxas
```sql
SELECT SUM(amount) as total_fees
FROM monthly_fees_charges
WHERE report_file_id = 'abc-123-def';
```

---

## 🎨 Views Prontas

1. **v_monthly_transactions_summary** - Transações por tipo
2. **v_monthly_portfolio_final** - Portfolio no fim do período
3. **v_monthly_dividends_summary** - Resumo de dividendos
4. **v_monthly_realized_pnl** - Vendas (base P&L)

---

## ⚡ Próximos Passos

1. ✅ Schema criado
2. ✅ Documentação pronta
3. ⏳ Deploy em Supabase (SQL Editor)
4. ⏳ Implementar parser PDF
5. ⏳ Testar com 3 ficheiros mensais
6. ⏳ API endpoints
7. ⏳ Dashboard

---

## 📞 Referência Rápida

| Preciso de... | Usa esta tabela |
|---|---|
| Saldo do mês | `monthly_balance_summary` |
| Histórico de compras/vendas | `monthly_transactions` |
| Portfolio atual | `monthly_open_positions` |
| Dividendos recebidos | `monthly_dividends` |
| Depósitos/Levantamentos | `monthly_cash_movements` |
| Comissões | `monthly_fees_charges` |
| Info técnica do PDF | `monthly_metadata` |
| Histórico de importações | `monthly_import_log` |

---

**Estrutura pronta para implementação! 🚀**

