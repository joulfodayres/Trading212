-- ============================================================================
-- CORREÇÃO: REPORT_POSITIONS - Versão Revisada
-- ============================================================================

-- PROBLEMA IDENTIFICADO:
-- O relatório mensal (Activity Statement) pág 3 "Invest Account - Open Positions"
-- só contém: ISIN, Instrument Name, Quantity, Market Value
--
-- O relatório anual (Annual Statement) contém MAIS campos:
-- Cost Basis, Total Cost Value, Unrealised P&L, etc
--
-- SOLUÇÃO: Fazer campos opcionais (NULLABLE) para suportar ambos os tipos

-- VERSÃO CORRIGIDA:
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

    -- Quantidade (SEMPRE presente)
    quantity DECIMAL(15, 8) NOT NULL,

    -- Valores de Custo (Cost Basis)
    -- ℹ️ NULLABLE: Só em relatórios anuais
    cost_basis_per_unit DECIMAL(15, 4),  -- Preço médio de compra
    total_cost_value DECIMAL(15, 2),  -- quantity × cost_basis_per_unit

    -- Valores de Mercado (SEMPRE presente)
    market_price_per_unit DECIMAL(15, 4),  -- Preço de fecho no dia (opcional se só temos market_value total)
    total_market_value DECIMAL(15, 2) NOT NULL,  -- quantity × market_price_per_unit

    -- Resultado Não Realizado
    -- ℹ️ NULLABLE: Só em relatórios anuais
    unrealised_pnl DECIMAL(15, 2),  -- total_market_value - total_cost_value
    unrealised_pnl_percentage DECIMAL(8, 2),  -- (unrealised_pnl / total_cost_value) × 100

    -- Moeda
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Flag: Indica se este registo tem info de cost basis
    has_cost_basis_info BOOLEAN DEFAULT FALSE,

    -- Auditoria
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_report ON report_positions(report_file_id);
CREATE INDEX idx_positions_date ON report_positions(position_date);
CREATE INDEX idx_positions_isin ON report_positions(isin);
CREATE UNIQUE INDEX idx_positions_unique ON report_positions(report_file_id, position_date, isin);
