#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Supabase authentication - create test user
"""
import sys
import os
from supabase import create_client

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_KEY = "sb_publishable_283LZ_pvCLRaxYLaikfA7w_h4oSLVCW"

TEST_EMAIL = "teste@trading212.com"
TEST_PASSWORD = "teste123"

def main():
    print("[*] Connecting to Supabase...")

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[OK] Supabase client created")
    except Exception as e:
        print(f"[ERROR] Failed to create Supabase client: {e}")
        return False

    # Try to sign up
    print(f"[*] Attempting to sign up: {TEST_EMAIL}")
    try:
        response = supabase.auth.sign_up({
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })

        if response and response.user:
            print(f"[OK] User signed up: {response.user.email}")
            print(f"[OK] User ID: {response.user.id}")
            return True
        else:
            print("[WARN] Sign up response empty")
            return False

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            print("[WARN] User already exists (expected on second run)")
            # Try to login instead
            print(f"[*] Attempting login: {TEST_EMAIL}")
            try:
                login_response = supabase.auth.sign_in_with_password({
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                })
                if login_response and login_response.user:
                    print(f"[OK] Login successful: {login_response.user.email}")
                    print(f"[OK] User ID: {login_response.user.id}")
                    return True
            except Exception as login_err:
                print(f"[ERROR] Login failed: {login_err}")
                return False
        else:
            print(f"[ERROR] Sign up failed: {error_msg}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
