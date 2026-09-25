# Trading 212 Bot - API Reference

## Base URL
- **Production:** `https://trading212-backend.onrender.com`
- **Local:** `http://localhost:8000`

## Authentication
All endpoints require JWT token from Supabase Auth (passed in `Authorization: Bearer <token>` header).

---

## Strategies Management

### List Strategies
```
GET /api/v1/strategies
```

**Response (200 OK):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Grid Trading 1%",
    "description": "Estratégia de grid com 1% de spread",
    "initial_investment": 10.0,
    "enabled": false,
    "is_valid": true,
    "created_at": "2026-09-20T14:30:00Z",
    "updated_at": "2026-09-20T14:30:00Z"
  }
]
```

**Query Parameters:** None

**Error (401 Unauthorized):**
```json
{ "detail": "Not authenticated" }
```

---

### Get Strategy with Parameters
```
GET /api/v1/strategies/{strategy_id}
```

**Path Parameters:**
- `strategy_id` (UUID): Strategy ID

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Grid Trading 1%",
  "description": "...",
  "initial_investment": 10.0,
  "enabled": false,
  "is_valid": true,
  "created_at": "2026-09-20T14:30:00Z",
  "updated_at": "2026-09-20T14:30:00Z",
  "parameters": [
    {
      "id": "456e1234-b12c-56d7-a890-426614174001",
      "pos": "0",
      "param1": -1.0,
      "param2": 1.0,
      "param3": null,
      ...
      "param10": null
    }
  ]
}
```

---

### Create Strategy
```
POST /api/v1/strategies
```

**Request Body:**
```json
{
  "name": "Grid Trading 1%",
  "description": "Estratégia com spreads 1% para cima/baixo",
  "initial_investment": 10.0
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Grid Trading 1%",
  "description": "...",
  "initial_investment": 10.0,
  "enabled": false,
  "is_valid": false,
  "created_at": "2026-09-20T14:30:00Z",
  "updated_at": "2026-09-20T14:30:00Z"
}
```

**Validation Errors (400 Bad Request):**
```json
{
  "detail": "name must be provided"
}
```

---

### Update Strategy
```
PUT /api/v1/strategies/{strategy_id}
```

**Request Body:**
```json
{
  "name": "Grid Trading 2%",
  "description": "Updated description",
  "enabled": true
}
```

**Response (200 OK):**
Same as Get Strategy

**Error (400 Bad Request):**
```json
{
  "detail": "Cannot enable strategy. Missing parameters for pos: -1, 0, 1"
}
```

---

### Create Strategy Parameter
```
POST /api/v1/strategies/{strategy_id}/parameters
```

**Path Parameters:**
- `strategy_id` (UUID): Strategy ID

**Request Body:**
```json
{
  "pos": "0",
  "param1": -1.0,
  "param2": 1.0,
  "param3": null,
  "param4": null,
  "param5": null,
  "param6": null,
  "param7": null,
  "param8": null,
  "param9": null,
  "param10": null
}
```

**Response (201 Created):**
```json
{
  "id": "456e1234-b12c-56d7-a890-426614174001",
  "strategy_id": "123e4567-e89b-12d3-a456-426614174000",
  "pos": "0",
  "param1": -1.0,
  "param2": 1.0,
  "param3": null,
  ...
  "param10": null,
  "created_at": "2026-09-20T14:30:00Z",
  "updated_at": "2026-09-20T14:30:00Z"
}
```

---

### Update Strategy Parameter
```
PUT /api/v1/strategies/{strategy_id}/parameters/{param_id}
```

**Request Body:**
Same as Create (all fields optional)

**Response (200 OK):**
Same as Create

---

### Delete Strategy Parameter
```
DELETE /api/v1/strategies/{strategy_id}/parameters/{param_id}
```

**Response (204 No Content)**

---

## ISINs Management

### List ISINs
```
GET /api/isins
```

**Response (200 OK):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "isin": "IE00B0M63284",
    "ticker": "VWRL",
    "name": "Vanguard FTSE All-World ETF",
    "currency": "EUR",
    "quantity": 14.84,
    "current_price": 166.86,
    "average_price_paid": 160.5,
    "quantity_available_for_trading": 14.84,
    "quantity_in_pies": 0.0,
    "automation_enabled": true,
    "initial_trade": false,
    "trades_balance": 0,
    "strategy_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2026-09-20T14:30:00Z",
    "updated_at": "2026-09-20T14:30:00Z"
  }
]
```

---

### Sync Portfolio with T212
```
POST /api/isins/sync
```

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "success": true,
  "synced": 5,
  "created": 1,
  "updated": 4,
  "errors": 0,
  "isins": [...]
}
```

---

### Update ISIN Automation
```
PUT /api/isins/{isin_id}/automation
```

**Request Body:**
```json
{
  "automation_enabled": true,
  "strategy_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "automation_enabled": true,
  "strategy_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

## Automation Control

### Get Global Automation Status
```
GET /api/v1/automation/global-status
```

**Response (200 OK):**
```json
{
  "grid_trading_enabled": true,
  "scheduler_running": true,
  "cycle_count": 42,
  "last_cycle_duration": 9.5,
  "cycles_in_error": 2
}
```

---

### Enable Global Automation
```
PUT /api/v1/automation/enable
```

**Response (200 OK):**
```json
{
  "grid_trading_enabled": true,
  "message": "Grid trading enabled"
}
```

---

### Disable Global Automation
```
PUT /api/v1/automation/disable
```

**Response (200 OK):**
```json
{
  "grid_trading_enabled": false,
  "message": "Grid trading disabled"
}
```

---

### Get Scheduler Status
```
GET /api/v1/automation/status
```

**Response (200 OK):**
```json
{
  "scheduler_running": true,
  "cycle_count": 42,
  "last_cycle_at": "2026-09-20T14:32:15Z",
  "last_cycle_duration": 9.5,
  "cycles_in_error": 2,
  "last_error": "Failed to fetch position for VWRL",
  "next_cycle_at": "2026-09-20T14:32:30Z"
}
```

---

### Update Scheduler Interval
```
PUT /api/v1/automation/config/interval
```

**Request Body:**
```json
{
  "interval": 15
}
```

**Response (200 OK):**
```json
{
  "scheduler_interval_seconds": 15,
  "message": "Interval updated. Will apply on next cycle."
}
```

**Validation Error (400):**
```json
{
  "detail": "Interval must be between 5 and 300 seconds"
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 204 | No Content - Success, no response body |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Duplicate entry |
| 500 | Internal Server Error |

---

## Rate Limiting

T212 API has built-in rate limits. Backend handles automatically:
- Positions: 1 req/1s
- Orders: 50 req/1m
- History: 6 req/1m

If rate limit reached, endpoint returns 429 with retry info.

---

## Example: Complete Flow

```bash
# 1. Create strategy
curl -X POST https://trading212-backend.onrender.com/api/v1/strategies \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grid 1%",
    "description": "Grid trading",
    "initial_investment": 10.0
  }'

# Response: {"id": "str-123", "enabled": false, "is_valid": false}

# 2. Add parameters for position -1
curl -X POST https://trading212-backend.onrender.com/api/v1/strategies/str-123/parameters \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pos": "-1",
    "param1": -1.0,
    "param2": 1.0
  }'

# 3. Add parameters for position 0
curl -X POST https://trading212-backend.onrender.com/api/v1/strategies/str-123/parameters \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pos": "0",
    "param1": -1.0,
    "param2": 1.0
  }'

# 4. Add parameters for position 1
curl -X POST https://trading212-backend.onrender.com/api/v1/strategies/str-123/parameters \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pos": "1",
    "param1": -1.0,
    "param2": 1.0
  }'

# 5. Enable strategy (now is_valid=true)
curl -X PUT https://trading212-backend.onrender.com/api/v1/strategies/str-123 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# 6. Sync portfolio
curl -X POST https://trading212-backend.onrender.com/api/isins/sync \
  -H "Authorization: Bearer TOKEN"

# 7. Enable automation for ISIN
curl -X PUT https://trading212-backend.onrender.com/api/isins/isin-456/automation \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "automation_enabled": true,
    "strategy_id": "str-123"
  }'

# 8. Enable global automation
curl -X PUT https://trading212-backend.onrender.com/api/v1/automation/enable \
  -H "Authorization: Bearer TOKEN"
```

---

**Last Updated:** 2026-09-20
