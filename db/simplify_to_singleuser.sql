-- =====================================================
-- TRADING 212 BOT - SIMPLIFY TO SINGLE-USER
-- =====================================================
-- Remove user_id from all tables (except users, auth.users)
-- Disable RLS policies
-- Simplify to single-user application
-- Date: 2026-09-17

-- =====================================================
-- 1. DROP RLS POLICIES (all tables)
-- =====================================================

-- config
DROP POLICY IF EXISTS "Users can view their own config" ON config;
DROP POLICY IF EXISTS "Users can insert their own config" ON config;
DROP POLICY IF EXISTS "Users can update their own config" ON config;

-- isins
DROP POLICY IF EXISTS "Users can view their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can insert their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can update their own ISINs" ON isins;
DROP POLICY IF EXISTS "Users can delete their own ISINs" ON isins;

-- isin_strategy_history
DROP POLICY IF EXISTS "Users can view their own ISIN strategy history" ON isin_strategy_history;
DROP POLICY IF EXISTS "Users can insert their own ISIN strategy history" ON isin_strategy_history;

-- strategies
DROP POLICY IF EXISTS "Can view strategies (own or public)" ON strategies;
DROP POLICY IF EXISTS "Can insert own strategies" ON strategies;
DROP POLICY IF EXISTS "Can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Can delete own strategies" ON strategies;

-- strategy_parameters
DROP POLICY IF EXISTS "Users can view their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can manage their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can update their own strategy parameters" ON strategy_parameters;
DROP POLICY IF EXISTS "Users can delete their own strategy parameters" ON strategy_parameters;

-- trades
DROP POLICY IF EXISTS "Users can view their own trades" ON trades;
DROP POLICY IF EXISTS "Users can insert their own trades" ON trades;

-- logs
DROP POLICY IF EXISTS "Users can view their own logs" ON logs;

-- =====================================================
-- 2. DISABLE ROW LEVEL SECURITY (all tables)
-- =====================================================

ALTER TABLE config DISABLE ROW LEVEL SECURITY;
ALTER TABLE isins DISABLE ROW LEVEL SECURITY;
ALTER TABLE isin_strategy_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE strategies DISABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_parameters DISABLE ROW LEVEL SECURITY;
ALTER TABLE trades DISABLE ROW LEVEL SECURITY;
ALTER TABLE logs DISABLE ROW LEVEL SECURITY;

-- =====================================================
-- 3. REMOVE user_id COLUMN & CONSTRAINTS
-- =====================================================

-- config: user_id is UNIQUE, need to handle FK first
ALTER TABLE config DROP CONSTRAINT IF EXISTS config_user_id_fkey;
ALTER TABLE config DROP CONSTRAINT IF EXISTS config_user_id_key;
ALTER TABLE config DROP COLUMN IF EXISTS user_id;

-- isins
ALTER TABLE isins DROP CONSTRAINT IF EXISTS isins_user_id_fkey;
ALTER TABLE isins DROP CONSTRAINT IF EXISTS isins_user_id_isin_key;
ALTER TABLE isins ADD CONSTRAINT isins_isin_key UNIQUE(isin);
ALTER TABLE isins DROP COLUMN IF EXISTS user_id;

-- isin_strategy_history
ALTER TABLE isin_strategy_history DROP CONSTRAINT IF EXISTS isin_strategy_history_user_id_fkey;
ALTER TABLE isin_strategy_history DROP CONSTRAINT IF EXISTS isin_strategy_history_user_id_isin_id_created_at_key;
ALTER TABLE isin_strategy_history ADD CONSTRAINT isin_strategy_history_isin_id_created_at_key UNIQUE(isin_id, created_at);
ALTER TABLE isin_strategy_history DROP COLUMN IF EXISTS user_id;

-- strategies
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS strategies_user_id_fkey;
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS strategies_user_id_strategy_name_key;
ALTER TABLE strategies ADD CONSTRAINT strategies_strategy_name_key UNIQUE(strategy_name);
ALTER TABLE strategies DROP COLUMN IF EXISTS user_id;

-- strategy_parameters: no user_id here, nothing to do

-- trades
ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_user_id_fkey;
ALTER TABLE trades DROP COLUMN IF EXISTS user_id;

-- logs
ALTER TABLE logs DROP CONSTRAINT IF EXISTS logs_user_id_fkey;
ALTER TABLE logs DROP COLUMN IF EXISTS user_id;

-- =====================================================
-- 4. CLEANUP INDEXES (remove user_id indexes)
-- =====================================================

DROP INDEX IF EXISTS idx_config_user_id;
DROP INDEX IF EXISTS idx_isins_user_id;
DROP INDEX IF EXISTS idx_isin_strategy_history_user_id;
DROP INDEX IF EXISTS idx_strategies_user_id;
DROP INDEX IF EXISTS idx_trades_user_id;
DROP INDEX IF EXISTS idx_logs_user_id;

-- =====================================================
-- 5. VERIFY CHANGES
-- =====================================================

-- Run these queries to verify:
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'config' AND column_name = 'user_id';
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'isins' AND column_name = 'user_id';
-- ... etc (should return 0 rows)

-- =====================================================
-- ✅ DONE!
-- =====================================================
-- All user_id columns removed
-- All RLS policies disabled
-- Application is now single-user
--
-- Next steps:
-- 1. Update backend code to remove user_id filters
-- 2. Remove get_current_user() calls (not needed)
-- 3. Simplify queries
-- 4. Test all endpoints
