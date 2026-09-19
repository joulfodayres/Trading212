-- =====================================================
-- TRADING 212 BOT - MOCK DATA FOR PHASE 4 TESTING
-- =====================================================
-- Test data for automation engine development
-- Date: 2026-09-20

-- =====================================================
-- 1. INSERT: Estratégia com parâmetros Grid Trading
-- =====================================================

INSERT INTO strategies (id, strategy_name, strategy_desc, strategy_status, initial_investment, created_at)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  'Grid Trading 1%',
  'Buy -1%, Sell +1% grid strategy',
  'E',
  1000.00,
  NOW()
);

-- =====================================================
-- 2. INSERT: Strategy Parameters para Grid Trading
-- =====================================================

-- Position 0 (starting level)
INSERT INTO strategy_parameters (id, strategy_id, pos, param1, param2, created_at)
VALUES (
  'a47ac10b-58cc-4372-a567-0e02b2c3d480',
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  '0',
  -1.0,    -- Buy at -1%
  1.0,     -- Sell at +1%
  NOW()
);

-- Position -1 (after first sell)
INSERT INTO strategy_parameters (id, strategy_id, pos, param1, param2, created_at)
VALUES (
  'b47ac10b-58cc-4372-a567-0e02b2c3d481',
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  '-1',
  -1.0,
  1.0,
  NOW()
);

-- Position 1 (after first buy)
INSERT INTO strategy_parameters (id, strategy_id, pos, param1, param2, created_at)
VALUES (
  'c47ac10b-58cc-4372-a567-0e02b2c3d482',
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  '1',
  -1.0,
  1.0,
  NOW()
);

-- =====================================================
-- 3. INSERT: ISINs para teste (with mock current prices)
-- =====================================================

-- ISIN 1: Apple (AAPL) - Ready for automation
INSERT INTO isins (
  id, isin, ticker, name, currency, automation_enabled,
  api_created_at, initial_trade, trades_balance,
  current_price, quantity, average_price_paid,
  quantity_available_for_trading, quantity_in_pies,
  wi_currency, wi_current_value, wi_total_cost,
  wi_unrealized_profit_loss, wi_fx_impact,
  strategy_id, created_at
)
VALUES (
  'd47ac10b-58cc-4372-a567-0e02b2c3d483',
  'US0378331005',
  'AAPL_US_EQ',
  'Apple Inc',
  'USD',
  TRUE,
  NOW() - INTERVAL '30 days',
  TRUE,  -- initial_trade = TRUE (ready for automation)
  0,     -- trades_balance = 0 (starting point)
  150.50,
  0,     -- No position yet
  0,
  0,
  0,
  'USD',
  0,
  0,
  0,
  0,
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',  -- Reference to strategy
  NOW()
);

-- ISIN 2: Microsoft (MSFT) - Another test case
INSERT INTO isins (
  id, isin, ticker, name, currency, automation_enabled,
  api_created_at, initial_trade, trades_balance,
  current_price, quantity, average_price_paid,
  quantity_available_for_trading, quantity_in_pies,
  wi_currency, wi_current_value, wi_total_cost,
  wi_unrealized_profit_loss, wi_fx_impact,
  strategy_id, created_at
)
VALUES (
  'e47ac10b-58cc-4372-a567-0e02b2c3d484',
  'US5949181045',
  'MSFT_US_EQ',
  'Microsoft Corp',
  'USD',
  TRUE,
  NOW() - INTERVAL '30 days',
  TRUE,  -- initial_trade = TRUE
  0,     -- trades_balance = 0
  380.25,
  0,
  0,
  0,
  0,
  'USD',
  0,
  0,
  0,
  0,
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  NOW()
);

-- ISIN 3: Tesla (TSLA) - Disabled (should NOT trigger automation)
INSERT INTO isins (
  id, isin, ticker, name, currency, automation_enabled,
  api_created_at, initial_trade, trades_balance,
  current_price, quantity, average_price_paid,
  quantity_available_for_trading, quantity_in_pies,
  wi_currency, wi_current_value, wi_total_cost,
  wi_unrealized_profit_loss, wi_fx_impact,
  strategy_id, created_at
)
VALUES (
  'f47ac10b-58cc-4372-a567-0e02b2c3d485',
  'US88160R1014',
  'TSLA_US_EQ',
  'Tesla Inc',
  'USD',
  FALSE,  -- automation_enabled = FALSE (should be skipped)
  NOW() - INTERVAL '30 days',
  TRUE,   -- initial_trade = TRUE
  0,
  250.75,
  0,
  0,
  0,
  0,
  'USD',
  0,
  0,
  0,
  0,
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  NOW()
);

-- =====================================================
-- 4. VERIFY: Check what we just inserted
-- =====================================================

-- View strategies
SELECT 'Strategies' as section, id, strategy_name, initial_investment FROM strategies;

-- View strategy parameters
SELECT 'Parameters' as section, strategy_id, pos, param1, param2 FROM strategy_parameters;

-- View ISINs ready for automation
SELECT 'ISINs Ready' as section, id, ticker, name, initial_trade, automation_enabled, current_price, trades_balance
FROM isins
WHERE initial_trade = TRUE AND automation_enabled = TRUE;

-- View disabled ISINs (should not trigger)
SELECT 'ISINs Disabled' as section, id, ticker, name, initial_trade, automation_enabled
FROM isins
WHERE automation_enabled = FALSE;

-- =====================================================
-- Notes for Testing
-- =====================================================
/*
MOCK DATA STRUCTURE:

Strategy: "Grid Trading 1%"
├─ initial_investment: €1000
├─ Parameters: Buy at -1%, Sell at +1%
│
└─ ISINs:
   ├─ AAPL (initial_trade=TRUE, automation_enabled=TRUE) ✅ WILL RUN
   ├─ MSFT (initial_trade=TRUE, automation_enabled=TRUE) ✅ WILL RUN
   └─ TSLA (initial_trade=TRUE, automation_enabled=FALSE) ❌ SKIPPED

When automation_engine.run_cycle() is called:
1. SELECT isins WHERE initial_trade=TRUE AND automation_enabled=TRUE
   → Returns: AAPL, MSFT (not TSLA)

2. For each ISIN:
   - Load strategy (Grid Trading 1%)
   - Load parameters (pos=0, param1=-1%, param2=1%)
   - Calculate:
     * BUY price: current_price * (1 + (-1)/100) = 0.99 * current_price
     * SELL price: current_price * (1 + 1/100) = 1.01 * current_price
     * Quantity: initial_investment / limitPrice

3. Place orders on T212 API
4. Save to orders table with related_order_id linking
5. Set initial_trade=FALSE

Expected first cycle:
├─ AAPL:
│  ├─ BUY @ 148.995 (AAPL 150.50 * 0.99)
│  ├─ SELL @ 152.005 (AAPL 150.50 * 1.01)
│  └─ Qty: ~6.72 shares (1000 / 148.995)
│
└─ MSFT:
   ├─ BUY @ 376.6475 (MSFT 380.25 * 0.99)
   ├─ SELL @ 384.2525 (MSFT 380.25 * 1.01)
   └─ Qty: ~2.65 shares (1000 / 376.6475)
*/

-- =====================================================
-- DONE!
-- =====================================================
-- Status: Ready for Phase 4 testing
-- Next: Deploy automation engine code to Render
