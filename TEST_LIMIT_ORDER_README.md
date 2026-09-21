# T212 Limit Order API Tester

Local testing tool for Testing T212 Limit Order API calls.

**Status:** Standalone test program - NOT integrated with project
**Location:** `test_limit_order_gui.py`
**Deployment:** Local only (no GitHub, no Render, no database access)

## Features

✅ Desktop GUI (Tkinter) - no external dependencies
✅ Input fields for Ticker, Quantity, Price, Time Validity, Order Type
✅ Automatic rounding of quantity and price to 3 decimal places
✅ Real-time preview of JSON payload being sent
✅ Live API call to T212 demo environment
✅ Full request/response display with formatted JSON
✅ Request/response metadata (timestamps, duration, status codes, headers)
✅ Support for BUY and SELL orders
✅ Dark mode UI

## Prerequisites

```bash
# Python 3.7+ (includes Tkinter by default)
# No external packages needed except:
pip install requests
```

On Ubuntu/Debian:
```bash
sudo apt-get install python3-tk
```

## Usage

```bash
cd "C:\claude\401. Trading 212 Hub"
python test_limit_order_gui.py
```

## GUI Sections

### 1. Input Parameters
- **Ticker:** Default "NQSEd_EQ" (change as needed)
- **Quantity:** Default "0.5777225565048442" (shows original with many decimals)
- **Limit Price:** Default "17.326656" (shows original with many decimals)
- **Time Validity:** Choose "DAY" or "GOOD_TILL_CANCEL"
- **Order Type:** Choose "BUY" or "SELL"

### 2. Request Payload Tab (📤)
Shows:
- Order type, ticker, validity
- Quantity rounding process (original → 3 decimals)
- Price rounding process (original → 3 decimals)
- Final JSON payload
- API endpoint URL
- Authentication details (masked)

### 3. Response Payload Tab (📥)
Shows:
- HTTP status code (✅ 2xx / ❌ 4xx / ⚠️ 5xx)
- Response headers
- Full JSON response from T212 API
- If error: error message and details

### 4. Request/Response Info Tab (📊)
Shows:
- Start/end times with milliseconds
- Total duration
- Environment (DEMO)
- Request size
- Status code and reason
- Response headers
- Error details (if any)

## Default Test Data

```
Ticker:           NQSEd_EQ
Quantity:         0.5777225565048442 (15 decimals)
Limit Price:      17.326656 (6 decimals)
Time Validity:    GOOD_TILL_CANCEL
Order Type:       BUY
Environment:      DEMO
```

These values are from the actual error logs, so you can immediately test.

## What Gets Rounded

| Field | Original | Rounded | Example |
|-------|----------|---------|---------|
| Quantity | Any | 3 decimals | 0.5777225565048442 → 0.578 |
| Price | Any | 3 decimals | 17.326656 → 17.327 |

The GUI shows both original and rounded values for verification.

## API Details

- **Base URL:** https://demo.trading212.com/api/v0
- **Endpoint:** POST /equity/orders/limit
- **Authentication:** HTTP Basic Auth
- **API Key:** 40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU
- **API Secret:** iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0
- **Environment:** DEMO (safe for testing)

## Example Workflow

1. **Launch GUI**
   ```bash
   python test_limit_order_gui.py
   ```

2. **View default values** (ticker, quantity, price already filled)

3. **Click "🚀 Test Limit Order"** button

4. **Check Request Payload tab** 
   - Verify quantity rounded to 0.578
   - Verify price rounded to 17.327
   - Review full JSON payload

5. **Check Response Payload tab**
   - ✅ If status 200/201: order created successfully
   - ❌ If status 400: error details shown
   - ⚠️ If status 5xx: server error

6. **Check Request/Response Info tab**
   - See timestamps and duration
   - Verify all headers
   - Read error message if any

## Troubleshooting

### "Connection refused"
- Check internet connection
- Verify T212 API is accessible: curl https://demo.trading212.com/api/v0/equity/account/summary

### "401 Unauthorized"
- API credentials might be invalid
- Edit test_limit_order_gui.py and update:
  ```python
  self.api_key = "YOUR_API_KEY"
  self.api_secret = "YOUR_API_SECRET"
  ```

### "400 Bad Request"
- Check quantity/price decimal places
- Verify ticker is valid on T212
- Check error detail in Response Payload tab

### "Cannot import tkinter"
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- For Mac: comes with Python from python.org
- For Windows: should be included by default

## Notes

- This is a standalone test tool, NOT part of the project
- It directly calls T212 API with demo credentials
- No data is saved or persisted
- No integration with project database
- Can be deleted after testing
- All API calls are on DEMO environment (safe)

## Testing Limit Order Fixes

Use this tool to verify the quantity/price precision fix:

1. Keep default values (0.5777225565048442 quantity, 17.326656 price)
2. Click "Test Limit Order"
3. Check Request Payload:
   - Quantity should show "Original: 0.5777225565048442" → "Rounded: 0.578"
   - Price should show "Original: 17.326656" → "Rounded: 17.327"
4. Check Response:
   - Should get 200/201 success (order created)
   - Should NOT get 400 precision error anymore

If you still get errors, check error details and adjust rounding logic.
