-- =====================================================
-- DROP ORPHANED COLUMN: scheduler_enabled
-- =====================================================
-- Purpose: Remove unused scheduler_enabled column from app_parameters
-- Status: Never used in application logic
-- Date: 2026-09-21
--
-- This field was defined but never actually used to control anything.
-- Only grid_trading_enabled is used for automation control.

-- Step 1: Drop the orphaned column
ALTER TABLE app_parameters
DROP COLUMN IF EXISTS scheduler_enabled;

-- Step 2: Verify the table structure
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'app_parameters' ORDER BY ordinal_position;
-- Expected columns: id, scheduler_interval_seconds, grid_trading_enabled, created_at, updated_at

-- =====================================================
-- DONE!
-- =====================================================
