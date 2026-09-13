#!/usr/bin/env python3
"""
Script para executar SQL no Supabase via REST API
"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_KEY = "sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4"  # Usar a secret key (mais permissões)

print("🔧 Executando SQL via Supabase REST API...")
print(f"URL: {SUPABASE_URL}")
print("=" * 60)

# Ler ficheiro SQL
with open("db/supabase_schema.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Split em blocos (separados por linhas em branco duplas)
# Mas na verdade vamos enviar tudo de uma vez
sql_commands = []
current_command = ""

for line in sql_content.split('\n'):
    # Ignorar comentários e linhas vazias
    if line.strip().startswith('--') or not line.strip():
        continue

    current_command += line + "\n"

    if line.strip().endswith(';'):
        sql_commands.append(current_command.strip())
        current_command = ""

# Endpoint do Supabase para SQL
endpoint = f"{SUPABASE_URL}/rest/v1/rpc/sql"

# Mas a Supabase não tem RPC direto para SQL arbitrário na free tier...
# Vamos usar o endpoint de query diretamente

print(f"\n📊 Total de comandos: {len(sql_commands)}")
print("\nAlternativa: Usando o SQL Editor do Supabase (via navegador)\n")

print("❌ Nota: A Supabase REST API não permite executar SQL arbitrário diretamente.")
print("✅ Solução: Vou dar-te uma forma alternativa...\n")

# Na verdade, vamos tentar uma abordagem diferente
# Vamos criar as tabelas usando a API de inserção do Supabase

print("=" * 60)
print("🔄 ABORDAGEM ALTERNATIVA - Execução via REST API")
print("=" * 60)

# Headers
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Tentar fazer uma query simples primeiro
print("\n1️⃣  Testando conexão à API...")

test_url = f"{SUPABASE_URL}/rest/v1/"

try:
    response = requests.get(test_url, headers=headers, timeout=10)

    if response.status_code == 200 or response.status_code == 400:
        print("✅ Conexão OK!")
    else:
        print(f"⚠️  Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("❌ Timeout - servidor não respondeu")
except Exception as e:
    print(f"❌ Erro: {str(e)}")

print("\n" + "=" * 60)
print("⚠️  RECOMENDAÇÃO:")
print("=" * 60)
print("""
A Supabase REST API tem limitações para executar SQL direto.

Melhor solução: Executar SQL no Supabase Dashboard via browser:

1. Abre: https://supabase.com/dashboard
2. Seleciona o projeto 'trading212-bot'
3. Vai a SQL Editor → New query
4. Copia TODO o conteúdo de: db/supabase_schema.sql
5. Cola no SQL Editor
6. Clica Run (ou Ctrl+Enter)
7. Aguarda alguns segundos...

Isto levará ~30 segundos no total.

Diz-me quando estiver feito! ✅
""")
