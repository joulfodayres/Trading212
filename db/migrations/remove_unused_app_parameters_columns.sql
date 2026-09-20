-- Migration: Remove unused columns from app_parameters table
-- Date: 2026-09-20
-- Reason: max_positions_per_isin and log_level are not used in code
-- Status: Run this in Supabase SQL Editor

-- Step 1: Drop the unused columns
ALTER TABLE app_parameters
DROP COLUMN IF EXISTS max_positions_per_isin,
DROP COLUMN IF EXISTS log_level;

-- Verify the table structure (should only have: id, scheduler_interval_seconds, scheduler_enabled, grid_trading_enabled, created_at, updated_at)
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'app_parameters';
