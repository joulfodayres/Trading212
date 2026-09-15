#!/usr/bin/env python3
"""
Script de diagnóstico do problema no Render
Verifica environment variables e tenta inicializar o backend
"""
import sys
import os

print("=" * 80)
print("[INFO] DIAGNOSTICO DO RENDER DEPLOYMENT")
print("=" * 80)

# 1. Verifica .env local
print("\n[1] Verificando ficheiro .env local...")
env_file = "backend/.env"
if os.path.exists(env_file):
    print("[OK] {} existe".format(env_file))
    with open(env_file, 'r') as f:
        lines = f.readlines()
        print("    Total de linhas: {}".format(len(lines)))

        # Mostra quais variáveis estão definidas (sem valores)
        env_vars = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                env_vars[key] = True

        print("    Variáveis encontradas: {}".format(len(env_vars)))
        for key in sorted(env_vars.keys()):
            print("      - {}".format(key))
else:
    print("[ERRO] {} NAO EXISTE!".format(env_file))
    print("       Isto é o problema! Render não tem .env")

print("\n[2] Verificando environment variables em runtime...")
required_vars = [
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_JWT_SECRET',
    'T212_API_KEY',
    'T212_API_SECRET',
    'T212_ENVIRONMENT',
    'T212_BASE_URL',
    'JWT_SECRET_KEY',
    'ENCRYPTION_KEY'
]

missing = []
found = []

for var in required_vars:
    if var in os.environ:
        value = os.environ[var]
        # Mostra apenas primeiros 10 chars para segurança
        if len(value) > 10:
            display = value[:10] + "..."
        else:
            display = value
        print("[OK] {} = {}".format(var, display))
        found.append(var)
    else:
        print("[FALTA] {} = (nao definida)".format(var))
        missing.append(var)

print("\nResumo: {}/{} variáveis encontradas".format(len(found), len(required_vars)))

if missing:
    print("\n[ALERTA] FALTAM {} VARIAVEIS:".format(len(missing)))
    for var in missing:
        print("   - {}".format(var))
    print("\nSOLUCAO:")
    print("   1. Vai a Render Dashboard")
    print("   2. Clica em trading212-4ojx (backend)")
    print("   3. Vai a 'Environment'")
    print("   4. Adiciona as variáveis em falta")
    print("   5. Manual Redeploy")
else:
    print("\n[OK] Todas as variáveis estão definidas!")

print("\n[3] Tentando importar backend...")
try:
    sys.path.insert(0, 'backend')
    from config.settings import settings
    print("[OK] Settings carregadas com sucesso")
    print("    SUPABASE_URL: {}...".format(settings.SUPABASE_URL[:50]))
    print("    T212_ENVIRONMENT: {}".format(settings.T212_ENVIRONMENT))

    # Tenta conectar ao Supabase
    print("\n[4] Testando conexão ao Supabase...")
    try:
        from supabase import create_client
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        # Tenta query simples
        response = supabase.table('users').select("id").limit(1).execute()
        print("[OK] Supabase conectado! Resposta: {} registos".format(len(response.data)))
    except Exception as e:
        print("[ERRO] Ao conectar Supabase: {}".format(e))

except Exception as e:
    print("[ERRO] Ao carregar settings: {}".format(e))
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Fim do diagnóstico")
print("=" * 80)
