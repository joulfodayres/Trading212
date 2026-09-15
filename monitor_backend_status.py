#!/usr/bin/env python3
"""
Monitor Render deployment status
Verifica se Backend está respondendo
"""
import requests
import time
import sys

print("[INFO] Monitorando Backend Render...")
print("[INFO] URL: https://trading212-4ojx.onrender.com")
print()

backend_url = "https://trading212-4ojx.onrender.com"
max_attempts = 30  # 5 minutos (10s * 30)
attempt = 0

while attempt < max_attempts:
    attempt += 1
    print(f"[{attempt}/{max_attempts}] Testando Backend...", end=" ")

    try:
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            print(f"OK (HTTP 200)")
            print(f"\nBackend resposta:")
            print(response.json())
            print("\n✅ Backend está ONLINE!")

            # Testa endpoint register
            print("\n[INFO] Testando /api/auth/register...")
            auth_response = requests.post(
                f"{backend_url}/api/auth/register",
                json={"email": "test@test.com", "password": "password123", "password_confirm": "password123"},
                timeout=5
            )
            print(f"Status: {auth_response.status_code}")
            print(f"Resposta: {auth_response.text[:200]}")
            break
        else:
            print(f"HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print("TIMEOUT")
    except requests.exceptions.ConnectionError:
        print("CONNECTION ERROR")
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")

    if attempt < max_attempts:
        time.sleep(10)
        print()

if attempt >= max_attempts:
    print("\n❌ Backend NÃO respondeu após 5 minutos")
    print("Possíveis razões:")
    print("  1. Deploy ainda em progresso")
    print("  2. Backend crashed (verifica logs no Render)")
    print("  3. Rede/DNS issues")
