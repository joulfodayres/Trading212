# T212 Limit Order API - Decimal Places Tester

Updated version that **does NOT automatically round** values.

## What Changed

### Before
- Automatically rounded quantity and price to 3 decimals
- User couldn't test different decimal places

### Now
- **NO automatic rounding**
- User specifies exactly how many decimals to send
- Can test: 1, 2, 3, 4, 5... 8, 16 decimal places
- Perfect for testing API behavior across different precisions

## How to Use

### Input Fields

1. **Quantity** - Enter the exact value (e.g., `0.5777225565048442`)
   - The raw value is preserved
   - You then choose how many decimals to round to

2. **Qty Decimals to Send** - Spinbox (0-16)
   - Choose how many decimal places to use
   - Value will be rounded to this precision before sending

3. **Limit Price** - Enter exact value (e.g., `17.326656`)
   - Raw value preserved

4. **Price Decimals to Send** - Spinbox (0-16)
   - Choose how many decimal places to use
   - Value will be rounded to this precision before sending

### Quick Test Presets

Buttons for quick testing:
- **3 decimals (current fix)** - What the code currently uses
- **2 decimals** - Test if T212 accepts
- **1 decimal** - Minimum precision
- **4 decimals** - More precision
- **8 decimals** - Very precise
- **Original (16)** - Full precision, no rounding

Click any button and it immediately tests with those decimal places.

### How to Test

1. **Default Test (3 decimals)**
   - Qty: 0.5777225565048442 → rounded to 0.578
   - Price: 17.326656 → rounded to 17.327
   - Should get 200 OK

2. **Test with 2 decimals**
   - Click "2 decimals" preset
   - Qty: 0.5777225565048442 → rounded to 0.58
   - Price: 17.326656 → rounded to 17.33
   - See if T212 accepts

3. **Test with 4 decimals**
   - Click "4 decimals" preset
   - Qty: 0.5777225565048442 → rounded to 0.5777
   - Price: 17.326656 → rounded to 17.3267
   - See if T212 rejects

4. **Test with original (16 decimals)**
   - Click "Original (16)" preset
   - Qty: 0.5777225565048442 (full precision)
   - Price: 17.326656 (full precision)
   - See if T212 rejects (likely will)

## What You'll See

### Request Tab
- Original value (e.g., 0.5777225565048442)
- Original decimal count (16)
- Decimals to send (your choice)
- Rounded value (what gets sent)
- JSON payload with final values

### Response Tab
- Status code (200 = success, 400 = error)
- Full JSON response from T212
- If error: error details explaining what's wrong

### Status Tab
- Timing information
- Error details
- Response headers
- Rate limit information

## Why This Matters

This lets you find the **exact decimal precision that T212 API requires**.

Possible results:
- **Accept:** Can send this many decimals
- **Reject:** "invalid quantity precision" - too many decimals
- **Reject:** "invalid payload" - different issue

By testing 1, 2, 3, 4, 5, 6, 7, 8, 16 decimals, you can find the exact limit.

## Example Test Session

```
Test 1: 16 decimals
  Qty: 0.5777225565048442
  Price: 17.326656
  Result: 400 - "invalid quantity precision"
  
Test 2: 8 decimals
  Qty: 0.57772256
  Price: 17.32665600
  Result: 400 - "invalid quantity precision"
  
Test 3: 3 decimals
  Qty: 0.578
  Price: 17.327
  Result: 200 OK - Order created!
  
Test 4: 2 decimals
  Qty: 0.58
  Price: 17.33
  Result: 400 - Something else wrong
```

From this, you'd know: T212 accepts exactly 3 decimal places (or maybe up to 3).

## Files

- `test_limit_order_gui.py` - The GUI application
- `setup_tester.py` - Install dependencies (requests)
- `RUN_LIMIT_ORDER_TESTER.bat` - Windows quick launch

## Run It

```bash
python test_limit_order_gui.py
```

Or Windows:
```
Double-click RUN_LIMIT_ORDER_TESTER.bat
```

## Notes

- This is a testing tool only
- No integration with project
- Safe to delete after testing
- All calls to DEMO environment (safe)
- Can create real orders in DEMO - view them at demo.trading212.com
