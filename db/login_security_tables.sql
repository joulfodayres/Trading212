-- =====================================================
-- TRADING 212 BOT - LOGIN SECURITY (Item #12)
-- =====================================================
-- MFA/TOTP + progressive delay + trusted devices + revocable sessions
-- Date: 2026-09-23

-- =====================================================
-- 1. USERS: add MFA columns
-- =====================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE;

-- =====================================================
-- 2. LOGIN_ATTEMPTS: every attempt, for progressive delay + alerting
-- =====================================================

CREATE TABLE IF NOT EXISTS login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_address VARCHAR NOT NULL,
  email VARCHAR,
  success BOOLEAN NOT NULL,
  stage VARCHAR NOT NULL DEFAULT 'password' CHECK (stage IN ('password', 'mfa')),
  user_agent VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_created ON login_attempts(ip_address, created_at DESC);

-- =====================================================
-- 3. TRUSTED_DEVICES: skip MFA on recognized devices
-- =====================================================

CREATE TABLE IF NOT EXISTS trusted_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_token VARCHAR NOT NULL UNIQUE,
  user_agent VARCHAR,
  ip_address VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trusted_devices_token ON trusted_devices(device_token);
CREATE INDEX IF NOT EXISTS idx_trusted_devices_user ON trusted_devices(user_id);

-- =====================================================
-- 4. ACTIVE_SESSIONS: revocable sessions + killswitch
-- =====================================================

CREATE TABLE IF NOT EXISTS active_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  jti VARCHAR NOT NULL UNIQUE,
  ip_address VARCHAR,
  user_agent VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_active_sessions_jti ON active_sessions(jti);
CREATE INDEX IF NOT EXISTS idx_active_sessions_user ON active_sessions(user_id);

-- =====================================================
-- NOTES
-- =====================================================
-- - MFA challenge (step 1 -> step 2 bridge) uses a short-lived signed JWT,
--   not a DB table (no extra state needed, self-expiring).
-- - Registration stays bootstrap-only at the app level (blocked once one
--   user row exists) — no DB-level enforcement needed for that.
