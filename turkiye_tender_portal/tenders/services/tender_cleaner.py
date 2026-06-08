"""Normalize/clean RawTender data and detect keyword matches before saving."""
from __future__ import annotations

from .public_source_adapter import RawTender
from .tender_parser import clean_text


def clean_raw_tender(raw: RawTender) -> RawTender:
    """Return a cleaned copy-in-place of a RawTender."""
    raw.title = clean_text(raw.title)
    raw.authority_name = clean_text(raw.authority_name)
    raw.province = clean_text(raw.province)
    raw.district = clean_text(raw.district)
    raw.work_location = clean_text(raw.work_location)
    raw.short_description = clean_text(raw.short_description)
    raw.tender_no = clean_text(raw.tender_no)
    raw.official_url = (raw.official_url or "").strip()
    return raw


def match_keywords(raw: RawTender, keywords: list[str]) -> str:
    """Return a comma-separated list of keywords found in the tender text."""
    if not keywords:
        return ""
    blob = " ".join(
        [raw.title, raw.authority_name, raw.short_description, raw.work_location]
    ).lower()
    found = [kw for kw in keywords if kw and kw.lower() in blob]
    return ", ".join(sorted(set(found)))
