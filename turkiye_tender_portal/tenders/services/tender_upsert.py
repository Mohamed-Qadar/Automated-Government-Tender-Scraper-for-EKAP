from __future__ import annotations

from django.utils import timezone
from ..models import Tender
from .public_source_adapter import RawTender


def upsert_tender(raw: RawTender, keywords: list[str]) -> tuple[Tender, bool, bool]:
    """
    Idempotently upsert a RawTender into the database.
    Matches by tender_no/source or fallback to official_url.
    Updates changed fields, sets last_seen_at, and saves raw data.
    
    Returns (tender_instance, created_boolean, updated_boolean).
    """
    # 1. Determine key matching conditions
    match_by_no = bool(raw.tender_no and raw.tender_no.strip())
    match_by_url = bool(raw.official_url and raw.official_url.strip() and 
                        raw.official_url not in ("https://ekap.kik.gov.tr/EKAP/", "https://ekapv2.kik.gov.tr/ekap/search"))
    
    tender = None
    if match_by_no:
        tender = Tender.objects.filter(tender_no=raw.tender_no, source=raw.source).first()
    
    if not tender and match_by_url:
        tender = Tender.objects.filter(official_url=raw.official_url).first()
        
    now = timezone.now()
    
    # Run keyword match
    from .tender_cleaner import match_keywords
    kw_matches = match_keywords(raw, keywords)
    
    if tender:
        # Check for changes
        has_changes = False
        fields_to_check = {
            "title": raw.title,
            "authority_name": raw.authority_name,
            "province": raw.province,
            "district": raw.district,
            "tender_type": raw.tender_type,
            "category": raw.category,
            "tender_procedure": raw.tender_procedure,
            "announcement_date": raw.announcement_date,
            "tender_date": raw.tender_date,
            "deadline_date": raw.deadline_date,
            "work_location": raw.work_location,
            "short_description": raw.short_description,
            "official_url": raw.official_url,
            "status": raw.status,
            "keyword_matches": kw_matches,
        }
        
        for field, new_val in fields_to_check.items():
            old_val = getattr(tender, field)
            if old_val != new_val:
                setattr(tender, field, new_val)
                has_changes = True
                
        # Also check raw_data
        if tender.raw_data != (raw.extra or {}):
            tender.raw_data = raw.extra or {}
            has_changes = True
            
        tender.last_seen_at = now
        tender.save()
        return tender, False, has_changes
    else:
        # Create new record
        tender = Tender.objects.create(
            tender_no=raw.tender_no,
            title=raw.title,
            authority_name=raw.authority_name,
            province=raw.province,
            district=raw.district,
            tender_type=raw.tender_type,
            category=raw.category,
            tender_procedure=raw.tender_procedure,
            announcement_date=raw.announcement_date,
            tender_date=raw.tender_date,
            deadline_date=raw.deadline_date,
            work_location=raw.work_location,
            short_description=raw.short_description,
            official_url=raw.official_url,
            source=raw.source,
            status=raw.status,
            keyword_matches=kw_matches,
            raw_data=raw.extra or {},
            first_seen_at=now,
            last_seen_at=now,
        )
        return tender, True, False
