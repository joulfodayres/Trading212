# Quick Reference: PDF Structure Mapping

**Visual Guide for Activity Statement Parser Implementation**

---

## Document Structure Diagram

```
ACTIVITY STATEMENT
│
├─ PAGE 1: HEADER + OVERVIEW
│  ├─ Header
│  │  ├─ Customer ID
│  │  ├─ Customer Name
│  │  ├─ Report Type: "Activity Statement"
│  │  ├─ Period: [START_DATE] to [END_DATE]
│  │  └─ Generated: [DATE & TIME]
│  │
│  └─ Overview (Account-Type Sections)
│     ├─ Trading 212 Invest Account
│     │  ├─ Deposits: €X
│     │  ├─ Withdrawals: €X
│     │  ├─ Realised Return: €X
│     │  ├─ Open Return: €X
│     │  ├─ Open Return Change: €X
│     │  ├─ Dividends: €X
│     │  ├─ Interest on Cash: €X
│     │  ├─ Cashback: €X
│     │  ├─ FX Fee: €X
│     │  ├─ Third Party Fees: €X
│     │  └─ Account Value: €X
│     │
│     ├─ Trading 212 CFD Account
│     │  ├─ Deposits: €X
│     │  ├─ Withdrawals: €X
│     │  ├─ FX Fee: €X
│     │  ├─ Dividend Adjustments: €X
│     │  ├─ Overnight Interest: €X
│     │  ├─ Closed Result: €X
│     │  ├─ Open Result: €X
│     │  ├─ Open Result Change: €X
│     │  ├─ Margin Requirement: €X
│     │  ├─ Available Margin: €X
│     │  └─ Account Value: €X
│     │
│     └─ Trading 212 Crypto Account
│        ├─ Deposits: €X
│        ├─ Withdrawals: €X
│        ├─ Closed Result: €X
│        ├─ Open Result: €X
│        ├─ Open Result Change: €X
│        └─ Account Value: €X
│
├─ INVEST ACCOUNT SECTION (Pages 2-9 / 2-5)
│  ├─ Executed Trades (Table)
│  │  └─ Columns: EXECUTION TIME | INSTRUMENT | ISIN | ORDER ID | DIRECTION |
│  │             QUANTITY | EXECUTION PRICE | VALUE | ORDER TYPE | 
│  │             EXECUTION VENUE | SESSION | FX RATE | FX FEE | 
│  │             EXCHANGE & GOVT FEES | RETURN VALUE
│  │
│  ├─ Open Positions Summary
│  │  ├─ Pending Orders (Table)
│  │  │  └─ Columns: INSTRUMENT | ISIN | CURRENCY | ORDER ID | TYPE | DIRECTION |
│  │  │             EXPIRATION | QUANTITY | LIMIT PRICE | STOP PRICE | VALUE
│  │  │
│  │  └─ Open Positions (Table)
│  │     └─ Columns: INSTRUMENT | ISIN | QUANTITY | AVERAGE PRICE | PRICE |
│  │                RETURN | VALUE | FX RATE | RETURN VALUE
│  │
│  ├─ Cash Breakdown
│  │  ├─ Settled Cash: €X
│  │  ├─ Unsettled Cash: €X
│  │  └─ Total Cash: €X
│  │
│  └─ Transactions & Dividends
│     ├─ Interest on Cash (Table)
│     │  └─ TIME | TYPE | AMOUNT
│     │
│     └─ Dividends (Table)
│        └─ EXECUTION TIME | INSTRUMENT | ISIN | QUANTITY | PRICE |
│           GROSS AMOUNT | DIVIDEND TAX | NET AMOUNT
│
├─ CFD ACCOUNT SECTION (Pages 11-17 / 6-9)
│  ├─ Executed Trades (Table) ⚠️ DIFFERENT COLUMNS!
│  │  └─ Columns: EXECUTION TIME | INSTRUMENT | ORDER ID | ORDER TYPE |
│  │             DIRECTION | EXECUTION VENUE | SESSION | QUANTITY |
│  │             EXECUTION PRICE | VALUE | PROFIT/LOSS | OVERNIGHT INTEREST
│  │
│  ├─ Open Positions Summary
│  │  ├─ Pending Orders (Table)
│  │  └─ Open Positions (Table)
│  │
│  ├─ Cash Breakdown
│  │  └─ [Same structure as Invest]
│  │
│  └─ Transactions, Dividends & Overnight Interest
│     ├─ Transactions (Table)
│     ├─ Overnight Interest (Table)
│     └─ (Dividends if applicable)
│
├─ CRYPTO ACCOUNT SECTION (Pages 18-25 / 10-13)
│  ├─ Executed Trades (Table) ⚠️ DIFFERENT FORMAT!
│  │  └─ Columns: EXECUTION TIME | SYMBOL | ASSET | ORDER ID | FILL ID |
│  │             DIRECTION | QUANTITY | EXECUTION PRICE | VALUE | FEE | RETURN
│  │
│  ├─ Open Positions Summary
│  │  ├─ Pending Orders (Table)
│  │  └─ Open Positions (Table)
│  │
│  ├─ Cash Breakdown
│  │  └─ [Same structure as Invest]
│  │
│  └─ Transactions
│     └─ [If any crypto transactions]
│
└─ FOOTER (Pages 26-27 / 14-15)
   ├─ Glossary (Terms & Definitions)
   └─ Disclosures & Legal Notices
```

---

## Column Differences by Account Type

### INVEST ACCOUNT - Executed Trades

```
✅ INVEST ONLY COLUMNS:
   - ISIN (instrument identifier)
   - FX RATE, FX FEE (forex costs)
   - EXCHANGE & GOVT FEES (regulatory fees)
   - RETURN VALUE (P&L on trade)

⚠️ NOT IN CFD/CRYPTO:
   - These columns don't appear in CFD or Crypto trades
```

### CFD ACCOUNT - Executed Trades

```
✅ CFD ONLY COLUMNS:
   - PROFIT/LOSS (immediate P&L)
   - OVERNIGHT INTEREST (financing cost)

⚠️ NOT IN INVEST/CRYPTO:
   - No ISIN (CFDs don't have ISINs)
   - No individual FX/fee breakdown
```

### CRYPTO ACCOUNT - Executed Trades

```
✅ CRYPTO ONLY COLUMNS:
   - SYMBOL (e.g., "BTC/EUR", "ETH/USD")
   - ASSET (e.g., "Bitcoin", "Ethereum")
   - FILL ID (crypto-specific identifier)
   - FEE (trading fee for crypto)

⚠️ NOT IN INVEST/CFD:
   - No ISIN (replaced by SYMBOL/ASSET)
   - No ORDER TYPE (crypto fills are instant)
   - No SESSION, VENUE (crypto is 24/7 OTC)
```

---

## Report Type Detection

```python
def detect_report_type(start_date: str, end_date: str) -> str:
    if start_date == end_date:
        return "DAILY"
    elif is_month_end(end_date):
        return "MONTHLY"
    else:
        return "INTERVAL"
```

### Expected Pages by Report Type

| Report Type | Pages | Reason |
|-------------|-------|--------|
| DAILY | ~15 | Few trades, minimal data |
| MONTHLY | ~27 | Full month activity |
| INTERVAL (7 days) | ~20 | Estimated |
| INTERVAL (3 months) | ~40+ | Estimated |

---

## Critical Implementation Notes

### ⚠️ Important Considerations

1. **Account Type Column Differences**
   - Must detect account type BEFORE parsing trade tables
   - Can't use single column list for all three types
   - Need separate parser methods per account type

2. **Empty Sections**
   - Sections may contain "No data available"
   - Parser must handle gracefully (return empty list)

3. **Multi-page Tables**
   - Invest trades can span pages 2-6 (monthly)
   - Must accumulate rows from multiple pages
   - Look for header repetition to detect new page

4. **Decimal/Currency Handling**
   - Values formatted as: €1,234.56 or €1.234,56 (European)
   - Must normalize to standard format
   - Handle missing € sign in some cells

5. **Date/Time Format**
   - Date: DD.MM.YYYY (European format)
   - Time: HH:MM (24-hour)
   - Must parse correctly

6. **Text Extraction Quality**
   - PyPDF may extract some characters incorrectly
   - Use fuzzy matching for headers
   - Implement fallback parsing strategies

---

## Parser Skeleton (Pseudocode)

```python
class ActivityStatementParser:
    """Parse Trading 212 Activity Statement PDFs"""
    
    def parse(self, pdf_path: str) -> ActivityStatement:
        with pdfplumber.open(pdf_path) as pdf:
            # Step 1: Extract text from all pages
            all_text = "\n".join(p.extract_text() for p in pdf.pages)
            
            # Step 2: Parse header (page 1)
            header = self._parse_header(all_text)
            
            # Step 3: Detect report type
            report_type = self._detect_report_type(
                header.period_start, 
                header.period_end
            )
            
            # Step 4: Parse overview (page 1)
            overview = self._parse_overview(all_text)
            
            # Step 5: Parse account sections
            invest = self._parse_invest_account(all_text)
            cfd = self._parse_cfd_account(all_text)
            crypto = self._parse_crypto_account(all_text)
            
            return ActivityStatement(
                report_type=report_type,
                customer_id=header.customer_id,
                customer_name=header.customer_name,
                period_start=header.period_start,
                period_end=header.period_end,
                overview=overview,
                invest_account=invest,
                cfd_account=cfd,
                crypto_account=crypto
            )
    
    def _parse_invest_account(self, text: str) -> InvestAccount:
        # Find "Invest Account" section
        invest_section = self._extract_section(text, "Invest Account")
        
        # Parse executed trades
        trades = self._parse_table(
            invest_section,
            headers=[
                "EXECUTION TIME", "INSTRUMENT", "ISIN", "ORDER ID",
                "DIRECTION", "QUANTITY", "EXECUTION PRICE", "VALUE",
                "ORDER TYPE", "EXECUTION VENUE", "SESSION", "FX RATE",
                "FX FEE", "EXCHANGE & GOVT FEES", "RETURN VALUE"
            ]
        )
        
        # Parse open positions
        positions = self._parse_table(...)
        
        # Parse cash breakdown
        cash = self._parse_cash_breakdown(invest_section)
        
        # Parse transactions & dividends
        transactions = self._parse_transactions(invest_section)
        
        return InvestAccount(
            trades=trades,
            positions=positions,
            cash=cash,
            transactions=transactions
        )
    
    def _parse_cfd_account(self, text: str) -> CFDAccount:
        # Similar to invest, but with CFD-specific columns
        cfd_section = self._extract_section(text, "CFD Account")
        
        # Note: Different column headers for trades!
        trades = self._parse_table(
            cfd_section,
            headers=[
                "EXECUTION TIME", "INSTRUMENT", "ORDER ID", "ORDER TYPE",
                "DIRECTION", "EXECUTION VENUE", "SESSION", "QUANTITY",
                "EXECUTION PRICE", "VALUE", "PROFIT/LOSS", "OVERNIGHT INTEREST"
            ]
        )
        
        return CFDAccount(trades=trades, ...)
    
    def _parse_crypto_account(self, text: str) -> CryptoAccount:
        # Similar to invest, but with crypto-specific columns
        crypto_section = self._extract_section(text, "Crypto Account")
        
        # Note: SYMBOL/ASSET instead of INSTRUMENT/ISIN!
        trades = self._parse_table(
            crypto_section,
            headers=[
                "EXECUTION TIME", "SYMBOL", "ASSET", "ORDER ID", "FILL ID",
                "DIRECTION", "QUANTITY", "EXECUTION PRICE", "VALUE", "FEE", "RETURN"
            ]
        )
        
        return CryptoAccount(trades=trades, ...)
    
    def _parse_table(self, text: str, headers: list[str]) -> list[dict]:
        """Generic table parser"""
        # Extract rows where each cell maps to a header
        # Handle multi-line rows, empty cells, etc.
        pass
    
    def _parse_overview(self, text: str) -> AccountOverview:
        """Parse summary metrics for each account type"""
        # Find "Deposits", "Withdrawals", etc.
        # Extract values with currency parsing
        pass
```

---

## Database Schema (Quick Reference)

```sql
-- Main statement table
CREATE TABLE activity_statements (
    id UUID PRIMARY KEY,
    customer_id VARCHAR(50),
    report_type VARCHAR(20),  -- DAILY, MONTHLY, INTERVAL
    period_start DATE,
    period_end DATE,
    generated_date DATETIME,
    page_count INT,
    parsed_at DATETIME
);

-- Summary metrics
CREATE TABLE account_overviews (
    id UUID PRIMARY KEY,
    statement_id UUID,
    account_type VARCHAR(20),  -- INVEST, CFD, CRYPTO
    account_id VARCHAR(50),
    deposits DECIMAL(15,2),
    withdrawals DECIMAL(15,2),
    realised_return DECIMAL(15,2),
    open_return DECIMAL(15,2),
    ... (other metrics)
);

-- All trades (unified table)
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    statement_id UUID,
    account_type VARCHAR(20),
    execution_time DATETIME,
    instrument_name VARCHAR(255),
    isin_or_symbol VARCHAR(50),  -- INVEST: ISIN, CRYPTO: SYMBOL
    order_id VARCHAR(50),
    direction VARCHAR(10),  -- BUY, SELL
    quantity DECIMAL(15,8),
    execution_price DECIMAL(15,8),
    value DECIMAL(15,2),
    ... (account-type specific fields with NULLs)
);

-- Open positions
CREATE TABLE open_positions (
    id UUID PRIMARY KEY,
    statement_id UUID,
    account_type VARCHAR(20),
    instrument_name VARCHAR(255),
    isin_or_symbol VARCHAR(50),
    quantity DECIMAL(15,8),
    average_price DECIMAL(15,8),
    current_price DECIMAL(15,8),
    return_value DECIMAL(15,2),
    value DECIMAL(15,2)
);
```

---

**Quick Reference Guide - Keep This Handy!**

Last Updated: 2026-09-20
