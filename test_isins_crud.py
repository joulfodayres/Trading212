"""
Testes para CRUD ISINs Endpoints

Este ficheiro documenta e testa todos os endpoints de ISINs implementados.
Executa testes contra a API local ou remota.

Usage:
    python test_isins_crud.py
"""
import requests
import json
import sys
from typing import Dict, Any

# Configuração
BASE_URL = "http://localhost:8000"  # Local - mudar para https://trading212-4ojx.onrender.com em produção
TEST_USER_ID = "ab1036ff-937d-46e5-8f5b-bab07f1fb100"

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(title: str):
    """Print test title"""
    print(f"\n{BLUE}{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}{RESET}")


def print_success(msg: str):
    """Print success message"""
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg: str):
    """Print error message"""
    print(f"{RED}❌ {msg}{RESET}")


def print_info(msg: str):
    """Print info message"""
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def print_response(data: Dict[str, Any]):
    """Print response JSON"""
    print(f"{YELLOW}Response:{RESET}")
    print(json.dumps(data, indent=2, default=str))


# ===== TESTES =====

def test_create_isin():
    """POST /api/isins - Criar novo ISIN"""
    print_test("1. CREATE ISIN - POST /api/isins")

    url = f"{BASE_URL}/api/isins"
    payload = {"isin": "IE00BK5BQT80"}

    print_info(f"POST {url}")
    print_info(f"Payload: {json.dumps(payload)}")

    try:
        response = requests.post(url, json=payload)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success("ISIN criado com sucesso")
            return data.get("id")  # Retornar ID para testes posteriores
        else:
            print_error(f"Erro: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return None


def test_list_isins():
    """GET /api/isins - Listar todos os ISINs"""
    print_test("2. LIST ISINs - GET /api/isins")

    url = f"{BASE_URL}/api/isins?limit=20&offset=0"

    print_info(f"GET {url}")

    try:
        response = requests.get(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success(f"Listados {len(data)} ISINs")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return []

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return []


def test_get_isin(isin_id: str):
    """GET /api/isins/{isin_id} - Obter detalhes de um ISIN"""
    print_test("3. GET ISIN - GET /api/isins/{isin_id}")

    if not isin_id:
        print_error("ID inválido, pulando teste")
        return None

    url = f"{BASE_URL}/api/isins/{isin_id}"

    print_info(f"GET {url}")

    try:
        response = requests.get(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success("ISIN obtido com sucesso")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return None


def test_update_isin(isin_id: str):
    """PUT /api/isins/{isin_id} - Atualizar ISIN"""
    print_test("4. UPDATE ISIN - PUT /api/isins/{isin_id}")

    if not isin_id:
        print_error("ID inválido, pulando teste")
        return None

    url = f"{BASE_URL}/api/isins/{isin_id}"
    payload = {
        "name": "Vanguard FTSE All-World ETF (atualizado)",
        "automation_enabled": True
    }

    print_info(f"PUT {url}")
    print_info(f"Payload: {json.dumps(payload)}")

    try:
        response = requests.put(url, json=payload)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success("ISIN atualizado com sucesso")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return None


def test_toggle_automation(isin_id: str):
    """PUT /api/isins/{isin_id}/automation/toggle - Toggle automação"""
    print_test("5. TOGGLE AUTOMATION - PUT /api/isins/{isin_id}/automation/toggle")

    if not isin_id:
        print_error("ID inválido, pulando teste")
        return None

    url = f"{BASE_URL}/api/isins/{isin_id}/automation/toggle"

    print_info(f"PUT {url}")

    try:
        response = requests.put(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success("Automação toggled com sucesso")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return None


def test_get_isin_trades(isin_id: str):
    """GET /api/isins/{isin_id}/trades - Obter histórico de trades"""
    print_test("6. GET ISIN TRADES - GET /api/isins/{isin_id}/trades")

    if not isin_id:
        print_error("ID inválido, pulando teste")
        return None

    url = f"{BASE_URL}/api/isins/{isin_id}/trades?limit=50"

    print_info(f"GET {url}")

    try:
        response = requests.get(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success(f"Listados {len(data)} trades")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return []

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return []


def test_sync_from_trading212():
    """GET /api/isins/sync-from-trading212 - Sincronizar ISINs"""
    print_test("7. SYNC FROM TRADING 212 - GET /api/isins/sync-from-trading212")

    url = f"{BASE_URL}/api/isins/sync-from-trading212"

    print_info(f"GET {url}")
    print_info("Sincronizando ISINs da carteira Trading 212...")

    try:
        response = requests.get(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_response(data)
            print_success(f"Sincronização completa: {data.get('synced_count')} criados, {data.get('updated_count')} atualizados")
            return data
        else:
            print_error(f"Erro: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return None


def test_delete_isin(isin_id: str):
    """DELETE /api/isins/{isin_id} - Deletar ISIN"""
    print_test("8. DELETE ISIN - DELETE /api/isins/{isin_id}")

    if not isin_id:
        print_error("ID inválido, pulando teste")
        return False

    url = f"{BASE_URL}/api/isins/{isin_id}"

    print_info(f"DELETE {url}")
    print_info("Deletando ISIN e todos os trades associados...")

    try:
        response = requests.delete(url)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 204:
            print_success("ISIN deletado com sucesso")
            return True
        else:
            print_error(f"Erro: {response.text}")
            return False

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return False


# ===== MAIN =====

def main():
    """Executar todos os testes"""
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════╗")
    print(f"║           TESTE DE CRUD ISINs - TRADING 212             ║")
    print(f"║                                                          ║")
    print(f"║  Base URL: {BASE_URL:<40} ║")
    print(f"╚══════════════════════════════════════════════════════════╝{RESET}\n")

    # Verificar se API está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API está online!")
        else:
            print_error("API retornou status inesperado")
            sys.exit(1)
    except Exception as e:
        print_error(f"Não foi possível conectar à API: {str(e)}")
        print_info("Certifique-se de que a API está rodando em http://localhost:8000")
        sys.exit(1)

    # Executar testes
    created_isin_id = None

    # Teste 1: Criar ISIN
    created_isin_id = test_create_isin()

    # Teste 2: Listar ISINs
    isins = test_list_isins()
    if isins and len(isins) > 0 and not created_isin_id:
        created_isin_id = isins[0].get("id")

    # Teste 3: Obter ISIN
    if created_isin_id:
        test_get_isin(created_isin_id)

        # Teste 4: Atualizar ISIN
        test_update_isin(created_isin_id)

        # Teste 5: Toggle Automation
        test_toggle_automation(created_isin_id)

        # Teste 6: Obter Trades
        test_get_isin_trades(created_isin_id)

    # Teste 7: Sincronizar de T212 (requer credenciais)
    # test_sync_from_trading212()

    # Teste 8: Deletar ISIN
    if created_isin_id:
        test_delete_isin(created_isin_id)

    print(f"\n{BLUE}{'=' * 60}")
    print(f"  Testes Concluídos!")
    print(f"{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    main()
