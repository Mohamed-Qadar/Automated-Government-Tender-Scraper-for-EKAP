"""Duplicate detection: a tender is a duplicate if (tender_no, source) exists,
or if the official_url already exists."""
from __future__ import annotations

from ..models import Tender
from .public_source_adapter import RawTender


def is_duplicate(raw: RawTender) -> bool:
    qs = Tender.objects.all()
    if raw.tender_no and qs.filter(tender_no=raw.tender_no, source=raw.source).exists():
        return True
    if raw.official_url and qs.filter(official_url=raw.official_url).exists():
        # Only treat URL as duplicate when it is a real, specific link.
        if raw.official_url not in ("", "https://ekap.kik.gov.tr/EKAP/"):
            return True
    return False


def filter_new(records: list[RawTender]):
    """Split records into (new, duplicates) using DB + in-batch dedupe."""
    new, dups = [], []
    seen = set()
    for r in records:
        key = (r.tender_no, r.source)
        if key in seen or is_duplicate(r):
            dups.append(r)
        else:
            seen.add(key)
            new.append(r)
    return new, dups
