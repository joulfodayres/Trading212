# Audit Quick Reference Card

**Generated:** 2026-09-17  
**File:** C:\claude\401. Trading 212 Hub\BACKEND_AUDIT_REPORT.md (full details)

---

## 📊 Issues At a Glance

```
TOTAL ISSUES: 5
├─ 🔴 CRITICAL: 3 (will crash)
├─ 🟠 HIGH: 1 (data integrity)
└─ 🟡 MEDIUM: 1 (security)

STATUS: ⚠️ DO NOT DEPLOY
```

---

## 🔴 The 3 Critical Issues

### 1️⃣ Missing Table: `isin_strategy_history`
- **Where:** Line 345 in `backend/routes/isins.py`
- **Error:** `table "isin_strategy_history" does not exist`
- **Fix:** Create table with 5 SQL statements (see remediation guide)
- **Impact:** Cannot save automation audit trail

### 2️⃣ Wrong Column Name: `strategy_name` → should be `name`
- **Where:** Lines 126, 204, 279 in `backend/routes/isins.py`
- **Error:** `column "strategy_name" does not exist`
- **Fix:** Replace text (5 occurrences)
- **Impact:** Cannot read strategy names

### 3️⃣ Missing Column: `strategy_status` in strategies
- **Where:** Line 204 in `backend/routes/isins.py`
- **Error:** `column "strategy_status" does not exist`
- **Fix:** Add 1 column to strategies table
- **Impact:** Cannot filter enabled strategies

---

## 🟠 The 1 High Priority Issue

### 4️⃣ Missing Column: `strategy_id` in isins
- **Where:** Lines 114, 120, 314, 324
- **Error:** `column "strategy_id" does not exist`
- **Fix:** Add 1 column to isins table
- **Impact:** Cannot link ISINs to strategies

---

## 🟡 The 1 Medium Priority Issue

### 5️⃣ Missing User Context in Endpoint
- **Where:** Line 225 in `backend/routes/isins.py`
- **Error:** Cross-user data access possible
- **Fix:** Add `current_user` parameter
- **Impact:** Security vulnerability

---

## ✅ What Needs to Be Done

```
Phase 1: DATABASE (5 minutes)
├─ ALTER TABLE isins ADD COLUMN strategy_id UUID...
├─ ALTER TABLE strategies ADD COLUMN strategy_status VARCHAR...
├─ CREATE TABLE isin_strategy_history (...)
├─ CREATE INDEX ... (3x)
└─ ALTER TABLE ... ENABLE ROW LEVEL SECURITY

Phase 2: CODE (10 minutes)
├─ Fix column names (strategy_name → name) in 5 places
├─ Add current_user parameter to toggle_automation()
├─ Add user_id to INSERT/UPDATE operations
├─ Add user_id to audit trail insert
└─ Add user_id filter to _get_isin_configs()

Phase 3: TESTING (10 minutes)
├─ Syntax check (python -m py_compile)
├─ Import check (python -c "from routes.isins...")
├─ Unit tests (test_isins_fix.py)
└─ Integration tests (against staging DB)
```

---

## 📋 Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `db/supabase_schema.sql` | Add 3 items | 🔴 Critical |
| `backend/routes/isins.py` | Fix 5 issues | 🔴 Critical |

---

## 🧪 Quick Test Commands

```bash
# Syntax check
cd C:\claude\401. Trading 212 Hub\backend
python -m py_compile routes/isins.py

# Import check
python -c "from routes.isins import router; print('OK')"

# Full audit report
cat BACKEND_AUDIT_REPORT.md | head -100
```

---

## 📍 Location Reference

```
Code Issues: backend/routes/isins.py
  ├─ Line 114:      SELECT "strategy_id" from isins
  ├─ Line 120:      GET "strategy_id" from row
  ├─ Line 126:      SELECT "strategy_name" from strategies  ← Wrong name
  ├─ Line 128:      GET "strategy_name" from result
  ├─ Line 204:      SELECT "strategy_name" and filter by "strategy_status"  ← Both wrong
  ├─ Line 225:      Missing current_user dependency
  ├─ Line 279:      SELECT "strategy_name"  ← Wrong name
  ├─ Line 283:      GET "strategy_name"
  ├─ Line 314:      SET "strategy_id" without user_id
  ├─ Line 324:      UPDATE without user_id filter
  └─ Line 345:      INSERT into "isin_strategy_history"  ← Table doesn't exist

Database Issues: db/supabase_schema.sql
  ├─ After isins table:       Missing "strategy_id" column
  ├─ After strategies table:  Missing "strategy_status" column
  └─ After all tables:        Missing "isin_strategy_history" table
```

---

## 🔍 Before vs After

### ❌ BEFORE (Broken)
```python
@router.put("/{isin_id}/automation")
async def toggle_automation(isin_id: str, data: AutomationToggleRequest):
    # No user context - anyone can toggle anyone's ISINs!
    
    result = db.client.table("strategies").select("id", "strategy_name").eq("strategy_status", "E").execute()
    # ❌ strategy_name doesn't exist (should be "name")
    # ❌ strategy_status doesn't exist
    
    isin_data = {
        "isin": isin_id,
        # ❌ No user_id - violates RLS
        "strategy_id": strategy_id,  # ❌ Column doesn't exist
    }
    
    db.client.table("isin_strategy_history").insert(audit_data).execute()
    # ❌ Table doesn't exist
```

### ✅ AFTER (Fixed)
```python
@router.put("/{isin_id}/automation")
async def toggle_automation(
    isin_id: str, 
    data: AutomationToggleRequest,
    current_user: dict = Depends(get_current_user)  # ✓ User context added
):
    user_id = current_user["id"]
    
    result = db.client.table("strategies").select("id", "name").eq("strategy_status", "E").execute()
    # ✓ Uses correct "name" column
    # ✓ strategy_status now exists
    
    isin_data = {
        "user_id": user_id,  # ✓ Added for RLS
        "isin": isin_id,
        "strategy_id": strategy_id,  # ✓ Column now exists
    }
    
    db.client.table("isin_strategy_history").insert(audit_data).execute()
    # ✓ Table now exists
```

---

## 🚀 Deployment Checklist

- [ ] Read AUDIT_SUMMARY.md (this file)
- [ ] Read BACKEND_AUDIT_REPORT.md (detailed analysis)
- [ ] Read REMEDIATION_GUIDE.md (step-by-step fixes)
- [ ] Apply database migrations
- [ ] Verify migrations succeeded
- [ ] Apply code fixes
- [ ] Run syntax check
- [ ] Run import check
- [ ] Run unit tests
- [ ] Deploy to staging
- [ ] Run integration tests on staging
- [ ] Code review
- [ ] Deploy to production
- [ ] Monitor logs

---

## 📞 Getting Help

1. **Need details?** → See `BACKEND_AUDIT_REPORT.md`
2. **Need steps?** → See `REMEDIATION_GUIDE.md`
3. **Need quick ref?** → This file
4. **Need code diffs?** → See REMEDIATION_GUIDE.md Phase 2

---

## ⏰ Time Estimate

```
Schema changes:       ~5 minutes
Code changes:        ~10 minutes
Testing:             ~10 minutes
Review & approval:   ~15 minutes (depends on team)
────────────────────────────────
TOTAL:              ~40 minutes (critical path)
```

---

## 🎯 Key Takeaways

| Point | Status |
|-------|--------|
| Code matches schema? | ❌ NO - 5 mismatches |
| Will it deploy? | ❌ NO - will crash |
| Can it be fixed? | ✅ YES - easy fixes |
| How long to fix? | ⏱️ ~30 minutes |
| Is it secure? | ⚠️ NO - missing user_id filter |
| After fixes: | ✅ PRODUCTION READY |

---

**Last Updated:** 2026-09-17  
**Full Report:** See BACKEND_AUDIT_REPORT.md  
**Action Plan:** See REMEDIATION_GUIDE.md
