-- =====================================================
-- TRADING 212 BOT - PHASE 4 SCHEMA CHANGES
-- =====================================================
-- Execute estes comandos no Supabase SQL Editor
-- Data: 2026-09-19
-- Objetivo: Preparar BD para Phase 4 (Grid Trading Automation)

-- =====================================================
-- 1. ALTER TABLE: ISINS (Adicionar campos da API)
-- =====================================================

-- Adicionar coluna para registar created_at da API (separado do created_at local)
ALTER TABLE isins ADD COLUMN api_created_at TIMESTAMP WITH TIME ZONE;

-- Campos de posição (vêm da API T212)
ALTER TABLE isins ADD COLUMN initial_trade BOOLEAN DEFAULT FALSE;
ALTER TABLE isins ADD COLUMN trades_balance INTEGER DEFAULT 0;
ALTER TABLE isins ADD COLUMN average_price_paid DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN current_price DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN quantity DOUBLE PRECISION DEFAULT 0;
ALTER TABLE isins ADD COLUMN quantity_available_for_trading DOUBLE PRECISION DEFAULT 0;
ALTER TABLE isins ADD COLUMN quantity_in_pies DOUBLE PRECISION DEFAULT 0;

-- Campos de wallet impact (calculados pela API)
ALTER TABLE isins ADD COLUMN wi_currency VARCHAR;
ALTER TABLE isins ADD COLUMN wi_current_value DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_fx_impact DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_total_cost DOUBLE PRECISION;
ALTER TABLE isins ADD COLUMN wi_unrealized_profit_loss DOUBLE PRECISION;

-- =====================================================
-- 2. ALTER TABLE: STRATEGIES (Adicionar initial_investment)
-- =====================================================

ALTER TABLE strategies ADD COLUMN initial_investment DOUBLE PRECISION;

-- =====================================================
-- 3. CREATE TABLE: ORDERS (Nova tabela para rastrear ordens T212)
-- =====================================================

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,

  -- Campos da API T212 (Order object)
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

  -- Coluna de automação
  automation_status CHAR(1) DEFAULT 'W' CHECK (automation_status IN ('W', 'E', 'C')),

  -- Relacionamento com outra ordem (BUY ↔ SELL)
  related_order_id UUID REFERENCES orders(id) ON DELETE SET NULL,

  -- Rastreamento local
  synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_orders_isin_id ON orders(isin_id);
CREATE INDEX idx_orders_t212_order_id ON orders(t212_order_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_side ON orders(side);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_automation_status ON orders(automation_status);
CREATE INDEX idx_orders_related_order_id ON orders(related_order_id);

-- RLS (Row Level Security) - através de isin_id
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Os utilizadores podem ver as suas próprias ordens (via isin_id → user_id da isins)
-- Nota: Em single-user mode, este é redundante mas mantém a estrutura
CREATE POLICY "Users can view their own orders" ON orders
  FOR SELECT USING (
    isin_id IN (SELECT id FROM isins)
  );

CREATE POLICY "Users can insert their own orders" ON orders
  FOR INSERT WITH CHECK (
    isin_id IN (SELECT id FROM isins)
  );

CREATE POLICY "Users can update their own orders" ON orders
  FOR UPDATE USING (
    isin_id IN (SELECT id FROM isins)
  );

-- =====================================================
-- 4. CONSTRAINTS & VALIDATIONS
-- =====================================================

-- Validar que related_order_id aponta para uma ordem diferente
ALTER TABLE orders ADD CONSTRAINT different_order_check
  CHECK (id != related_order_id);

-- Validar que related_order_id tem side oposto (BUY ↔ SELL)
-- Nota: Esta constraint é complexa em SQL puro, mantém-se em nível de aplicação

-- =====================================================
-- 5. COMENTÁRIOS (Para documentação do esquema)
-- =====================================================

COMMENT ON TABLE orders IS 'Rastreia todas as ordens colocadas via Trading 212 API. Campos sincronizados da API, com rastreamento local de automação.';
COMMENT ON COLUMN orders.automation_status IS 'W=Watch (pendente), E=Executed (executada), C=Canceled (cancelada)';
COMMENT ON COLUMN orders.related_order_id IS 'Aponta para a ordem relacionada (BUY↔SELL pair). Sempre 1 BUY e 1 SELL.';
COMMENT ON COLUMN orders.t212_order_id IS 'ID único da ordem na plataforma Trading 212 (BIGINT da API)';

COMMENT ON TABLE isins IS 'Instrumentos financeiros. Campos api_created_at, current_price, quantity, etc. sincronizados da API T212.';
COMMENT ON COLUMN isins.api_created_at IS 'Timestamp da criação da posição na API T212 (separado do created_at local)';
COMMENT ON COLUMN isins.wi_current_value IS 'Wallet Impact: Valor de mercado atual (moeda da conta)';

COMMENT ON TABLE strategies IS 'Estratégias de trading. Campo initial_investment rastreia capital inicial da estratégia.';
COMMENT ON COLUMN strategies.initial_investment IS 'Valor em EUR que o utilizador investiu nesta estratégia';

-- =====================================================
-- 6. DONE!
-- =====================================================
-- Status: Ready to sync Phase 4 data
-- Próximos passos:
-- 1. Executar este script no Supabase SQL Editor
-- 2. Atualizar backend/models/db.py (SQLAlchemy models)
-- 3. Atualizar backend/models/schemas.py (Pydantic schemas)
-- 4. Implementar OrderHistoryManager no backend
