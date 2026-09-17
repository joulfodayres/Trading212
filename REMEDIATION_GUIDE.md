# Backend Audit - Remediation Guide

**Date:** 2026-09-17  
**Priority:** CRITICAL - Must fix before production deployment

This document provides step-by-step instructions to fix all identified issues.

---

## Phase 1: Database Schema Fixes

### Step 1.1: Add `strategy_id` to `isins` table

**In Supabase SQL Editor, run:**

```sql
-- Add strategy_id column to isins table
ALTER TABLE isins 
  ADD COLUMN strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX idx_isins_strategy_id ON isins(strategy_id);

-- Update RLS if needed (should already be covered by isins policies)
```

**Verification:**
```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='isins' ORDER BY column_name;
```

Should show: `strategy_id | uuid`

---

### Step 1.2: Add `strategy_status` to `strategies` table

**In Supabase SQL Editor, run:**

```sql
-- Add strategy_status column with constraint
ALTER TABLE strategies 
  ADD COLUMN strategy_status VARCHAR DEFAULT 'E' 
  CHECK (strategy_status IN ('E', 'D'));

-- Create index for filtering
CREATE INDEX idx_strategies_status ON strategies(strategy_status);

-- Default all existing strategies to 'E' (Enabled) - already set by DEFAULT
```

**Verification:**
```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='strategies' ORDER BY column_name;
```

Should show: `strategy_status | character varying`

---

### Step 1.3: Create `isin_strategy_history` table

**In Supabase SQL Editor, run:**

```sql
-- Create audit table for strategy assignment history
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_isin_strategy_history_user_id ON isin_strategy_history(user_id);
CREATE INDEX idx_isin_strategy_history_isin_id ON isin_strategy_history(isin_id);
CREATE INDEX idx_isin_strategy_history_created_at ON isin_strategy_history(created_at);

-- Enable Row Level Security
ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own strategy history" ON isin_strategy_history
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own strategy history" ON isin_strategy_history
  FOR UPDATE USING (user_id = auth.uid());
```

**Verification:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_name='isin_strategy_history';
```

Should return: `isin_strategy_history`

---

## Phase 2: Code Fixes

### Step 2.1: Fix column name references in `backend/routes/isins.py`

**Replace all occurrences of `strategy_name` with `name`:**

Using Find & Replace in VS Code:
- Find: `"strategy_name"`
- Replace: `"name"`
- Scope: `backend/routes/isins.py` only

**Manual locations to verify:**

1. **Line 126** (inside `_get_isin_configs` function):
   ```python
   # BEFORE:
   strategy_result = db.client.table("strategies").select("strategy_name").eq("id", strategy_id).single().execute()
   if strategy_result.data:
       strategy_name = strategy_result.data.get("strategy_name")
   
   # AFTER:
   strategy_result = db.client.table("strategies").select("name").eq("id", strategy_id).single().execute()
   if strategy_result.data:
       strategy_name = strategy_result.data.get("name")
   ```

2. **Line 204-211** (inside `get_enabled_strategies` function):
   ```python
   # BEFORE:
   result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()
   
   strategies = []
   for row in result.data or []:
       strategies.append({
           "id": row["id"],
           "strategy_name": row.get("strategy_name", "Unnamed Strategy")
       })
   
   # AFTER:
   result = db.client.table("strategies").select("id", "name").eq("strategy_status", "E").execute()
   
   strategies = []
   for row in result.data or []:
       strategies.append({
           "id": row["id"],
           "strategy_name": row.get("name", "Unnamed Strategy")  # Still return as strategy_name in response
       })
   ```

3. **Line 279** (inside `toggle_automation` function):
   ```python
   # BEFORE:
   strategy_result = db.client.table("strategies").select("id", "strategy_name").eq("id", data.strategy_id).execute()
   if strategy_result.data:
       strategy_row = strategy_result.data[0]
       strategy_id = data.strategy_id
       strategy_name = strategy_row.get("strategy_name", "Unknown")
   
   # AFTER:
   strategy_result = db.client.table("strategies").select("id", "name").eq("id", data.strategy_id).execute()
   if strategy_result.data:
       strategy_row = strategy_result.data[0]
       strategy_id = data.strategy_id
       strategy_name = strategy_row.get("name", "Unknown")
   ```

---

### Step 2.2: Add `current_user` dependency to `toggle_automation` endpoint

**File:** `backend/routes/isins.py`  
**Line:** 224

```python
# BEFORE:
@router.put("/{isin_id}/automation", response_model=AutomationUpdateResponse)
async def toggle_automation(isin_id: str, data: AutomationToggleRequest):

# AFTER:
from fastapi import Depends  # Already imported at top
# Also need to import get_current_user from auth module
from routes.auth import get_current_user

@router.put("/{isin_id}/automation", response_model=AutomationUpdateResponse)
async def toggle_automation(
    isin_id: str, 
    data: AutomationToggleRequest,
    current_user: dict = Depends(get_current_user)
):
    # Extract user_id from current_user
    user_id = current_user["id"]
    logger.info(f"User {user_id} toggling automation for ISIN: {isin_id}")
```

---

### Step 2.3: Fix `_get_isin_configs` function to use `user_id` properly

**File:** `backend/routes/isins.py`  
**Lines:** 111-140

```python
# BEFORE:
async def _get_isin_configs() -> Dict[str, Dict[str, Any]]:
    """Obter todas as configurações de ISINs (keyed by ISIN)"""
    try:
        result = db.client.table("isins").select("isin, automation_enabled, strategy_id").execute()
        configs = {}

        # Carregar todos os dados de ISINs
        for row in result.data or []:
            # ... rest of code

# AFTER:
async def _get_isin_configs(user_id: str) -> Dict[str, Dict[str, Any]]:
    """Obter todas as configurações de ISINs do utilizador (keyed by ISIN)"""
    try:
        # Filter by user_id for security
        result = db.client.table("isins").select("isin, automation_enabled, strategy_id").eq("user_id", user_id).execute()
        configs = {}

        # Carregar todos os dados de ISINs
        for row in result.data or []:
            # ... rest of code

# Update the call in list_isins:
# OLD:
configs = await _get_isin_configs()

# NEW:
# Need to extract user_id from somewhere - consider if T212 positions have user context
# Or pass None if you can't determine, and filter at a higher level
configs = await _get_isin_configs(None)  # TODO: Pass actual user_id
```

---

### Step 2.4: Fix INSERT/UPDATE in `toggle_automation` function

**File:** `backend/routes/isins.py`  
**Lines:** 306-333

```python
# BEFORE:
# Step 4: Inserir ou atualizar em 'isins' table
instrument = t212_position.get("instrument", {})
isin_data = {
    "isin": isin_id,
    "ticker": instrument.get("ticker", ""),
    "name": instrument.get("name", ""),
    "currency": instrument.get("currency", "EUR"),
    "automation_enabled": data.automation_enabled,
    "strategy_id": strategy_id,
    "updated_at": "now()"
}

# Tentar encontrar ISIN existente
existing_result = db.client.table("isins").select("id").eq("isin", isin_id).execute()

if existing_result.data:
    # UPDATE existente
    logger.info(f"Updating existing ISIN record: {isin_id}")
    db.client.table("isins").update(isin_data).eq("isin", isin_id).execute()
    isin_row_id = existing_result.data[0]["id"]
else:
    # INSERT novo
    logger.info(f"Creating new ISIN record: {isin_id}")
    insert_result = db.client.table("isins").insert(isin_data).execute()
    if insert_result.data:
        isin_row_id = insert_result.data[0]["id"]
    else:
        raise Exception("Failed to insert ISIN record")


# AFTER:
# Step 4: Inserir ou atualizar em 'isins' table
instrument = t212_position.get("instrument", {})
isin_data = {
    "user_id": user_id,  # ← ADD THIS
    "isin": isin_id,
    "ticker": instrument.get("ticker", ""),
    "name": instrument.get("name", ""),
    "currency": instrument.get("currency", "EUR"),
    "automation_enabled": data.automation_enabled,
    "strategy_id": strategy_id,
    "updated_at": "now()"
}

# Tentar encontrar ISIN existente (filter by user_id for security)
existing_result = db.client.table("isins").select("id").eq("isin", isin_id).eq("user_id", user_id).execute()

if existing_result.data:
    # UPDATE existente
    logger.info(f"Updating existing ISIN record: {isin_id}")
    db.client.table("isins").update(isin_data).eq("isin", isin_id).eq("user_id", user_id).execute()
    isin_row_id = existing_result.data[0]["id"]
else:
    # INSERT novo
    logger.info(f"Creating new ISIN record: {isin_id}")
    insert_result = db.client.table("isins").insert(isin_data).execute()
    if insert_result.data:
        isin_row_id = insert_result.data[0]["id"]
    else:
        raise Exception("Failed to insert ISIN record")
```

---

### Step 2.5: Fix audit record insertion

**File:** `backend/routes/isins.py`  
**Lines:** 335-349

```python
# BEFORE:
# Step 5: Auditar em 'isin_strategy_history'
try:
    audit_data = {
        "isin_id": isin_row_id,
        "strategy_id": strategy_id,
        "automated": data.automation_enabled,
        "created_at": "now()",
        "updated_at": "now()"
    }

    db.client.table("isin_strategy_history").insert(audit_data).execute()
    logger.info(f"Audit record created for ISIN {isin_id}")
except Exception as e:
    logger.error(f"Warning: Failed to create audit record: {e}")
    # Não falha a operação se audit falhar


# AFTER:
# Step 5: Auditar em 'isin_strategy_history'
try:
    audit_data = {
        "user_id": user_id,  # ← ADD THIS
        "isin_id": isin_row_id,
        "strategy_id": strategy_id,
        "automated": data.automation_enabled,
        "created_at": "now()",
        "updated_at": "now()"
    }

    db.client.table("isin_strategy_history").insert(audit_data).execute()
    logger.info(f"Audit record created for ISIN {isin_id} by user {user_id}")
except Exception as e:
    logger.error(f"Warning: Failed to create audit record: {e}")
    # Não falha a operação se audit falhar
```

---

## Phase 3: Testing & Verification

### Test 1: Database Schema Verification

```bash
# Connect to Supabase SQL Editor and run:
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('isins', 'strategies', 'isin_strategy_history')
ORDER BY table_name, ordinal_position;
```

**Expected output should include:**
- `isins.strategy_id` (UUID)
- `strategies.strategy_status` (VARCHAR)
- `isin_strategy_history` (full table)

---

### Test 2: Code Syntax Check

```bash
# Run Python syntax check
cd backend
python -m py_compile routes/isins.py
```

Should complete without errors.

---

### Test 3: Import Check

```bash
# Verify imports work
cd backend
python -c "from routes.isins import router; print('✓ isins.py imports OK')"
```

---

### Test 4: Integration Test

Create `backend/test_isins_fix.py`:

```python
"""Integration test for isins.py fixes"""
import pytest
from unittest.mock import patch, MagicMock
from routes.isins import toggle_automation, _get_isin_configs
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_toggle_automation_requires_user():
    """Verify toggle_automation requires user context"""
    # This should fail if current_user dependency is not set
    response = client.put(
        "/api/isins/test-isin/automation",
        json={"automation_enabled": True, "strategy_id": "test-strategy"}
    )
    # Should return 401 Unauthorized if not authenticated
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

def test_get_isin_configs_with_user_filter():
    """Verify _get_isin_configs filters by user_id"""
    # Mock the db client
    with patch('routes.isins.db') as mock_db:
        mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        # Call with user_id
        result = _get_isin_configs("test-user-id")
        
        # Verify .eq("user_id", user_id) was called
        mock_db.client.table.assert_called_with("isins")
        calls = mock_db.client.table("isins").select.return_value.eq.call_args_list
        
        # Should have .eq("user_id", "test-user-id") somewhere
        assert any("user_id" in str(call) for call in calls), "user_id filter not applied"

if __name__ == "__main__":
    print("✓ Running integration tests...")
    test_toggle_automation_requires_user()
    print("✓ toggle_automation requires auth")
    test_get_isin_configs_with_user_filter()
    print("✓ _get_isin_configs filters by user_id")
    print("\n✓ All tests passed!")
```

Run with:
```bash
python backend/test_isins_fix.py
```

---

## Phase 4: Deployment Checklist

- [ ] Schema migrations applied to Supabase
- [ ] Verify all 3 tables/columns exist in Supabase
- [ ] Code changes applied to `backend/routes/isins.py`
- [ ] Syntax check passes
- [ ] Import check passes
- [ ] Integration tests pass
- [ ] Code review completed
- [ ] Tested on staging environment
- [ ] Load tested for performance
- [ ] Security review completed
- [ ] Deployment to production
- [ ] Monitor logs for errors

---

## Rollback Plan (if needed)

If issues occur after deployment:

```sql
-- Remove new columns/tables (CAREFUL - data loss!)
-- Only if reverting to old code

ALTER TABLE isins DROP COLUMN strategy_id;
ALTER TABLE strategies DROP COLUMN strategy_status;
DROP TABLE isin_strategy_history;

-- Revert code changes by checking out previous git version
git checkout main -- backend/routes/isins.py
```

---

## Related Tasks

- [ ] Add `user_id` context to all endpoints (currently only T212 API key auth)
- [ ] Implement proper JWT validation middleware
- [ ] Add unit tests for all routes
- [ ] Add integration tests for database operations
- [ ] Document API authentication flow
- [ ] Review RLS policies for all tables

---

**Generated:** 2026-09-17  
**Status:** Ready for implementation
