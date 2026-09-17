# 🎯 Backend Simplification - Single User

**Data:** 2026-09-17  
**Status:** Ready to implement  
**Impacto:** Código backend vai ficar 50% mais simples!

---

## 📋 Mudanças Necessárias no Backend

### **1. Remover imports desnecessários**

**Ficheiro:** `backend/routes/isins.py`

```python
# REMOVER isto:
from auth.jwt import get_current_user  # ← Não mais necessário

# REMOVER isto também:
from typing import ... current_user  # Se existir
```

---

### **2. Remover parâmetro current_user de funções**

**Função:** `list_isins()`
```python
# ANTES:
async def list_isins(current_user: User = Depends(get_current_user)):
    configs = await _get_isin_configs()

# DEPOIS:
async def list_isins():
    configs = await _get_isin_configs()
```

---

### **3. Remover filtros user_id de queries**

**Ficheiro:** `backend/routes/isins.py` - função `_get_isin_configs()`

```python
# ANTES:
result = db.client.table("isins").select("isin, automation_enabled, strategy_id").eq("user_id", current_user.id).execute()

# DEPOIS:
result = db.client.table("isins").select("isin, automation_enabled, strategy_id").execute()
```

---

### **4. Remover user_id de INSERT/UPDATE**

**Função:** `toggle_automation()`

```python
# ANTES:
isin_data = {
    "user_id": current_user.id,  # ← REMOVER
    "isin": isin_id,
    "automation_enabled": data.automation_enabled,
    "strategy_id": strategy_id,
}

# DEPOIS:
isin_data = {
    "isin": isin_id,
    "automation_enabled": data.automation_enabled,
    "strategy_id": strategy_id,
}
```

---

### **5. Remover user_id do histórico**

**Função:** `toggle_automation()` - audit section

```python
# ANTES:
audit_data = {
    "user_id": current_user.id,  # ← REMOVER
    "isin_id": isin_row_id,
    "strategy_id": strategy_id,
    "automated": data.automation_enabled,
}

# DEPOIS:
audit_data = {
    "isin_id": isin_row_id,
    "strategy_id": strategy_id,
    "automated": data.automation_enabled,
}
```

---

## 🔍 **Checklist - Onde Procurar**

| Ficheiro | O que procurar | Ação |
|----------|---|---|
| `backend/routes/isins.py` | `.eq("user_id",` | Remover linha |
| `backend/routes/isins.py` | `current_user` | Remover parâmetro |
| `backend/routes/isins.py` | `"user_id": ` | Remover de dicts |
| `backend/db/supabase_client.py` | `user_id` | Remover parâmetros |
| `backend/models/db.py` | `user_id` | Remover coluna de models |

---

## 📝 **Síntese de Mudanças**

### **Linhas a remover/modificar em `backend/routes/isins.py`:**

1. Line ~127: `.eq("user_id", current_user.id)` → Remover `.eq(...)`
2. Line ~139: `.eq("user_id", user_id)` → Remover `.eq(...)`
3. Line ~204: `.eq("strategy_status", "E")` → MANTER (não tem user_id)
4. Line ~314: Remover `"user_id": current_user.id` do dict
5. Line ~458: Remover `"user_id": isin_row_id` do dict (audit)

---

## ✅ **Depois de fazer as mudanças:**

1. **Testa localmente:**
   ```bash
   python -m pytest backend/tests/  # Se houver testes
   ```

2. **Testa endpoint:**
   ```bash
   curl -X PUT http://localhost:8000/api/isins/ABCD1234/automation \
     -H "Content-Type: application/json" \
     -d '{"automation_enabled": true, "strategy_id": "abc123"}'
   ```

3. **Push para GitHub:**
   ```bash
   git add -A
   git commit -m "refactor: Simplify to single-user (remove user_id, RLS)"
   git push
   ```

---

## 🚀 **Ordem de Execução**

1. ✅ Executar SQL em Supabase (`simplify_to_singleuser.sql`)
2. ⏳ Atualizar código backend
3. ⏳ Testar endpoints
4. ⏳ Push e deploy

---

**Pronto para começar?** 👍
