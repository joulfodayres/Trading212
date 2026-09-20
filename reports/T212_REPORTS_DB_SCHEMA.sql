-- ============================================================================
-- Trading 212 Reports Database Schema
-- Armazena TODA a informação dos relatórios (Anual, Mensal, Por Intervalo)
-- ============================================================================

-- ============================================================================
-- 1. TABELA DE CONTROLO: Ficheiros Importados
-- ============================================================================
CREATE TABLE report_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identificação do Ficheiro
    filename VARCHAR(255) NOT NULL UNIQUE,
    file_hash VARCHAR(64),  -- SHA256 para detetar duplicatas

    -- Tipo e Período
    report_type VARCHAR(20) NOT NULL CHECK (report_type IN ('annual', 'monthly', 'interval')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Conteúdo Extraído (Metadados)
    account_holder_name VARCHAR(255),
    account_number VARCHAR(50),
    account_type VARCHAR(50),  -- Invest, ISA, etc
    total_transactions INT DEFAULT 0,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    imported_by VARCHAR(100),  -- Utilizador ou sistema que importou
    import_status VARCHAR(20) DEFAULT 'processed' CHECK (import_status IN ('pending', 'processing', 'processed', 'error'))
);

CREATE INDEX idx_report_files_period ON report_files(period_start, period_end);
CREATE INDEX idx_report_files_type ON report_files(report_type);
CREATE INDEX idx_report_files_status ON report_files(import_status);


-- ============================================================================
-- 2. TABELA: Resumo de Saldo por Relatório
-- ============================================================================
CREATE TABLE report_balance_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Período
    report_date DATE NOT NULL,  -- Data de emissão do relatório
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Saldos
    beginning_balance DECIMAL(15, 2) NOT NULL,
    ending_balance DECIMAL(15, 2) NOT NULL,

    -- Movimentações
    total_deposits DECIMAL(15, 2) DEFAULT 0,
    total_withdrawals DECIMAL(15, 2) DEFAULT 0,
    total_interest DECIMAL(15, 2) DEFAULT 0,
    total_commission DECIMAL(15, 2) DEFAULT 0,

    -- Resultado
    net_cash_flow DECIMAL(15, 2),  -- deposits - withdrawals
    net_pnl DECIMAL(15, 2),  -- ending_balance - beginning_balance - net_cash_flow

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_balance_summary_report ON report_balance_summary(report_file_id);
CREATE INDEX idx_balance_summary_period ON report_balance_summary(period_start, period_end);


-- ============================================================================
-- 3. TABELA: Transações (BUY, SELL, DIVIDEND, DEPOSIT, WITHDRAWAL, etc)
-- ============================================================================
CREATE TABLE report_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Identifikação da Transação
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(30) NOT NULL CHECK (transaction_type IN (
        'BUY', 'SELL', 'DIVIDEND', 'INTEREST',
        'DEPOSIT', 'WITHDRAWAL', 'STOCK_SPLIT', 'FRACTIONAL_SHARE',
        'CASH_DIVIDEND', 'STOCK_DIVIDEND', 'CORPORATE_ACTION', 'FEE', 'TAX'
    )),

    -- Referência do Negócio (T212)
    order_id VARCHAR(50),  -- Order ID do T212 se disponível

    -- Instrumento (quando aplicável)
    isin VARCHAR(20),  -- NULL para transações de cash puro
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Quantidade e Preço
    quantity DECIMAL(15, 8),  -- Podem ser fracionárias
    unit_price DECIMAL(15, 4),  -- Preço por unidade (NULL para cash)

    -- Valores
    gross_amount DECIMAL(15, 2),  -- Valor bruto (antes de comissões)
    commission DECIMAL(15, 2) DEFAULT 0,
    net_amount DECIMAL(15, 2),  -- Valor líquido (após comissões)

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Cash Balance após Transação
    cash_balance_after DECIMAL(15, 2),  -- Saldo de cash reportado após esta transação

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_report ON report_transactions(report_file_id);
CREATE INDEX idx_transactions_date ON report_transactions(transaction_date);
CREATE INDEX idx_transactions_type ON report_transactions(transaction_type);
CREATE INDEX idx_transactions_isin ON report_transactions(isin);
CREATE INDEX idx_transactions_order_id ON report_transactions(order_id);


-- ============================================================================
-- 4. TABELA: Posições (Estado num ponto no tempo)
-- ============================================================================
CREATE TABLE report_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data da Posição (fim de período)
    position_date DATE NOT NULL,

    -- Instrumento
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255) NOT NULL,

    -- Quantidade
    quantity DECIMAL(15, 8) NOT NULL,

    -- Valores de Custo (Cost Basis)
    cost_basis_per_unit DECIMAL(15, 4),  -- Preço médio de compra
    total_cost_value DECIMAL(15, 2),  -- quantity × cost_basis_per_unit

    -- Valores de Mercado
    market_price_per_unit DECIMAL(15, 4) NOT NULL,  -- Preço de fecho no dia
    total_market_value DECIMAL(15, 2) NOT NULL,  -- quantity × market_price_per_unit

    -- Resultado Não Realizado
    unrealised_pnl DECIMAL(15, 2),  -- total_market_value - total_cost_value
    unrealised_pnl_percentage DECIMAL(8, 2),  -- (unrealised_pnl / total_cost_value) × 100

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_report ON report_positions(report_file_id);
CREATE INDEX idx_positions_date ON report_positions(position_date);
CREATE INDEX idx_positions_isin ON report_positions(isin);
CREATE UNIQUE INDEX idx_positions_unique ON report_positions(report_file_id, position_date, isin);


-- ============================================================================
-- 5. TABELA: Dividendos Recebidos
-- ============================================================================
CREATE TABLE report_dividends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    ex_date DATE,  -- Data ex-dividend
    payment_date DATE NOT NULL,  -- Data que foi creditado

    -- Instrumento
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Dividend Info
    quantity_held DECIMAL(15, 8),  -- Quantidade detida que gerou o dividendo
    dividend_per_share DECIMAL(15, 4),  -- Dividendo por ação
    total_dividend DECIMAL(15, 2) NOT NULL,

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dividends_report ON report_dividends(report_file_id);
CREATE INDEX idx_dividends_payment_date ON report_dividends(payment_date);
CREATE INDEX idx_dividends_isin ON report_dividends(isin);


-- ============================================================================
-- 6. TABELA: Movimentações de Cash (Depósitos e Levantamentos)
-- ============================================================================
CREATE TABLE report_cash_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    movement_date DATE NOT NULL,

    -- Tipo
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('deposit', 'withdrawal', 'interest', 'fee')),

    -- Valores
    amount DECIMAL(15, 2) NOT NULL,  -- Positivo para entradas, negativo para saídas

    -- Descrição
    description VARCHAR(500),
    reference VARCHAR(100),  -- Referência bancária ou outro identificador

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cash_movements_report ON report_cash_movements(report_file_id);
CREATE INDEX idx_cash_movements_date ON report_cash_movements(movement_date);
CREATE INDEX idx_cash_movements_type ON report_cash_movements(movement_type);


-- ============================================================================
-- 7. TABELA: Custos e Comissões
-- ============================================================================
CREATE TABLE report_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    cost_date DATE NOT NULL,

    -- Tipo
    cost_type VARCHAR(30) NOT NULL CHECK (cost_type IN (
        'commission', 'trading_fee', 'management_fee', 'tax', 'withholding_tax', 'other'
    )),

    -- Referência (se aplicável)
    isin VARCHAR(20),  -- NULL se custo geral da conta
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Valor
    amount DECIMAL(15, 2) NOT NULL,

    -- Descrição
    description VARCHAR(500),

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_costs_report ON report_costs(report_file_id);
CREATE INDEX idx_costs_date ON report_costs(cost_date);
CREATE INDEX idx_costs_type ON report_costs(cost_type);
CREATE INDEX idx_costs_isin ON report_costs(isin);


-- ============================================================================
-- 8. TABELA: Ganhos/Perdas Realizadas (Realized P&L)
-- ============================================================================
CREATE TABLE report_realized_pnl (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Transação de Venda
    sale_date DATE NOT NULL,
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Quantidade Vendida
    quantity_sold DECIMAL(15, 8) NOT NULL,

    -- Preço de Compra vs Venda
    average_purchase_price DECIMAL(15, 4),
    sale_price DECIMAL(15, 4),

    -- Resultado
    total_cost DECIMAL(15, 2),  -- quantity_sold × average_purchase_price
    total_proceeds DECIMAL(15, 2),  -- quantity_sold × sale_price
    gross_gain_loss DECIMAL(15, 2),  -- total_proceeds - total_cost
    commission DECIMAL(15, 2) DEFAULT 0,
    net_gain_loss DECIMAL(15, 2),  -- gross_gain_loss - commission
    gain_loss_percentage DECIMAL(8, 2),  -- (net_gain_loss / total_cost) × 100

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_realized_pnl_report ON report_realized_pnl(report_file_id);
CREATE INDEX idx_realized_pnl_date ON report_realized_pnl(sale_date);
CREATE INDEX idx_realized_pnl_isin ON report_realized_pnl(isin);


-- ============================================================================
-- 9. TABELA: Acções Corporativas (Stock Splits, Desdobramentos, etc)
-- ============================================================================
CREATE TABLE report_corporate_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    action_date DATE NOT NULL,

    -- Instrumento
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Tipo de Ação
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN (
        'stock_split', 'reverse_split', 'fractional_share', 'rights_offering',
        'bonus_shares', 'spin_off', 'merger', 'consolidation', 'other'
    )),

    -- Impacto
    quantity_before DECIMAL(15, 8),
    quantity_after DECIMAL(15, 8),
    ratio VARCHAR(20),  -- Ex: "2:1", "3:2" (antes:depois)

    -- Descrição
    description VARCHAR(500),

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_corporate_actions_report ON report_corporate_actions(report_file_id);
CREATE INDEX idx_corporate_actions_date ON report_corporate_actions(action_date);
CREATE INDEX idx_corporate_actions_isin ON report_corporate_actions(isin);


-- ============================================================================
-- 10. TABELA: Informação Fiscal (apenas em Relatórios Anuais)
-- ============================================================================
CREATE TABLE report_tax_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Ano Fiscal
    tax_year INT NOT NULL,

    -- Ganhos e Perdas
    total_realized_gains DECIMAL(15, 2) DEFAULT 0,
    total_realized_losses DECIMAL(15, 2) DEFAULT 0,
    net_realized_gain_loss DECIMAL(15, 2),  -- gains - losses

    -- Carry-forward
    loss_carryforward_previous DECIMAL(15, 2) DEFAULT 0,  -- Perdas do ano anterior disponíveis
    loss_carryforward_current DECIMAL(15, 2) DEFAULT 0,  -- Perdas deste ano para usar no futuro

    -- Dividendos e Juros
    total_dividend_income DECIMAL(15, 2) DEFAULT 0,
    total_interest_income DECIMAL(15, 2) DEFAULT 0,
    total_other_income DECIMAL(15, 2) DEFAULT 0,

    -- Retençao de Impostos (Withholding)
    total_withholding_tax DECIMAL(15, 2) DEFAULT 0,

    -- Notas Fiscais
    notes TEXT,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tax_summary_report ON report_tax_summary(report_file_id);
CREATE INDEX idx_tax_summary_year ON report_tax_summary(tax_year);


-- ============================================================================
-- 11. TABELA: Metadata e Anotações dos Relatórios
-- ============================================================================
CREATE TABLE report_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Metadata Técnica
    page_count INT,
    total_lines INT,
    encoding VARCHAR(20),

    -- Validação
    has_discrepancies BOOLEAN DEFAULT FALSE,
    discrepancy_notes TEXT,

    -- Notas Gerais
    general_notes TEXT,
    extraction_warnings TEXT,  -- Avisos durante a extração

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_report ON report_metadata(report_file_id);


-- ============================================================================
-- TABELAS DE AUDITORIA E SINCRONIZAÇÃO
-- ============================================================================

-- 12. Tabela de Log de Importações
CREATE TABLE report_import_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    import_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'completed', 'failed', 'partial')),

    records_imported INT,
    records_skipped INT,
    error_message TEXT,

    duration_seconds DECIMAL(6, 2)
);

CREATE INDEX idx_import_log_report ON report_import_log(report_file_id);
CREATE INDEX idx_import_log_timestamp ON report_import_log(import_timestamp);


-- 13. Tabela de Validação de Integridade
CREATE TABLE report_validation_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    check_type VARCHAR(50) NOT NULL,  -- Ex: 'balance_reconciliation', 'transaction_count', 'position_value'
    check_description VARCHAR(255),

    expected_value VARCHAR(100),
    actual_value VARCHAR(100),

    passed BOOLEAN NOT NULL,
    error_details TEXT,

    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_validation_checks_report ON report_validation_checks(report_file_id);
CREATE INDEX idx_validation_checks_passed ON report_validation_checks(passed);


-- ============================================================================
-- VIEWS ÚTEIS PARA QUERIES
-- ============================================================================

-- View: Resumo Geral de Transações por Tipo
CREATE VIEW v_transaction_summary AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    rt.transaction_type,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN rt.transaction_type IN ('BUY', 'DEPOSIT') THEN rt.net_amount ELSE 0 END) as total_inflow,
    SUM(CASE WHEN rt.transaction_type IN ('SELL', 'WITHDRAWAL') THEN ABS(rt.net_amount) ELSE 0 END) as total_outflow,
    SUM(rt.commission) as total_commission
FROM report_files rf
LEFT JOIN report_transactions rt ON rf.id = rt.report_file_id
GROUP BY rf.id, rf.filename, rf.period_start, rf.period_end, rt.transaction_type;


-- View: Posições Finais por Relatório
CREATE VIEW v_final_positions_by_report AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rp.position_date,
    rp.isin,
    rp.ticker,
    rp.instrument_name,
    rp.quantity,
    rp.total_cost_value,
    rp.total_market_value,
    rp.unrealised_pnl,
    rp.unrealised_pnl_percentage
FROM report_files rf
JOIN report_positions rp ON rf.id = rp.report_file_id;


-- View: Consolidado de P&L por Período
CREATE VIEW v_pnl_by_period AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    rbs.beginning_balance,
    rbs.ending_balance,
    rbs.net_cash_flow,
    rbs.net_pnl,
    COALESCE(SUM(rrp.net_gain_loss), 0) as total_realized_pnl,
    COALESCE(SUM(rp.unrealised_pnl), 0) as total_unrealised_pnl
FROM report_files rf
JOIN report_balance_summary rbs ON rf.id = rbs.report_file_id
LEFT JOIN report_realized_pnl rrp ON rf.id = rrp.report_file_id
LEFT JOIN report_positions rp ON rf.id = rp.report_file_id
GROUP BY rf.id, rf.filename, rf.period_start, rf.period_end,
         rbs.beginning_balance, rbs.ending_balance, rbs.net_cash_flow, rbs.net_pnl;

