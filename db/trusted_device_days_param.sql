-- =====================================================
-- TRADING 212 BOT - TRUSTED DEVICE DAYS (Item #27)
-- =====================================================
-- Moves TRUSTED_DEVICE_DAYS from a fixed env var (settings.py) to a
-- per-environment configurable parameter in app_parameters, editable
-- from ConfigPage (Security section), consistent with other Item #15
-- parameters (trading limits, alert_settings, mo_* thresholds).
--
-- Run manually in Supabase SQL Editor — DEMO and PROD independently,
-- per this project's "SQL first, code after" convention (see Item #18).
-- Date: 2026-10-08

ALTER TABLE app_parameters ADD COLUMN IF NOT EXISTS trusted_device_days INTEGER DEFAULT 7;

-- Backfill existing row(s) with the previous env-var default (7, per user
-- decision during Item #27 scoping — more conservative than the original
-- 30-day suggestion in Item #12, since PROD involves real money).
UPDATE app_parameters SET trusted_device_days = 7 WHERE trusted_device_days IS NULL;

-- NOTES
-- - Valid range enforced at the API layer (0-90, same bounds as the old
--   settings.py field_validator): 0 = always require MFA (never trust a
--   device), clamped server-side on write.
-- - settings.TRUSTED_DEVICE_DAYS (backend/config/settings.py) is kept only
--   as the fallback default used if this column is read before the
--   migration runs in a given environment (fail-safe, not fail-open on
--   security: falls back to the old conservative value, never to 0/off).
