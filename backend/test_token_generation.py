#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test login and token generation
"""
import os
import sys

# Force reload of environment
for key in list(os.environ.keys()):
    if key.startswith('FASTAPI_') or key.startswith('SUPABASE_') or key.startswith('T212_'):
        del os.environ[key]

# Read .env manually
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key] = value

# Now import after setting env vars
from config.settings import settings
from routes.auth import create_jwt_token

print(f"[OK] FASTAPI_ENV: {settings.FASTAPI_ENV}")
print(f"[OK] FASTAPI_DEBUG: {settings.FASTAPI_DEBUG}")

# Test creating JWT token
test_user_id = "17780beb-e61f-4604-ba5a-b6329312ac90"
test_email = "teste@trading212.com"

try:
    token = create_jwt_token(test_user_id, test_email)
    print(f"[OK] JWT Token generated successfully")
    print(f"[OK] Token: {token[:50]}...")
    print(f"\n[OK] Test user credentials:")
    print(f"     Email: {test_email}")
    print(f"     Password: teste123")
    print(f"     User ID: {test_user_id}")
except Exception as e:
    print(f"[ERROR] Failed to generate token: {e}")
    sys.exit(1)
