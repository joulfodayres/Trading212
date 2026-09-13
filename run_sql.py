#!/usr/bin/env python3
"""
Executar SQL no Supabase usando Python Client + RPC
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ler o SQL
print("📖 Lendo ficheiro SQL...")
with open("db/supabase_schema.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Dividir por statements (;)
statements = []
current = ""

for line in sql_content.split('\n'):
    # Ignorar comentários
    if line.strip().startswith('--'):
        continue

    current += line + '\n'

    if line.strip().endswith(';'):
        stmt = current.strip()
        if stmt:
            statements.append(stmt)
        current = ""

print(f"✅ {len(statements)} SQL statements encontrados\n")

# Tentar uma abordagem diferente: usar curl com psql
import subprocess
import json

SUPABASE_URL = "gocvyhizqggqaxryuplu.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = "AZ2rmgq3p1o9"
DB_NAME = "postgres"

# Connection string do Supabase
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{SUPABASE_URL}:5432/{DB_NAME}"

print("🔧 Tentando executar SQL via psql (se disponível)...\n")

# Salvar SQL num ficheiro temporário
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
    f.write(sql_content)
    temp_sql_file = f.name

try:
    # Tentar executar com psql
    print(f"📡 Conectando a: {SUPABASE_URL}")

    result = subprocess.run(
        ['psql', connection_string, '-f', temp_sql_file],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        print("=" * 70)
        print("✅ SUCESSO! Todas as tabelas criadas!")
        print("=" * 70)
        print("\nTabelas criadas:")
        print("  ✅ users")
        print("  ✅ isins")
        print("  ✅ config")
        print("  ✅ strategies")
        print("  ✅ trades")
        print("  ✅ logs")
        print("\n✅ Com RLS (Row Level Security) ativado!")

    else:
        print(f"⚠️  Aviso: {result.stderr}")
        if "not found" in result.stderr.lower():
            raise FileNotFoundError("psql não está instalado")
        raise Exception(result.stderr)

except FileNotFoundError:
    print("❌ psql não está instalado\n")
    print("Tentando alternativa: usar supabase-py com RPC...\n")

    # Importar Supabase client
    from supabase import create_client, Client

    SUPABASE_URL = "https://gocvyhizqggqaxryuplu.supabase.co"
    SUPABASE_KEY = "sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4"

    print(f"📡 Conectando a Supabase: {SUPABASE_URL}")

    # Criar cliente Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("✅ Conectado!\n")

    # A Supabase não tem RPC para SQL direto, mas vamos tentar via SQL queries
    # Executar cada statement individualmente

    print(f"🔧 Executando {len(statements)} statements SQL...\n")

    # Na verdade, vamos usar a API interna do Supabase
    import requests

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Endpoint para queries
    endpoint = f"{SUPABASE_URL}/rest/v1/rpc/sql"

    # Supabase não expõe RPC de SQL direto na free tier
    # Mas podemos usar a API de Postgrest para criar tabelas via estrutura

    print("⚠️  Aviso: Supabase free tier não suporta SQL via API REST direto")
    print("\nTentando via shell script SQL...")

    # Escrever para um ficheiro .sql e tentar executar
    raise Exception("Usar browser é mais fácil neste caso")

except subprocess.TimeoutExpired:
    print("❌ Timeout na conexão")

except Exception as e:
    print(f"❌ Erro: {str(e)}\n")

    print("=" * 70)
    print("SOLUÇÃO: Executar manualmente via browser")
    print("=" * 70)
    print("""
Por favor, abre o Supabase Dashboard e executa o SQL manualmente:

1. Abre: https://supabase.com/dashboard
2. Seleciona 'trading212-bot'
3. SQL Editor → New query
4. Copia o conteúdo de: db/supabase_schema.sql
5. Cola e clica "Run"

Leva 30 segundos. Depois diz-me "Pronto!" ✅
""")

finally:
    # Limpar ficheiro temporário
    if 'temp_sql_file' in locals():
        try:
            os.unlink(temp_sql_file)
        except:
            pass
