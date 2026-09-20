# Análise: "Invest Account - Open Positions" (Activity Statement pág 3)

## 🔍 O Que Encontrei

Na página 3 do PDF `Activity-Statement-2026-09-01-2026-09-01.pdf`, existe uma secção:

```
INVEST ACCOUNT - OPEN POSITIONS
═══════════════════════════════════════════════════════════════════════════
ISIN          Instrument Name                    Quantity  Market Value €
───────────────────────────────────────────────────────────────────────────
IE00B4L5Y983  Vanguard FTSE All-World UCITS ETF  14.840    €2,467.42
US0846707026  Berkshire Hathaway Inc Class B     0.100     €31.89
───────────────────────────────────────────────────────────────────────────
```

---

## 📊 Campos Presentes vs Faltantes

### ✅ Campos Presentes (Extraíveis)
| Campo | Presente? | Exemplo |
|-------|-----------|---------|
| **ISIN** | ✅ SIM | IE00B4L5Y983 |
| **Instrument Name** | ✅ SIM | Vanguard FTSE All-World UCITS ETF |
| **Quantity** | ✅ SIM | 14.840 |
| **Market Value** | ✅ SIM | €2,467.42 |

### ❌ Campos FALTANTES (Não aparecem neste relatório)
| Campo | Presente? | Por quê? |
|-------|-----------|----------|
| **Cost Basis Per Unit** | ❌ NÃO | Relatório mensal não contém histórico de compra |
| **Total Cost Value** | ❌ NÃO | Relatório mensal não contém histórico de compra |
| **Unrealised P&L** | ❌ NÃO | Não pode ser calculado sem cost basis |
| **Unrealised P&L %** | ❌ NÃO | Não pode ser calculado sem cost basis |

---

## 🆚 Comparação: Mensal vs Anual

### Relatório MENSAL (Activity Statement)
```
INVEST ACCOUNT - OPEN POSITIONS
───────────────────────────────────────────────────────────────
ISIN | Instrument Name | Quantity | Market Value
───────────────────────────────────────────────────────────────
```
**Dados:** Apenas posições atuais (snapshot do fim do período)

---

### Relatório ANUAL (Annual Statement)
```
INVEST ACCOUNT - OPEN POSITIONS
─────────────────────────────────────────────────────────────────────────
ISIN | Instrument | Quantity | Cost Basis | Total Cost | Market Value | P&L
─────────────────────────────────────────────────────────────────────────
```
**Dados:** Posições + histórico acumulado (cost basis, P&L)

---

## 🛠️ Implicações para o Schema

### Problema Original:
A tabela `REPORT_POSITIONS` foi desenhada assumindo que **TODOS os relatórios** têm:
- `cost_basis_per_unit`
- `total_cost_value`
- `unrealised_pnl`
- `unrealised_pnl_percentage`

### Realidade:
- ✅ Relatórios **ANUAIS** têm esses campos
- ❌ Relatórios **MENSAIS** NÃO têm esses campos

---

## ✅ SOLUÇÃO IMPLEMENTADA

### Tabela `REPORT_POSITIONS` Revisada

Mudanças:
1. **Tornei campos NULLABLE**: `cost_basis_per_unit`, `total_cost_value`, `unrealised_pnl`, `unrealised_pnl_percentage`
2. **Adicionei flag**: `has_cost_basis_info BOOLEAN` - para saber se o registo tem info de cost basis
3. **Campo sempre obrigatório**: `quantity` + `total_market_value`

```sql
CREATE TABLE report_positions (
    id UUID PRIMARY KEY,
    report_file_id UUID NOT NULL REFERENCES report_files(id),
    position_date DATE NOT NULL,
    
    -- Campos SEMPRE presentes (em mensal e anual)
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(15, 8) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    
    -- Campos OPCIONAIS (apenas anual)
    cost_basis_per_unit DECIMAL(15, 4),  -- NULL em relatórios mensais
    total_cost_value DECIMAL(15, 2),     -- NULL em relatórios mensais
    unrealised_pnl DECIMAL(15, 2),       -- NULL em relatórios mensais
    unrealised_pnl_percentage DECIMAL(8, 2),  -- NULL em relatórios mensais
    
    -- Flag para saber se tem info de cost basis
    has_cost_basis_info BOOLEAN DEFAULT FALSE,
    
    currency VARCHAR(3) DEFAULT 'EUR',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 📝 Exemplos de Inserção

### Exemplo 1: Relatório MENSAL (Activity Statement)
```sql
INSERT INTO report_positions (
    report_file_id,
    position_date,
    isin,
    instrument_name,
    quantity,
    total_market_value,
    cost_basis_per_unit,     -- NULL
    total_cost_value,         -- NULL
    unrealised_pnl,           -- NULL
    unrealised_pnl_percentage, -- NULL
    has_cost_basis_info,
    currency,
    created_at,
    updated_at
) VALUES (
    'uuid-do-ficheiro-mensal',
    '2026-09-01',
    'IE00B4L5Y983',
    'Vanguard FTSE All-World UCITS ETF',
    14.840,
    2467.42,
    NULL,    -- Não temos cost basis no relatório mensal
    NULL,
    NULL,
    NULL,
    FALSE,   -- Flag: não tem cost basis info
    'EUR',
    NOW(),
    NOW()
);
```

### Exemplo 2: Relatório ANUAL (Annual Statement)
```sql
INSERT INTO report_positions (
    report_file_id,
    position_date,
    isin,
    instrument_name,
    quantity,
    total_market_value,
    cost_basis_per_unit,
    total_cost_value,
    unrealised_pnl,
    unrealised_pnl_percentage,
    has_cost_basis_info,
    currency,
    created_at,
    updated_at
) VALUES (
    'uuid-do-ficheiro-anual',
    '2025-12-31',
    'IE00B4L5Y983',
    'Vanguard FTSE All-World UCITS ETF',
    14.840,
    2467.42,
    155.50,   -- Cost basis per unit (temos esta info no anual)
    2304.62,  -- 14.840 × 155.50
    162.80,   -- 2467.42 - 2304.62
    7.07,     -- (162.80 / 2304.62) × 100
    TRUE,     -- Flag: tem cost basis info
    'EUR',
    NOW(),
    NOW()
);
```

---

## 🎯 Resposta à Pergunta Original

### "Em que tabela estás a guardar a informação do ficheiro mensal?"

**Resposta:** `REPORT_POSITIONS`

**Mas com uma correção importante:**
- Os campos `cost_basis_per_unit`, `total_cost_value`, `unrealised_pnl`, `unrealised_pnl_percentage` estarão **NULL**
- O campo `has_cost_basis_info` estará **FALSE**
- Apenas `ISIN`, `quantity`, `market_value` terão valores

**Porque?** Porque o relatório mensal (Activity Statement) não fornece informação de cost basis - essa informação está disponível apenas no relatório anual.

---

## 📋 Checklist de Atualização

- [x] ✅ Identificado o problema
- [x] ✅ Criada correção SQL (`CORRECTION_REPORT_POSITIONS.sql`)
- [x] ✅ Documentado impacto
- [ ] ⏳ Atualizar `T212_REPORTS_DB_SCHEMA.sql` com versão corrigida
- [ ] ⏳ Atualizar `DATABASE_DESIGN_DOCUMENTATION.md` com notas
- [ ] ⏳ Implementar parser com lógica de NULLABLE fields

---

## 🔗 Relação com Outras Tabelas

A tabela `REPORT_POSITIONS` não é a única forma de obter P&L:

| Se procuras... | Usa esta tabela | Notas |
|---|---|---|
| **Portfolio ATUAL (snapshot)** | `REPORT_POSITIONS` | Posições no fim do período |
| **P&L REALIZADO (já vendido)** | `REPORT_REALIZED_PNL` | Para vendas, sempre tem P&L |
| **P&L NÃO REALIZADO (aberto)** | `REPORT_POSITIONS` | Apenas em relatórios anuais (NOT NULL) |
| **P&L TOTAL (realizado + não realizado)** | `REPORT_TAX_SUMMARY` | Apenas em relatórios anuais |

---

## 💡 Lições Aprendidas

1. ✅ Relatórios mensais são "snapshots leves" (posições + transações)
2. ✅ Relatórios anuais são "resumos completos" (tudo + cost basis + P&L)
3. ✅ Schema deve ser flexível para acomodar ambos
4. ✅ NULLs são OK quando o dado não está disponível
5. ✅ Flags booleanas ajudam a saber que tipo de dados temos

