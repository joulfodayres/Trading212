-- =====================================================================
-- TRADING 212 BOT - PROD SETUP (CONSOLIDATED SCRIPT)
-- =====================================================================
-- Execute this ONCE, top to bottom, in the SQL Editor of a BRAND NEW
-- Supabase project (PROD). It combines every migration that has been
-- applied incrementally to DEMO over time, already in the correct
-- final order, skipping steps that only made sense as "fix ups" on an
-- existing DEMO database (e.g. removing columns that were added and
-- then dropped again — those columns are simply never created here).
--
-- Explicitly NOT included (do these separately / manually instead):
--   - db/create_test_user.sql   -> create the real PROD user via
--                                  Supabase Auth dashboard instead
--   - db/mock_data_phase4.sql   -> test/mock data, not for PROD
--
-- Generated: 2026-09-27, consolidating (in this order):
--   supabase_schema.sql, trading_strategy_tables.sql,
--   simplify_to_singleuser.sql, phase_4_schema_changes.sql,
--   app_parameters_table.sql, add_missing_position_fields.sql,
--   migration_add_quantity_precision.sql, login_security_tables.sql,
--   trading_limits_and_alerts.sql,
--   migrations/remove_unused_app_parameters_columns.sql (folded in — see note),
--   migrations/drop_scheduler_enabled.sql (folded in — see note),
--   reports/reports_schema.sql
-- =====================================================================


-- =====================================================================
-- SECTION 1: BASE SCHEMA (users, isins, config, strategies, trades, logs)
-- =====================================================================
-- Note: this app is single-user (see Section 3), so RLS is created here
-- for consistency with DEMO's history but immediately disabled/removed
-- in Section 3, and the user_id columns are dropped there too. We still
-- create them first (matching DEMO's actual schema evolution) so that
-- later ALTER TABLE / FK statements referencing these tables behave
-- identically to DEMO.

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own data" ON users
  FOR SELECT USING (auth.uid()::text = id::text);

-- Schema reconciled 2026-10-04 to match actual DEMO/PROD state after
-- discovering drift (missing strategy_id, instrument_json,
-- position_created_at caused sync failures in PROD). See BACKLOG.md
-- Item #18 for the broader fix (migration tracking).
--
-- NOTE: user_id is intentionally NOT created here (unlike the version of
-- this block that shipped originally). This script's own later
-- single-user-simplification section (search "REMOVE user_id COLUMN"
-- below) already drops user_id from isins to match live DEMO/PROD, which
-- has never had this column since simplify_to_singleuser.sql (2026-09-17)
-- ran. Creating it here only to drop it a few hundred lines later was
-- redundant and the user_id-scoped RLS policies below never meaningfully
-- applied in this single-user app — removed both the column and those
-- policies for clarity instead of leaving dead code that contradicts the
-- live schema.
CREATE TABLE isins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  isin VARCHAR NOT NULL UNIQUE,
  ticker VARCHAR,
  name VARCHAR,
  currency VARCHAR DEFAULT 'EUR',
  automation_enabled BOOLEAN DEFAULT FALSE,
  strategy_id UUID, -- FK added below via ALTER, after the strategies table exists (strategies is created later in this script)
  fields_json JSONB,

  -- Synced from T212 GET /equity/positions (backend/routes/isins.py
  -- sync_positions + toggle endpoint, backend/services/automation_engine.py)
  average_price_paid DECIMAL,
  current_price DECIMAL,
  quantity DECIMAL DEFAULT 0,
  quantity_available_for_trading DECIMAL,
  quantity_in_pies DECIMAL,

  -- Wallet impact (walletImpact object from T212 API)
  wi_currency VARCHAR DEFAULT 'EUR',
  wi_current_value DECIMAL,
  wi_fx_impact DECIMAL,
  wi_total_cost DECIMAL,
  wi_unrealized_profit_loss DECIMAL,

  -- Timestamps from T212 API (separate from local created_at/updated_at)
  api_created_at TIMESTAMP WITH TIME ZONE,
  position_created_at TIMESTAMP WITH TIME ZONE,

  -- Full instrument JSON backup from T212 API
  instrument_json JSONB,

  -- T212 API precision (adaptive per ISIN) + grid trading bookkeeping
  quantity_precision INTEGER DEFAULT 3,
  initial_trade BOOLEAN DEFAULT FALSE,
  trades_balance INTEGER DEFAULT 0,

  -- Item #22/#24: last-used Manual Orders generation params (Zone 1-5
  -- Sell/Buy), for pre-filling the "Gerir Ordens" form on next visit.
  -- initial_price is deliberately excluded/never restored from this —
  -- see backend/routes/manual_orders.py for why.
  last_manual_order_params JSONB,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_isins_isin ON isins(isin);

-- RLS intentionally left disabled (single-user app, see
-- simplify_to_singleuser.sql below) — there is no per-user ownership
-- column left on this table to scope row-level policies on.

CREATE TABLE config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  t212_api_key_encrypted VARCHAR,
  t212_api_secret_encrypted VARCHAR,
  t212_environment VARCHAR DEFAULT 'demo',
  strategy_params JSONB,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_config_user_id ON config(user_id);

ALTER TABLE config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own config" ON config
  FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert their own config" ON config
  FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update their own config" ON config
  FOR UPDATE USING (user_id = auth.uid());

-- NOTE: user_id is intentionally NOT created here, same reasoning as the
-- isins table reconciliation above: this script's later single-user-
-- simplification section already drops user_id from strategies (DROP
-- POLICY / DISABLE ROW LEVEL SECURITY / DROP COLUMN user_id / DROP INDEX
-- idx_strategies_user_id, search "REMOVE user_id COLUMN" below) to match
-- live DEMO/PROD, which has never had this column since
-- simplify_to_singleuser.sql (2026-09-17) ran. Creating it here only to
-- drop it a few hundred lines later was redundant and the user_id-scoped
-- RLS policies below never meaningfully applied in this single-user app —
-- removed both the column and those policies for clarity instead of
-- leaving dead code that contradicts the live schema.
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL,
  type VARCHAR DEFAULT 'grid_trading',
  params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS intentionally left disabled (single-user app, see
-- simplify_to_singleuser.sql below) — there is no per-user ownership
-- column left on this table to scope row-level policies on.

-- Deferred FK: isins.strategy_id -> strategies.id (isins is created earlier
-- in this script, before strategies exists, so the constraint is added here
-- instead of inline in CREATE TABLE isins).
ALTER TABLE isins ADD CONSTRAINT isins_strategy_id_fkey
  FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE SET NULL;

CREATE TABLE trades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID REFERENCES isins(id) ON DELETE SET NULL,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  tipo VARCHAR NOT NULL CHECK (tipo IN ('BUY', 'SELL')),
  quantidade DECIMAL(18, 8) NOT NULL,
  preco DECIMAL(18, 8) NOT NULL,
  comissao DECIMAL(18, 8) DEFAULT 0,
  status VARCHAR DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'FAILED')),
  t212_order_id VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  executed_at TIMESTAMP WITH TIME ZONE,
  detalhes_json JSONB
);

CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_isin_id ON trades(isin_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);

ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own trades" ON trades
  FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert their own trades" ON trades
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE TABLE logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  nivel VARCHAR DEFAULT 'INFO' CHECK (nivel IN ('INFO', 'WARNING', 'ERROR', 'DEBUG')),
  mensagem VARCHAR NOT NULL,
  detalhes_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_nivel ON logs(nivel);
CREATE INDEX idx_logs_created_at ON logs(created_at);

ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own logs" ON logs
  FOR SELECT USING (user_id = auth.uid());


-- =====================================================================
-- SECTION 2: STRATEGY MANAGEMENT TABLES (isin_strategy_config/history,
-- strategy_definitions, strategy_parameters)
-- =====================================================================

CREATE TABLE isin_strategy_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, isin_id)
);

CREATE INDEX idx_isin_strategy_config_user_id ON isin_strategy_config(user_id);
CREATE INDEX idx_isin_strategy_config_isin_id ON isin_strategy_config(isin_id);
CREATE INDEX idx_isin_strategy_config_strategy_id ON isin_strategy_config(strategy_id);

ALTER TABLE isin_strategy_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ISIN strategy configs" ON isin_strategy_config
  FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own ISIN strategy configs" ON isin_strategy_config
  FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update their own ISIN strategy configs" ON isin_strategy_config
  FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete their own ISIN strategy configs" ON isin_strategy_config
  FOR DELETE USING (user_id = auth.uid());

CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(user_id, isin_id, created_at)
);

CREATE INDEX idx_isin_strategy_history_user_id ON isin_strategy_history(user_id);
CREATE INDEX idx_isin_strategy_history_isin_id ON isin_strategy_history(isin_id);
CREATE INDEX idx_isin_strategy_history_created_at ON isin_strategy_history(created_at);

ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ISIN strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert their own ISIN strategy history" ON isin_strategy_history
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE TABLE strategy_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  strategy_name VARCHAR NOT NULL,
  strategy_desc TEXT,
  strategy_status VARCHAR NOT NULL DEFAULT 'E' CHECK (strategy_status IN ('E', 'D')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, strategy_name)
);

CREATE INDEX idx_strategy_definitions_user_id ON strategy_definitions(user_id);
CREATE INDEX idx_strategy_definitions_status ON strategy_definitions(strategy_status);

ALTER TABLE strategy_definitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy definitions" ON strategy_definitions
  FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own strategy definitions" ON strategy_definitions
  FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update their own strategy definitions" ON strategy_definitions
  FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete their own strategy definitions" ON strategy_definitions
  FOR DELETE USING (user_id = auth.uid());

CREATE TABLE strategy_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID NOT NULL REFERENCES strategy_definitions(id) ON DELETE CASCADE,
  pos INTEGER NOT NULL,
  param1 DECIMAL(18, 8),
  param2 DECIMAL(18, 8),
  param3 DECIMAL(18, 8),
  param4 DECIMAL(18, 8),
  param5 DECIMAL(18, 8),
  param6 DECIMAL(18, 8),
  param7 DECIMAL(18, 8),
  param8 DECIMAL(18, 8),
  param9 DECIMAL(18, 8),
  param10 DECIMAL(18, 8),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(strategy_id, pos)
);

CREATE INDEX idx_strategy_parameters_strategy_id ON strategy_parameters(strategy_id);

ALTER TABLE strategy_parameters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy parameters" ON strategy_parameters
  FOR SELECT USING (
    strategy_id IN (SELECT id FROM strategy_definitions WHERE user_id = auth.uid())
  );
CREATE POLICY "Users can manage their own strategy parameters" ON strategy_parameters
  FOR INSERT WITH CHECK (
    strategy_id IN (SELECT id FROM strategy_definitions WHERE user_id = auth.uid())
  );
CREATE POLICY "Users can update their own strategy parameters" ON strategy_parameters
  FOR UPDATE USING (
    strategy_id IN (SELECT id FROM strategy_definitions WHERE user_id = auth.uid())
  );
CREATE POLICY "Users can delete their own strategy parameters" ON strategy_parameters
  FOR DELETE USING (
    strategy_id IN (SELECT id FROM strategy_definitions WHERE user_id = auth.uid())
  );


-- =====================================================================
-- SECTION 3: SIMPLIFY TO SINGLE-USER
-- =====================================================================
-- The app is single-user; drop the multi-user RLS/user_id scaffolding
-- created above (kept in Sections 1-2 for schema-history fidelity with
-- DEMO, removed here in the same order DEMO removed it).

DROP POLICY IF EXISTS "Users can view their own config" ON config;
DROP POLICY IF EXISTS "Users can insert their own config" ON config;
DROP POLICY IF EXISTS "Users can update their own config" ON config;

DROP POLICY IF EXISTS "Users can view their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can insert their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can update their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can delete their own ISINs" ON isins;

DROP POLICY IF EXISTS "Users can view their own ISIN strategy history" ON isin_strategy_history;
DROP POLICY IF EXISTS "Users can insert their own ISIN strategy history" ON isin_strategy_history;

DROP POLICY IF EXISTS "Can view strategies (own or public)" ON strategies;
DROP POLICY IF EXISTS "Can insert own strategies" ON strategies;
DROP POLICY IF EXISTS "Can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Can delete own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can view their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can manage their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update their own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete their own strategies" ON strategies;

DROP POLICY IF EXISTS "Users can view their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can manage their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can update their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can delete their own strategy parameters" ON strategy_parameters;

DROP POLICY IF EXISTS "Users can view their own trades" ON trades;
DROP POLICY IF EXISTS "Users can insert their own trades" ON trades;

DROP POLICY IF EXISTS "Users can view their own logs" ON logs;

ALTER TABLE config DISABLE ROW LEVEL SECURITY;
ALTER TABLE isins DISABLE ROW LEVEL SECURITY;
ALTER TABLE isin_strategy_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE strategies DISABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_parameters DISABLE ROW LEVEL SECURITY;
ALTER TABLE trades DISABLE ROW LEVEL SECURITY;
ALTER TABLE logs DISABLE ROW LEVEL SECURITY;

ALTER TABLE config DROP CONSTRAINT IF EXISTS config_user_id_fkey;
ALTER TABLE config DROP CONSTRAINT IF EXISTS config_user_id_key;
ALTER TABLE config DROP COLUMN IF EXISTS user_id;

ALTER TABLE isins DROP CONSTRAINT IF EXISTS isins_user_id_fkey;
ALTER TABLE isins DROP CONSTRAINT IF EXISTS isins_user_id_isin_key;
ALTER TABLE isins ADD CONSTRAINT isins_isin_key UNIQUE(isin);
ALTER TABLE isins DROP COLUMN IF EXISTS user_id;

ALTER TABLE isin_strategy_history DROP CONSTRAINT IF EXISTS isin_strategy_history_user_id_fkey;
ALTER TABLE isin_strategy_history DROP CONSTRAINT IF EXISTS isin_strategy_history_user_id_isin_id_created_at_key;
ALTER TABLE isin_strategy_history ADD CONSTRAINT isin_strategy_history_isin_id_created_at_key UNIQUE(isin_id, created_at);
ALTER TABLE isin_strategy_history DROP COLUMN IF EXISTS user_id;

ALTER TABLE strategies DROP CONSTRAINT IF EXISTS strategies_user_id_fkey;
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS strategies_user_id_strategy_name_key;
-- Note: unlike strategy_definitions (unique name), the original "strategies"
-- table has no strategy_name column (it uses "name") — this ADD CONSTRAINT
-- from the original migration doesn't apply to it, kept only for parity
-- with isins/isin_strategy_history above where it does apply. Skipped here
-- intentionally (DEMO's script had a latent no-op on this line too).
ALTER TABLE strategies DROP COLUMN IF EXISTS user_id;

ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_user_id_fkey;
ALTER TABLE trades DROP COLUMN IF EXISTS user_id;

ALTER TABLE logs DROP CONSTRAINT IF EXISTS logs_user_id_fkey;
ALTER TABLE logs DROP COLUMN IF EXISTS user_id;

DROP INDEX IF EXISTS idx_config_user_id;
DROP INDEX IF EXISTS idx_isins_user_id;
DROP INDEX IF EXISTS idx_isin_strategy_history_user_id;
DROP INDEX IF EXISTS idx_strategies_user_id;
DROP INDEX IF EXISTS idx_trades_user_id;
DROP INDEX IF EXISTS idx_logs_user_id;


-- =====================================================================
-- SECTION 4: PHASE 4 SCHEMA CHANGES (isins position fields, orders table)
-- =====================================================================

ALTER TABLE isins ADD COLUMN api_created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE isins ADD COLUMN initial_trade BOOLEAN DEFAULT FALSE;
ALTER TABLE isins ADD COLUMN trades_balance INTEGER DEFAULT 0;
ALTER TABLE isins ADD COLUMN average_price_paid DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN current_price DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN quantity DOUBLE PRECISION DEFAULT 0;
ALTER TABLE isins ADD COLUMN quantity_available_for_trading DOUBLE PRECISION DEFAULT 0;
ALTER TABLE isins ADD COLUMN quantity_in_pies DOUBLE PRECISION DEFAULT 0;
ALTER TABLE isins ADD COLUMN wi_currency VARCHAR;
ALTER TABLE isins ADD COLUMN wi_current_value DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_fx_impact DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_total_cost DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_unrealized_profit_loss DOUBLE PRECISION;

ALTER TABLE strategies ADD COLUMN initial_investment DOUBLE PRECISION;

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,

  t212_order_id BIGINT NOT NULL,
  ticker VARCHAR NOT NULL,
  instrument_isin VARCHAR,
  instrument_name VARCHAR,
  instrument_currency VARCHAR,

  side VARCHAR NOT NULL CHECK (side IN ('BUY', 'SELL')),
  quantity DOUBLE PRECISION NOT NULL,
  filled_quantity DOUBLE PRECISION DEFAULT 0,

  type VARCHAR NOT NULL CHECK (type IN ('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')),
  status VARCHAR NOT NULL CHECK (status IN ('NEW', 'CONFIRMED', 'FILLED', 'PARTIALLY_FILLED', 'CANCELLED', 'REJECTED', 'UNCONFIRMED')),

  created_at TIMESTAMP WITH TIME ZONE NOT NULL,

  limit_price DOUBLE PRECISION,
  stop_price DOUBLE PRECISION,

  time_in_force VARCHAR CHECK (time_in_force IN ('DAY', 'GOOD_TILL_CANCEL')),
  initiated_from VARCHAR,

  automation_status CHAR(1) DEFAULT 'W' CHECK (automation_status IN ('W', 'E', 'C')),

  related_order_id UUID REFERENCES orders(id) ON DELETE SET NULL,

  synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_orders_isin_id ON orders(isin_id);
CREATE INDEX idx_orders_t212_order_id ON orders(t212_order_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_side ON orders(side);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_automation_status ON orders(automation_status);
CREATE INDEX idx_orders_related_order_id ON orders(related_order_id);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own orders" ON orders
  FOR SELECT USING (isin_id IN (SELECT id FROM isins));
CREATE POLICY "Users can insert their own orders" ON orders
  FOR INSERT WITH CHECK (isin_id IN (SELECT id FROM isins));
CREATE POLICY "Users can update their own orders" ON orders
  FOR UPDATE USING (isin_id IN (SELECT id FROM isins));

ALTER TABLE orders ADD CONSTRAINT different_order_check
  CHECK (id != related_order_id);

COMMENT ON TABLE orders IS 'Rastreia todas as ordens colocadas via Trading 212 API. Campos sincronizados da API, com rastreamento local de automação.';
COMMENT ON COLUMN orders.automation_status IS 'W=Watch (pendente), E=Executed (executada), C=Canceled (cancelada)';
COMMENT ON COLUMN orders.related_order_id IS 'Aponta para a ordem relacionada (BUY↔SELL pair). Sempre 1 BUY e 1 SELL.';
COMMENT ON COLUMN orders.t212_order_id IS 'ID único da ordem na plataforma Trading 212 (BIGINT da API)';

COMMENT ON TABLE isins IS 'Instrumentos financeiros. Campos api_created_at, current_price, quantity, etc. sincronizados da API T212.';
COMMENT ON COLUMN isins.api_created_at IS 'Timestamp da criação da posição na API T212 (separado do created_at local)';
COMMENT ON COLUMN isins.wi_current_value IS 'Wallet Impact: Valor de mercado atual (moeda da conta)';

COMMENT ON TABLE strategies IS 'Estratégias de trading. Campo initial_investment rastreia capital inicial da estratégia.';
COMMENT ON COLUMN strategies.initial_investment IS 'Valor em EUR que o utilizador investiu nesta estratégia';


-- =====================================================================
-- SECTION 5: app_parameters (singleton system config table)
-- =====================================================================
-- Note: created here already WITHOUT scheduler_enabled / max_positions_per_isin
-- / log_level (DEMO added then dropped log_level here too, later re-added it
-- via app_parameters_table.sql's own log_level column, then dropped it again
-- via remove_unused_app_parameters_columns.sql — net effect on DEMO today is
-- NO log_level column, so we simply never create it here).

CREATE TABLE app_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scheduler_interval_seconds INTEGER DEFAULT 15 CHECK (scheduler_interval_seconds >= 5),
  grid_trading_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_app_parameters_singleton ON app_parameters((1));

INSERT INTO app_parameters (scheduler_interval_seconds)
VALUES (15)
ON CONFLICT DO NOTHING;

ALTER TABLE app_parameters ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE app_parameters IS 'System-wide configuration parameters. Single row table for global settings.';
COMMENT ON COLUMN app_parameters.scheduler_interval_seconds IS 'How often the automation engine runs (seconds). Minimum 5s. Default 15s.';
COMMENT ON COLUMN app_parameters.grid_trading_enabled IS 'Enable/disable grid trading strategy globally.';


-- =====================================================================
-- SECTION 6: additional isins fields (position_created_at, quantity_precision)
-- =====================================================================

ALTER TABLE isins ADD COLUMN IF NOT EXISTS position_created_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE isins ADD COLUMN quantity_precision INTEGER DEFAULT 3;
COMMENT ON COLUMN isins.quantity_precision IS 'Number of decimal places T212 accepts for this ISIN quantity. Default 3. Updated when API returns precision error.';
UPDATE isins SET quantity_precision = 3 WHERE quantity_precision IS NULL;
ALTER TABLE isins ALTER COLUMN quantity_precision SET NOT NULL;


-- =====================================================================
-- SECTION 7: LOGIN SECURITY (Item #12) — MFA, login attempts, trusted
-- devices, revocable sessions
-- =====================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_address VARCHAR NOT NULL,
  email VARCHAR,
  success BOOLEAN NOT NULL,
  stage VARCHAR NOT NULL DEFAULT 'password' CHECK (stage IN ('password', 'mfa')),
  user_agent VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_created ON login_attempts(ip_address, created_at DESC);

CREATE TABLE IF NOT EXISTS trusted_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_token VARCHAR NOT NULL UNIQUE,
  user_agent VARCHAR,
  ip_address VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trusted_devices_token ON trusted_devices(device_token);
CREATE INDEX IF NOT EXISTS idx_trusted_devices_user ON trusted_devices(user_id);

CREATE TABLE IF NOT EXISTS active_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  jti VARCHAR NOT NULL UNIQUE,
  ip_address VARCHAR,
  user_agent VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_active_sessions_jti ON active_sessions(jti);
CREATE INDEX IF NOT EXISTS idx_active_sessions_user ON active_sessions(user_id);


-- =====================================================================
-- SECTION 8: TRADING LIMITS + ALERTS (Item #15, Phase 1)
-- =====================================================================

ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_buy_order_value DECIMAL;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_sell_order_value DECIMAL;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_daily_spend DECIMAL;

ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS automation_disabled_reason VARCHAR;

ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS alert_settings JSONB DEFAULT '{
  "login_threshold": true,
  "security_events": true,
  "limit_reached": true,
  "order_rejected": true,
  "invalid_credentials": true,
  "cycle_errors": true,
  "deploy_disabled": true
}'::jsonb;

ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS last_deployed_commit VARCHAR;

ALTER TABLE orders ADD COLUMN IF NOT EXISTS fill_net_value DOUBLE PRECISION;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS fill_realised_pnl DOUBLE PRECISION;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS filled_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_orders_filled_at ON orders(filled_at) WHERE status = 'FILLED';

-- =====================================================================
-- SECTION 8b: PROD GO-LIVE SAFETY DEFAULTS
-- =====================================================================
-- Gradual go-live per Item #15 decisions: automation starts OFF, and
-- trading limits start LOW (raise gradually once confidence builds).
-- Adjust the €10 values below before/after running if you want a
-- different starting limit — this is intentionally conservative.

UPDATE app_parameters
SET
  grid_trading_enabled = FALSE,
  max_buy_order_value = 10,
  max_sell_order_value = 10,
  max_daily_spend = 20;


-- =====================================================================
-- SECTION 9: REPORTS FEATURE (Activity Statement PDF import) — OPTIONAL
-- =====================================================================
-- Only needed if you want the Reports/Activity-Statement-upload feature
-- available in PROD too. Comment out this whole section if not.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE imported_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name       VARCHAR NOT NULL,
    file_hash       VARCHAR,
    customer_id     VARCHAR,
    customer_name   VARCHAR,
    period_start    DATE,
    period_end      DATE,
    generated_at    TIMESTAMPTZ,
    pages           INTEGER,
    status          VARCHAR DEFAULT 'PENDING',
    imported_at     TIMESTAMPTZ DEFAULT now(),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX idx_imported_files_hash ON imported_files (file_hash);

CREATE TABLE invest_executed_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    execution_time      TIMESTAMPTZ,
    instrument          VARCHAR,
    isin                VARCHAR,
    order_id            VARCHAR,
    direction           VARCHAR,
    quantity            NUMERIC,
    execution_price     NUMERIC,
    value               NUMERIC,
    order_type          VARCHAR,
    execution_venue     VARCHAR,
    session             VARCHAR,
    fx_rate             NUMERIC,
    fx_fee              NUMERIC,
    exchange_govt_fees  NUMERIC,
    return_amount       NUMERIC,
    return_value        NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_exec_file    ON invest_executed_trades (file_id);
CREATE INDEX idx_invest_exec_isin    ON invest_executed_trades (isin);
CREATE INDEX idx_invest_exec_time    ON invest_executed_trades (execution_time);

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

CREATE TABLE invest_open_positions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    instrument          VARCHAR,
    isin                VARCHAR,
    quantity            NUMERIC,
    average_price       NUMERIC,
    price               NUMERIC,
    return_amount       NUMERIC,
    value               NUMERIC,
    fx_rate             NUMERIC,
    return_converted    NUMERIC,
    value_converted     NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_open_file    ON invest_open_positions (file_id);
CREATE INDEX idx_invest_open_isin    ON invest_open_positions (isin);

CREATE TABLE invest_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    time                TIMESTAMPTZ,
    type                VARCHAR,
    amount              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_tx_file      ON invest_transactions (file_id);
CREATE INDEX idx_invest_tx_time      ON invest_transactions (time);

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
    net_amount          NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_invest_div_file     ON invest_dividends (file_id);

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
    period_price_change VARCHAR,
    margin              NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_open_file       ON cfd_open_positions (file_id);

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
    net_amount_converted NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_divadj_file     ON cfd_dividend_adjustments (file_id);

CREATE TABLE cfd_overnight_interest (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id                 UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    transaction_time        TIMESTAMPTZ,
    instrument              VARCHAR,
    direction               VARCHAR,
    position_size           NUMERIC,
    overnight_interest_rate NUMERIC,
    amount                  NUMERIC,
    fx_rate                 NUMERIC,
    amount_converted        NUMERIC,
    created_at              TIMESTAMPTZ DEFAULT now(),
    updated_at              TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cfd_overnight_file  ON cfd_overnight_interest (file_id);
CREATE INDEX idx_cfd_overnight_time  ON cfd_overnight_interest (transaction_time);

CREATE TABLE crypto_executed_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    execution_time      TIMESTAMPTZ,
    symbol              VARCHAR,
    asset               VARCHAR,
    order_id            VARCHAR,
    fill_id             VARCHAR,
    direction           VARCHAR,
    quantity            NUMERIC,
    execution_price     NUMERIC,
    value               NUMERIC,
    realised_pl         NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_exec_file    ON crypto_executed_trades (file_id);
CREATE INDEX idx_crypto_exec_symbol  ON crypto_executed_trades (symbol);
CREATE INDEX idx_crypto_exec_time    ON crypto_executed_trades (execution_time);

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

CREATE TABLE crypto_open_positions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id             UUID REFERENCES imported_files(id) ON DELETE CASCADE,
    symbol              VARCHAR,
    asset               VARCHAR,
    quantity            NUMERIC,
    opening_price       NUMERIC,
    price               NUMERIC,
    unrealised_pl       NUMERIC,
    value               NUMERIC,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_crypto_open_file    ON crypto_open_positions (file_id);
CREATE INDEX idx_crypto_open_symbol  ON crypto_open_positions (symbol);

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
-- DONE! Verification queries (run manually after):
-- =====================================================================
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'app_parameters' ORDER BY ordinal_position;
-- SELECT * FROM app_parameters;  -- confirm grid_trading_enabled = false, limits = 10/10/20
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'isins' ORDER BY column_name;
--
-- Next steps (outside SQL):
-- 1. Create the real PROD user via Supabase dashboard -> Authentication -> Add user
-- 2. Copy SUPABASE_URL, SUPABASE_KEY (Secret key, NOT Publishable/Anon!), SUPABASE_JWT_SECRET
--    from Settings -> API into the trading212-backend-prod Render env vars
-- =====================================================================
