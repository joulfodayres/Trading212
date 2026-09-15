#!/usr/bin/env python3
"""
Monitora o deploy do backend e executa testes quando estiver pronto
"""

import sys
import io
import time
import subprocess
import requests
from datetime import datetime

# UTF-8 support on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BACKEND_URL = "https://trading212-4ojx.onrender.com"
TEST_ENDPOINT = f"{BACKEND_URL}/api/auth/test-token"
MAX_RETRIES = 60  # 60 * 10s = 10 minutes
RETRY_DELAY = 10

print("\n" + "="*70)
print("🚀 MONITOR DE DEPLOY - Aguardando /api/auth/test-token")
print("="*70 + "\n")

for attempt in range(1, MAX_RETRIES + 1):
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5,
            verify=True
        )

        # Tenta o endpoint de teste
        try:
            test_response = requests.post(
                TEST_ENDPOINT,
                json={},
                timeout=5,
                verify=True
            )

            if test_response.status_code in [200, 400, 403]:
                print(f"✅ Endpoint /api/auth/test-token respondeu com status {test_response.status_code}")
                print(f"✅ Backend deployado com sucesso!\n")

                # Executa os testes
                print("🧪 Iniciando testes CRUD...\n")
                result = subprocess.run(
                    ["python", "test_isins_crud.py"],
                    cwd=r"C:\claude\401. Trading 212 Hub",
                    capture_output=False
                )
                sys.exit(result.returncode)
        except requests.exceptions.RequestException:
            pass

        # Se chegou aqui, o health check passou mas o endpoint não
        print(f"⏳ [{attempt}/{MAX_RETRIES}] Backend online, mas endpoint não pronto. Aguardando...")

    except requests.exceptions.RequestException as e:
        if attempt < 5:
            print(f"⏳ [{attempt}/{MAX_RETRIES}] Backend ainda a fazer deploy...")
        elif attempt % 5 == 0:
            print(f"⏳ [{attempt}/{MAX_RETRIES}] Backend ainda não online...")

    time.sleep(RETRY_DELAY)

print(f"\n❌ Endpoint ainda não pronto após {MAX_RETRIES * RETRY_DELAY}s")
print(f"🕐 Por favor, aguarde que o Render conclua a reexecução do backend.")
print(f"📊 Verifica https://dashboard.render.com para status do deploy.\n")
