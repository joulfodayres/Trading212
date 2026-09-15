-- =====================================================
-- CRIAR UTILIZADOR DE TESTE EM SUPABASE
-- =====================================================

-- Inserir user de teste
INSERT INTO users (id, email, is_admin, created_at)
VALUES (
  'ab1036ff-937d-46e5-8f5b-bab07f1fb100'::uuid,
  'teste@trading212.com',
  true,
  NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Verificar se foi criado
SELECT id, email, is_admin, created_at FROM users WHERE email = 'teste@trading212.com';

-- =====================================================
-- CRIAR CONFIG DE TESTE (API T212 DEMO)
-- =====================================================

INSERT INTO config (
  id,
  user_id,
  t212_api_key_encrypted,
  t212_api_secret_encrypted,
  t212_environment,
  strategy_params,
  updated_at
)
VALUES (
  gen_random_uuid(),
  'ab1036ff-937d-46e5-8f5b-bab07f1fb100'::uuid,
  'demo_key_encrypted',
  'demo_secret_encrypted',
  'demo',
  '{"buy_threshold": 1.0, "sell_threshold": 1.0}',
  NOW()
)
ON CONFLICT (user_id) DO NOTHING;

-- Verificar config
SELECT user_id, t212_environment FROM config WHERE user_id = 'ab1036ff-937d-46e5-8f5b-bab07f1fb100'::uuid;
