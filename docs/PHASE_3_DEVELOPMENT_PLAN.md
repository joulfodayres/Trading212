# 🚀 Phase 3 Development Plan - Funcionalidades

**Date:** 2026-09-16  
**Status:** ✅ Login Working → Now implementing features  
**User:** teste@trading212.com (dev mode)

---

## 📊 **Current State Assessment**

### ✅ What's Working:
- ✅ Login flow (dev-mode bypass in Render)
- ✅ Frontend routing (Login → Dashboard)
- ✅ Dashboard UI (sidebar, ISINs table, config page)
- ✅ Backend structure (FastAPI + Supabase + T212 API)
- ✅ API endpoints skeleton (GET/POST/PUT/DELETE /isins)

### ⚠️ What's Mock/Partial:
- ⚠️ ISINs list returns **empty** (no data in Supabase)
- ⚠️ T212 API integration has **mock data** (not real API calls)
- ⚠️ JWT token extraction from frontend **not implemented** (using TEST_USER_ID hardcoded)
- ⚠️ Automation toggle exists but **no scheduler backend**
- ⚠️ Sync with T212 endpoint exists but **mock implementation**

### ❌ What's Not Done:
- ❌ Real T212 credentials storage/encryption
- ❌ Grid Trading strategy logic
- ❌ APScheduler for automated trades
- ❌ WebSocket for real-time updates
- ❌ P&L calculations from real trades

---

## 🎯 **Phase 3 Roadmap (Priority Order)**

### **Sprint 1: Connect Frontend to Real Backend (TODAY/TOMORROW)**

#### 1.1: Extract JWT Token & Get Real user_id ⭐ HIGH PRIORITY
- **Problem:** Backend uses hardcoded `TEST_USER_ID` for all users
- **Goal:** Extract user_id from JWT token, use real user_id from DB
- **Work:**
  - Modify `/api/isins` endpoints to get `user_id` from JWT (not hardcoded)
  - Add `Depends(get_current_user)` to all protected routes
  - Update backend to use real user_id in all queries
  - Test: Each logged-in user should see their own ISINs (not shared)

**Files to change:**
- `backend/routes/isins.py` - Add JWT dependency
- `backend/routes/auth.py` - Already has `get_current_user()`

---

#### 1.2: Test ISINs Endpoints with Real User ⭐ HIGH PRIORITY
- **Problem:** No ISINs in database for test user
- **Goal:** Add test data and verify CRUD works
- **Work:**
  - Create script to insert test ISINs for `teste@trading212.com`
  - Test GET `/api/isins` returns the data
  - Test POST `/api/isins` to add new ISIN
  - Test PUT to toggle automation
  - Test DELETE to remove ISIN

**Files to create:**
- `backend/seed_test_data.py` - Insert test ISINs

---

### **Sprint 2: Mock Data → Real T212 Integration (NEXT)**

#### 2.1: Mock T212 Data to Realistic Values
- **Problem:** All ISINs return same mock data ("Vanguard FTSE All-World")
- **Goal:** Show different ISINs with appropriate data
- **Work:**
  - Create mock database of ISINs (VWRX, VUSA, CSSPX, etc)
  - Return appropriate data for each ISIN code
  - Implement basic T212 search (mock for now)

---

#### 2.2: Connect Real T212 API
- **Problem:** T212 API calls are stubbed with mock data
- **Goal:** Fetch real instrument data from T212
- **Work:**
  - Test T212 API client with actual credentials
  - Implement `search_instrument()` function
  - Get real ticker, name, currency for ISINs
  - Handle T212 API errors gracefully

---

### **Sprint 3: Automation Setup (NEXT WEEK)**

#### 3.1: Configure T212 Credentials
- Store encrypted T212 API key + secret per user
- GET/POST `/api/config` endpoints
- Test with actual T212 account

#### 3.2: Grid Trading Strategy
- Implement buy/sell logic
- Calculate grid levels
- Execute trades via T212 API

#### 3.3: APScheduler Integration
- Run trades every 5 minutes
- Check market conditions
- Execute orders if conditions met

---

## 📋 **Immediate Next Steps (Next 30 mins)**

### **Option A: Quick Win - Test Current Endpoints** ⭐ RECOMMENDED
1. Add sample ISINs to Supabase (manually or via script)
2. Test if frontend loads them
3. Test POST/PUT/DELETE endpoints
4. See dashboard populate with real data

**Time: ~15 mins**
**Result: Dashboard looks "alive" with ISINs**

### **Option B: Backend Refactor - JWT Extract** ⭐ BETTER FOR PRODUCTION
1. Modify isins.py to use JWT token (not hardcoded TEST_USER_ID)
2. Add `Depends(get_current_user)` to all routes
3. Test with curl to verify multi-user safety
4. Each user sees only their own ISINs

**Time: ~30 mins**
**Result: Multi-user safe, real user isolation**

### **Option C: Both** ⭐ COMPREHENSIVE
1. Do Option B first (JWT extract)
2. Then do Option A (test data)

**Time: ~45 mins**
**Result: Production-ready + working UI**

---

## 🎯 **My Recommendation**

**Do Option C (Both) in this order:**

1. **15 mins - Refactor JWT handling** (backend safety first)
   - Modify `backend/routes/isins.py`
   - Add `Depends(get_current_user)` 
   - Use real `user_id` instead of `TEST_USER_ID`

2. **10 mins - Create test data script**
   - Create `backend/seed_test_data.py`
   - Insert 3-5 test ISINs for `teste@trading212.com`

3. **5 mins - Test in browser**
   - Refresh dashboard
   - See ISINs load
   - Try adding/deleting/toggling

4. **5 mins - Commit & Push**
   - Git commit with clear message
   - Auto-deploy to Render

---

## 📊 **Success Criteria**

After Phase 3 Sprint 1:
- ✅ User JWT token extracted and used
- ✅ Each user sees only their own data (multi-user safe)
- ✅ Dashboard shows real ISINs (not mock)
- ✅ Add/Delete/Edit ISINs works end-to-end
- ✅ Toggle automation UI works (backend not needed yet)

---

## 🚀 **What Would You Like to Do?**

1. **Option A:** Add test data to dashboard (5 mins, UI focused)
2. **Option B:** Refactor JWT handling (30 mins, backend safety)
3. **Option C:** Do both (45 mins, comprehensive)
4. **Something else?** Tell me what interests you

---

**What shall we tackle first?** 🤔
