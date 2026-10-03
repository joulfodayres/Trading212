-- =====================================================
-- TRADING 212 BOT - MANUAL ORDER MANAGEMENT - VALIDATION PARAMS (Item #22, NEW)
-- =====================================================
-- Run this in Supabase (SQL Editor) BEFORE deploying the new backend code.
-- Independent per environment (DEMO / PROD each run this separately against
-- their own app_parameters row, same convention as Item #15's trading limits).

-- Price validation (vs current market price of the ISIN)
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_price_max_variation_pct DECIMAL DEFAULT 10;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_price_alert_variation_pct DECIMAL DEFAULT 1;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_price_max_interval_bp DECIMAL DEFAULT 100;

-- Amount validation (absolute ceilings, not variations)
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_amount_max DECIMAL DEFAULT 100;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_amount_max_interval_pct DECIMAL DEFAULT 10;

-- Quantity validation (absolute ceilings, not variations)
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_quantity_max DECIMAL DEFAULT 10;
ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS mo_quantity_max_interval_pct DECIMAL DEFAULT 10;

-- Notes:
-- - "mo_" prefix = "Manual Orders", to avoid collision with any future unrelated
--   params and to keep this feature's config grouped/greppable.
-- - These are NOT subject to the Item #15/#19 trading limits (max_buy_order_value,
--   max_sell_order_value, max_daily_spend) by deliberate product decision: this
--   is a manual, deliberate action path, not automation.
-- - Only mo_price_max_variation_pct is a hard block; the other 6 are soft
--   confirm-to-proceed alerts (see backend/services/manual_orders_service.py).
