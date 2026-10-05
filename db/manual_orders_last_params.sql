-- =====================================================
-- TRADING 212 BOT - MANUAL ORDER MANAGEMENT - LAST-USED PARAMS (Item #22/#24, NEW)
-- =====================================================
-- Run this in Supabase (SQL Editor) BEFORE deploying the new backend code.

ALTER TABLE isins ADD COLUMN IF NOT EXISTS last_manual_order_params JSONB;

-- Notes:
-- - Stores the full Sell+Buy parameter set (price interval, acc flags,
--   amount/quantity zone, step/multiplier, number of orders) from the
--   last SUCCESSFUL "GERAR" (generate) action for this ISIN on the
--   "Gerir Ordens" screen. One row per ISIN, always overwritten — no
--   history is kept.
-- - Used to pre-fill the Sell/Buy parameter form next time the screen is
--   opened for this ISIN. The user must still click "GERAR" manually;
--   this does not auto-generate New Orders on page load.
-- - initial_price is intentionally NEVER restored from this saved JSON —
--   the form always defaults initial_price to the ISIN's current market
--   price at screen-load time, regardless of what was saved, since the
--   saved value was relative to market conditions that have likely moved
--   since (restoring it verbatim risks immediately tripping the Price Max
--   Variation hard block on reopen). See backend/routes/manual_orders.py.
