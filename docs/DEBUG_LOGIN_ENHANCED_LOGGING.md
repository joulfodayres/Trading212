# 🔍 Debug Login Issue - Enhanced Logging

**Date:** 2026-09-16  
**Issue:** Login page not transitioning to dashboard - error message appears too briefly  
**Solution:** Added comprehensive debug logging to identify the exact failure point

---

## 🛠️ Changes Made

### 1. **LoginPage.tsx** - Enhanced Error Handling
- ✅ Added `console.log()` before login attempt
- ✅ Added `console.error()` with full error details
- ✅ Error message now stays visible for 5 seconds (instead of disappearing immediately)
- ✅ Logs: email, error message, full error object

### 2. **authStore.ts** - Request/Response Logging
- ✅ Logs when login request starts
- ✅ Logs when response is received (status, data)
- ✅ Logs when token is saved to localStorage
- ✅ Logs when state is updated
- ✅ Detailed error logging with status code, backend detail, and full error

### 3. **client.ts** - HTTP Client Logging
- ✅ Logs API base URL on initialization
- ✅ Logs every request (URL, method)
- ✅ Logs every successful response (status)
- ✅ Logs every error response (status, backend detail)
- ✅ Logs when token is added to headers
- ✅ Logs when 401 errors trigger redirect

---

## 🚀 How to Test Now

### **Terminal 1: Backend**
```bash
cd "C:\claude\401. Trading 212 Hub\backend"
python main.py
# Should see: "Application startup complete"
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

### **Terminal 2: Frontend**
```bash
cd "C:\claude\401. Trading 212 Hub\frontend"
npm install  # Only first time
npm run dev
# Should see: "VITE v... ready in ... ms"
# Should see: "Local: http://localhost:5173"
```

### **Browser: F12 Console + Network**
1. Open http://localhost:5173
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Go to **Network** tab and select **Fetch/XHR**
5. Enter credentials:
   - Email: `teste@trading212.com`
   - Password: `teste123` (or anything in dev mode)
6. Click "Entrar"

### **Expected Console Output**
You should see (in order):

```
[apiClient] Initializing with API_BASE: http://localhost:8000
[apiClient.request] Making request to: /auth/login method: post
[LoginPage] Attempting login with email: teste@trading212.com
[authStore.login] Starting login request to /api/auth/login
[apiClient.response] Received response from: /auth/login status: 200
[authStore.login] Login response received: 200 {...data...}
[authStore.login] Token received, saving to localStorage
[authStore.login] Login state updated successfully
[LoginPage] Login successful, navigating to dashboard
```

### **If Error Occurs**
Console will show something like:
```
[apiClient.response] Error response: {
  url: '/auth/login',
  status: 401,
  detail: 'Email ou password inválidos',
  message: '...'
}
[authStore.login] Login error: {...}
[LoginPage] Login error: {...}
```

---

## 📊 Expected Behavior

| Step | Result | Evidence |
|------|--------|----------|
| Click "Entrar" | No immediate redirect | See console logs starting |
| Backend processes | Response received | Console shows status 200 or error |
| Token saved | localStorage has 'token' key | F12 → Application → Local Storage |
| Navigate to dashboard | Browser URL changes to /dashboard | Console shows "Login successful" |
| Dashboard loads | ISINs displayed | Page shows table with data |

---

## 🐛 Common Issues & Solutions

### **Issue: All requests go to `/api` but backend doesn't respond**
- **Cause:** Backend might be crashing or not listening on 8000
- **Check:** Terminal 1 shows "Uvicorn running on http://0.0.0.0:8000"?

### **Issue: Console shows "Network Error" or "Failed to fetch"**
- **Cause:** Backend port conflict or CORS issue
- **Check:** Kill old Python processes: `Get-Process python | Stop-Process -Force`

### **Issue: 401 Unauthorized from backend**
- **Cause:** Email doesn't match "teste@trading212.com" or backend not in dev mode
- **Check:** Backend `.env` has `FASTAPI_ENV=development`

### **Issue: Error message appears but quickly disappears**
- **Before:** Error cleared immediately ❌
- **After:** Error stays for 5 seconds ✅
- **Still not enough?** Can increase to 10000ms in LoginPage.tsx line: `setTimeout(..., 5000)`

---

## 📡 Network Tab Details

When you click "Entrar", you should see:

**POST /auth/login**
- **Headers:** 
  - Content-Type: application/json
  - No Authorization header yet (not logged in)
- **Request Body:**
  ```json
  {"email":"teste@trading212.com","password":"teste123"}
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user_id": "17780beb-e61f-4604-ba5a-b6329312ac90",
    "email": "teste@trading212.com",
    "message": "Login bem-sucedido (modo desenvolvimento)"
  }
  ```

After successful login:

**GET /isins** (or other API calls)
- **Headers:**
  - Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - (Token added automatically by interceptor)

---

## 🎯 Next Steps

1. **Run both backends with new code**
2. **Open F12 Console while logging in**
3. **Copy all console output and send it**
4. **Tell me:**
   - ✅ Does it show "Login successful"?
   - ✅ Does it navigate to /dashboard?
   - ❌ Or does it show an error? Which one?

This enhanced logging will help us pinpoint **exactly where** the login flow is breaking.

---

## 📝 Git Info

**Files Modified:**
- `frontend/src/pages/LoginPage.tsx` - Added logging + error visibility
- `frontend/src/stores/authStore.ts` - Added request/response logging
- `frontend/src/api/client.ts` - Added HTTP client logging

**Commit:** (Ready to commit after you confirm changes work)

---

**Let's find that bug! 🔍🐛**
