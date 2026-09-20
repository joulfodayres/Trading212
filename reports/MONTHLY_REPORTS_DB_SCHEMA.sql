-- ============================================================================
-- Trading 212 Monthly Activity Statement - Database Schema
--
-- Focado EXCLUSIVAMENTE em relatórios mensais
-- Estrutura otimizada para armazenar TODA a informação do Activity Statement
-- ============================================================================

-- ============================================================================
-- 1. TABELA DE CONTROLO: Ficheiros Importados
-- ============================================================================
CREATE TABLE report_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identificação do Ficheiro
    filename VARCHAR(255) NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA256 para detetar duplicatas
    file_size_bytes INT,

    -- Período do Relatório
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Metadados da Conta
    account_holder_name VARCHAR(255),
    account_number VARCHAR(50),
    account_type VARCHAR(50),  -- "Invest", "ISA", etc

    -- Estatísticas de Importação
    total_transactions INT DEFAULT 0,
    total_positions INT DEFAULT 0,

    -- Status de Importação
    import_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (import_status IN ('pending', 'processing', 'completed', 'error')),
    error_message TEXT,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    imported_by VARCHAR(100),
    import_completed_at TIMESTAMP
);

CREATE INDEX idx_report_files_period ON report_files(period_start, period_end);
CREATE INDEX idx_report_files_status ON report_files(import_status);
CREATE INDEX idx_report_files_created ON report_files(created_at);


-- ============================================================================
-- 2. TABELA: Resumo de Saldo do Período
-- ============================================================================
CREATE TABLE monthly_balance_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL UNIQUE REFERENCES report_files(id) ON DELETE CASCADE,

    -- Saldos
    opening_balance DECIMAL(15, 2) NOT NULL,  -- Saldo no início do mês
    closing_balance DECIMAL(15, 2) NOT NULL,  -- Saldo no fim do mês

    -- Movimentações de Cash
    total_deposits DECIMAL(15, 2) DEFAULT 0,
    total_withdrawals DECIMAL(15, 2) DEFAULT 0,
    total_interest_earned DECIMAL(15, 2) DEFAULT 0,

    -- Fees
    total_trading_fees DECIMAL(15, 2) DEFAULT 0,
    total_charges DECIMAL(15, 2) DEFAULT 0,

    -- Valores de Mercado das Posições
    total_positions_value DECIMAL(15, 2) DEFAULT 0,  -- Valor total do portfolio
    total_cash_in_account DECIMAL(15, 2) DEFAULT 0,

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_balance_summary_report ON monthly_balance_summary(report_file_id);


-- ============================================================================
-- 3. TABELA: Transações do Mês (Compras, Vendas, Dividendos, Depósitos, etc)
-- ============================================================================
CREATE TABLE monthly_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data e Sequência
    transaction_date DATE NOT NULL,
    transaction_seq INT,  -- Sequência se múltiplas transações no mesmo dia

    -- Tipo de Transação
    transaction_type VARCHAR(30) NOT NULL CHECK (transaction_type IN (
        'BUY',           -- Compra de ação/ETF
        'SELL',          -- Venda de ação/ETF
        'DIVIDEND',      -- Dividendo recebido
        'CASH_DIVIDEND', -- Dividendo em cash
        'INTEREST',      -- Juros do saldo em cash
        'DEPOSIT',       -- Depósito bancário
        'WITHDRAWAL',    -- Levantamento bancário
        'FRACTIONAL_BALANCE_ADJUSTMENT',  -- Ajuste de saldo fracionário
        'FEE',           -- Taxa ou comissão
        'CORPORATE_ACTION'  -- Ação corporativa
    )),

    -- Referência do Negócio
    order_id VARCHAR(50),  -- Order ID do T212 se disponível
    settlement_date DATE,  -- Data de liquidação

    -- Instrumento (quando aplicável - NULL para cash)
    isin VARCHAR(20),
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Quantidade e Preço
    quantity DECIMAL(15, 8),  -- Pode ser fracionária
    unit_price DECIMAL(15, 4),  -- Preço por unidade (NULL para não-securities)

    -- Valores
    gross_amount DECIMAL(15, 2),  -- Valor bruto (quantidade × preço)
    fees_charged DECIMAL(15, 2) DEFAULT 0,  -- Comissões/taxas
    net_amount DECIMAL(15, 2),  -- Valor líquido (gross - fees)

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Notas
    notes TEXT,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_report ON monthly_transactions(report_file_id);
CREATE INDEX idx_transactions_date ON monthly_transactions(transaction_date);
CREATE INDEX idx_transactions_type ON monthly_transactions(transaction_type);
CREATE INDEX idx_transactions_isin ON monthly_transactions(isin);
CREATE INDEX idx_transactions_order_id ON monthly_transactions(order_id);


-- ============================================================================
-- 4. TABELA: Posições Abertas (Fim de Período)
-- ============================================================================
CREATE TABLE monthly_open_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data da Posição (fim do período do relatório)
    position_date DATE NOT NULL,

    -- Instrumento
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255) NOT NULL,

    -- Quantidade
    quantity DECIMAL(15, 8) NOT NULL,

    -- Valores de Mercado
    market_price_per_unit DECIMAL(15, 4) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_open_positions_report ON monthly_open_positions(report_file_id);
CREATE INDEX idx_open_positions_date ON monthly_open_positions(position_date);
CREATE INDEX idx_open_positions_isin ON monthly_open_positions(isin);
CREATE UNIQUE INDEX idx_open_positions_unique ON monthly_open_positions(report_file_id, isin);


-- ============================================================================
-- 5. TABELA: Dividend Transactions (Desagregação)
-- ============================================================================
CREATE TABLE monthly_dividends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    ex_date DATE,
    payment_date DATE NOT NULL,

    -- Instrumento
    isin VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Dividend Details
    shares_held DECIMAL(15, 8),  -- Quantidade de ações que geraram dividendo
    dividend_per_share DECIMAL(15, 4),
    total_dividend_amount DECIMAL(15, 2) NOT NULL,

    -- Retenção de Impostos
    withholding_tax DECIMAL(15, 2) DEFAULT 0,
    net_dividend DECIMAL(15, 2),  -- total_dividend_amount - withholding_tax

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dividends_report ON monthly_dividends(report_file_id);
CREATE INDEX idx_dividends_payment_date ON monthly_dividends(payment_date);
CREATE INDEX idx_dividends_isin ON monthly_dividends(isin);


-- ============================================================================
-- 6. TABELA: Movimentações de Cash (Depósitos, Levantamentos, Juros)
-- ============================================================================
CREATE TABLE monthly_cash_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    movement_date DATE NOT NULL,

    -- Tipo
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN (
        'DEPOSIT',      -- Depósito na conta
        'WITHDRAWAL',   -- Levantamento da conta
        'INTEREST',     -- Juros do cash
        'FEE'           -- Taxa da conta
    )),

    -- Valores
    amount DECIMAL(15, 2) NOT NULL,  -- Positivo para entradas, negativo para saídas

    -- Descrição
    description VARCHAR(500),
    reference VARCHAR(100),  -- Referência bancária ou T212 order ID

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cash_movements_report ON monthly_cash_movements(report_file_id);
CREATE INDEX idx_cash_movements_date ON monthly_cash_movements(movement_date);
CREATE INDEX idx_cash_movements_type ON monthly_cash_movements(movement_type);


-- ============================================================================
-- 7. TABELA: Fees and Charges (Detalhamento de Custos)
-- ============================================================================
CREATE TABLE monthly_fees_charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Data
    charge_date DATE NOT NULL,

    -- Tipo de Taxa
    fee_type VARCHAR(50) NOT NULL CHECK (fee_type IN (
        'TRADING_COMMISSION',    -- Comissão de negociação
        'SETTLEMENT_FEE',        -- Taxa de liquidação
        'CUSTODY_FEE',           -- Taxa de custódia
        'PLATFORM_FEE',          -- Taxa de plataforma
        'ACCOUNT_MANAGEMENT_FEE',-- Taxa de gestão de conta
        'DIVIDEND_FEE',          -- Taxa no dividendo
        'CONVERSION_FEE',        -- Taxa de conversão de moeda
        'OTHER'
    )),

    -- Instrumentos Relacionados (pode ser NULL se taxa geral)
    isin VARCHAR(20),
    ticker VARCHAR(20),
    instrument_name VARCHAR(255),

    -- Valor
    amount DECIMAL(15, 2) NOT NULL,  -- Sempre positivo (débito)

    -- Descrição
    description VARCHAR(500),

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fees_charges_report ON monthly_fees_charges(report_file_id);
CREATE INDEX idx_fees_charges_date ON monthly_fees_charges(charge_date);
CREATE INDEX idx_fees_charges_type ON monthly_fees_charges(fee_type);


-- ============================================================================
-- 8. TABELA: Metadata e Validação do Relatório
-- ============================================================================
CREATE TABLE monthly_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Referência ao Ficheiro
    report_file_id UUID NOT NULL UNIQUE REFERENCES report_files(id) ON DELETE CASCADE,

    -- Informação Técnica do PDF
    pdf_page_count INT,
    pdf_generated_date TIMESTAMP,
    pdf_parsing_notes TEXT,

    -- Validação de Integridade
    is_validated BOOLEAN DEFAULT FALSE,
    validation_errors TEXT,  -- Se houver erros de validação

    -- Discrepâncias Encontradas
    has_discrepancies BOOLEAN DEFAULT FALSE,
    discrepancy_notes TEXT,

    -- Notas Gerais
    general_notes TEXT,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_report ON monthly_metadata(report_file_id);


-- ============================================================================
-- 9. TABELA: Import Log (Histórico de Importações)
-- ============================================================================
CREATE TABLE monthly_import_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_file_id UUID NOT NULL REFERENCES report_files(id) ON DELETE CASCADE,

    -- Timestamps
    import_start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    import_end_time TIMESTAMP,

    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'completed', 'failed', 'partial')),

    -- Contadores
    transactions_imported INT DEFAULT 0,
    transactions_skipped INT DEFAULT 0,
    positions_imported INT DEFAULT 0,
    dividends_imported INT DEFAULT 0,
    cash_movements_imported INT DEFAULT 0,
    fees_imported INT DEFAULT 0,

    -- Erros
    error_message TEXT,
    error_stack_trace TEXT,

    -- Duração
    duration_seconds DECIMAL(10, 2),

    -- Notas
    import_notes TEXT
);

CREATE INDEX idx_import_log_report ON monthly_import_log(report_file_id);
CREATE INDEX idx_import_log_status ON monthly_import_log(status);
CREATE INDEX idx_import_log_time ON monthly_import_log(import_start_time);


-- ============================================================================
-- VIEWS ÚTEIS PARA QUERIES
-- ============================================================================

-- View: Resumo de Transações por Tipo
CREATE VIEW v_monthly_transactions_summary AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    mt.transaction_type,
    COUNT(*) as count,
    COUNT(DISTINCT mt.transaction_date) as days_with_activity,
    COALESCE(SUM(CASE WHEN mt.transaction_type IN ('BUY', 'DEPOSIT') THEN mt.net_amount ELSE 0 END), 0) as total_inflow,
    COALESCE(SUM(CASE WHEN mt.transaction_type IN ('SELL', 'WITHDRAWAL') THEN ABS(mt.net_amount) ELSE 0 END), 0) as total_outflow,
    COALESCE(SUM(mt.fees_charged), 0) as total_fees
FROM report_files rf
LEFT JOIN monthly_transactions mt ON rf.id = mt.report_file_id
GROUP BY rf.id, rf.filename, rf.period_start, rf.period_end, mt.transaction_type;


-- View: Portfolio Final (Posições no fim do período)
CREATE VIEW v_monthly_portfolio_final AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    mop.position_date,
    mop.isin,
    mop.ticker,
    mop.instrument_name,
    mop.quantity,
    mop.market_price_per_unit,
    mop.total_market_value
FROM report_files rf
JOIN monthly_open_positions mop ON rf.id = mop.report_file_id
ORDER BY mop.total_market_value DESC;


-- View: Resumo de Dividendos
CREATE VIEW v_monthly_dividends_summary AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    COUNT(*) as dividend_count,
    COALESCE(SUM(md.total_dividend_amount), 0) as total_dividends_gross,
    COALESCE(SUM(md.withholding_tax), 0) as total_withholding_tax,
    COALESCE(SUM(md.net_dividend), 0) as total_dividends_net
FROM report_files rf
LEFT JOIN monthly_dividends md ON rf.id = md.report_file_id
GROUP BY rf.id, rf.filename, rf.period_start, rf.period_end;


-- View: P&L Realizado no Período (vendas com ganho/perda)
CREATE VIEW v_monthly_realized_pnl AS
SELECT
    rf.id as report_file_id,
    rf.filename,
    rf.period_start,
    rf.period_end,
    mt.transaction_date,
    mt.isin,
    mt.ticker,
    mt.instrument_name,
    mt.quantity,
    mt.unit_price as sale_price,
    mt.gross_amount,
    mt.fees_charged,
    mt.net_amount
FROM report_files rf
JOIN monthly_transactions mt ON rf.id = mt.report_file_id
WHERE mt.transaction_type = 'SELL'
ORDER BY mt.transaction_date DESC;

