# Automation Toggle Endpoints

## Overview

Two new endpoints have been implemented in `backend/routes/isins.py` to support automation toggling for ISINs with strategy association.

---

## Endpoint 1: GET /api/isins/strategies

**Purpose:** Fetch enabled strategies for selection in the automation toggle dialog.

### Request
```http
GET /api/isins/strategies
```

### Response (200 OK)
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "strategy_name": "Grid Trading Strategy"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "strategy_name": "RSI Breakout"
  }
]
```

### Response Schema
```python
class StrategyOption(BaseModel):
    id: str                    # UUID of the strategy
    strategy_name: str         # Name of the strategy
```

### Error Responses

**500 Internal Server Error**
```json
{
  "detail": "Erro ao buscar estratégias: [error details]"
}
```

### Notes
- Returns only strategies with `strategy_status = 'E'` (Enabled)
- Queries the `strategies` table
- Used to populate dropdown/list in automation UI

---

## Endpoint 2: PUT /api/isins/{isin_id}/automation

**Purpose:** Toggle automation for a specific ISIN and associate a strategy.

### Request
```http
PUT /api/isins/{isin_id}/automation
Content-Type: application/json

{
  "automation_enabled": true,
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Request Schema
```python
class AutomationToggleRequest(BaseModel):
    automation_enabled: bool       # Enable/disable automation
    strategy_id: Optional[str]     # UUID of strategy (required if automation_enabled=true)
```

### Response (200 OK)
```json
{
  "isin_id": "550e8400-e29b-41d4-a716-446655440000",
  "automation_enabled": true,
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "strategy_name": "Grid Trading Strategy"
}
```

### Response Schema
```python
class AutomationUpdateResponse(BaseModel):
    isin_id: str                   # UUID of the ISIN record in DB
    automation_enabled: bool       # Current automation status
    strategy_id: Optional[str]     # Associated strategy ID (null if disabled)
    strategy_name: Optional[str]   # Associated strategy name (null if disabled)
```

### Error Responses

**400 Bad Request** - Missing strategy_id when enabling automation
```json
{
  "detail": "strategy_id é obrigatório quando automation_enabled=true"
}
```

**404 Not Found** - ISIN not in T212 positions
```json
{
  "detail": "ISIN {isin_id} não encontrado nas posições da T212"
}
```

**404 Not Found** - Strategy not found
```json
{
  "detail": "Estratégia {strategy_id} não encontrada"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Erro ao alternar automação: [error details]"
}
```

---

## Business Logic

### Flow when `automation_enabled=true`:

1. ✅ Validates that ISIN exists in T212 positions (source of truth)
2. ✅ Validates that strategy_id exists in `strategies` table
3. ✅ If ISIN exists in `isins` table → UPDATE
4. ✅ If ISIN doesn't exist → INSERT with data from T212 position
5. ✅ Creates audit record in `isin_strategy_history` table
6. ✅ Returns updated configuration with strategy details

### Flow when `automation_enabled=false`:

1. ✅ Validates that ISIN exists in T212 positions
2. ✅ Updates `isins` table: `automation_enabled=false, strategy_id=null`
3. ✅ Creates audit record in `isin_strategy_history` table
4. ✅ Returns updated configuration

### Data Written to Database

**`isins` table (UPDATE or INSERT):**
```sql
{
  "isin": "IE00B4L5Y983",
  "ticker": "VWRL",
  "name": "Vanguard FTSE All-World",
  "currency": "EUR",
  "automation_enabled": true,
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "updated_at": "2026-09-17 10:30:00"
}
```

**`isin_strategy_history` table (INSERT for audit trail):**
```sql
{
  "isin_id": "550e8400-e29b-41d4-a716-446655440000",
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "automated": true,
  "created_at": "2026-09-17 10:30:00",
  "updated_at": "2026-09-17 10:30:00"
}
```

---

## Frontend Integration Examples

### React/TypeScript Example

```typescript
// Enable automation
const toggleAutomation = async (isinId: string, strategyId: string) => {
  try {
    const response = await fetch(`/api/isins/${isinId}/automation`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        automation_enabled: true,
        strategy_id: strategyId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('Automation enabled:', result);
    return result;
  } catch (error) {
    console.error('Failed to toggle automation:', error);
  }
};

// Fetch available strategies for dropdown
const loadStrategies = async () => {
  try {
    const response = await fetch('/api/isins/strategies');
    const strategies = await response.json();
    // Populate UI dropdown
  } catch (error) {
    console.error('Failed to load strategies:', error);
  }
};
```

### cURL Examples

**Fetch enabled strategies:**
```bash
curl -X GET https://trading212-backend.onrender.com/api/isins/strategies \
  -H "Content-Type: application/json"
```

**Enable automation:**
```bash
curl -X PUT https://trading212-backend.onrender.com/api/isins/IE00B4L5Y983/automation \
  -H "Content-Type: application/json" \
  -d '{
    "automation_enabled": true,
    "strategy_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Disable automation:**
```bash
curl -X PUT https://trading212-backend.onrender.com/api/isins/IE00B4L5Y983/automation \
  -H "Content-Type: application/json" \
  -d '{
    "automation_enabled": false,
    "strategy_id": null
  }'
```

---

## Implementation Details

### Code Location
- **File:** `backend/routes/isins.py`
- **Lines:** 294-471 (new automation endpoints)
- **Lines:** 70-87 (new schemas)

### Dependencies Used
- `fastapi.APIRouter` - Route registration
- `fastapi.HTTPException` - Error handling
- `pydantic.BaseModel` - Schema validation
- `logging` - Audit trail
- `db.client` - Supabase client (already imported)
- `get_t212_client()` - Trading212 API client

### Logging
All operations are logged with proper context:
- ✅ Fetching strategies
- ✅ Toggling automation
- ✅ ISIN validation
- ✅ Database operations
- ✅ Audit trail creation
- ✅ Error details

### Error Handling
- HTTPException with proper status codes (400, 404, 500)
- Audit failures don't fail the entire operation
- All exceptions are logged with `exc_info=True`

---

## Database Requirements

### Tables Used
1. **`strategies`** - Read access
   - Columns: `id`, `name`, `strategy_status`
   - Filter: `strategy_status = 'E'`

2. **`isins`** - Read/Write access
   - Columns: `id`, `isin`, `ticker`, `name`, `currency`, `automation_enabled`, `strategy_id`, `updated_at`
   - Operations: SELECT, INSERT, UPDATE

3. **`isin_strategy_history`** - Write access (audit trail)
   - Columns: `isin_id`, `strategy_id`, `automated`, `created_at`, `updated_at`
   - Operations: INSERT

### Expected Row-Level Security (RLS)
- Should be filtered by `user_id` (not yet implemented in current endpoints)
- Consider adding user_id parameter for multi-tenant support in Phase 6

---

## Testing Checklist

- [ ] GET /api/isins/strategies returns enabled strategies only
- [ ] PUT /api/isins/{isin_id}/automation with valid strategy_id enables automation
- [ ] PUT /api/isins/{isin_id}/automation with automation_enabled=false disables automation
- [ ] Missing strategy_id when automation_enabled=true returns 400
- [ ] Invalid ISIN returns 404
- [ ] Invalid strategy_id returns 404
- [ ] Audit records are created in isin_strategy_history
- [ ] Existing ISIN records are updated (not inserted twice)
- [ ] New ISIN records are inserted with T212 metadata
- [ ] All errors are logged properly

---

## Future Enhancements

1. **Authentication:** Add `current_user` parameter from JWT
2. **Multi-tenancy:** Filter strategies/isins by user_id
3. **Webhooks:** Notify frontend on automation status changes
4. **Batch operations:** Enable/disable automation for multiple ISINs
5. **History view:** Fetch isin_strategy_history for audit trail display
6. **Strategy details:** Return more strategy info (parameters, last run, etc.)

---

**Last Updated:** 2026-09-17
**Status:** ✅ Ready for integration
