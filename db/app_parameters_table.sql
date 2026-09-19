-- =====================================================
-- TRADING 212 BOT - GENERAL PARAMETERS TABLE
-- =====================================================
-- Table for system-wide parameters (scheduler interval, etc)
-- Date: 2026-09-20

-- =====================================================
-- 1. CREATE TABLE: app_parameters
-- =====================================================

CREATE TABLE app_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Scheduler configuration
  scheduler_interval_seconds INTEGER DEFAULT 15 CHECK (scheduler_interval_seconds >= 5),
  scheduler_enabled BOOLEAN DEFAULT TRUE,

  -- Grid trading configuration (future use)
  grid_trading_enabled BOOLEAN DEFAULT TRUE,
  max_positions_per_isin INTEGER DEFAULT 5,

  -- Logging and monitoring
  log_level VARCHAR DEFAULT 'INFO' CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR')),

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Only one row should exist (enforced at app level)
CREATE UNIQUE INDEX idx_app_parameters_singleton ON app_parameters((1));

-- Insert default row
INSERT INTO app_parameters (scheduler_interval_seconds, scheduler_enabled)
VALUES (15, TRUE)
ON CONFLICT DO NOTHING;

-- RLS (optional, single-user mode)
ALTER TABLE app_parameters ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE app_parameters IS 'System-wide configuration parameters. Single row table for global settings.';
COMMENT ON COLUMN app_parameters.scheduler_interval_seconds IS 'How often the automation engine runs (seconds). Minimum 5s. Default 15s.';
COMMENT ON COLUMN app_parameters.scheduler_enabled IS 'Enable/disable the automation scheduler globally.';
COMMENT ON COLUMN app_parameters.grid_trading_enabled IS 'Enable/disable grid trading strategy globally.';

-- =====================================================
-- DONE!
-- =====================================================
