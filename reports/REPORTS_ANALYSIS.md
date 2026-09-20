# Trading 212 Reports - Análise Estrutural

## Visão Geral

Trading 212 oferece três tipos de relatórios financeiros com diferentes granularidades:
1. **Relatório Anual** - Resumo completo do ano fiscal
2. **Relatório Mensal** - Atividade de um mês específico
3. **Relatório por Intervalo** - Atividade entre duas datas (inclui períodos de 1 dia)

---

## 1. Relatório Anual (`annual-statement-2025.pdf`)

### Estrutura Geral
Documento oficial de resumo financeiro anual, apresentado num formato formal compatível com auditoria fiscal.

### Seções Principais

#### **Cabeçalho & Identificação**
- Nome do titular da conta
- Número de conta (IBAN ou referência interna T212)
- Período fiscal: **2025** (01 Jan - 31 Dec)
- Data de emissão
- Tipo de conta (Invest, ISA, etc)

#### **Resumo de Saldo**
- **Saldo inicial** do ano
- **Saldo final** do ano
- **Valor de depósitos** realizados durante o ano
- **Valor de levantamentos** realizados durante o ano
- **Ganho/perda líquido** (P&L do período)

#### **Posições Abertas (EOY - End of Year)**
- Lista de todas as posições **abertas em 31 de Dezembro de 2025**
- Para cada posição:
  - ISIN / Ticker do instrumento
  - Nome da empresa/fundo
  - Quantidade detida
  - Preço de compra médio (cost basis)
  - Preço de mercado final do dia
  - Valor em custo (cost)
  - Valor de mercado (current value)
  - Ganho/perda não realizado (unrealised P&L)

#### **Transações ao Longo do Ano**
- Histórico **completo** de todas as transações de 2025:
  - **Compras** (BUY)
  - **Vendas** (SELL)
  - **Dividendos** recebidos
  - **Depósitos/Levantamentos** de cash
  - **Desdobramentos de ações** (stock splits)
  - **Fracionamentos** (fractional shares)
  - **Juros** de cash em conta

- Para cada transação:
  - Data
  - Tipo (BUY/SELL/DIVIDEND/DEPOSIT/WITHDRAWAL/etc)
  - ISIN do ativo
  - Nome do ativo
  - Quantidade
  - Preço unitário
  - Comissão/custos
  - Valor líquido (net amount)
  - Saldo de cash após a transação

#### **Resumo Fiscal (Tax Summary)**
- **Ganhos realizados** (realized gains) - quando venderam com lucro
- **Perdas realizadas** (realized losses) - quando venderam com prejuízo
- **Saldo de perdas** (carry-forward losses) - perdas que podem abater ganhos futuros
- **Documentação de imposto** - referências para preenchimento de IRS/fiscal

#### **Notas Finais**
- Declaração de autenticidade
- Aviso legal (não é aconselhamento financeiro)
- Contacto de suporte

### Casos de Uso
✅ Declaração de impostos anual (IRS, fisco)
✅ Auditoria pessoal de performance anual
✅ Reconciliação com contabilista
✅ Análise de padrões de investimento ao longo do ano
✅ Arquivo de segurança/conformidade

---

## 2. Relatório Mensal (`Activity-Statement-2026-06-01-2026-06-30.pdf`)

### Estrutura Geral
Documento detalhado de atividade mensal, focado em movimentos de cash e transações.

### Seções Principais

#### **Cabeçalho & Período**
- Nome do titular
- Número de conta
- **Período:** Junho de 2026 (01 Jun - 30 Jun)
- Data de emissão (normalmente emitido no 1º ou 2º dia do mês seguinte)

#### **Resumo Mensal de Saldo**
- **Saldo inicial** (1º dia do mês)
- **Saldo final** (último dia do mês)
- **Variação de saldo** (diferença)
- **Depósitos** no mês
- **Levantamentos** no mês
- **Ganhos/perdas líquidos** de transações (net P&L)

#### **Atividade de Cash**
- Todas as movimentações de cash:
  - Transferências bancárias (depósitos)
  - Levantamentos para conta bancária
  - Juros creditados
  - Comissões/taxas debitadas
  - Conversão de moeda (se aplicável)

#### **Transações de Valores Mobiliários (Securities)**
- Todas as operações de compra/venda:
  - Data da transação
  - Tipo (BUY/SELL)
  - ISIN + Nome do ativo
  - Quantidade
  - Preço por unidade
  - Comissão
  - Valor total
  - Referência da ordem (order ID T212)

#### **Dividendos e Rendimentos**
- Dividendos recebidos no mês
- Juros de cash
- Outros rendimentos (direitos de subscrição, etc)

#### **Posições Atuais (Snapshot)**
- Estado das posições **no final do mês**:
  - ISIN
  - Quantidade
  - Valor de custo acumulado
  - Valor de mercado (preço de fecho do mês)
  - Ganho/perda não realizado

#### **Notas & Custos**
- Resumo de comissões do mês
- Taxas de gestão (se aplicável)
- Alertas ou avisos (conta suspensa, etc)

### Casos de Uso
✅ Reconciliação mensal com banco
✅ Análise de atividade mensal (quantas transações, volume)
✅ Rastreamento de depósitos/levantamentos
✅ Comparação mês-a-mês
✅ Identificação de padrões de trading

---

## 3. Relatório por Intervalo de Datas (`Activity-Statement-2026-09-01-2026-09-01.pdf`)

### Estrutura Geral
Documento de atividade para um período **customizável** (pode ser 1 dia, 1 semana, qualquer intervalo).

**Nota:** Neste exemplo, é um relatório de **um único dia** (01 Set - 01 Set), mostrando um snapshot das operações desse dia.

### Seções Principais

#### **Cabeçalho & Período**
- Nome do titular
- Número de conta
- **Período:** Data início - Data fim (customizável)
  - Neste caso: 01 Set 2026 a 01 Set 2026 (1 dia apenas)
- Data de emissão

#### **Resumo do Período**
- **Saldo no início** do período
- **Saldo no fim** do período
- **Variação total**
- **Depósitos** no intervalo
- **Levantamentos** no intervalo
- **P&L de transações** no intervalo

#### **Transações Detalhadas**
Mesmo formato que o relatório mensal, mas apenas para o intervalo selecionado:
- Todas as compras/vendas
- Toda a movimentação de cash
- Dividendos recebidos
- Comissões

#### **Posições no Final do Intervalo**
- Snapshot das posições no último dia do intervalo
- ISIN, quantidade, valores de custo e mercado

#### **Sumário de Atividade**
- Número de transações
- Volume total transacionado
- Custos totais
- Ganho/perda do período

### Casos de Uso
✅ Análise de atividade em período específico
✅ Auditoria de um dia específico de trading
✅ Relatório customizado para fins externos
✅ Análise de performance entre datas (ex: antes/depois de evento de mercado)
✅ Validação de operações específicas

---

## 4. Diferenças Chave Entre os Três Tipos

| Aspecto | Anual | Mensal | Por Intervalo |
|--------|-------|--------|---------------|
| **Período** | 12 meses (Jan-Dec) | 1 mês | Customizável |
| **Foco Principal** | Resumo fiscal anual + posições EOY | Atividade de mês + reconciliação | Atividade específica |
| **Uso Típico** | IRS, auditoria, arquivo | Controlo mensal, reconciliação | Análise customizada |
| **Detalhe de Transações** | Todas as 12 meses | Apenas mês especificado | Apenas intervalo |
| **Posições** | Apenas posições no final do ano | Snapshot fim de mês | Snapshot fim de intervalo |
| **Informação Fiscal** | Sim (gains/losses/carry-forward) | Não | Não |

---

## 5. Campos de Dados Comuns em Todos os Relatórios

### Por Transação:
```
- Data
- Tipo de Operação (BUY, SELL, DIVIDEND, DEPOSIT, WITHDRAWAL, INTEREST, etc)
- ISIN ou Ticker
- Nome do Instrumento
- Quantidade
- Preço Unitário (onde aplicável)
- Comissão / Taxa
- Valor Líquido / Bruto
- Referência / Order ID
```

### Por Posição:
```
- ISIN / Ticker
- Nome
- Quantidade
- Preço Médio de Compra (Cost Basis)
- Preço Atual / Preço de Fecho
- Valor de Custo (Cost Value = Quantity × Cost Basis)
- Valor de Mercado (Market Value = Quantity × Current Price)
- Ganho/Perda Não Realizado (Unrealised P&L = Market Value - Cost Value)
```

---

## 6. Insights Estruturais Importantes

### 📌 Estrutura Hierárquica
1. **Nível 1:** Resumo de Saldo (1 linha)
2. **Nível 2:** Movimentação de Cash (N linhas)
3. **Nível 3:** Transações de Valores Mobiliários (N linhas)
4. **Nível 4:** Posições Abertas (N linhas)

### 📊 Dados Temporais
- **Anual:** Evento único (31 Dez)
- **Mensal:** 30/31 dias de atividade
- **Por Intervalo:** N dias (flexível)

### 💰 Fluxos de Dinheiro
Todos os relatórios rastreiam:
- **Entradas:** Depósitos, Dividendos, Juros
- **Saídas:** Levantamentos, Comissões, Compras de ativos
- **Net:** Saldo final = Saldo inicial + Entradas - Saídas

---

## 7. Potencial de Integração com T212 Bot

### Oportunidades de Automação:
1. **Sincronização de Posições**
   - Parser dos relatórios para atualizar BD de ISINs automaticamente
   - Validar posições do API contra relatórios

2. **Rastreamento de P&L**
   - Importar ganhos/perdas realizadas
   - Calcular P&L acumulado por período

3. **Auditoria de Trades**
   - Comparar trades automatizados vs. relatórios
   - Detectar discrepâncias

4. **Dashboard Histórico**
   - Mostrar histórico de transações do relatório
   - Gráficos de saldo ao longo do tempo

5. **Conformidade Fiscal**
   - Gerar sumário de gains/losses para IRS
   - Rastreamento de carry-forward losses

### Estrutura Proposta de Modelo DB:
```python
# Importar dados dos relatórios
class ReportTransaction(Base):
    report_date: date
    report_type: str  # 'annual', 'monthly', 'interval'
    transaction_type: str  # BUY, SELL, DIVIDEND, etc
    isin: str
    quantity: float
    price: float
    commission: float
    net_value: float
    
class ReportPosition(Base):
    report_date: date
    report_type: str
    isin: str
    quantity: float
    cost_basis: float
    market_price: float
    unrealised_pnl: float
    
class ReportSummary(Base):
    report_date: date
    report_type: str
    beginning_balance: float
    ending_balance: float
    deposits: float
    withdrawals: float
    net_pnl: float
```

---

## 📝 Conclusão

Os três tipos de relatórios complementam-se:
- **Anual** = conformidade fiscal + visão full-year
- **Mensal** = controlo operacional + reconciliação
- **Por Intervalo** = análise ad-hoc + auditoria específica

Para o T212 Bot, estes relatórios são uma **fonte de verdade secundária** que valida a atividade do API e fornece contexto histórico não disponível apenas através de chamadas ao endpoint `/history/orders`.
