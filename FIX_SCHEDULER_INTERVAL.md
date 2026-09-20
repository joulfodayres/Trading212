# Fix: Scheduler Interval API Issue

## Problema
Quando o utilizador tenta:
1. Carregar a página Configuration → "Not Found" error
2. Tentar atualizar o "New Interval" → erro e não atualiza

## Causa
1. **GET endpoint não existia**: O frontend tentava GET `/v1/automation/config/interval` mas o endpoint não estava implementado
2. **PUT endpoint com query parameter**: O endpoint estava à espera de um query parameter em vez de um request body
3. **API path errada no frontend**: Chamava `/automation/config/interval` em vez de `/v1/automation/config/interval`
4. **Supabase update syntax errado**: Tentava usar `"updated_at": "now()"` como string, o que não funciona

## Solução

### Backend (routes/automation.py)
1. ✅ Adicionado novo GET endpoint: `GET /api/v1/automation/config/interval`
   - Retorna: `{ "scheduler_interval_seconds": int, "status": "ok" }`
   - Busca o valor de `app_parameters` table

2. ✅ Corrigido PUT endpoint: `PUT /api/v1/automation/config/interval`
   - Aceita request body: `{ "scheduler_interval_seconds": int }`
   - Atualiza o valor em `app_parameters` table
   - Valida intervalo 5-300 segundos usando Pydantic Field

3. ✅ Adicionado Pydantic schema `SchedulerIntervalRequest`
   - Validação: `scheduler_interval_seconds: int = Field(..., ge=5, le=300)`

4. ✅ Removido `"updated_at": "now()"` de todos os updates
   - Supabase Python SDK não interpreta `now()` como função SQL
   - O banco de dados deve ter `CURRENT_TIMESTAMP` como default

5. ✅ Adicionado logging detalhado para debug

### Frontend (src/pages/ConfigPage.tsx)
1. ✅ Corrigido path GET: `/v1/automation/config/interval`
2. ✅ Corrigido path PUT: `/v1/automation/config/interval`
3. ✅ Adicionado logging detalhado

## Commits
- `7c45357`: Initial fix - Add GET endpoint and fix API paths
- `adb3cf5`: Remove invalid updated_at and add detailed logging

## Status Deployment
- ✅ Código local: Correto
- ⏳ GitHub: Pushed
- ⏳ Render: Auto-deploy em progresso (2-3 minutos)

## Teste
Após deploy completar, testar:

### GET interval
```bash
curl https://trading212-4ojx.onrender.com/api/v1/automation/config/interval
# Expected: {"scheduler_interval_seconds": 15, "status": "ok"}
```

### PUT interval
```bash
curl -X PUT https://trading212-4ojx.onrender.com/api/v1/automation/config/interval \
  -H "Content-Type: application/json" \
  -d '{"scheduler_interval_seconds": 20}'
# Expected: {"status": "updated", "scheduler_interval_seconds": 20}
```

## Próximas Etapas
1. Esperar Render auto-deploy (2-3 min)
2. Testar Configuration page no browser
3. Verificar que GET fetch funciona na page load
4. Testar atualizar intervalo com sucesso

