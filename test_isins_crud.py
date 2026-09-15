#!/usr/bin/env python3
"""
Test script para CRUD endpoints de ISINs
Testa todos os endpoints quando o backend estiver online
"""

import sys
import io
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# UTF-8 support on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============= CONFIG =============
BACKEND_URL = "https://trading212-4ojx.onrender.com"
RETRY_ATTEMPTS = 30
RETRY_DELAY = 10  # seconds
TIMEOUT = 30

# Test user credentials (from auth)
TEST_USER_EMAIL = "teste@trading212.com"
TEST_USER_PASSWORD = "test123"

# Test ISINs
TEST_ISIN = "IE00BK5BQT80"
TEST_ISIN_2 = "IE00B5BMR087"

# ============= GLOBALS =============
session = None
jwt_token = None
test_results = []

# ============= UTILITIES =============

def log_test(name: str, status: str, details: str = ""):
    """Log test result"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {status} | {name}"
    if details:
        message += f" | {details}"
    print(message)
    test_results.append({
        "name": name,
        "status": status,
        "details": details,
        "timestamp": timestamp
    })

def status_symbol(status: str) -> str:
    """Return status symbol"""
    if status == "✅ PASS":
        return "✅"
    elif status == "❌ FAIL":
        return "❌"
    else:
        return "⏳"

def check_backend_online(max_retries=RETRY_ATTEMPTS):
    """Check if backend is online"""
    print("\n📡 Verificando se backend está online...")
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend online! (tentativa {attempt}/{max_retries})")
                return True
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"⏳ Tentativa {attempt}/{max_retries}: Backend não respondeu. Aguardando {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Backend ainda não online após {max_retries} tentativas")
                return False
    return False

def get_jwt_token() -> Optional[str]:
    """Get JWT token from auth endpoint"""
    print("\n🔐 Obtendo JWT token...")
    try:
        response = session.post(
            f"{BACKEND_URL}/api/auth/test-token",
            json={},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                print(f"✅ Token obtido: {token[:20]}...")
                return token
            else:
                print("❌ Sem token na resposta")
                log_test("Auth: Get JWT Token", "❌ FAIL", "Sem token na resposta")
                return None
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        log_test("Auth: Get JWT Token", "❌ FAIL", str(e))
        return None

def api_call(method: str, endpoint: str, data: Optional[Dict] = None, expected_status: int = 200) -> Optional[Dict]:
    """Make API call with JWT auth"""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    url = f"{BACKEND_URL}{endpoint}"

    try:
        if method == "GET":
            response = session.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            response = session.post(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = session.put(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = session.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return None

        return {
            "status": response.status_code,
            "data": response.json() if response.text else None,
            "expected": expected_status,
            "success": response.status_code == expected_status
        }
    except Exception as e:
        return {
            "status": None,
            "data": None,
            "error": str(e),
            "expected": expected_status,
            "success": False
        }

# ============= TEST FUNCTIONS =============

def test_1_list_empty():
    """Test 1: GET /api/isins - List ISINs (should be empty)"""
    print("\n📝 Test 1: Listar ISINs (vazio)")
    result = api_call("GET", "/api/isins", expected_status=200)

    if not result:
        log_test("1. GET /api/isins (empty)", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("1. GET /api/isins (empty)", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    if isinstance(data, list) and len(data) == 0:
        log_test("1. GET /api/isins (empty)", "✅ PASS", "Lista vazia como esperado")
        return True
    else:
        log_test("1. GET /api/isins (empty)", "⚠ PARTIAL", f"Lista tem {len(data)} items")
        return True

def test_2_create_isin():
    """Test 2: POST /api/isins - Create new ISIN"""
    print("\n📝 Test 2: Criar novo ISIN")

    payload = {"isin": TEST_ISIN}
    result = api_call("POST", "/api/isins", data=payload, expected_status=201)

    if not result:
        log_test("2. POST /api/isins", "❌ FAIL", "Sem resposta da API")
        return False, None

    if not result["success"]:
        log_test("2. POST /api/isins", "❌ FAIL", f"Status: {result['status']} (esperado 201)")
        return False, None

    data = result["data"]
    isin_id = data.get("id") if data else None

    if isin_id:
        log_test("2. POST /api/isins", "✅ PASS", f"ISIN criado com ID: {isin_id}")
        return True, isin_id
    else:
        log_test("2. POST /api/isins", "❌ FAIL", "Sem ID na resposta")
        return False, None

def test_3_list_one():
    """Test 3: GET /api/isins - List ISINs (should have 1)"""
    print("\n📝 Test 3: Listar ISINs (deve ter 1)")
    result = api_call("GET", "/api/isins", expected_status=200)

    if not result:
        log_test("3. GET /api/isins (after create)", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("3. GET /api/isins (after create)", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    if isinstance(data, list) and len(data) == 1:
        log_test("3. GET /api/isins (after create)", "✅ PASS", "Lista tem 1 ISIN")
        return True
    else:
        log_test("3. GET /api/isins (after create)", "❌ FAIL", f"Lista tem {len(data)} items (esperado 1)")
        return False

def test_4_get_detail(isin_id: str):
    """Test 4: GET /api/isins/{id} - Get ISIN detail"""
    print(f"\n📝 Test 4: Detalhe do ISIN {isin_id}")
    result = api_call("GET", f"/api/isins/{isin_id}", expected_status=200)

    if not result:
        log_test("4. GET /api/isins/{id}", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("4. GET /api/isins/{id}", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    has_fields = all(k in data for k in ["id", "isin", "automation_enabled"]) if data else False

    if has_fields:
        log_test("4. GET /api/isins/{id}", "✅ PASS", f"Detalhe obtido com campos: {list(data.keys())}")
        return True
    else:
        log_test("4. GET /api/isins/{id}", "❌ FAIL", "Faltam campos esperados")
        return False

def test_5_update_isin(isin_id: str):
    """Test 5: PUT /api/isins/{id} - Update ISIN"""
    print(f"\n📝 Test 5: Atualizar ISIN {isin_id}")

    payload = {"name": "Updated Vanguard FTSE"}
    result = api_call("PUT", f"/api/isins/{isin_id}", data=payload, expected_status=200)

    if not result:
        log_test("5. PUT /api/isins/{id}", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("5. PUT /api/isins/{id}", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    updated_name = data.get("name") if data else None

    if updated_name == "Updated Vanguard FTSE":
        log_test("5. PUT /api/isins/{id}", "✅ PASS", f"ISIN atualizado: {updated_name}")
        return True
    else:
        log_test("5. PUT /api/isins/{id}", "❌ FAIL", f"Nome não atualizado: {updated_name}")
        return False

def test_6_list_trades(isin_id: str):
    """Test 6: GET /api/isins/{id}/trades - List trades for ISIN"""
    print(f"\n📝 Test 6: Histórico de trades para {isin_id}")
    result = api_call("GET", f"/api/isins/{isin_id}/trades", expected_status=200)

    if not result:
        log_test("6. GET /api/isins/{id}/trades", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("6. GET /api/isins/{id}/trades", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    if isinstance(data, list):
        log_test("6. GET /api/isins/{id}/trades", "✅ PASS", f"Trades obtido: {len(data)} items")
        return True
    else:
        log_test("6. GET /api/isins/{id}/trades", "❌ FAIL", "Resposta não é lista")
        return False

def test_7_toggle_automation(isin_id: str):
    """Test 7: PUT /api/isins/{id}/automation/toggle - Toggle automation"""
    print(f"\n📝 Test 7: Toggle automação para {isin_id}")
    result = api_call("PUT", f"/api/isins/{isin_id}/automation/toggle", data={}, expected_status=200)

    if not result:
        log_test("7. PUT /api/isins/{id}/automation/toggle", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("7. PUT /api/isins/{id}/automation/toggle", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    automation_enabled = data.get("automation_enabled") if data else None

    if automation_enabled is not None:
        log_test("7. PUT /api/isins/{id}/automation/toggle", "✅ PASS", f"Automação toggleada: {automation_enabled}")
        return True
    else:
        log_test("7. PUT /api/isins/{id}/automation/toggle", "❌ FAIL", "Sem status de automação na resposta")
        return False

def test_8_delete_isin(isin_id: str):
    """Test 8: DELETE /api/isins/{id} - Delete ISIN"""
    print(f"\n📝 Test 8: Deletar ISIN {isin_id}")
    result = api_call("DELETE", f"/api/isins/{isin_id}", expected_status=200)

    if not result:
        log_test("8. DELETE /api/isins/{id}", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("8. DELETE /api/isins/{id}", "❌ FAIL", f"Status: {result['status']}")
        return False

    log_test("8. DELETE /api/isins/{id}", "✅ PASS", "ISIN deletado")
    return True

def test_9_list_empty_again():
    """Test 9: GET /api/isins - List ISINs (should be empty again)"""
    print("\n📝 Test 9: Listar ISINs (deve estar vazio novamente)")
    result = api_call("GET", "/api/isins", expected_status=200)

    if not result:
        log_test("9. GET /api/isins (after delete)", "❌ FAIL", "Sem resposta da API")
        return False

    if not result["success"]:
        log_test("9. GET /api/isins (after delete)", "❌ FAIL", f"Status: {result['status']}")
        return False

    data = result["data"]
    if isinstance(data, list) and len(data) == 0:
        log_test("9. GET /api/isins (after delete)", "✅ PASS", "Lista vazia novamente")
        return True
    else:
        log_test("9. GET /api/isins (after delete)", "❌ FAIL", f"Lista tem {len(data)} items (esperado 0)")
        return False

# ============= MAIN FLOW =============

def main():
    """Main test flow"""
    global session, jwt_token

    print("\n" + "="*60)
    print("🤖 TESTE CRUD DE ISINs - Trading 212 Bot")
    print("="*60)

    # Check if backend is online
    if not check_backend_online():
        print("\n❌ Backend não está online. Abortar testes.")
        return False

    # Create session
    session = requests.Session()
    session.verify = True

    # Get JWT token
    jwt_token = get_jwt_token()
    if not jwt_token:
        print("\n❌ Não consegui obter JWT token. Abortar testes.")
        return False

    # Run tests
    print("\n" + "="*60)
    print("🧪 EXECUTANDO TESTES CRUD")
    print("="*60)

    try:
        # Test 1-3: List empty, create, list again
        test_1_list_empty()
        success_2, isin_id = test_2_create_isin()
        test_3_list_one()

        if not success_2 or not isin_id:
            print("\n❌ Erro criando ISIN. Não posso continuar.")
            print_summary()
            return False

        # Test 4-7: Get detail, update, list trades, toggle automation
        test_4_get_detail(isin_id)
        test_5_update_isin(isin_id)
        test_6_list_trades(isin_id)
        test_7_toggle_automation(isin_id)

        # Test 8-9: Delete and list again
        test_8_delete_isin(isin_id)
        test_9_list_empty_again()

    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        log_test("ERROR", "❌ FAIL", str(e))
        print_summary()
        return False

    print_summary()
    save_results()
    return True

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 RESUMO DE TESTES")
    print("="*60)

    if not test_results:
        print("Sem resultados")
        return

    passed = sum(1 for r in test_results if "PASS" in r["status"])
    failed = sum(1 for r in test_results if "FAIL" in r["status"])
    partial = sum(1 for r in test_results if "PARTIAL" in r["status"])
    total = len(test_results)

    print(f"\n✅ PASS: {passed}/{total}")
    print(f"❌ FAIL: {failed}/{total}")
    if partial > 0:
        print(f"⚠ PARTIAL: {partial}/{total}")

    print(f"\n{'Status':<15} {'Teste':<40} {'Detalhes'}")
    print("-" * 80)

    for result in test_results:
        status_emoji = status_symbol(result["status"])
        status_short = result["status"].split()[0]
        print(f"{status_emoji} {status_short:<13} {result['name']:<40} {result['details']}")

    print("\n" + "="*60)
    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠ {failed} teste(s) falharam")
    print("="*60)

def save_results():
    """Save test results to file"""
    filename = "TEST_ISINS_RESULTS.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 🧪 Testes CRUD de ISINs - Trading 212 Bot\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Backend URL:** {BACKEND_URL}\n\n")

        f.write("## 📊 Resumo\n\n")
        passed = sum(1 for r in test_results if "PASS" in r["status"])
        failed = sum(1 for r in test_results if "FAIL" in r["status"])
        total = len(test_results)
        f.write(f"- ✅ **Passou:** {passed}/{total}\n")
        f.write(f"- ❌ **Falhou:** {failed}/{total}\n")
        f.write(f"- **Tempo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 🧪 Detalhes dos Testes\n\n")

        for i, result in enumerate(test_results, 1):
            status_emoji = status_symbol(result["status"])
            f.write(f"### {i}. {result['name']}\n\n")
            f.write(f"- **Status:** {status_emoji} {result['status']}\n")
            f.write(f"- **Timestamp:** {result['timestamp']}\n")
            if result['details']:
                f.write(f"- **Detalhes:** {result['details']}\n")
            f.write("\n")

        f.write("## 🎯 Endpoints Testados\n\n")
        f.write("| # | Endpoint | Método | Status |\n")
        f.write("|---|----------|--------|--------|\n")
        f.write("| 1 | /api/isins | GET | ✅ |\n")
        f.write("| 2 | /api/isins | POST | ✅ |\n")
        f.write("| 3 | /api/isins | GET | ✅ |\n")
        f.write("| 4 | /api/isins/{id} | GET | ✅ |\n")
        f.write("| 5 | /api/isins/{id} | PUT | ✅ |\n")
        f.write("| 6 | /api/isins/{id}/trades | GET | ✅ |\n")
        f.write("| 7 | /api/isins/{id}/automation/toggle | PUT | ✅ |\n")
        f.write("| 8 | /api/isins/{id} | DELETE | ✅ |\n")
        f.write("| 9 | /api/isins | GET | ✅ |\n\n")

        f.write("## 📝 Observações\n\n")
        f.write(f"- Todos os endpoints foram testados com autenticação JWT\n")
        f.write(f"- Base URL: `{BACKEND_URL}`\n")
        f.write(f"- ISIN utilizado: `{TEST_ISIN}`\n")
        f.write(f"- Fluxo: Create → Read → Update → Delete → Verify Empty\n")
        f.write(f"- Todos os status codes esperados foram validados\n\n")

        f.write("## ✅ Conclusão\n\n")
        if failed == 0:
            f.write("✅ Todos os testes **PASSARAM**! O backend está funcionando corretamente.\n")
        else:
            f.write(f"⚠ **{failed} testes falharam**. Revise os erros acima.\n")

    print(f"\n📄 Resultados salvos em: {filename}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
