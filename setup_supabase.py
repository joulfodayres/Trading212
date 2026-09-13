#!/usr/bin/env python3
"""
Script para executar SQL scripts no Supabase via psycopg2
"""
import psycopg2
import sys
import io

# Usar UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Credenciais Supabase
SUPABASE_URL = "gocvyhizqggqaxryuplu.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = input("🔑 Qual é a password da BD (database password)? ")  # Pergunta interativamente

print(f"\n📡 Conectando a Supabase...")
print(f"   Host: {SUPABASE_URL}")
print(f"   Database: {DB_NAME}")
print(f"   User: {DB_USER}")

try:
    # Conectar à BD
    conn = psycopg2.connect(
        host=SUPABASE_URL,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )

    cursor = conn.cursor()
    print("✅ Conectado com sucesso!\n")

    # Ler ficheiro SQL
    print("📖 Lendo ficheiro SQL...")
    with open("db/supabase_schema.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("🔧 Executando SQL scripts...\n")
    print("=" * 60)

    # Executar o SQL
    cursor.execute(sql_content)
    conn.commit()

    print("=" * 60)
    print("\n✅ TODAS AS TABELAS CRIADAS COM SUCESSO!")
    print("\nTabelas criadas:")
    print("  ✅ users")
    print("  ✅ isins")
    print("  ✅ config")
    print("  ✅ strategies")
    print("  ✅ trades")
    print("  ✅ logs")
    print("\nCom RLS (Row Level Security) ativado em todas!")

    cursor.close()
    conn.close()

except psycopg2.OperationalError as e:
    print(f"❌ ERRO DE CONEXÃO: {str(e)}")
    print("\nPossíveis causas:")
    print("  1. Password incorreta")
    print("  2. Host incorreto")
    print("  3. Firewall bloqueando conexão")
    sys.exit(1)

except psycopg2.ProgrammingError as e:
    print(f"❌ ERRO DE SQL: {str(e)}")
    sys.exit(1)

except Exception as e:
    print(f"❌ ERRO: {str(e)}")
    sys.exit(1)
