"""
Report Parser - Trading 212 Activity Statement (PDF)
Extrai as 15 tabelas do statement mensal + metadados.

Usa PyMuPDF (fitz) para ler o texto pagina-a-pagina.
Retorna:
{
    "metadata": {customer_id, customer_name, period_start, period_end, generated_at, pages},
    "tables": { "<table_name>": [ {col: value, ...}, ... ], ... }
}

Nota: a extracao do PDF produz o simbolo de moeda como caractere de
substituicao (ex: euro/dollar). Os helpers de parsing removem qualquer
simbolo nao numerico e preservam o sinal.
"""
import io
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# ===== Regex anchors =====
RE_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_PAGE_FOOTER = re.compile(r"^\d+/\d+$")

# ===== Section titles (delimitadores de bloco, em ordem no documento) =====
SECTION_TITLES = [
    "Invest account - executed trades",
    "Invest account - open positions summary",
    "Invest account - transactions and dividends",
    "CFD account - executed trades",
    "CFD account - open positions summary",
    "CFD account - transactions, dividends and overnight interest",
    "Crypto account - executed trades",
    "Crypto account - open positions summary",
    "Crypto account - transactions",
]

# Cash breakdown / glossary / disclosures titles - usados apenas para cortar blocos
STOP_TITLES = [
    "Invest account - cash breakdown",
    "CFD account - cash breakdown",
    "Crypto account - cash breakdown",
    "Glossary",
    "Disclosures",
]

# Field keys por tabela (ordem = ordem das colunas no PDF)
FIELDS_INVEST_EXEC = [
    "execution_time", "instrument", "isin", "order_id", "direction", "quantity",
    "execution_price", "value", "order_type", "execution_venue", "session",
    "fx_rate", "fx_fee", "exchange_govt_fees", "return_amount", "return_value",
]
FIELDS_INVEST_OPEN = [
    "instrument", "isin", "quantity", "average_price", "price", "return_amount",
    "value", "fx_rate", "return_converted", "value_converted",
]
FIELDS_INVEST_TX = ["time", "type", "amount"]
FIELDS_INVEST_DIV = [
    "instrument", "isin", "issuing_country", "eligible_holdings", "pay_date",
    "amount_per_share", "total_amount", "wht_rate", "wht", "fx_rate", "net_amount",
]
FIELDS_CFD_EXEC = [
    "execution_time", "instrument", "order_id", "order_type", "direction",
    "execution_venue", "position_size", "average_price", "execution_price",
    "value", "spread", "fx_rate", "fx_fee", "result", "dividend_adjustments",
    "overnight_interest", "total_result",
]
FIELDS_CFD_OPEN = [
    "instrument", "direction", "position_size", "average_price", "price", "value",
    "fx_rate", "fx_fee", "result", "dividend_adjustments", "overnight_interest",
    "total_result", "period_price_change", "margin",
]
FIELDS_CFD_TX = ["time", "type", "amount"]
FIELDS_CFD_DIVADJ = [
    "transaction_time", "instrument", "direction", "ex_date", "position_size",
    "amount_per_share", "gross_amount", "wht_tax_rate", "wht_tax", "net_amount",
    "fx_rate", "net_amount_converted",
]
FIELDS_CFD_OVERNIGHT = [
    "transaction_time", "instrument", "direction", "position_size",
    "overnight_interest_rate", "amount", "fx_rate", "amount_converted",
]
FIELDS_CRYPTO_EXEC = [
    "execution_time", "symbol", "asset", "order_id", "fill_id", "direction",
    "quantity", "execution_price", "value", "realised_pl",
]
FIELDS_CRYPTO_OPEN = [
    "symbol", "asset", "quantity", "opening_price", "price", "unrealised_pl", "value",
]
FIELDS_CRYPTO_TX = ["time", "type", "amount"]

# Colunas que sao texto puro (nao converter para numero)
TEXT_FIELDS = {
    "instrument", "isin", "order_id", "direction", "order_type", "execution_venue",
    "session", "type", "symbol", "asset", "fill_id", "issuing_country",
    "period_price_change",
}
# Colunas datetime/date
DATETIME_FIELDS = {"execution_time", "time", "transaction_time"}
DATE_FIELDS = {"pay_date", "ex_date"}


def _clean_number(val: str) -> Optional[float]:
    """Converte string monetaria/numerica em float. '-' -> None."""
    if val is None:
        return None
    s = val.strip()
    if s in ("-", "", "�", "$", "N/A"):
        return None
    negative = s.startswith("-")
    # remover tudo excepto digitos, ponto
    cleaned = re.sub(r"[^0-9.]", "", s)
    if cleaned in ("", "."):
        return None
    try:
        num = float(cleaned)
    except ValueError:
        return None
    return -num if negative else num


def _parse_datetime(val: str) -> Optional[str]:
    s = val.strip()
    if RE_DATETIME.match(s):
        return s  # ja ISO-like, Supabase aceita
    if RE_DATE.match(s):
        return s
    return None


def _parse_date(val: str) -> Optional[str]:
    s = val.strip()
    if RE_DATE.match(s):
        return s
    return None


def _coerce(field: str, val: str) -> Any:
    if val is None:
        return None
    s = val.strip()
    if s == "-" or s == "":
        return None
    if field in TEXT_FIELDS:
        return s
    if field in DATETIME_FIELDS:
        return _parse_datetime(s) or s
    if field in DATE_FIELDS:
        return _parse_date(s)
    return _clean_number(s)


def _build_record(file_id: str, fields: List[str], values: List[str]) -> Dict[str, Any]:
    rec: Dict[str, Any] = {"file_id": file_id}
    for i, f in enumerate(fields):
        raw = values[i] if i < len(values) else None
        rec[f] = _coerce(f, raw) if raw is not None else None
    return rec


# ===== Extraction helpers =====

def _extract_lines(doc: "fitz.Document") -> List[str]:
    """Junta todas as linhas de texto, removendo ruido comum (customer/pagina)."""
    lines: List[str] = []
    skip_next = 0
    for page in doc:
        raw = [l.strip() for l in page.get_text().splitlines()]
        i = 0
        while i < len(raw):
            l = raw[i]
            if l == "":
                i += 1
                continue
            # Remover cabecalho "CUSTOMER ID\n<id>\nCUSTOMER NAME\n<name>"
            if l == "CUSTOMER ID":
                i += 2  # skip label + value
                continue
            if l == "CUSTOMER NAME":
                i += 2
                continue
            if RE_PAGE_FOOTER.match(l):
                i += 1
                continue
            lines.append(l)
            i += 1
    return lines


def _find_indices(lines: List[str], targets: set) -> List[int]:
    return [i for i, l in enumerate(lines) if l in targets]


def _anchor_records(block: List[str], anchor: re.Pattern, field_count: int) -> List[List[str]]:
    """Divide o bloco em registos comecando em cada linha que casa com o anchor."""
    idxs = [i for i, l in enumerate(block) if anchor.match(l)]
    records = []
    for n, start in enumerate(idxs):
        end = idxs[n + 1] if n + 1 < len(idxs) else len(block)
        slice_ = block[start:end][:field_count]
        records.append(slice_)
    return records


def _chunk_records(values: List[str], field_count: int) -> List[List[str]]:
    """Divide sequencialmente em blocos de field_count."""
    records = []
    for i in range(0, len(values) - field_count + 1, field_count):
        records.append(values[i:i + field_count])
    return records


def _strip_header_tokens(block: List[str], header_tokens: set) -> List[str]:
    """Remove linhas que sao cabecalhos de coluna ou 'No data available'."""
    out = []
    for l in block:
        if l in header_tokens:
            continue
        if l == "No data available":
            continue
        out.append(l)
    return out


# ===== Metadata =====

def _parse_metadata(doc: "fitz.Document") -> Dict[str, Any]:
    text = doc[0].get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    customer_id = None
    customer_name = None
    for i, l in enumerate(lines):
        if l == "CUSTOMER ID" and i + 1 < len(lines):
            customer_id = lines[i + 1]
        if l == "CUSTOMER NAME" and i + 1 < len(lines):
            customer_name = lines[i + 1]

    period_start = period_end = generated_at = None
    m = re.search(
        r"on (\d{1,2} \w+ \d{4}).*?from (\d{2}\.\d{2}\.\d{4}).*?to (\d{2}\.\d{2}\.\d{4})",
        text, re.DOTALL,
    )
    if m:
        try:
            generated_at = datetime.strptime(m.group(1), "%d %B %Y").date().isoformat()
        except ValueError:
            generated_at = None
        try:
            period_start = datetime.strptime(m.group(2), "%d.%m.%Y").date().isoformat()
        except ValueError:
            period_start = None
        try:
            period_end = datetime.strptime(m.group(3), "%d.%m.%Y").date().isoformat()
        except ValueError:
            period_end = None

    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "period_start": period_start,
        "period_end": period_end,
        "generated_at": generated_at,
        "pages": doc.page_count,
    }


# ===== Section parsers =====

def _section_block(lines: List[str], title: str) -> List[str]:
    """Devolve as linhas entre o titulo da seccao e o proximo titulo (seccao/stop)."""
    try:
        start = lines.index(title)
    except ValueError:
        return []
    delimiters = set(SECTION_TITLES + STOP_TITLES) - {title}
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i] in delimiters:
            end = i
            break
    return lines[start + 1:end]


def _subsection_block(block: List[str], marker: str, all_markers: List[str]) -> List[str]:
    """Dentro de um bloco, isola a subseccao 'marker' ate ao proximo marker."""
    try:
        start = block.index(marker)
    except ValueError:
        return []
    others = set(all_markers) - {marker}
    end = len(block)
    for i in range(start + 1, len(block)):
        if block[i] in others:
            end = i
            break
    return block[start + 1:end]


def parse_report(pdf_bytes: bytes, file_id: str) -> Dict[str, Any]:
    """Ponto de entrada. Devolve metadata + registos por tabela."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    metadata = _parse_metadata(doc)
    lines = _extract_lines(doc)

    tables: Dict[str, List[Dict[str, Any]]] = {}

    # ---- 1. Invest executed trades (anchor datetime, 16) ----
    block = _section_block(lines, "Invest account - executed trades")
    recs = _anchor_records(block, RE_DATETIME, len(FIELDS_INVEST_EXEC))
    tables["invest_executed_trades"] = [_build_record(file_id, FIELDS_INVEST_EXEC, r) for r in recs]

    # ---- 2 & 3. Invest open positions summary ----
    block = _section_block(lines, "Invest account - open positions summary")
    markers = ["Pending orders", "Open positions"]
    # pending orders (normalmente vazio)
    pend = _subsection_block(block, "Pending orders", markers)
    tables["invest_pending_orders"] = []  # sem parsing (No data). Se houver dados sera raro.
    # open positions
    op = _subsection_block(block, "Open positions", markers)
    header_tokens = {
        "INSTRUMENT", "ISIN", "QUANTITY", "AVERAGE PRICE", "PRICE",
        "RETURN", "VALUE", "FX RATE",
    }
    op = _strip_header_tokens(op, header_tokens)
    recs = _chunk_records(op, len(FIELDS_INVEST_OPEN))
    tables["invest_open_positions"] = [_build_record(file_id, FIELDS_INVEST_OPEN, r) for r in recs]

    # ---- 4 & 5. Invest transactions and dividends ----
    block = _section_block(lines, "Invest account - transactions and dividends")
    markers = ["Transactions", "Dividends"]
    tx = _subsection_block(block, "Transactions", markers)
    tx = _strip_header_tokens(tx, {"TIME", "TYPE", "AMOUNT"})
    recs = _anchor_records(tx, RE_DATETIME, len(FIELDS_INVEST_TX))
    tables["invest_transactions"] = [_build_record(file_id, FIELDS_INVEST_TX, r) for r in recs]
    tables["invest_dividends"] = []  # normalmente No data

    # ---- 6. CFD executed trades (date+time em 2 linhas) ----
    block = _section_block(lines, "CFD account - executed trades")
    tables["cfd_executed_trades"] = _parse_cfd_exec(block, file_id)

    # ---- 7 & 8. CFD open positions summary ----
    block = _section_block(lines, "CFD account - open positions summary")
    markers = ["Pending orders", "Open positions"]
    tables["cfd_pending_orders"] = []
    op = _subsection_block(block, "Open positions", markers)
    header_tokens = {
        "INSTRUMENT", "DIRECTION", "POSITION SIZE", "AVERAGE PRICE", "PRICE",
        "VALUE", "FX RATE", "FX FEE", "RESULT", "DIVIDEND ADJUSTMENTS",
        "OVERNIGHT INTEREST", "TOTAL RESULT", "PERIOD PRICE CHANGE", "MARGIN",
    }
    op = _strip_header_tokens(op, header_tokens)
    recs = _chunk_records(op, len(FIELDS_CFD_OPEN))
    tables["cfd_open_positions"] = [_build_record(file_id, FIELDS_CFD_OPEN, r) for r in recs]

    # ---- 9,10,11. CFD transactions, dividend adj, overnight interest ----
    block = _section_block(lines, "CFD account - transactions, dividends and overnight interest")
    markers = ["Transactions", "Dividend adjustments", "Overnight interest"]
    tables["cfd_transactions"] = []
    tables["cfd_dividend_adjustments"] = []
    ov = _subsection_block(block, "Overnight interest", markers)
    ov = _strip_header_tokens(ov, {
        "TRANSACTION TIME", "INSTRUMENT", "DIRECTION", "POSITION SIZE",
        "OVERNIGHT INTEREST RATE", "AMOUNT", "FX RATE",
    })
    recs = _anchor_records(ov, RE_DATE, len(FIELDS_CFD_OVERNIGHT))
    tables["cfd_overnight_interest"] = [_build_record(file_id, FIELDS_CFD_OVERNIGHT, r) for r in recs]

    # ---- 12. Crypto executed trades (anchor datetime, 10) ----
    block = _section_block(lines, "Crypto account - executed trades")
    ce = _strip_header_tokens(block, {
        "EXECUTION TIME", "SYMBOL", "ASSET", "ORDER ID", "FILL ID", "DIRECTION",
        "QUANTITY", "EXECUTION PRICE", "VALUE", "REALISED P/L",
    })
    recs = _anchor_records(ce, RE_DATETIME, len(FIELDS_CRYPTO_EXEC))
    tables["crypto_executed_trades"] = [_build_record(file_id, FIELDS_CRYPTO_EXEC, r) for r in recs]

    # ---- 13 & 14. Crypto open positions summary ----
    block = _section_block(lines, "Crypto account - open positions summary")
    markers = ["Pending orders", "Open positions"]
    tables["crypto_pending_orders"] = []
    op = _subsection_block(block, "Open positions", markers)
    op = _strip_header_tokens(op, {
        "SYMBOL", "ASSET", "QUANTITY", "OPENING PRICE", "PRICE",
        "UNREALISED P/L", "VALUE",
    })
    recs = _chunk_records(op, len(FIELDS_CRYPTO_OPEN))
    tables["crypto_open_positions"] = [_build_record(file_id, FIELDS_CRYPTO_OPEN, r) for r in recs]

    # ---- 15. Crypto transactions ----
    block = _section_block(lines, "Crypto account - transactions")
    tables["crypto_transactions"] = []  # normalmente No data

    doc.close()
    return {"metadata": metadata, "tables": tables}


def _parse_cfd_exec(block: List[str], file_id: str) -> List[Dict[str, Any]]:
    """CFD executed trades: execution time vem em 2 linhas (data + hora)."""
    header_tokens = {
        "EXECUTION TIME", "INSTRUMENT", "ORDER ID", "ORDER TYPE", "DIRECTION",
        "EXECUTION", "VENUE", "POSITION SIZE", "AVERAGE PRICE", "EXECUTION PRICE",
        "VALUE", "SPREAD", "FX RATE", "FX FEE", "RESULT", "DIVIDEND",
        "ADJUSTMENTS", "OVERNIGHT", "INTEREST", "TOTAL RESULT",
    }
    clean = _strip_header_tokens(block, header_tokens)
    # anchor: linha data seguida de linha hora
    records = []
    idxs = [i for i, l in enumerate(clean) if RE_DATE.match(l)]
    n_fields = len(FIELDS_CFD_EXEC)  # 17 (execution_time conta como 1)
    for n, start in enumerate(idxs):
        end = idxs[n + 1] if n + 1 < len(idxs) else len(clean)
        slice_ = clean[start:end]
        if len(slice_) < 2:
            continue
        # combinar data + hora
        dt = f"{slice_[0]} {slice_[1]}"
        values = [dt] + slice_[2:2 + (n_fields - 1)]
        records.append(_build_record(file_id, FIELDS_CFD_EXEC, values))
    return records
