# 🔧 FIX: Supabase Lazy Initialization

**Data:** 2026-09-15 23:30 UTC  
**Commit:** 49066e5  
**Status:** ✅ Fixed and pushed to GitHub

---

## 🔴 PROBLEMA ENCONTRADO

**Quando:** User tentou fazer Register no Frontend
**Erro:** "Not Found" ao clicar Register

**Causa:** Supabase era inicializado **imediatamente** ao importar o router:

```python
# ANTES (problemático):
from routes.auth import router  # <-- Executa aqui!
supabase = create_client(...)   # <-- Tenta conectar a Supabase
```

Se Supabase credentials estavam inválidas ou não conseguia conectar:
- O router inteiro falhava ao importar
- Backend iniciava, mas os endpoints `/api/auth/*` nunca eram registados
- Frontend recebia 404 "Not Found" em vez de erro HTTP

---

## ✅ SOLUÇÃO IMPLEMENTADA

**Lazy Initialization:** Supabase só se conecta quando **realmente necessário**

```python
# DEPOIS (correto):
_supabase_client = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(...)  # Conecta na primeira chamada
    return _supabase_client

# No handler:
@router.post("/register")
async def register(request: RegisterRequest):
    supabase = get_supabase()  # Conecta aqui, não na importação
    # ... resto do código
```

**Benefício:**
- Router é importado com sucesso
- Endpoints são registados no FastAPI
- Supabase só se conecta quando `/register` é chamado
- Se Supabase falha depois, retorna erro apropriado (500) em vez de 404

---

## 📊 IMPACTO

| Antes | Depois |
|-------|--------|
| Router falha ao importar | ✅ Router importa OK |
| Endpoints não registados | ✅ Endpoints registados |
| Frontend recebe 404 | ✅ Frontend recebe resposta |
| Erro confuso | ✅ Erro claro (se Supabase falha) |

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Commit feito e pushed
2. ⏳ Render auto-deploy (5-10 minutos)
3. ⏳ Backend redeploy completo
4. ⏳ Endpoints `/api/auth/login` e `/api/auth/register` funcionam
5. ⏳ User consegue fazer Register + Login

---

## 📝 Ficheiros Modificados

- `backend/routes/auth.py`
  - Adicionado: `get_supabase()` function
  - Modificado: `login()` para usar `get_supabase()`
  - Modificado: `register()` para usar `get_supabase()`

---

**Status:** ✅ Fix aplicado e em deploy  
**ETA Render:** 5-10 minutos  
**Próxima Ação:** Aguardar deploy + retomar testes
