#!/usr/bin/env python3
"""
Setup script to install dependencies for T212 Limit Order Tester
Run this once before using the GUI tester
"""

import subprocess
import sys

print("=" * 60)
print("T212 Limit Order Tester - Setup")
print("=" * 60)
print()

# Check Python version
print(f"✓ Python version: {sys.version}")
print()

# Install requests
print("Installing dependencies...")
print()

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("You can now run the tester:")
    print()
    print("  python test_limit_order_gui.py")
    print()
    print("Or on Windows, double-click:")
    print()
    print("  RUN_LIMIT_ORDER_TESTER.bat")
    print()
except subprocess.CalledProcessError as e:
    print()
    print("=" * 60)
    print("❌ Setup Failed!")
    print("=" * 60)
    print()
    print(f"Error: {e}")
    print()
    sys.exit(1)
