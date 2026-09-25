# Trading 212 Bot - Troubleshooting Guide

## Startup Issues

### Backend won't start

**Error: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Or reinstall from scratch
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

**Error: "Could not connect to Supabase"**
```bash
# Check .env file
cat .env

# Verify credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection manually
python -c "from db.supabase_client import get_db; db = get_db(); print('Connected!')"

# If fails: Check Supabase dashboard for URL/key
# https://supabase.com/dashboard -> Project Settings -> API
```

**Error: "Port 8000 already in use"**
```bash
# Find process using port 8000
lsof -i :8000
# or on Windows
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>
# or on Windows
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

**Error: "ValueError: ENCRYPTION_KEY not found in .env"**
```bash
# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
ENCRYPTION_KEY=<generated-key>
```

### Frontend won't start

**Error: "npm ERR! Could not resolve dependency"**
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Error: "Port 5173 already in use"**
```bash
# Kill process on port 5173
lsof -i :5173 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

---

## Authentication Issues

### "Not authenticated" error on API calls

**Frontend:**
```typescript
// Check if token is in localStorage
console.log(localStorage.getItem('auth_token'))

// Check if header is sent
// Open DevTools > Network > select request > Headers
// Look for: Authorization: Bearer <token>
```

**Backend:**
```python
# Check JWT validation
# Add debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload

# Verify token
import jwt
from config.settings import settings

token = "..."
try:
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    print("Token valid:", payload)
except jwt.InvalidTokenError as e:
    print("Token invalid:", e)
```

**Solution:**
1. Login again to get fresh token
2. Check token expiration: `settings.JWT_EXPIRATION_HOURS`
3. Verify JWT_SECRET_KEY matches in .env

---

## Database Issues

### "Column 'X' not found"

**Error: `psycopg2.errors.UndefinedColumn: column "x" does not exist`**

This means the column doesn't exist in the database schema.

**Solution:**
1. Check Supabase Schema Editor for the table
2. If column missing, run migration or add manually:
   ```sql
   ALTER TABLE isins ADD COLUMN new_column_name TYPE;
   ```
3. Restart backend to reload models

**Migrations in Supabase:**
```bash
# Create migration script
alembic revision --autogenerate -m "Add new column"

# View migration
cat alembic/versions/<migration>.py

# Apply migration (if using Alembic locally)
# Note: Supabase doesn't sync migrations, must do manually

# Or execute SQL directly in Supabase dashboard
```

### "Foreign key constraint violated"

**Error: `psycopg2.errors.ForeignKeyViolation: insert or update on table "orders" violates foreign key constraint`**

**Solution:**
1. Check that referenced record exists
   ```sql
   SELECT * FROM isins WHERE id = 'the-isin-id';
   ```
2. If not exists, create it first
3. Or use cascade delete if parent is deleted
   ```sql
   ALTER TABLE orders
   DROP CONSTRAINT orders_isin_id_fkey,
   ADD CONSTRAINT orders_isin_id_fkey
   FOREIGN KEY (isin_id) REFERENCES isins(id) ON DELETE CASCADE;
   ```

### Row Level Security (RLS) blocking queries

**Error: `policy "..." violates row level security policy"`**

This means the current user doesn't have permission to access the data.

**Solution:**
1. Check RLS policies in Supabase:
   - Dashboard → Tables → Select table → Row Security Policies
2. Verify policy allows the operation
3. Check that `user_id` in data matches authenticated user
4. Temporarily disable RLS for testing:
   ```sql
   ALTER TABLE isins DISABLE ROW LEVEL SECURITY;
   ```
5. Don't do #4 in production!

---

## Automation Engine Issues

### Scheduler not running

**Check status:**
```bash
curl http://localhost:8000/api/v1/automation/status
```

**Response should be:**
```json
{
  "scheduler_running": true,
  "cycle_count": 5,
  "last_cycle_at": "2026-09-20T14:32:15Z"
}
```

**If `scheduler_running: false`:**

1. Check backend logs:
   ```bash
   # Render: Dashboard → Logs tab
   # Local: Console output
   ```

2. Verify app_parameters:
   ```bash
   curl http://localhost:8000/api/v1/automation/global-status
   ```
   Should show `"grid_trading_enabled": true`

3. Enable automation:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/automation/enable
   ```

4. Restart backend if needed

### Orders not being placed

**Check:**
1. Is automation enabled globally?
   ```bash
   curl http://localhost:8000/api/v1/automation/global-status
   ```

2. Is ISIN automation enabled?
   ```bash
   curl http://localhost:8000/api/isins
   # Check: "automation_enabled": true
   ```

3. Does ISIN have a strategy?
   ```bash
   curl http://localhost:8000/api/isins
   # Check: "strategy_id" is not null
   ```

4. Is strategy enabled and valid?
   ```bash
   curl http://localhost:8000/api/v1/strategies/<id>
   # Check: "enabled": true, "is_valid": true
   ```

5. Check backend logs for errors:
   ```bash
   LOG_LEVEL=DEBUG uvicorn main:app --reload
   # Look for: ERROR, Exception, Traceback
   ```

### T212 API errors

**Error: "401 Unauthorized"**
```
Solution: Check API credentials in .env
- T212_API_KEY
- T212_API_SECRET
- T212_ENVIRONMENT (demo vs live)

Verify in T212 dashboard that API keys are correct.
```

**Error: "429 Too Many Requests"**
```
T212 has rate limits:
- Positions: 1 req/1s
- Orders: 50 req/1m
- History: 6 req/1m

Solution: Backend handles automatic backoff.
Check logs: "Rate limit, retrying..."
Increase delay_between_requests if needed.
```

**Error: "400 Bad Request"**
```
Possible causes:
1. Invalid quantity (usually < 1)
2. Price too far from market
3. Order size too large
4. Invalid ticker/ISIN

Check backend logs for exact error.
```

### Strategy not valid

**Error: "Cannot enable strategy. Missing parameters for pos: -1, 0, 1"**

**Solution:**
1. Go to Strategies page in frontend
2. Select the strategy
3. Look for the "Parâmetros" table
4. Add missing positions (pos = "-1", "0", or "1")
5. Try enabling again

**Or via API:**
```bash
# Check strategy
curl http://localhost:8000/api/v1/strategies/<strategy-id>

# If is_valid=false, missing parameters

# Add missing parameter
curl -X POST http://localhost:8000/api/v1/strategies/<strategy-id>/parameters \
  -H "Content-Type: application/json" \
  -d '{
    "pos": "-1",
    "param1": -1.0,
    "param2": 1.0
  }'

# Try enabling again
curl -X PUT http://localhost:8000/api/v1/strategies/<strategy-id> \
  -d '{"enabled": true}'
```

---

## Frontend Issues

### Page blank or not loading

**Check browser console (F12):**
- Look for JavaScript errors
- Check Network tab for failed requests
- Check if API_URL is correct

**Solution:**
```bash
# Verify .env.local has correct API URL
cat frontend/.env.local

# Should be:
# VITE_API_URL=http://localhost:8000  (local)
# or
# VITE_API_URL=https://trading212-backend.onrender.com  (production)

# Rebuild frontend
npm run build
npm run preview
```

### API calls returning 404

**Error: "GET /api/v1/strategies 404 Not Found"**

**Causes:**
1. Backend not running
2. Wrong API URL in frontend
3. Typo in endpoint path

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# If fails, start backend:
cd backend
uvicorn main:app --reload

# Check API_URL in frontend
echo $VITE_API_URL
# Should be http://localhost:8000 locally

# Test endpoint directly
curl http://localhost:8000/api/v1/strategies
```

### State not updating after action

**Example: Create strategy, but list doesn't update**

**Solution:**
```typescript
// Check if component is re-fetching data
useEffect(() => {
  loadStrategies()
}, []) // This only runs once on mount

// Add refetch trigger
const [refetchKey, setRefetchKey] = useState(0)

useEffect(() => {
  loadStrategies()
}, [refetchKey])

// After creating strategy
const handleCreate = async () => {
  await apiClient.post('/v1/strategies', data)
  setRefetchKey(prev => prev + 1) // Trigger refetch
}
```

---

## Render Deployment Issues

### Deployment takes too long

**Backend deployment > 20 minutes:**
1. Check Render dashboard → Logs
2. Look for `pip install` taking long time
3. Solution: Clear cache in Render settings

**Frontend deployment > 30 minutes:**
1. Check build output for errors
2. Look for `npm install` taking long time
3. Solution: Use npm ci instead of npm install (faster)

### App crashes after deploy

**Error: "Application crashed"**

1. Check Render dashboard → Logs
2. Look for error message
3. Common causes:
   - Missing environment variable
   - Database connection failed
   - Import error in Python

**Solution:**
1. Add missing env vars to Render dashboard
2. Verify database is online
3. Test locally first

### Frontend not showing latest code

**Solution:**
1. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
2. Clear browser cache
3. Check Render deployment status (should show "Live")

---

## Performance Issues

### Slow API responses (>5s)

**Check:**
1. Database query performance
   ```sql
   EXPLAIN ANALYZE SELECT * FROM isins WHERE automation_enabled = true;
   ```

2. T212 API delays
   - Add logging to see how long requests take

3. Network latency
   - Use Render metrics to check

**Solution:**
1. Add database indexes:
   ```sql
   CREATE INDEX idx_isins_automation ON isins(automation_enabled);
   ```

2. Optimize queries:
   ```python
   # Bad: N+1 queries
   for isin in isins:
       print(isin.strategy.name)  # Extra query per isin

   # Good: Join
   isins = db.query(ISIN).join(Strategy).all()
   ```

3. Cache responses:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def get_strategies():
       return db.query(Strategy).all()
   ```

### High memory usage

**Check Render metrics:**
1. Dashboard → Backend → Metrics
2. Look for Memory % trending up

**Solution:**
1. Restart service (Render → More → Restart)
2. Optimize automation engine (reduce cycle frequency)
3. Add pagination to list endpoints

---

## Getting Help

### Check logs

```bash
# Backend (local)
LOG_LEVEL=DEBUG uvicorn main:app --reload

# Backend (Render)
# Dashboard → Backend → Logs tab → View in browser/CLI

# Frontend (local)
# Browser Console (F12)

# Frontend (Render)
# Dashboard → Frontend → Logs tab
```

### Debug endpoints

```bash
# Health check
curl http://localhost:8000/health

# App status
curl http://localhost:8000/

# Automation status
curl http://localhost:8000/api/v1/automation/status

# Database connection
curl http://localhost:8000/api/isins/sync
```

### Common fixes

1. Restart backend: `Ctrl+C`, then `uvicorn main:app --reload`
2. Restart frontend: `Ctrl+C`, then `npm run dev`
3. Clear database cache: Redeploy backend
4. Clear frontend cache: Hard refresh (Ctrl+F5)

---

**Last Updated:** 2026-09-20
**Need help?** Check backend logs first, then frontend console
