-- =====================================================
-- TRADING 212 BOT - TRADING LIMITS + ALERTS (Item #15, Phase 1)
-- =====================================================
-- Run this in Supabase (SQL Editor) BEFORE deploying the new backend code.
-- Date: 2026-09-24

-- =====================================================
-- 1. APP_PARAMETERS: trading limits, disable reason, alert toggles, deploy tracking
-- =====================================================

-- NULL = no limit configured (never blocks). Values in EUR.
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_buy_order_value DECIMAL;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_sell_order_value DECIMAL;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS max_daily_spend DECIMAL;

-- Set by the engine/startup when automation is auto-disabled (limit hit, new
-- deploy). Cleared when the user manually re-enables via PUT /enable.
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS automation_disabled_reason VARCHAR;

-- Per-alert on/off toggles. Missing keys default to enabled (see
-- backend/services/alert_service.py DEFAULT_ALERT_SETTINGS).
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS alert_settings JSONB DEFAULT '{
  "login_threshold": true,
  "security_events": true,
  "limit_reached": true,
  "order_rejected": true,
  "invalid_credentials": true,
  "cycle_errors": true,
  "deploy_disabled": true
}'::jsonb;

-- Tracks the RENDER_GIT_COMMIT seen on the last startup, to detect a new
-- deploy and auto-disable automation (see backend/main.py lifespan).
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS last_deployed_commit VARCHAR;

-- =====================================================
-- 2. ORDERS: fill data needed for the daily spend calculation
-- =====================================================
-- Captured from T212's GET /equity/history/orders `fill` object when an
-- order is found FILLED (walletImpact.netValue / .realisedProfitLoss).

ALTER TABLE orders ADD COLUMN IF NOT EXISTS fill_net_value DOUBLE PRECISION;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS fill_realised_pnl DOUBLE PRECISION;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS filled_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_orders_filled_at ON orders(filled_at) WHERE status = 'FILLED';

-- =====================================================
-- NOTES
-- =====================================================
-- - max_buy_order_value / max_sell_order_value: checked before EACH order
--   placement (AutomationEngine._place_order_with_precision_retry).
-- - max_daily_spend: checked before each order placement too, using the
--   SUM of already-FILLED orders today (Europe/Lisbon) — can be exceeded
--   by orders that fill in a batch between checks (accepted risk, per
--   brainstorming decision).
-- - Hitting any limit sets grid_trading_enabled=FALSE (whole automation
--   stops) + automation_disabled_reason + a "limit_reached" alert.
--   Pending T212 orders are left untouched; resume is manual only.
