# 🔐 Teste de Endpoints de Autenticação

**Data:** 2026-09-15T19:38:45.813754
**Backend:** https://trading212-4ojx.onrender.com

## 📊 Resumo

| Métrica | Valor |
|---------|-------|
| Total de testes | 3 |
| ✔ Passou | 1 |
| ✗ Falhou | 2 |
| Taxa de sucesso | 33.3% |

## 📋 Detalhes dos Testes

### Teste 1: POST /api/auth/register

**Status:** ❌ FALHOU  
**HTTP Status Code:** 400  
**Resposta:** 
```json
{"detail":"Erro ao criar conta"}
```

### Teste 2: POST /api/auth/login

**Status:** ❌ FALHOU  
**HTTP Status Code:** 401  
**Resposta:** 
```json
{"detail":"Email ou password inválidos"}
```

### Teste 3: POST /api/auth/verify-token (inválido)

**Status:** ✅ PASSOU  
**HTTP Status Code:** 401  
**Resposta:** 
```json
{"detail":"Authorization header ausente"}
```

## ⚠️ Recomendações

Alguns testes falharam. Verifique:

1. Se o backend está realmente online
2. Se os endpoints existem e estão implementados
3. Se a autenticação está corretamente configurada
4. Os logs do backend em Render para mais detalhes
