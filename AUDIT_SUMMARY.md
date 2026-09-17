# Backend Audit - Executive Summary

**Audit Date:** 2026-09-17  
**Auditor:** Claude Code  
**Project:** Trading 212 Bot MVP  
**Environment:** Backend Python/FastAPI + Supabase

---

## 🔴 CRITICAL FINDINGS

**Total Issues Found:** 5  
**Severity Breakdown:**
- 🔴 CRITICAL: 3 issues
- 🟠 HIGH: 1 issue  
- 🟡 MEDIUM: 1 issue

**Deployment Status:** ⚠️ **DO NOT DEPLOY** - Code will fail at runtime

---

## Quick Reference Table

| Issue | File | Type | Impact | Severity |
|-------|------|------|--------|----------|
| Missing table `isin_strategy_history` | routes/isins.py:345 | Missing Schema | Runtime crash on automation toggle | 🔴 CRITICAL |
| Missing column `strategy_name` | routes/isins.py:126,204,279 | Wrong Column Name | 3 runtime crashes when reading strategy names | 🔴 CRITICAL |
| Missing column `strategy_status` | routes/isins.py:204 | Missing Schema | Runtime crash when filtering strategies | 🔴 CRITICAL |
| Missing column `strategy_id` in isins | routes/isins.py:114,120,314,324 | Missing Schema | Runtime crash when managing automation | 🟠 HIGH |
| Missing `user_id` in toggle endpoint | routes/isins.py:225-369 | Security & Logic | Cross-user data access, audit trail broken | 🟡 MEDIUM |

---

## What's Broken

### 🔴 Endpoint: `PUT /api/isins/{isin_id}/automation`

This endpoint will **CRASH** when you try to use it because:

1. **No user context** - Doesn't know which user is making the request
2. **Tries to insert to non-existent table** - `isin_strategy_history` doesn't exist
3. **Tries to select non-existent column** - `strategy_name` doesn't exist (should be `name`)
4. **Tries to filter by non-existent column** - `strategy_status` doesn't exist
5. **Tries to read/write non-existent column** - `strategy_id` in `isins` table doesn't exist

### 🟠 Endpoint: `GET /api/isins/strategies`

This endpoint will **CRASH** because:

1. **Tries to filter by non-existent column** - `strategy_status` doesn't exist
2. **Tries to select non-existent column** - `strategy_name` doesn't exist (should be `name`)

---

## Root Cause Analysis

The backend code in `routes/isins.py` was written to expect a database schema that doesn't match the actual schema in `db/supabase_schema.sql`.

**Mismatch Examples:**

| Expected by Code | Actual in Schema | Issue |
|------------------|------------------|-------|
| `isin_strategy_history` table | Doesn't exist | Code tries to INSERT, will fail 404 |
| `isins.strategy_id` column | Doesn't exist | Code tries to UPDATE, will fail FK error |
| `strategies.strategy_name` column | Has `name` instead | Code SELECTs wrong column, will return null |
| `strategies.strategy_status` column | Doesn't exist | Code tries to filter, will fail validation |

**Why did this happen?**
- Schema was defined early in project
- Code was developed in parallel without syncing
- No validation that code matches schema before deployment
- Missing pre-deployment schema audit

---

## How to Fix

### **Option A: Fix Schema (Recommended)** ⭐

Add the 3 missing columns/tables to Supabase:

```sql
-- 1. Add strategy_id to isins
ALTER TABLE isins ADD COLUMN strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL;

-- 2. Add strategy_status to strategies  
ALTER TABLE strategies ADD COLUMN strategy_status VARCHAR DEFAULT 'E' CHECK (strategy_status IN ('E', 'D'));

-- 3. Create isin_strategy_history table
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  isin_id UUID NOT NULL REFERENCES isins(id) ON DELETE CASCADE,
  strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
  automated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE isin_strategy_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own strategy history" ON isin_strategy_history
  FOR SELECT USING (user_id = auth.uid());
```

**Pros:**
- Code works as-is
- Minimal code changes
- Matches original design intent

**Cons:**
- Schema changes need testing
- Must coordinate with production database

**Effort:** Low (5 SQL statements)

---

### **Option B: Fix Code (Alternative)**

Rewrite code to match existing schema:

1. Remove `strategy_status` filter from `get_enabled_strategies()`
2. Replace all `strategy_name` with `name` (5 locations)
3. Remove `strategy_id` from isins operations
4. Don't insert to `isin_strategy_history`

**Pros:**
- No database changes needed
- Faster immediate fix

**Cons:**
- Loses audit trail feature
- Removes strategy assignment capability  
- Requires more code rewrites

**Effort:** High (20+ lines changed, logic altered)

---

## Recommended Path Forward

**Use Option A** (Fix Schema) because:

1. Schema changes are declarative and simple
2. Code already implements the right logic
3. Audit trail is important for compliance
4. Test coverage easier
5. Future features depend on this structure

**Implementation Timeline:**
1. Review this audit report ✓
2. Apply schema migrations to Supabase (5 min)
3. Apply code fixes from remediation guide (10 min)
4. Run tests (5 min)
5. Deploy (2-5 min)

**Total Time:** ~20-30 minutes

---

## Testing Before Deployment

### Must Test:

1. **Unit Tests:**
   - `test_toggle_automation_with_valid_user`
   - `test_toggle_automation_with_invalid_strategy`
   - `test_get_enabled_strategies_filters_correctly`

2. **Integration Tests:**
   - POST /api/auth/login → verify JWT
   - PUT /api/isins/{isin_id}/automation → verify audit record created
   - GET /api/isins/strategies → verify only enabled strategies returned

3. **Security Tests:**
   - User A cannot toggle User B's ISINs
   - Authentication is required
   - RLS policies are enforced

4. **Database Tests:**
   - Verify all columns exist
   - Verify foreign keys work
   - Verify indexes are created

---

## Files Affected

### Database:
- `db/supabase_schema.sql` - **Must add 3 items**

### Backend Code:
- `backend/routes/isins.py` - **Must fix 5 issues**
  - Lines 114, 120, 126, 128, 204, 225, 279, 283, 308-333, 345

### Documentation:
- `BACKEND_AUDIT_REPORT.md` - Generated ✓
- `REMEDIATION_GUIDE.md` - Generated ✓

---

## Detailed Issue Descriptions

### Issue #1: Missing `isin_strategy_history` Table

**Where it breaks:** Line 345 in `toggle_automation` endpoint

```python
db.client.table("isin_strategy_history").insert(audit_data).execute()  # ← Table doesn't exist
```

**What the endpoint is trying to do:**
- Store audit trail of when strategies were assigned to ISINs
- Track automation toggles
- Enable compliance reporting

**Schema to add:**
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
```

---

### Issue #2: Column Named `strategy_name` But Schema Has `name`

**Where it breaks:** 3 locations

1. Line 126: `db.client.table("strategies").select("strategy_name")`
2. Line 204: `db.client.table("strategies").select("id", "strategy_name")`  
3. Line 279: `db.client.table("strategies").select("id", "strategy_name")`

**What happens:**
- Selects non-existent column `strategy_name`
- Returns NULL or empty
- Code tries to `.get("strategy_name")` which fails

**Fix:** Replace `strategy_name` with `name` in all 5 locations

```python
# Line 126 - BEFORE:
strategy_result = db.client.table("strategies").select("strategy_name").eq("id", strategy_id).single().execute()
if strategy_result.data:
    strategy_name = strategy_result.data.get("strategy_name")

# Line 126 - AFTER:
strategy_result = db.client.table("strategies").select("name").eq("id", strategy_id).single().execute()
if strategy_result.data:
    strategy_name = strategy_result.data.get("name")
```

---

### Issue #3: Missing `strategy_status` Column

**Where it breaks:** Line 204 in `get_enabled_strategies`

```python
result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()
```

**What's happening:**
- Trying to filter strategies by `strategy_status = 'E'` (Enabled)
- Column doesn't exist in schema
- Filter will fail with validation error

**Fix:** Add column to schema

```sql
ALTER TABLE strategies ADD COLUMN strategy_status VARCHAR DEFAULT 'E' CHECK (strategy_status IN ('E', 'D'));
```

---

### Issue #4: Missing `strategy_id` Column in `isins`

**Where it breaks:** Lines 114, 120, 314, 324

The code tries to:
1. **Read** `strategy_id` from isins table (line 114)
2. **Write** `strategy_id` to isins table (line 314, 324)

But the column doesn't exist in the schema.

**Fix:** Add column to schema

```sql
ALTER TABLE isins ADD COLUMN strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL;
```

---

### Issue #5: Missing `current_user` Context

**Where it breaks:** Line 225 in `toggle_automation` endpoint

**Security issue:**
- Endpoint doesn't know who the user is
- Could allow User A to toggle automation for User B's ISINs
- Violates RLS policy "Users can update their own ISINs"

**Fix:** Add `current_user` parameter

```python
# BEFORE:
async def toggle_automation(isin_id: str, data: AutomationToggleRequest):

# AFTER:
async def toggle_automation(
    isin_id: str, 
    data: AutomationToggleRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
```

Then use `user_id` in all database operations.

---

## Risk Assessment

### If NOT Fixed Before Deployment:

🔴 **CRITICAL RISKS:**

1. **Automation feature doesn't work** - Core functionality broken
2. **Data corruption** - Wrong users' ISINs could be modified
3. **Audit trail missing** - No compliance record of changes
4. **API crashes** - 500 errors on endpoints
5. **User experience** - Frustrated users, support tickets

### If Fixed Now:

✅ **BENEFITS:**

1. All features work as designed
2. Security is enforced (RLS + user_id filtering)
3. Audit trail is complete
4. Endpoints return proper responses
5. Production-ready code

---

## Sign-Off

**Audit Completed:** 2026-09-17  
**Auditor:** Claude Code  
**Status:** Ready for remediation

**Next Steps:**
1. Review this report with team
2. Approve remediation plan  
3. Execute Phase 1 (schema fixes)
4. Execute Phase 2 (code fixes)
5. Run Phase 3 (testing)
6. Deploy

---

**Questions?** See `BACKEND_AUDIT_REPORT.md` for detailed analysis or `REMEDIATION_GUIDE.md` for step-by-step fixes.
