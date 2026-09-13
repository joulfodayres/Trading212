#!/usr/bin/env python3
"""
Executar SQL no Supabase via Admin API
"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4"

print("🔧 Executando SQL no Supabase via Management API...")
print("=" * 70)

# Ler ficheiro SQL
with open("db/supabase_schema.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Headers para a API
headers = {
    "apikey": SUPABASE_SECRET_KEY,
    "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
    "Content-Type": "application/json",
}

# Endpoint da API de queries (não existe directamente...)
# Vamos tentar via o edge function approach

print("\n📋 Ficheiro SQL lido com sucesso!")
print(f"   Tamanho: {len(sql_content)} caracteres")
print(f"   Linhas: {len(sql_content.split(chr(10)))}")

# Split em comandos individuais
commands = []
current_cmd = ""

for line in sql_content.split('\n'):
    current_cmd += line + "\n"
    if line.strip().endswith(';'):
        cmd = current_cmd.strip()
        if cmd and not cmd.startswith('--'):
            commands.append(cmd)
        current_cmd = ""

print(f"   Comandos: {len(commands)}")

print("\n" + "=" * 70)
print("⚠️  AVISO:")
print("=" * 70)

print("""
A Supabase REST API (grátis) não permite executar SQL arbitrário diretamente.

Preciso que TU:

1. Abre: https://supabase.com/dashboard
2. Clica no projeto 'trading212-bot'
3. Sidebar esquerdo → SQL Editor
4. Clica "New query"
5. COPIA este URL (ficheiro SQL no GitHub):
   https://raw.githubusercontent.com/joulfodayres/Trading212/main/db/supabase_schema.sql
6. OU copia manualmente o conteúdo de db/supabase_schema.sql
7. Cola no SQL Editor do Supabase
8. Clica "Run" (ou Ctrl+Enter)
9. Aguarda ~5-10 segundos

✅ Quando vires "Success" (indicador verde), está pronto!

Diz-me quando estiver feito: "Pronto!" ou manda-me uma screenshot! 📸
""")
