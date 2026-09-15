#!/bin/bash

# Mover ficheiros extras para docs
mv -f BACKLOG.md docs/guides/ 2>/dev/null || true
mv -f FINAL_STATUS.md docs/architecture/ 2>/dev/null || true
mv -f FRONTEND_INTEGRATION_QUICK_GUIDE.md docs/frontend/ 2>/dev/null || true
mv -f INTEGRATION_SUMMARY.md docs/architecture/ 2>/dev/null || true
mv -f ISINS_CRUD_IMPLEMENTATION.md docs/api/ 2>/dev/null || true
mv -f DEPLOYMENT_RESUMO.txt docs/deployment/ 2>/dev/null || true
mv -f TEST_AUTH_RESULTS.md docs/api/ 2>/dev/null || true

# Manter só no root:
# - CLAUDE.md (instruções principais)
# - README.md (overview)
# - CHECKLIST_FINAL.md (status)
# - COMECA_AQUI.md (quick start)
# - TESTES.md (testing guide)
# - TESTE_RESUMO.md (test summary)
# - .env, .env.example, .gitignore, etc

echo "✅ Root directory cleaned up!"
echo "✅ All documentation organized in docs/"
