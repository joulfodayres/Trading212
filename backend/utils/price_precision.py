"""
Price precision inference helper.

T212's /equity/positions response documents `currentPrice` only as
`type: number` (see docs/t212-api/api.yaml) — there is no explicit
"how many decimals does this instrument use" field. Different instruments
return different decimal counts (e.g. "166.80" vs "4.125" vs "23.5"
vs a whole number like "166"), and this varies per ISIN.

A Python float can't distinguish 166.80 from 166.8 (both normalize to
166.8), so the only reliable way to recover "how many decimals did T212
actually send" is to look at the ORIGINAL JSON TEXT before it gets parsed
into floats. This module extracts, in document order, the decimal-digit
count of every top-level "currentPrice" occurrence in the raw response
body, so callers can zip() that list against the already-parsed list of
position dicts (array order is preserved identically by both a regex
walk over the raw text and `response.json()` — both are a single
left-to-right pass over the same document).

Unrelated to `isins.quantity_precision` (which is about how many decimal
places T212 accepts for an ISIN's QUANTITY, not its price) — do not
conflate the two.
"""

import re
from typing import List

DEFAULT_PRICE_PRECISION = 2

# Matches a top-level `"currentPrice": <number>` occurrence, capturing the
# fractional digits if present. Deliberately simple/non-nested — T212's
# positions array has `currentPrice` as a flat numeric field per position,
# never nested under another object with the same key.
_CURRENT_PRICE_RE = re.compile(r'"currentPrice"\s*:\s*-?\d+(?:\.(\d+))?')


def infer_price_precisions_from_raw_json(raw_text: str) -> List[int]:
    """
    Walks the raw JSON response text and returns the inferred decimal
    precision for each "currentPrice" occurrence found, in document order.

    Falls back to DEFAULT_PRICE_PRECISION (2) for any value with no decimal
    point in the JSON (e.g. `"currentPrice":166`) is handled explicitly as
    precision 0, NOT the default — an integer price is a valid, deliberate
    precision of 0 decimals. The default only applies when inference itself
    is impossible (e.g. this function found no matches at all, or the
    caller index runs past the end of the list — see
    `get_price_precision_at` below).
    """
    precisions = []
    for m in _CURRENT_PRICE_RE.finditer(raw_text):
        fractional = m.group(1)
        precisions.append(len(fractional) if fractional else 0)
    return precisions


def get_price_precision_at(precisions: List[int], index: int) -> int:
    """Safe lookup with fallback to DEFAULT_PRICE_PRECISION if the raw-text
    walk didn't find a matching occurrence for this position's index
    (e.g. unexpected response shape)."""
    if 0 <= index < len(precisions):
        return precisions[index]
    return DEFAULT_PRICE_PRECISION
