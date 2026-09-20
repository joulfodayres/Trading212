# Trading 212 Activity Statement Parser - Quick Reference Guide

**Last Updated:** 2026-09-20  
**For:** Developers implementing the PDF parser

---

## 🎯 Core Facts

| Aspect | Details |
|--------|---------|
| **Report Types** | Monthly (27-30 pages) + Daily (15 pages) |
| **Compatibility** | ✅ Same structure (use single parser) |
| **Main Tables** | 7-15 depending on trading activity |
| **Accounts** | Invest + CFD (both usually present) |
| **Encoding** | UTF-8 with potential currency symbol corruption |
| **Decimal Format** | Mixed (comma and period separators) |

---

## 🏗️ High-Level Architecture

```
PDF File
  ├── Page 1: Title & Metadata
  ├── Pages 2-X: Invest Account
  │   ├── Executed Trades (table)
  │   ├── Pending Orders (table)
  │   ├── Open Positions (table)
  │   ├── Cash Breakdown (table)
  │   ├── Transactions (table)
  │   └── Dividends (table)
  ├── Pages X+1-Y: CFD Account
  │   ├── Executed Trades (CFD table)
  │   ├── Positions (CFD table)
  │   ├── Overnight Interest (table)
  │   └── Transactions (table)
  └── Last Page: Regulatory Footer
```

---

## 📋 Essential Tables to Extract

### 1. Executed Trades (Equity) - **MUST HAVE**

**Identifier:** "EXECUTION TIME" + "INSTRUMENT ISIN" in header

**Columns (15):**
```
1. EXECUTION TIME      → datetime
2. INSTRUMENT          → string (name)
3. ISIN                → string (format: XX00XXXXXXXXX)
4. ORDER ID            → string
5. DIRECTION           → enum [BUY|SELL]
6. QUANTITY            → float
7. EXECUTION PRICE     → float (4 decimals)
8. VALUE               → float (total in currency)
9. ORDER TYPE          → string [Market|Limit|Stop]
10. VENUE              → string [NYSE|XETRA|OTC|LSE|XEUR]
11. SESSION            → string [Regular|Extended]
12. FX RATE            → float
13. FX FEE             → float
14. GOVT FEES          → float
15. RETURN VALUE       → float (€ currency)
```

**Validation:**
- `VALUE = QUANTITY × EXECUTION PRICE` (±2% tolerance)
- `DIRECTION ∈ {BUY, SELL}`
- `EXECUTION TIME` must be UTC

---

### 2. Open Positions (Equity) - **MUST HAVE**

**Identifier:** "QUANTITY" + "AVERAGE PRICE" + "PRICE" together (not in trades table)

**Columns (10):**
```
1. INSTRUMENT          → string
2. ISIN                → string
3. QUANTITY            → float (can be decimal)
4. AVERAGE PRICE       → float
5. CURRENT PRICE       → float
6. UNREALISED P/L      → float (€ currency)
7. RETURN %            → float (percentage)
8. TOTAL VALUE         → float
9. FX RATE             → float
10. FX ADJUSTED VALUE  → float
```

**Validation:**
- `TOTAL VALUE = QUANTITY × CURRENT PRICE`
- `UNREALISED P/L = (CURRENT PRICE - AVERAGE PRICE) × QUANTITY`

---

### 3. Cash Breakdown - **MUST HAVE**

**Identifier:** "FUND" + "ISIN" + "QUANTITY" + "PRICE" + "VALUE"

**Data:** Money market fund holdings

**Common Funds:**
- JPMorgan Liquidit Funds EUR Liquidit (ISIN: LU0326635387)
- Goldman Sachs Euro Liquid Reserves Fund Inst (ISIN: IE00BDX1MM09)
- BlackRock ICS Euro Liquidit Fund (ISIN: IE00BAFXJO29)

---

### 4. Transactions & Interest - **IMPORTANT**

**Identifier:** "TRANSACTION TIME" + "TYPE" + "AMOUNT"

**Fields:**
```
TIME    → datetime
TYPE    → [Deposit|Withdrawal|Interest|Fee|Dividend]
AMOUNT  → float (signed: +/- )
```

---

### 5. Pending Orders - **CONDITIONAL** (may be empty)

**Columns:**
```
INSTRUMENT, ISIN, ORDER TYPE, DIRECTION, QUANTITY, LIMIT PRICE, 
STOP PRICE, EXPIRATION
```

---

### 6. CFD Executed Trades - **CONDITIONAL** (if CFD account active)

**Columns (10):**
```
EXECUTION TIME, SYMBOL, ASSET, ORDER ID, FILL ID, DIRECTION,
QUANTITY, EXECUTION PRICE, VALUE, REALISED P/L
```

---

### 7. CFD Open Positions - **CONDITIONAL**

**Columns (12):**
```
SYMBOL, ASSET, CURRENCY, QUANTITY, OPENING PRICE, CURRENT PRICE,
UNREALISED P/L, VALUE, FX RATE, RESULT, DIVIDEND, INTEREST
```

---

### 8. Overnight Interest (CFD) - **CONDITIONAL**

**Columns:**
```
TRANSACTION TIME, INSTRUMENT, DIRECTION, POSITION SIZE,
OVERNIGHT INTEREST RATE, AMOUNT, FX RATE, AMOUNT (FXD)
```

---

## 🔑 Data Extraction Patterns

### Pattern 1: Multi-Page Tables
```
Some tables span multiple pages. Indicators:
- Table has 15+ rows
- Header row repeats on next page
- Row numbers/pagination appear

Solution: Merge data from consecutive pages with same headers
```

### Pattern 2: Account Headers
```
Before each account section:
"CUSTOMER ID    CUSTOMER NAME"
"João Luis Varela da Fonseca"
"Invest Account - Executed Trades"

Use this to segment PDF into account sections
```

### Pattern 3: Section Separators
```
Sections marked by:
- New account header line
- Blank space (3+ empty lines)
- "=====" divider lines
- Page breaks

Use these to detect section transitions
```

---

## 🎨 Parsing Code Template

```python
import pdfplumber
import pandas as pd
from datetime import datetime
import re

class Trading212Parser:
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = {
            'metadata': {},
            'invest': {'trades': [], 'positions': [], 'cash': {}},
            'cfd': {'trades': [], 'positions': []}
        }
    
    def parse(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            # Extract metadata from first page
            self._parse_metadata(pdf.pages[0])
            
            # Extract tables from all pages
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    self._process_tables(tables)
        
        return self.data
    
    def _parse_metadata(self, page):
        text = page.extract_text()
        
        # Extract customer info
        match = re.search(r'Account ID:\s+(\w+)', text)
        if match:
            self.data['metadata']['account_id'] = match.group(1)
        
        # Extract period
        match = re.search(r'covering from (.+?) to (.+?) \(UTC\)', text)
        if match:
            self.data['metadata']['from'] = match.group(1)
            self.data['metadata']['to'] = match.group(2)
    
    def _process_tables(self, tables):
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            headers = table[0]
            headers_str = ' '.join(str(h) for h in headers).upper()
            
            # Identify table type by headers
            if 'EXECUTION TIME' in headers_str and 'ISIN' in headers_str:
                self._parse_equity_trades(table)
            elif 'QUANTITY' in headers_str and 'AVERAGE PRICE' in headers_str:
                self._parse_positions(table)
            elif 'FUND' in headers_str and 'ISIN' in headers_str:
                self._parse_cash(table)
    
    def _parse_equity_trades(self, table):
        headers = table[0]
        
        for row in table[1:]:
            if not any(row):  # Skip empty rows
                continue
            
            trade = {
                'timestamp': self._parse_datetime(row[0]),
                'instrument': row[1],
                'isin': row[2],
                'order_id': row[3],
                'direction': row[4].upper(),
                'quantity': self._parse_float(row[5]),
                'price': self._parse_float(row[6]),
                'value': self._parse_float(row[7]),
                'order_type': row[8],
                'venue': row[9],
            }
            
            self.data['invest']['trades'].append(trade)
    
    def _parse_positions(self, table):
        for row in table[1:]:
            if not any(row):
                continue
            
            position = {
                'instrument': row[0],
                'isin': row[1],
                'quantity': self._parse_float(row[2]),
                'avg_price': self._parse_float(row[3]),
                'current_price': self._parse_float(row[4]),
                'unrealised_pl': self._parse_float(row[5]),
                'total_value': self._parse_float(row[7]),
            }
            
            self.data['invest']['positions'].append(position)
    
    def _parse_float(self, value):
        """Parse number with mixed separators"""
        if not value:
            return 0.0
        
        # Remove currency symbols
        clean = re.sub(r'[^\d.,\-]', '', str(value))
        
        # Handle mixed separators: 16,234.50 vs 16,50
        if clean.count(',') == 1 and clean.count('.') == 0:
            return float(clean.replace(',', '.'))  # EU: 16,50
        else:
            return float(clean.replace(',', ''))   # US: 16,234.50
    
    def _parse_datetime(self, value):
        """Parse timestamp in UTC"""
        try:
            return datetime.strptime(str(value).strip(), '%Y-%m-%d %H:%M:%S')
        except:
            return None
```

---

## ⚠️ Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| **Currency symbol corruption** | Clean text: `€` ← `â‚¬` |
| **Decimal parsing fails** | Normalize: remove all commas for US format |
| **Multi-line table headers** | Merge rows if header exceeds 50 chars |
| **Missing sections in daily** | Handle gracefully: `if not table: continue` |
| **Order of tables varies** | Identify by header content, not position |
| **Empty position/order sections** | Check for "No data available" text |
| **Timestamp timezone** | All times are UTC (Z suffix implicit) |
| **CFD account may not exist** | Check section count before parsing CFD |

---

## 📈 Performance Tips

```python
# ✅ DO: Use pdfplumber's streaming
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        # Process immediately, don't store all

# ❌ DON'T: Load all into memory
all_pages = [p.extract_text() for p in pdf.pages]  # Slow!

# ✅ DO: Cache headers
headers_cache = {}
for table in tables:
    header_sig = tuple(table[0])
    if header_sig not in headers_cache:
        headers_cache[header_sig] = self._identify_table_type(header_sig)

# ✅ DO: Validate early
if len(table) < 2:  # No data rows
    continue
```

---

## ✅ Testing Checklist

```bash
# Test Case 1: Monthly PDF (June)
✓ Extract all 4 trade tables
✓ Parse 100+ positions correctly
✓ Handle 30-day date range
✓ Extract cash in multiple currencies

# Test Case 2: Daily PDF (Sept 1)
✓ Extract 2-3 trade tables
✓ Handle single-day date range
✓ Parse positions (may be fewer)
✓ Verify currency handling

# Edge Cases
✓ Empty sections ("No data available")
✓ Partial shares (14.84 quantity)
✓ Multi-line values wrapping
✓ High-precision prices (4+ decimals)
```

---

## 🚀 Implementation Roadmap

1. **Phase 1: Basic Structure** (1-2 days)
   - Extract tables from PDF
   - Identify table types by headers
   - Parse basic fields (datetime, float, string)

2. **Phase 2: Data Validation** (2-3 days)
   - Validate trade calculations
   - Normalize decimals/currencies
   - Handle errors gracefully

3. **Phase 3: Output Formats** (1-2 days)
   - Export to CSV
   - Export to JSON
   - Export to DataFrame

4. **Phase 4: Testing & Optimization** (2-3 days)
   - Test with 10+ real PDFs
   - Benchmark performance
   - Add error recovery

---

## 📚 Reference Files

- **Main Analysis:** `STRUCTURE_ANALYSIS.md`
- **Detailed Structure:** `DETAILED_STRUCTURE_COMPARISON.md`
- **Monthly PDF Breakdown:** `Activity-Statement-2026-06-01-2026-06-30_DETAILED_ANALYSIS.md`
- **Daily PDF Breakdown:** `Activity-Statement-2026-09-01-2026-09-01_DETAILED_ANALYSIS.md`

---

*Created: 2026-09-20 | Status: Ready for Implementation*
