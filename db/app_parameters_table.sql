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

  -- Grid trading configuration
  grid_trading_enabled BOOLEAN DEFAULT TRUE,

  -- Logging configuration
  log_level VARCHAR DEFAULT 'OFF' CHECK (log_level IN ('OFF', 'LOW', 'MEDIUM', 'HIGH')),

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Only one row should exist (enforced at app level)
CREATE UNIQUE INDEX idx_app_parameters_singleton ON app_parameters((1));

-- Insert default row
INSERT INTO app_parameters (scheduler_interval_seconds)
VALUES (15)
ON CONFLICT DO NOTHING;

-- RLS (optional, single-user mode)
ALTER TABLE app_parameters ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE app_parameters IS 'System-wide configuration parameters. Single row table for global settings.';
COMMENT ON COLUMN app_parameters.scheduler_interval_seconds IS 'How often the automation engine runs (seconds). Minimum 5s. Default 15s.';
COMMENT ON COLUMN app_parameters.grid_trading_enabled IS 'Enable/disable grid trading strategy globally.';
COMMENT ON COLUMN app_parameters.log_level IS 'Logging verbosity level. OFF=no logging, LOW=minimal, MEDIUM=detailed DB/API logs, HIGH=reserved for future.';

-- =====================================================
-- DONE!
-- =====================================================
