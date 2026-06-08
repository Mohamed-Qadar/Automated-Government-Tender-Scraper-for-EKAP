"""Parse raw source payloads (HTML/JSON) into RawTender objects.

Kept source-agnostic: parsing helpers live here so adapters stay thin.
For the mock adapter no parsing is needed; these helpers are ready for the
real EKAP adapter step.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

_DATE_FORMATS = ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y %H:%M")


def parse_date(value) -> Optional[date]:
    """Best-effort Turkish date parsing -> date or None."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # try to extract dd.mm.yyyy from a longer string
    m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", text)
    if m:
        d, mo, y = (int(g) for g in m.groups())
        try:
            return date(y, mo, d)
        except ValueError:
            return None
    return None


def clean_text(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()
