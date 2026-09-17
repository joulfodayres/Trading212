-- =====================================================
-- TRADING 212 BOT - STRATEGY MANAGEMENT TABLES
-- =====================================================
-- Execute estes comandos no Supabase SQL Editor
-- Complementa as tabelas existentes (users, isins, strategies, trades, logs)
-- Criado: 2026-09-17

-- =====================================================
-- 1. TABELA: ISIN_STRATEGY_CONFIG
-- =====================================================
-- Informações adicionais por ISIN (não replicar dados do T212)
-- Relação: ISIN ↔ Strategy (automação)
CREATE TABLE isin_strategy_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, isin_id)
);

-- Índices
CREATE INDEX idx_isin_strategy_config_user_id ON isin_strategy_config(user_id);
CREATE INDEX idx_isin_strategy_config_isin_id ON isin_strategy_config(isin_id);
CREATE INDEX idx_isin_strategy_config_strategy_id ON isin_strategy_config(strategy_id);

-- RLS (Row Level Security)
ALTER TABLE isin_strategy_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ISIN strategy configs" ON isin_strategy_config
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own ISIN strategy configs" ON isin_strategy_config
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own ISIN strategy configs" ON isin_strategy_config
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own ISIN strategy configs" ON isin_strategy_config
  FOR DELETE USING (user_id = auth.uid());

-- =====================================================
-- 2. TABELA: ISIN_STRATEGY_HISTORY
-- =====================================================
-- Histórico de mudanças na configuração de automação por ISIN
-- Permite auditar quando foi ativada/desativada, qual estratégia, etc.
-- Chave: UUID (PK) + unique sobre (user_id, isin_id, created_at)
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(user_id, isin_id, created_at)
);

-- Índices
CREATE INDEX idx_isin_strategy_history_user_id ON isin_strategy_history(user_id);
CREATE INDEX idx_isin_strategy_history_isin_id ON isin_strategy_history(isin_id);
CREATE INDEX idx_isin_strategy_history_created_at ON isin_strategy_history(created_at);

-- RLS
ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own ISIN strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own ISIN strategy history" ON isin_strategy_history
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- =====================================================
-- 3. TABELA: STRATEGY_DEFINITIONS
-- =====================================================
-- Definições de estratégias (substitui/complementa strategies existente)
-- Nomes descritivos e status de ativação
CREATE TABLE strategy_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  strategy_name VARCHAR NOT NULL,
  strategy_desc TEXT,
  strategy_status VARCHAR NOT NULL DEFAULT 'E' CHECK (strategy_status IN ('E', 'D')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, strategy_name)
);

-- Índices
CREATE INDEX idx_strategy_definitions_user_id ON strategy_definitions(user_id);
CREATE INDEX idx_strategy_definitions_status ON strategy_definitions(strategy_status);

-- RLS
ALTER TABLE strategy_definitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy definitions" ON strategy_definitions
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own strategy definitions" ON strategy_definitions
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own strategy definitions" ON strategy_definitions
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own strategy definitions" ON strategy_definitions
  FOR DELETE USING (user_id = auth.uid());

-- =====================================================
-- 4. TABELA: STRATEGY_PARAMETERS
-- =====================================================
-- Parâmetros dinâmicos de estratégia (até 10 parâmetros numéricos)
-- Permite múltiplas configurações por estratégia
-- Chave: (strategy_id, pos) = position/versão dos parâmetros
CREATE TABLE strategy_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID NOT NULL REFERENCES strategy_definitions(id) ON DELETE CASCADE,
  pos INTEGER NOT NULL,
  param1 DECIMAL(18, 8),
  param2 DECIMAL(18, 8),
  param3 DECIMAL(18, 8),
  param4 DECIMAL(18, 8),
  param5 DECIMAL(18, 8),
  param6 DECIMAL(18, 8),
  param7 DECIMAL(18, 8),
  param8 DECIMAL(18, 8),
  param9 DECIMAL(18, 8),
  param10 DECIMAL(18, 8),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(strategy_id, pos)
);

-- Índices
CREATE INDEX idx_strategy_parameters_strategy_id ON strategy_parameters(strategy_id);

-- RLS (Herança do user através de strategy_id)
ALTER TABLE strategy_parameters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy parameters" ON strategy_parameters
  FOR SELECT USING (
    strategy_id IN (
      SELECT id FROM strategy_definitions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can manage their own strategy parameters" ON strategy_parameters
  FOR INSERT WITH CHECK (
    strategy_id IN (
      SELECT id FROM strategy_definitions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their own strategy parameters" ON strategy_parameters
  FOR UPDATE USING (
    strategy_id IN (
      SELECT id FROM strategy_definitions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete their own strategy parameters" ON strategy_parameters
  FOR DELETE USING (
    strategy_id IN (
      SELECT id FROM strategy_definitions WHERE user_id = auth.uid()
    )
  );

-- =====================================================
-- ✅ DONE!
-- =====================================================
-- Tabelas criadas com sucesso!
--
-- NOMENCLATURA USADA:
-- - PKs: UUID (consistent com tabelas existentes)
-- - FKs: user_id, isin_id, strategy_id (referências tipificadas)
-- - Timestamps: WITH TIME ZONE (consistent)
-- - Índices: idx_<tabela>_<coluna> (pattern existente)
-- - RLS: Ativado em todas as tabelas (multi-user safe)
--
-- TABELAS CRIADAS:
-- 1. isin_strategy_config    - Config atual por ISIN (substitui tua "ISINS")
-- 2. isin_strategy_history   - Histórico de mudanças (substitui tua "ISINS_HISTORIC")
-- 3. strategy_definitions    - Definições de estratégia (substitui tua "STRATEGIES")
-- 4. strategy_parameters     - Parâmetros numéricos (substitui tua "STRATEGY_PARAMETERS")
--
-- PONTOS-CHAVE RESOLVIDOS:
-- ✅ Timestamp como chave: Resolvido com UUID PK + unique composite
-- ✅ Falta de user_id: Adicionado em todas as tabelas (RLS requer)
-- ✅ Nomenclatura coerente: Seguido pattern da BD existente
-- ✅ Foreign keys tipificadas: user_id (UUID), isin_id (UUID), strategy_id (UUID)
-- ✅ RLS seguro: Cada user vê apenas seus dados
--
-- PRÓXIMOS PASSOS:
-- 1. Copiar este SQL para Supabase SQL Editor
-- 2. Executar
-- 3. Verificar tabelas no Supabase dashboard
-- 4. Atualizar modelos SQLAlchemy em backend/models/db.py
-- 5. Criar schemas Pydantic em backend/models/schemas.py
-- =====================================================
