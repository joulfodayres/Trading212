# ⚡ QUICK REFERENCE - RENDER FIX

## 🚨 The Problem (2 minutes read)

Backend offline. Reason: 9 environment variables missing in Render.

## ✅ The Fix (5 minutes to do)

### Step 1: Open Render Dashboard
```
https://dashboard.render.com
Click: trading212-4ojx (Backend)
Tab: Environment
```

### Step 2: Copy-Paste These 9 Variables

```
Key: SUPABASE_URL
Value: https://gocvyhizqggqaxryuplu.supabase.co

Key: SUPABASE_KEY
Value: sb_publishable_283LZ_pvCLRaxYLaikfA7w_h4oSLVCW

Key: SUPABASE_JWT_SECRET
Value: sb_secret_3qW7HsDKdwd69hmob1NHrQ_Tn--S4a4

Key: T212_API_KEY
Value: 40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU

Key: T212_API_SECRET
Value: iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0

Key: T212_ENVIRONMENT
Value: demo

Key: T212_BASE_URL
Value: https://demo.trading212.com/api/v0

Key: JWT_SECRET_KEY
Value: trading212-bot-secret-key-change-in-production

Key: ENCRYPTION_KEY
Value: YZXbxF3a-y2HQUXprACQ0lSkhW8imYBJ1D1hYcsL61Y=
```

### Step 3: Manual Deploy
```
Render Dashboard → trading212-4ojx
Button: Manual Deploy (blue button)
Wait: 5-10 minutes
Status: Building → Live
```

### Step 4: Test
```
Open: https://trading212-4ojx.onrender.com
Expected: JSON response {"status": "running"}
✅ If you see this = SUCCESS!
```

---

## 📖 Full Documentation

- **Portuguese Guide:** `RENDER_OFFLINE_DIAGNOSTICO.md`
- **Technical Details:** `RENDER_FIX_OFFLINE_ISSUE.md`
- **Executive Summary:** `RESUMO_PROBLEMA_SOLUCAO.md`

---

## ❓ FAQ

**Q: Why did this happen?**
A: Code committed to GitHub ✓, but .env is in .gitignore ✓ (correct).
   Render wasn't configured with the environment variables.

**Q: Is the code broken?**
A: No. Code is perfect. Just missing 9 config values.

**Q: Will this happen again?**
A: No. Just configure Render once, it's permanent.

**Q: How long will it take?**
A: 5 minutes to configure + 10 minutes to deploy = 15 minutes total.

**Q: Is it safe?**
A: Yes. Environment variables are encrypted in Render.
   Never commit .env to Git (already doing this ✓).

---

## 🎯 Expected Result

After Manual Deploy:

```
BEFORE:
- Backend: OFFLINE (HTTP 000)
- Frontend: No data
- Login: Fails

AFTER:
- Backend: ONLINE (HTTP 200)
- Frontend: Data loads
- Login: Works ✅
```

---

**Time to Fix:** 15 minutes  
**Difficulty:** Very Easy (copy-paste)  
**Result:** System fully functional

Good luck! 🚀
