"""
Script de teste rápido da API T212
Testa a conexão sem precisar de FastAPI rodando
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from api.trading212 import Trading212Client

# Credenciais DEMO (já testadas)
API_KEY = "40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU"
API_SECRET = "iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0"

print("=" * 60)
print("🧪 TESTE DA API TRADING 212")
print("=" * 60)

try:
    # Inicializar cliente
    print("\n1️⃣  Inicializando cliente T212...")
    client = Trading212Client(API_KEY, API_SECRET, environment="demo")
    print("   ✅ Cliente criado com sucesso")

    # Teste 1: Saldo
    print("\n2️⃣  Consultando saldo da conta...")
    account = client.get_account_summary()
    print(f"   ✅ Saldo: €{account['totalValue']}")
    print(f"      - Cash disponível: €{account['cash']['availableToTrade']}")
    print(f"      - Investido: €{account['investments']['currentValue']}")

    # Teste 2: Posições
    print("\n3️⃣  Consultando posições abertas...")
    positions = client.get_positions()
    print(f"   ✅ Posições: {len(positions)}")
    for pos in positions:
        print(f"      - {pos['instrument']['name']} ({pos['instrument']['ticker']})")
        print(f"        Quantidade: {pos['quantity']} | Preço: €{pos['currentPrice']}")

    # Teste 3: Ordens
    print("\n4️⃣  Consultando ordens pendentes...")
    orders = client.get_pending_orders()
    print(f"   ✅ Ordens pendentes: {len(orders)}")

    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
