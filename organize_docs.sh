#!/bin/bash

# Criar mapeamento de ficheiros para pastas
mkdir -p docs/{architecture,api,frontend,deployment,guides}

# API Documentation
mv -f AUTH_JWT_IMPLEMENTATION.md docs/api/ 2>/dev/null || true
mv -f JWT_TESTING_GUIDE.md docs/api/ 2>/dev/null || true
mv -f README_JWT_AUTHENTICATION.md docs/api/ 2>/dev/null || true
mv -f INTEGRACAO_FRONTEND.md docs/frontend/ 2>/dev/null || true
mv -f FRONTEND_JWT_INTEGRATION.md docs/frontend/ 2>/dev/null || true
mv -f FRONTEND_BACKEND_INTEGRATION.md docs/frontend/ 2>/dev/null || true

# Architecture & Design
mv -f DEPLOYMENT.md docs/architecture/ 2>/dev/null || true
mv -f IMPLEMENTATION_SUMMARY.md docs/architecture/ 2>/dev/null || true
mv -f IMPLEMENTATION_COMPLETE.txt docs/architecture/ 2>/dev/null || true
mv -f IMPLEMENTATION_CHECKLIST.txt docs/architecture/ 2>/dev/null || true
mv -f ROADMAP_FINAL.md docs/guides/ 2>/dev/null || true

# Deployment & Status
mv -f DEPLOYMENT_COMPLETE.txt docs/deployment/ 2>/dev/null || true
mv -f DEPLOYMENT_STEP_BY_STEP.md docs/deployment/ 2>/dev/null || true
mv -f RENDER_DEPLOYMENT_INSTRUCTIONS.txt docs/deployment/ 2>/dev/null || true
mv -f RENDER_FRONTEND_SETUP.txt docs/deployment/ 2>/dev/null || true

# Temporary files to delete
rm -f JWT_SUMMARY.md 2>/dev/null || true
rm -f STATUS_IMPLEMENTACAO.md 2>/dev/null || true
rm -f STATUS_IMPLEMENTACAO_TEMPO_REAL.md 2>/dev/null || true
rm -f PROXIMOS_PASSOS.md 2>/dev/null || true
rm -f generate_key.py 2>/dev/null || true
rm -f test_backend.py 2>/dev/null || true
rm -f test_suite.py 2>/dev/null || true
rm -f generate_jwt_secret.py 2>/dev/null || true

echo "✅ Documentação organizada!"
echo "✅ Ficheiros temporários removidos!"
