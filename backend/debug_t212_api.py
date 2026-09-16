#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug Trading 212 API responses
"""
import sys
import os
import json
from pprint import pprint

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load .env
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

from api.trading212 import Trading212Client
from config.settings import settings

def main():
    print("[*] Initializing T212 Client...")
    print(f"[*] Environment: {settings.T212_ENVIRONMENT}")
    print(f"[*] API Key: {settings.T212_API_KEY[:20]}...")

    try:
        t212 = Trading212Client(
            api_key=settings.T212_API_KEY,
            api_secret=settings.T212_API_SECRET,
            environment=settings.T212_ENVIRONMENT
        )
        print("[OK] Client created\n")
    except Exception as e:
        print(f"[ERROR] Failed to create client: {e}")
        return False

    # Test 1: Get account summary
    print("[*] Testing: GET /equity/account/summary")
    try:
        summary = t212.get_account_summary()
        print("[OK] Account Summary:")
        pprint(summary)
        print()
    except Exception as e:
        print(f"[ERROR] {e}\n")

    # Test 2: Get positions (MOST IMPORTANT)
    print("[*] Testing: GET /equity/positions")
    try:
        positions = t212.get_positions()
        print(f"[OK] Positions returned: {type(positions)}")
        print(f"[OK] Number of positions: {len(positions) if positions else 0}")
        print("[OK] Positions data:")
        pprint(positions)
        print()

        # Detailed analysis
        if positions:
            print("[ANALYSIS] Position structure:")
            for i, pos in enumerate(positions):
                print(f"\n  Position {i+1}:")
                for key, value in pos.items():
                    print(f"    {key}: {value}")
        else:
            print("[WARNING] No positions returned!")
            print("[DEBUG] This could mean:")
            print("  1. Account has no open positions")
            print("  2. API returned wrong format")
            print("  3. Authentication failed silently")

    except Exception as e:
        print(f"[ERROR] {e}\n")
        import traceback
        traceback.print_exc()

    # Test 3: Get pending orders
    print("\n[*] Testing: GET /equity/orders")
    try:
        orders = t212.get_pending_orders()
        print(f"[OK] Pending orders: {len(orders) if orders else 0}")
        pprint(orders)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
