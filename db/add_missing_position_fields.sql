-- =====================================================
-- TRADING 212 BOT - ADD MISSING FIELDS TO ISINS TABLE
-- =====================================================
-- Execute estes comandos no Supabase SQL Editor
-- Data: 2026-09-20
-- Objetivo: Adicionar campos que faltam para sync completo com T212 API

-- Verificar se campos já existem antes de adicionar

-- instrument.currency já deve existir, mas se não:
-- ALTER TABLE isins ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'EUR';

-- createdAt da position (ainda não temos este campo)
ALTER TABLE isins ADD COLUMN IF NOT EXISTS position_created_at TIMESTAMP WITH TIME ZONE;

-- Se quisermos guardar o json completo da instrument (backup):
-- ALTER TABLE isins ADD COLUMN IF NOT EXISTS instrument_json JSONB;

-- Confirmar que todos estes campos existem:
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'isins' ORDER BY column_name;
