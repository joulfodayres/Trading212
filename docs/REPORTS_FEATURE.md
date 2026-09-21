# Reports Feature — T212 Activity Statement Import

## 🎯 Overview

The **Reports** feature lets the user upload Trading 212 **Activity Statement PDFs** and
automatically parse them into 15 structured database tables. It adds a new **Reports** item to
the frontend sidebar with upload, a per-table insertion summary, an uploaded-files counter, and a
list of already-processed files.

**Status:** ✅ Implemented (Phase 5 — "Upload T212 Data Files")
**Shipped in commit:** `76bee94` — *feat: Add Reports feature - import T212 Activity Statement PDFs*

---

## 📄 PDF Structure Parsed

The Trading 212 Activity Statement PDF is split into 3 accounts (Invest / CFD / Crypto). The
parser extracts **15 tables** (documented in detail in `reports/SECOES_PDF.md`). Ignored sections
by design: page 1 overview, "Cash breakdown", "Glossary", "Disclosures". Empty sections (e.g.
Dividends) are still created as tables with 0 rows.

| # | Table | Account | Notes |
|---|-------|---------|-------|
| 1 | `invest_executed_trades` | Invest | 16 columns |
| 2 | `invest_pending_orders` | Invest | Often empty |
| 3 | `invest_open_positions` | Invest | |
| 4 | `invest_transactions` | Invest | |
| 5 | `invest_dividends` | Invest | Often empty |
| 6 | `cfd_executed_trades` | CFD | Execution time split across 2 lines |
| 7 | `cfd_pending_orders` | CFD | Often empty |
| 8 | `cfd_open_positions` | CFD | |
| 9 | `cfd_transactions` | CFD | |
| 10 | `cfd_dividend_adjustments` | CFD | |
| 11 | `cfd_overnight_interest` | CFD | |
| 12 | `crypto_executed_trades` | Crypto | |
| 13 | `crypto_pending_orders` | Crypto | Often empty |
| 14 | `crypto_open_positions` | Crypto | |
| 15 | `crypto_transactions` | Crypto | Often empty |

---

## 🗄️ Database Schema

Defined in `reports/reports_schema.sql` (16 tables total). Requires the `pgcrypto` extension
(`gen_random_uuid()`).

### Control table: `imported_files`
```sql
- id (UUID, PK, default gen_random_uuid())
- file_name (VARCHAR)
- file_hash (VARCHAR)          -- SHA-256, unique index for dedup
- customer_id (VARCHAR)
- customer_name (VARCHAR)
- period_start (DATE)
- period_end (DATE)
- generated_at (TIMESTAMPTZ)
- pages (INTEGER)
- status (VARCHAR)             -- PENDING / IMPORTED / FAILED
- imported_at (TIMESTAMPTZ)
- created_at, updated_at (TIMESTAMPTZ, default now())
```

### The 15 data tables
Every data table carries three common columns in addition to its own fields:
```sql
- id (UUID, PK, default gen_random_uuid())
- file_id (UUID, FK → imported_files(id) ON DELETE CASCADE)  -- source file
- created_at (TIMESTAMPTZ, default now())
- updated_at (TIMESTAMPTZ, default now())
```

> ⚠️ **Prerequisite:** `reports_schema.sql` must be run in the Supabase SQL Editor before the
> upload endpoint can insert rows.

---

## 🔌 API Endpoints

Router prefix: `/api/reports` (`backend/routes/reports.py`).

### **POST /api/reports/upload**
Multipart upload of one or more PDF files (`files` field).
- Computes SHA-256 per file; if the hash already exists → **skipped** (dedup).
- Creates an `imported_files` row (status PENDING), parses the PDF, batch-inserts rows
  (chunk size 500), updates metadata + status → IMPORTED / FAILED.
```json
Response: {
  "files_processed": 1,
  "grand_total": { "invest_executed_trades": 71, "invest_open_positions": 3, ... },
  "grand_total_inserted": 314,
  "results": [
    { "file_name": "...", "status": "imported", "total_inserted": 314,
      "inserted": { "invest_executed_trades": 71, ... } }
  ]
}
```

### **GET /api/reports/files**
List of processed files (ordered by `imported_at` desc): id, file_name, customer_id/name,
period_start, period_end, generated_at, pages, status, imported_at.

### **GET /api/reports/summary**
```json
Response: { "total_files": 3, "imported": 2, "failed": 1 }
```

---

## 🧠 Parser (`backend/services/report_parser.py`)

- Uses **PyMuPDF** (`fitz`) for text extraction (`doc[i].get_text()`).
- Entry point: `parse_report(pdf_bytes, file_id) -> {"metadata": {...}, "tables": {name: [rows]}}`.
- Regex anchors (`RE_DATETIME`, `RE_DATE`) delimit section blocks between section/stop titles.
- `_clean_number` strips currency symbols/replacement chars, preserves sign, maps `-` → None.
- `_coerce` casts each field by type (text/date/datetime/number).
- `_parse_metadata` extracts customer id/name + period from the statement header.
- Special handling: CFD executed-trades execution time is split across two text lines.
- Strips `CUSTOMER ID` / `CUSTOMER NAME` headers and page footers.

**Validated against the real PDF** (2026-06 statement): metadata correct (customer_id=18182509,
period 2026-05-31 → 2026-06-30, pages=27) and record counts matched the source
(invest_executed=71, invest_open=3, invest_tx=33, cfd_exec=2, cfd_open=5, cfd_overnight=86,
crypto_exec=99, crypto_open=15; empty sections=0).

---

## 🖥️ Frontend

- **`components/Sidebar.tsx`** — new `reports` item with the `FileText` icon.
- **`pages/ReportsPage.tsx`** — KPI cards (Files uploaded / Imported / Failed), drag-style upload
  dropzone (multiple PDFs), per-file + aggregated per-table insertion summary, and a
  processed-files table (ID, File, Period start, Period end, Uploaded at, Status).
- **`pages/DashboardPage.tsx`** — renders `ReportsPage` when `activeView === 'reports'`.
- **`api/index.ts`** — `reportsAPI.upload()` / `listFiles()` / `summary()`.
- Follows the project **no-toast** rule: all feedback is UI-state + `console.log/error`.

---

## 🔑 Key Files

**Backend:**
- `services/report_parser.py` — PyMuPDF PDF parser (15 tables + metadata)
- `routes/reports.py` — upload / files / summary endpoints
- `main.py` — registers `reports_router`
- `requirements.txt` — adds `PyMuPDF>=1.24.0`

**Frontend:**
- `pages/ReportsPage.tsx`, `pages/DashboardPage.tsx`
- `components/Sidebar.tsx`, `api/index.ts`

**Schema & spec:**
- `reports/reports_schema.sql` — 16-table schema
- `reports/SECOES_PDF.md` — field-by-field PDF section spec

---

**Last Updated:** 2026-09-21
**Status:** ✅ Implemented (backend + frontend + schema)
</content>
</invoke>
