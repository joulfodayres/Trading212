import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_KEY = "sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4"

print("🔐 Criando utilizador de teste em Supabase...")
print()

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

data = {
    "email": "teste@trading212.com",
    "is_admin": True
}

try:
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/users",
        headers=headers,
        json=data,
        timeout=10
    )

    print(f"Status: {response.status_code}")
    print()

    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ UTILIZADOR CRIADO COM SUCESSO!")
        print()
        if isinstance(result, list) and len(result) > 0:
            user = result[0]
            print(f"   Email: {user.get('email')}")
            print(f"   ID: {user.get('id')}")
            print(f"   Admin: {user.get('is_admin')}")
        else:
            print(json.dumps(result, indent=2))
    else:
        print(f"⚠️  Resposta: {response.text}")

except Exception as e:
    print(f"❌ Erro: {str(e)}")

