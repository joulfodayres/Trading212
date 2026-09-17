# Backend Code Audit Report - Trading 212 Bot
**Date:** 2026-09-17  
**Auditor:** Claude Code  
**Scope:** Compare backend Python code against Supabase database schema

---

## Executive Summary

**Critical Issues Found:** 5  
**High Priority:** 3  
**Medium Priority:** 2  
**Status:** ⚠️ **BLOCKERS IDENTIFIED** - Code references tables and columns that do NOT exist in schema

The backend code expects 3 additional tables and multiple schema extensions that are not defined in `db/supabase_schema.sql`. This will cause runtime failures in production.

---

## Database Schema Overview

**Actual Schema (from `supabase_schema.sql`):**
- ✅ users
- ✅ isins
- ✅ config
- ✅ strategies
- ✅ trades
- ✅ logs

**Expected by Code (NOT IN SCHEMA):**
- ❌ isin_strategy_history (referenced in code but table doesn't exist)
- ❌ strategy_parameters (implied in CLAUDE.md but not implemented)
- ❌ Additional columns in strategies and isins tables

---

## Critical Issues

### 🔴 ISSUE #1: Missing Table `isin_strategy_history`

**File:** `backend/routes/isins.py`  
**Line:** 345  
**Severity:** CRITICAL - Will cause runtime crash

**Current Code:**
```python
db.client.table("isin_strategy_history").insert(audit_data).execute()
```

**What's Wrong:**
- Table `isin_strategy_history` is NOT defined in `supabase_schema.sql`
- Code tries to insert audit records when toggling automation (line 345)
- This will fail with 404 or permission error at runtime

**Referenced Columns (Expected to exist but don't):**
- `isin_strategy_history.isin_id` (FK to isins)
- `isin_strategy_history.strategy_id` (FK to strategies)
- `isin_strategy_history.automated` (BOOLEAN)
- `isin_strategy_history.created_at` (TIMESTAMP)
- `isin_strategy_history.updated_at` (TIMESTAMP)

**Recommended Fix:**
1. Create the missing table in SQL migration:
```sql
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_isin_strategy_history_user_id ON isin_strategy_history(user_id);
CREATE INDEX idx_isin_strategy_history_isin_id ON isin_strategy_history(isin_id);

ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());
```

2. Update code to include `user_id` when inserting:
```python
audit_data = {
    "user_id": current_user_id,  # Add this
    "isin_id": isin_row_id,
    "strategy_id": strategy_id,
    "automated": data.automation_enabled,
    "created_at": "now()",
    "updated_at": "now()"
}
```

---

### 🔴 ISSUE #2: Missing Column `strategy_status` in `strategies` Table

**File:** `backend/routes/isins.py`  
**Line:** 204  
**Severity:** CRITICAL - Will cause runtime crash

**Current Code:**
```python
result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()
```

**What's Wrong:**
- Column `strategy_status` does NOT exist in `strategies` table (schema only has: id, user_id, name, type, params, created_at)
- Trying to filter on non-existent column will fail
- Function is looking for enabled strategies ('E' status)

**Schema Definition (ACTUAL):**
```sql
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  type VARCHAR DEFAULT 'grid_trading',
  params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Recommended Fix:**

**Option A (Add `strategy_status` column):**
```sql
ALTER TABLE strategies ADD COLUMN strategy_status VARCHAR DEFAULT 'E' CHECK (strategy_status IN ('E', 'D'));
```

Then update code to:
```python
result = db.client.table("strategies").select("id", "name").eq("strategy_status", "E").execute()
```

**Option B (Use `type` for enabled check):**
```python
# Don't filter by status, return all strategies
result = db.client.table("strategies").select("id", "name").execute()
```

---

### 🔴 ISSUE #3: Missing Column `strategy_name` in `strategies` Table

**File:** `backend/routes/isins.py`  
**Lines:** 126, 204, 279  
**Severity:** CRITICAL - Multiple occurrences

**Current Code (Line 126):**
```python
strategy_result = db.client.table("strategies").select("strategy_name").eq("id", strategy_id).single().execute()
```

**What's Wrong:**
- Column `strategy_name` does NOT exist in `strategies` table
- Schema has column `name` (not `strategy_name`)
- Code references `strategy_name` in 3 locations
- This will fail when trying to read strategy name

**Schema Definition (ACTUAL):**
```sql
CREATE TABLE strategies (
  ...
  name VARCHAR NOT NULL,  -- ← Should use this, not strategy_name
  ...
);
```

**Current Code Issues:**
1. **Line 126:** Selects `strategy_name` (doesn't exist)
   ```python
   strategy_result = db.client.table("strategies").select("strategy_name").eq("id", strategy_id).single().execute()
   if strategy_result.data:
       strategy_name = strategy_result.data.get("strategy_name")
   ```

2. **Line 204:** Selects `strategy_name` (doesn't exist)
   ```python
   result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()
   ```

3. **Line 279:** Selects `strategy_name` (doesn't exist)
   ```python
   strategy_result = db.client.table("strategies").select("id", "strategy_name").eq("id", data.strategy_id).execute()
   ```

**Recommended Fix:**
Replace all occurrences of `strategy_name` with `name`:

**Line 126:**
```python
strategy_result = db.client.table("strategies").select("name").eq("id", strategy_id).single().execute()
if strategy_result.data:
    strategy_name = strategy_result.data.get("name")
```

**Line 204:**
```python
result = db.client.table("strategies").select("id", "name").eq("strategy_status", "E").execute()
# ...
strategies.append({
    "id": row["id"],
    "strategy_name": row.get("name", "Unnamed Strategy")  # ← Map "name" to "strategy_name"
})
```

**Line 279:**
```python
strategy_result = db.client.table("strategies").select("id", "name").eq("id", data.strategy_id).execute()
if strategy_result.data:
    strategy_row = strategy_result.data[0]
    strategy_id = data.strategy_id
    strategy_name = strategy_row.get("name", "Unknown")  # ← Use "name"
```

---

### 🟠 ISSUE #4: Missing Column `strategy_id` in `isins` Table

**File:** `backend/routes/isins.py`  
**Lines:** 114, 120, 314, 324  
**Severity:** HIGH - Will cause runtime crash

**Current Code (Line 114):**
```python
result = db.client.table("isins").select("isin, automation_enabled, strategy_id").execute()
```

**What's Wrong:**
- Column `strategy_id` does NOT exist in `isins` table
- Schema for `isins` has: id, user_id, isin, ticker, name, currency, automation_enabled, fields_json, created_at, updated_at
- Code tries to read and write `strategy_id` but it's not in the schema

**Schema Definition (ACTUAL):**
```sql
CREATE TABLE isins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin VARCHAR NOT NULL,
  ticker VARCHAR,
  name VARCHAR,
  currency VARCHAR DEFAULT 'EUR',
  automation_enabled BOOLEAN DEFAULT FALSE,
  fields_json JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, isin)
  -- ❌ NO strategy_id column!
);
```

**Code References:**
1. **Line 114:** Select `strategy_id`
   ```python
   result = db.client.table("isins").select("isin, automation_enabled, strategy_id").execute()
   ```

2. **Line 120:** Read `strategy_id`
   ```python
   strategy_id = row.get("strategy_id")
   ```

3. **Line 314:** Write `strategy_id`
   ```python
   isin_data = {
       ...
       "strategy_id": strategy_id,
       ...
   }
   ```

4. **Line 324:** Update `strategy_id`
   ```python
   db.client.table("isins").update(isin_data).eq("isin", isin_id).execute()
   ```

**Recommended Fix:**
Add the missing column to `isins` table:

```sql
ALTER TABLE isins ADD COLUMN strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL;
```

Then the code will work as-is.

---

### 🟡 ISSUE #5: Missing `user_id` in Automation Toggle Logic

**File:** `backend/routes/isins.py`  
**Lines:** 308-333  
**Severity:** MEDIUM - Security & data integrity issue

**Current Code:**
```python
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
```

**What's Wrong:**
1. **Missing `user_id` on INSERT:** Code doesn't set `user_id` when creating new ISIN (line 329)
2. **Missing `user_id` filter on UPDATE:** Query only filters by `isin` (line 324), not by `user_id`
   - This violates RLS and allows users to update OTHER users' ISINs
3. **Missing `user_id` in INSERT data:** New ISIN record won't have user_id, violating FK constraint
4. **Race condition:** Another user with same ISIN code could cause conflicts

**Security Impact:**
- User A could toggle automation for User B's ISIN if they know the ISIN code
- Violates the RLS policy: "Users can update their own ISINs"

**Recommended Fix:**
The function needs to:
1. Get the current user_id (from JWT token)
2. Include user_id when inserting
3. Filter by both isin AND user_id when updating

```python
# Step 0: Get current user from JWT (add as function parameter)
async def toggle_automation(isin_id: str, data: AutomationToggleRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # ... existing code ...
    
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

    # Tentar encontrar ISIN existente (filter by user_id too)
    existing_result = db.client.table("isins").select("id").eq("isin", isin_id).eq("user_id", user_id).execute()

    if existing_result.data:
        # UPDATE existente (filter by user_id too)
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
        logger.info(f"Audit record created for ISIN {isin_id}")
    except Exception as e:
        logger.error(f"Warning: Failed to create audit record: {e}")
```

---

## Summary of Required Schema Changes

To make the backend code work, the following SQL migrations are needed:

### Migration 1: Add `strategy_id` to `isins`
```sql
ALTER TABLE isins ADD COLUMN strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL;
```

### Migration 2: Add `strategy_status` to `strategies`
```sql
ALTER TABLE strategies ADD COLUMN strategy_status VARCHAR DEFAULT 'E' CHECK (strategy_status IN ('E', 'D'));
```

### Migration 3: Create `isin_strategy_history` table
```sql
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_isin_strategy_history_user_id ON isin_strategy_history(user_id);
CREATE INDEX idx_isin_strategy_history_isin_id ON isin_strategy_history(isin_id);

ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own strategy history" ON isin_strategy_history
  FOR INSERT WITH CHECK (user_id = auth.uid());
```

---

## Summary of Required Code Changes

### File: `backend/routes/isins.py`

| Line | Issue | Fix |
|------|-------|-----|
| 114 | Select non-existent `strategy_id` | Add column to schema OR remove from select if not in schema |
| 120 | Read non-existent `strategy_id` | Add column to schema OR remove if not in schema |
| 126 | Select non-existent `strategy_name` | Replace with `name` |
| 128 | Read non-existent `strategy_name` | Replace with `name` |
| 204 | Filter by non-existent `strategy_status` | Add column to schema OR remove filter |
| 204 | Select non-existent `strategy_name` | Replace with `name` |
| 225-369 | Missing `current_user` parameter | Add `Depends(get_current_user)` parameter |
| 279 | Select non-existent `strategy_name` | Replace with `name` |
| 283 | Read non-existent `strategy_name` | Replace with `name` |
| 308-333 | Missing `user_id` in INSERT/UPDATE | Add `user_id` to both operations, filter UPDATE by user_id too |
| 345 | Insert into non-existent table | Create `isin_strategy_history` table in schema |

---

## Testing Recommendations

After fixing these issues:

1. **Unit Tests:** Test each function with mocked database
2. **Integration Tests:** Test against staging Supabase database
3. **Security Tests:** Verify RLS prevents cross-user access
4. **End-to-End Tests:** Test full automation toggle workflow

---

## Files Reviewed

✅ `backend/models/db.py` - Models OK (but not used by current routes)  
✅ `backend/models/schemas.py` - Schemas OK  
✅ `backend/routes/auth.py` - No schema issues (different scope)  
✅ `backend/routes/config.py` - No active database calls  
❌ `backend/routes/isins.py` - **5 CRITICAL ISSUES**  
✅ `backend/db/supabase_client.py` - SupabaseDB client is OK (but routes not using it)  

---

## Deployment Blocker Status

🔴 **DO NOT DEPLOY** - Critical issues will cause runtime failures

**Required Actions Before Production:**
1. Add 3 missing columns/tables to Supabase schema
2. Fix all column name references (strategy_name → name)
3. Add `current_user` dependency to toggle_automation endpoint
4. Add proper `user_id` filtering to prevent cross-user access

---

## Notes

- The SQLAlchemy models in `backend/models/db.py` are well-designed but are **NOT BEING USED** by the FastAPI routes
- Routes use Supabase client directly with `.table()` API
- The schema in `supabase_schema.sql` is missing 2 columns and 1 table that the code expects
- Several TODO comments in code indicate incomplete implementation
- No JWT-based user context is being passed to the `toggle_automation` endpoint, relying on environment variables instead

---

**Generated:** 2026-09-17 by Claude Code Audit System
