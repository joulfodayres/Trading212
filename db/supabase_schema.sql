-- =====================================================
-- TRADING 212 BOT - SUPABASE SQL SETUP
-- =====================================================
-- Execute estes comandos no Supabase SQL Editor

-- =====================================================
-- 1. TABELA: USERS
-- =====================================================
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para email
CREATE INDEX idx_users_email ON users(email);

-- RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own data" ON users
  FOR SELECT USING (auth.uid()::text = id::text);

-- =====================================================
-- 2. TABELA: ISINS
-- =====================================================
CREATE TABLE isins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin VARCHAR NOT NULL,
  ticker VARCHAR,
  name VARCHAR,
  currency VARCHAR DEFAULT 'EUR',
  automation_enabled BOOLEAN DEFAULT FALSE,
  fields_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, isin)
);

-- Index
CREATE INDEX idx_isins_user_id ON isins(user_id);
CREATE INDEX idx_isins_isin ON isins(isin);

-- RLS
ALTER TABLE isins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ISINs" ON isins
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own ISINs" ON isins
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own ISINs" ON isins
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own ISINs" ON isins
  FOR DELETE USING (user_id = auth.uid());

-- =====================================================
-- 3. TABELA: CONFIG
-- =====================================================
CREATE TABLE config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  t212_api_key_encrypted VARCHAR,
  t212_api_secret_encrypted VARCHAR,
  t212_environment VARCHAR DEFAULT 'demo',
  strategy_params JSONB,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_config_user_id ON config(user_id);

-- RLS
ALTER TABLE config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own config" ON config
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own config" ON config
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own config" ON config
  FOR UPDATE USING (user_id = auth.uid());

-- =====================================================
-- 4. TABELA: STRATEGIES
-- =====================================================
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  type VARCHAR DEFAULT 'grid_trading',
  params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_strategies_user_id ON strategies(user_id);

-- RLS
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategies" ON strategies
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own strategies" ON strategies
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own strategies" ON strategies
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own strategies" ON strategies
  FOR DELETE USING (user_id = auth.uid());

-- =====================================================
-- 5. TABELA: TRADES
-- =====================================================
CREATE TABLE trades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID REFERENCES isins(id) ON DELETE SET NULL,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  tipo VARCHAR NOT NULL CHECK (tipo IN ('BUY', 'SELL')),
  quantidade DECIMAL(18, 8) NOT NULL,
  preco DECIMAL(18, 8) NOT NULL,
  comissao DECIMAL(18, 8) DEFAULT 0,
  status VARCHAR DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'FAILED')),
  t212_order_id VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  executed_at TIMESTAMP WITH TIME ZONE,
  detalhes_json JSONB
);

-- Index
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_isin_id ON trades(isin_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);

-- RLS
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own trades" ON trades
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own trades" ON trades
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- =====================================================
-- 6. TABELA: LOGS
-- =====================================================
CREATE TABLE logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  nivel VARCHAR DEFAULT 'INFO' CHECK (nivel IN ('INFO', 'WARNING', 'ERROR', 'DEBUG')),
  mensagem VARCHAR NOT NULL,
  detalhes_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_nivel ON logs(nivel);
CREATE INDEX idx_logs_created_at ON logs(created_at);

-- RLS
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own logs" ON logs
  FOR SELECT USING (user_id = auth.uid());

-- =====================================================
-- DONE!
-- =====================================================
-- Próximos passos:
-- 1. Copiar SUPABASE_URL e SUPABASE_KEY (Settings → API)
-- 2. Copiar JWT_SECRET (Settings → API → JWT Secret)
-- 3. Adicionar em Render environment variables
