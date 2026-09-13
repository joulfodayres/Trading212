#!/usr/bin/env python3
"""
Script para executar SQL scripts no Supabase
"""
import requests
import sys

SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
SUPABASE_KEY = "sb_publishable_283LZ_pvCLRaxYLaikfA7w_h4oSLVCW"

# Ler o ficheiro SQL
with open("db/supabase_schema.sql", "r") as f:
    sql_content = f.read()

# Dividir em comandos individuais (separados por ;)
commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]

print(f"🔧 Executando {len(commands)} comandos SQL no Supabase...")
print(f"URL: {SUPABASE_URL}")
print("=" * 60)

success_count = 0
error_count = 0

for i, command in enumerate(commands, 1):
    # Saltar comentários e linhas vazias
    if command.strip().startswith("--") or not command.strip():
        continue

    print(f"\n[{i}/{len(commands)}] Executando comando...")

    try:
        # A Supabase RPC endpoint para executar SQL
        # Nota: Isto requer que a key tenha permissões (é a publishable key)
        # Alternativa: usar psycopg2 diretamente com connection string

        print(f"  Comando: {command[:60]}...")

    except Exception as e:
        print(f"  ❌ Erro: {str(e)}")
        error_count += 1

print("\n" + "=" * 60)
print(f"✅ Sucesso: {success_count}")
print(f"❌ Erros: {error_count}")
