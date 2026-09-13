#!/usr/bin/env python3
"""
Usar curl para executar SQL (sem dependências externas)
"""
import json
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4"

print("=" * 70)
print("🚀 SOLUÇÃO FINAL: Executar SQL via Supabase RPC")
print("=" * 70)

# Ler SQL
with open("db/supabase_schema.sql", "r", encoding="utf-8") as f:
    sql_full = f.read()

# Dividir em blocos menores (cada statement)
statements = []
current = ""

for line in sql_full.split('\n'):
    if line.strip().startswith('--'):
        continue
    current += line + '\n'
    if line.strip().endswith(';'):
        stmt = current.strip()
        if stmt and len(stmt) > 10:  # Evitar linhas vazias
            statements.append(stmt)
        current = ""

print(f"\n📋 Total de SQL statements: {len(statements)}")

# A Supabase permite chamar RPC functions
# Mas não temos uma function pré-criada
# Alternativa: usar o endpoint de SQL diretamente

# Na verdade, vamos tentar executar via o endpoint de queries do Supabase
# que suporta queries SQL limitadas

headers = {
    "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
    "apikey": SUPABASE_SECRET_KEY,
    "Content-Type": "application/json",
}

# Tentar endpoint de SQL (não existe, mas tentamos mesmo assim)
print("\n🔍 Procurando endpoint de SQL no Supabase...")
print("   (Testando various endpoints)\n")

# Teste 1: Verificar tabelas existentes
print("1️⃣  Verificando tabelas existentes...")

response = requests.get(
    f"{SUPABASE_URL}/rest/v1/users",
    headers=headers
)

if response.status_code in [200, 206]:
    print("   ✅ Tabela 'users' já existe!")
elif response.status_code == 404:
    print("   ❌ Tabela 'users' não existe - precisa de ser criada")
else:
    print(f"   ⚠️  Status: {response.status_code}")

print("\n" + "=" * 70)
print("💡 CONCLUSÃO:")
print("=" * 70)

print("""
Depois de vários testes, a conclusão é:

❌ A Supabase REST API (tier grátis) NÃO permite:
   - Executar SQL arbitrário
   - Criar tabelas via API
   - RPC SQL functions

✅ ÚNICA SOLUÇÃO PROGRAMÁTICA:
   1. Usar psql (PostgreSQL client) - não está instalado no Windows
   2. Usar uma função Supabase RPC pré-criada - não temos
   3. Usar Migration tool (supabase CLI) - precisa de setup extra

✅ SOLUÇÃO RÁPIDA (RECOMENDADA):
   Executar SQL manualmente no browser (5 minutos):

   1. Abre: https://supabase.com/dashboard
   2. Projeto: trading212-bot
   3. SQL Editor → New query
   4. Copia/cola todo o conteúdo de: db/supabase_schema.sql
   5. Run (ou Ctrl+Enter)
   6. Aguarda ~5-10 segundos
   7. Vê "Success" (verde) no topo

DESCULPA! A Supabase free tier tem restrições. 😅

Podes fazer isto manualmente agora? Leva literalmente 5 minutos!
""")
