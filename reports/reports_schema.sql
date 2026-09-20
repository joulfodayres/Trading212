-- =====================================================================
-- Trading 212 - Activity Statement (Monthly Reports) Database Schema
-- =====================================================================
-- PostgreSQL / Supabase
-- 15 tabelas de dados (uma por cada tabela do Activity Statement PDF)
--  + 1 tabela de controlo de ficheiros importados.
--
-- Convencoes:
--  - Cada tabela de dados tem PK propria "id" (UUID).
--  - Cada tabela de dados tem as 3 colunas de auditoria:
--        file_id     UUID  -> FK para imported_files(id) (origem da info)
--        created_at  TIMESTAMPTZ
--        updated_at  TIMESTAMPTZ
--  - Nomes de coluna mapeiam 1:1 com os campos descritos em SECOES_PDF.md.
--  - Colunas monetarias/quantidades em NUMERIC para preservar precisao.
-- =====================================================================

-- Extensao para gen_random_uuid() (Supabase ja tem pgcrypto ativo)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================================
-- 0. Tabela de controlo de ficheiros importados
-- =====================================================================
CREATE TABLE imported_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name       VARCHAR NOT NULL,
    file_hash       VARCHAR,                 -- hash SHA-256 p/ evitar duplicados
    customer_id     VARCHAR,                 -- CUSTOMER ID no topo de cada pagina
    customer_name   VARCHAR,                 -- CUSTOMER NAME no topo de cada pagina
    period_start    DATE,                    -- inicio do periodo do statement
    period_end      DATE,                    -- fim do periodo do statement
    generated_at    TIMESTAMPTZ,             -- data de geracao do PDF (T212)
    pages           INTEGER,                 -- nr de paginas
    status          VARCHAR DEFAULT 'PENDING', -- PENDING, IMPORTED, FAILED
    imported_at     TIMESTAMPTZ DEFAULT now(),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX idx_imported_files_hash ON imported_files (file_hash);

-- =====================================================================
-- ============  INVEST ACCOUNT  =======================================
-- =====================================================================

-- 1. Invest account - executed trades (pag. 2-6)
CREATE TABLE invest_executed_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    execution_time      TIMESTAMPTZ,
    instrument          VARCHAR,
    isin                VARCHAR,
    order_id            VARCHAR,
    direction           VARCHAR,             -- Buy / Sell
    quantity            NUMERIC,
    execution_price     NUMERIC,
    value               NUMERIC,
    order_type          VARCHAR,             -- Limit / Market / Stop-limit
    execution_venue     VARCHAR,             -- OTC / ...
    session             VARCHAR,             -- Regular hours / ...
    fx_rate             NUMERIC,
    fx_fee              NUMERIC,
    exchange_govt_fees  NUMERIC,
    return_amount       NUMERIC,             -- coluna "RETURN"
    return_value        NUMERIC,             -- coluna "VALUE" (par convertido)
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_exec_file    ON invest_executed_trades (file_id);
CREATE INDEX idx_invest_exec_isin    ON invest_executed_trades (isin);
CREATE INDEX idx_invest_exec_time    ON invest_executed_trades (execution_time);

-- 2. Invest account - pending orders (pag. 7)
CREATE TABLE invest_pending_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    isin                VARCHAR,
    instrument_currency VARCHAR,
    order_id            VARCHAR,
    type                VARCHAR,
    direction           VARCHAR,
    expiration          VARCHAR,
    quantity            NUMERIC,
    limit_price         NUMERIC,
    stop_price          NUMERIC,
    value               NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_pending_file ON invest_pending_orders (file_id);

-- 3. Invest account - open positions (pag. 7)
CREATE TABLE invest_open_positions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    isin                VARCHAR,
    quantity            NUMERIC,
    average_price       NUMERIC,
    price               NUMERIC,
    return_amount       NUMERIC,             -- coluna "RETURN"
    value               NUMERIC,             -- coluna "VALUE"
    fx_rate             NUMERIC,
    return_converted    NUMERIC,             -- coluna "RETURN" (par convertido)
    value_converted     NUMERIC,             -- coluna "VALUE"  (par convertido)
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_open_file    ON invest_open_positions (file_id);
CREATE INDEX idx_invest_open_isin    ON invest_open_positions (isin);

-- 4. Invest account - transactions (pag. 9-10)
CREATE TABLE invest_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    time                TIMESTAMPTZ,
    type                VARCHAR,             -- Interest on cash / Card purchase / ...
    amount              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_tx_file      ON invest_transactions (file_id);
CREATE INDEX idx_invest_tx_time      ON invest_transactions (time);

-- 5. Invest account - dividends (pag. 10)
CREATE TABLE invest_dividends (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    isin                VARCHAR,
    issuing_country     VARCHAR,
    eligible_holdings   NUMERIC,
    pay_date            DATE,
    amount_per_share    NUMERIC,
    total_amount        NUMERIC,
    wht_rate            NUMERIC,
    wht                 NUMERIC,
    fx_rate             NUMERIC,
    net_amount          NUMERIC,             -- Net Amount (Account Currency)
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_div_file     ON invest_dividends (file_id);

-- =====================================================================
-- ============  CFD ACCOUNT  ==========================================
-- =====================================================================

-- 6. CFD account - executed trades (pag. 11)
CREATE TABLE cfd_executed_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    execution_time      TIMESTAMPTZ,
    instrument          VARCHAR,
    order_id            VARCHAR,
    order_type          VARCHAR,
    direction           VARCHAR,
    execution_venue     VARCHAR,
    position_size       NUMERIC,
    average_price       NUMERIC,
    execution_price     NUMERIC,
    value               NUMERIC,
    spread              NUMERIC,
    fx_rate             NUMERIC,
    fx_fee              NUMERIC,
    result              NUMERIC,
    dividend_adjustments NUMERIC,
    overnight_interest  NUMERIC,
    total_result        NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_exec_file       ON cfd_executed_trades (file_id);
CREATE INDEX idx_cfd_exec_time       ON cfd_executed_trades (execution_time);

-- 7. CFD account - pending orders (pag. 12)
CREATE TABLE cfd_pending_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    instrument_currency VARCHAR,
    order_id            VARCHAR,
    type                VARCHAR,
    expiration          VARCHAR,
    direction           VARCHAR,
    position_size       NUMERIC,
    price               NUMERIC,
    value               NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_pending_file    ON cfd_pending_orders (file_id);

-- 8. CFD account - open positions (pag. 12)
CREATE TABLE cfd_open_positions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    direction           VARCHAR,
    position_size       NUMERIC,
    average_price       NUMERIC,
    price               NUMERIC,
    value               NUMERIC,
    fx_rate             NUMERIC,
    fx_fee              NUMERIC,
    result              NUMERIC,
    dividend_adjustments NUMERIC,
    overnight_interest  NUMERIC,
    total_result        NUMERIC,
    period_price_change VARCHAR,             -- ex: "-31.13%"
    margin              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_open_file       ON cfd_open_positions (file_id);

-- 9. CFD account - transactions (pag. 14)
CREATE TABLE cfd_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    time                TIMESTAMPTZ,
    type                VARCHAR,
    amount              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_tx_file         ON cfd_transactions (file_id);

-- 10. CFD account - dividend adjustments (pag. 14)
CREATE TABLE cfd_dividend_adjustments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    transaction_time    TIMESTAMPTZ,
    instrument          VARCHAR,
    direction           VARCHAR,
    ex_date             DATE,
    position_size       NUMERIC,
    amount_per_share    NUMERIC,
    gross_amount        NUMERIC,
    wht_tax_rate        NUMERIC,
    wht_tax             NUMERIC,
    net_amount          NUMERIC,
    fx_rate             NUMERIC,
    net_amount_converted NUMERIC,            -- 2a coluna "Net Amount" (convertido)
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_divadj_file     ON cfd_dividend_adjustments (file_id);

-- 11. CFD account - overnight interest (pag. 14-17)
CREATE TABLE cfd_overnight_interest (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id                 UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    transaction_time        TIMESTAMPTZ,
    instrument              VARCHAR,
    direction               VARCHAR,
    position_size           NUMERIC,
    overnight_interest_rate NUMERIC,
    amount                  NUMERIC,         -- coluna "AMOUNT" (moeda instrumento)
    fx_rate                 NUMERIC,
    amount_converted        NUMERIC,         -- 2a coluna "AMOUNT" (convertido)
    created_at              TIMESTAMPTZ DEFAULT now(),
    updated_at              TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_overnight_file  ON cfd_overnight_interest (file_id);
CREATE INDEX idx_cfd_overnight_time  ON cfd_overnight_interest (transaction_time);

-- =====================================================================
-- ============  CRYPTO ACCOUNT  =======================================
-- =====================================================================

-- 12. Crypto account - executed trades (pag. 18-22)
CREATE TABLE crypto_executed_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    execution_time      TIMESTAMPTZ,
    symbol              VARCHAR,             -- ex: BTC/EUR
    asset               VARCHAR,             -- ex: Bitcoin
    order_id            VARCHAR,
    fill_id             VARCHAR,
    direction           VARCHAR,
    quantity            NUMERIC,
    execution_price     NUMERIC,
    value               NUMERIC,
    realised_pl         NUMERIC,             -- Realised P/L
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_exec_file    ON crypto_executed_trades (file_id);
CREATE INDEX idx_crypto_exec_symbol  ON crypto_executed_trades (symbol);
CREATE INDEX idx_crypto_exec_time    ON crypto_executed_trades (execution_time);

-- 13. Crypto account - pending orders (pag. 23)
CREATE TABLE crypto_pending_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    symbol              VARCHAR,
    asset               VARCHAR,
    currency            VARCHAR,
    order_id            VARCHAR,
    type                VARCHAR,
    direction           VARCHAR,
    expiration          VARCHAR,
    quantity            NUMERIC,
    limit_price         NUMERIC,
    value               NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_pending_file ON crypto_pending_orders (file_id);

-- 14. Crypto account - open positions (pag. 23)
CREATE TABLE crypto_open_positions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    symbol              VARCHAR,
    asset               VARCHAR,
    quantity            NUMERIC,
    opening_price       NUMERIC,
    price               NUMERIC,
    unrealised_pl       NUMERIC,             -- Unrealised P/L
    value               NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_open_file    ON crypto_open_positions (file_id);
CREATE INDEX idx_crypto_open_symbol  ON crypto_open_positions (symbol);

-- 15. Crypto account - transactions (pag. 25)
CREATE TABLE crypto_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    time                TIMESTAMPTZ,
    type                VARCHAR,
    amount              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_tx_file      ON crypto_transactions (file_id);

-- =====================================================================
-- FIM DO SCHEMA
-- =====================================================================
