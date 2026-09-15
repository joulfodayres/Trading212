#!/usr/bin/env python3
"""
Test script for authentication endpoints.
Tests all auth endpoints sequentially and reports results.
"""

import sys
import io
import time
import requests
import json
from datetime import datetime

# UTF-8 support on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Configuration
BACKEND_URL = "https://trading212-4ojx.onrender.com"
MAX_WAIT_TIME = 300  # 5 minutes
CHECK_INTERVAL = 5   # Check every 5 seconds

# Use unique email with timestamp to avoid conflicts
timestamp = int(time.time())
TEST_EMAIL = f"teste_automate_{timestamp}@example.com"
TEST_PASSWORD = "TestPassword123"

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "backend_url": BACKEND_URL,
    "tests": []
}

def wait_for_backend():
    """Wait for backend to be online."""
    print(f"⏳ Aguardando backend online em {BACKEND_URL}...")
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            print(f"✗ Backend não ficou online após {MAX_WAIT_TIME}s")
            return False

        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"✔ Backend está online! (levou {int(elapsed)}s)")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"  Tentando novamente em {CHECK_INTERVAL}s... ({int(elapsed)}s/{MAX_WAIT_TIME}s)")
        time.sleep(CHECK_INTERVAL)

def test_register():
    """Test POST /api/auth/register"""
    print("\n" + "="*60)
    print("TESTE 1: POST /api/auth/register")
    print("="*60)

    endpoint = f"{BACKEND_URL}/api/auth/register"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "POST /api/auth/register",
            "status_code": status_code,
            "success": status_code in [200, 201],
            "response": response.text[:500] if response.text else ""
        }

        test_results["tests"].append(result)

        if status_code in [200, 201]:
            print("✔ SUCESSO")
            return True
        else:
            print(f"✗ FALHA (esperava 200 ou 201)")
            return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/register",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return False

def test_login():
    """Test POST /api/auth/login"""
    print("\n" + "="*60)
    print("TESTE 2: POST /api/auth/login")
    print("="*60)

    endpoint = f"{BACKEND_URL}/api/auth/login"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "POST /api/auth/login",
            "status_code": status_code,
            "success": status_code == 200,
            "response": response.text[:500] if response.text else ""
        }

        # Extract token for next tests
        token = None
        if status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    token = data["access_token"]
                elif "token" in data:
                    token = data["token"]
                result["token"] = token
            except:
                pass

        test_results["tests"].append(result)

        if status_code == 200 and token:
            print("✔ SUCESSO - Token obtido")
            return token
        else:
            print(f"✗ FALHA (esperava 200 com token)")
            return None

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/login",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return None

def test_get_me(token):
    """Test GET /api/auth/me"""
    print("\n" + "="*60)
    print("TESTE 3: GET /api/auth/me")
    print("="*60)

    if not token:
        print("⚠ Token não disponível - pulando teste")
        test_results["tests"].append({
            "endpoint": "GET /api/auth/me",
            "status_code": 0,
            "success": False,
            "error": "Token não disponível do teste anterior"
        })
        return False

    endpoint = f"{BACKEND_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Headers: Authorization: Bearer {token[:20]}...")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "GET /api/auth/me",
            "status_code": status_code,
            "success": status_code == 200,
            "response": response.text[:500] if response.text else ""
        }

        test_results["tests"].append(result)

        if status_code == 200:
            print("✔ SUCESSO")
            return True
        else:
            print(f"✗ FALHA (esperava 200)")
            return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "GET /api/auth/me",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return False

def test_verify_token_valid(token):
    """Test POST /api/auth/verify-token com token válido"""
    print("\n" + "="*60)
    print("TESTE 4a: POST /api/auth/verify-token (token VÁLIDO)")
    print("="*60)

    if not token:
        print("⚠ Token não disponível - pulando teste")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/verify-token (válido)",
            "status_code": 0,
            "success": False,
            "error": "Token não disponível"
        })
        return False

    endpoint = f"{BACKEND_URL}/api/auth/verify-token"
    payload = {
        "token": token
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "POST /api/auth/verify-token (válido)",
            "status_code": status_code,
            "success": status_code == 200,
            "response": response.text[:500] if response.text else ""
        }

        test_results["tests"].append(result)

        if status_code == 200:
            print("✔ SUCESSO")
            return True
        else:
            print(f"✗ FALHA (esperava 200)")
            return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/verify-token (válido)",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return False

def test_verify_token_invalid():
    """Test POST /api/auth/verify-token com token INVÁLIDO"""
    print("\n" + "="*60)
    print("TESTE 4b: POST /api/auth/verify-token (token INVÁLIDO)")
    print("="*60)

    endpoint = f"{BACKEND_URL}/api/auth/verify-token"
    payload = {
        "token": "invalid_token_12345_should_fail"
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "POST /api/auth/verify-token (inválido)",
            "status_code": status_code,
            "success": status_code in [401, 400],  # Esperamos erro
            "response": response.text[:500] if response.text else ""
        }

        test_results["tests"].append(result)

        if status_code in [401, 400]:
            print(f"✔ SUCESSO - Token inválido corretamente rejeitado")
            return True
        else:
            print(f"✗ FALHA (esperava 401 ou 400 para token inválido)")
            return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/verify-token (inválido)",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return False

def test_logout(token):
    """Test POST /api/auth/logout"""
    print("\n" + "="*60)
    print("TESTE 5: POST /api/auth/logout")
    print("="*60)

    if not token:
        print("⚠ Token não disponível - pulando teste")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/logout",
            "status_code": 0,
            "success": False,
            "error": "Token não disponível"
        })
        return False

    endpoint = f"{BACKEND_URL}/api/auth/logout"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(endpoint, headers=headers, timeout=10)
        status_code = response.status_code

        print(f"URL: {endpoint}")
        print(f"Status: {status_code}")

        try:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta (text): {response.text}")

        result = {
            "endpoint": "POST /api/auth/logout",
            "status_code": status_code,
            "success": status_code in [200, 204],
            "response": response.text[:500] if response.text else ""
        }

        test_results["tests"].append(result)

        if status_code in [200, 204]:
            print("✔ SUCESSO")
            return True
        else:
            print(f"✗ FALHA (esperava 200 ou 204)")
            return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        test_results["tests"].append({
            "endpoint": "POST /api/auth/logout",
            "status_code": 0,
            "success": False,
            "error": str(e)
        })
        return False

def main():
    """Main test runner"""
    print("\n" + "🔐 TESTE DE ENDPOINTS DE AUTENTICAÇÃO".center(60))
    print("="*60)

    # Step 1: Wait for backend
    if not wait_for_backend():
        print("\n✗ Backend não ficou online. Abortando testes.")
        return False

    # Step 2: Run tests in sequence
    print("\n📋 Iniciando testes...")

    test_register()
    time.sleep(2)

    token = test_login()
    time.sleep(2)

    if token:
        test_get_me(token)
        time.sleep(2)

        test_verify_token_valid(token)
        time.sleep(2)

    test_verify_token_invalid()
    time.sleep(2)

    if token:
        test_logout(token)

    # Step 3: Print summary
    print_summary()

    # Step 4: Save results to file
    save_results()

    return True

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)

    total = len(test_results["tests"])
    passed = sum(1 for t in test_results["tests"] if t["success"])
    failed = total - passed

    print(f"\nTotal: {total}")
    print(f"✔ Passou: {passed}")
    print(f"✗ Falhou: {failed}")

    if failed > 0:
        print("\n❌ TESTES COM FALHA:")
        for test in test_results["tests"]:
            if not test["success"]:
                print(f"  - {test['endpoint']} (Status: {test.get('status_code', '?')})")
                if "error" in test:
                    print(f"    Erro: {test['error']}")
    else:
        print("\n✅ TODOS OS TESTES PASSARAM!")

def save_results():
    """Save results to TEST_AUTH_RESULTS.md"""
    md_content = generate_markdown_report()

    with open("TEST_AUTH_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n📄 Resultados salvos em: TEST_AUTH_RESULTS.md")

def generate_markdown_report():
    """Generate markdown report"""
    total = len(test_results["tests"])
    passed = sum(1 for t in test_results["tests"] if t["success"])
    failed = total - passed

    report = f"""# 🔐 Teste de Endpoints de Autenticação

**Data:** {test_results['timestamp']}
**Backend:** {test_results['backend_url']}

## 📊 Resumo

| Métrica | Valor |
|---------|-------|
| Total de testes | {total} |
| ✔ Passou | {passed} |
| ✗ Falhou | {failed} |
| Taxa de sucesso | {(passed/total)*100:.1f}% |

"""

    # Test details
    report += "## 📋 Detalhes dos Testes\n\n"

    for i, test in enumerate(test_results["tests"], 1):
        status = "✅ PASSOU" if test["success"] else "❌ FALHOU"
        report += f"### Teste {i}: {test['endpoint']}\n\n"
        report += f"**Status:** {status}  \n"
        report += f"**HTTP Status Code:** {test.get('status_code', 'N/A')}  \n"

        if "error" in test:
            report += f"**Erro:** {test['error']}  \n"

        if test.get("response"):
            report += f"**Resposta:** \n```json\n{test['response'][:500]}\n```\n"

        report += "\n"

    # Recommendations
    if failed > 0:
        report += "## ⚠️ Recomendações\n\n"
        report += "Alguns testes falharam. Verifique:\n\n"
        report += "1. Se o backend está realmente online\n"
        report += "2. Se os endpoints existem e estão implementados\n"
        report += "3. Se a autenticação está corretamente configurada\n"
        report += "4. Os logs do backend em Render para mais detalhes\n"
    else:
        report += "## ✅ Status\n\n"
        report += "**Todos os testes passaram com sucesso!**\n"

    return report

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo utilizador")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
