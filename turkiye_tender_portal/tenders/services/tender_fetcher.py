"""
Orchestration layer: ties the source adapter + cleaner + duplicate checker +
persistence + fetch logging together. Used by the dashboard "Yeni İlanları Çek"
button and the fetch_tenders management command.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from django.utils import timezone

from ..models import Keyword, Tender, TenderFetchLog
from . import duplicate_checker, tender_cleaner
from .public_source_adapter import FetchParams, get_adapter
from .province_filter import is_all_turkiye, normalize_province

logger = logging.getLogger("tenders")


def _active_keywords() -> list[str]:
    return list(Keyword.objects.filter(is_active=True).values_list("name", flat=True))


def _save_raw(raw) -> Tender:
    return Tender.objects.create(
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
        keyword_matches=raw.keyword_matches if hasattr(raw, "keyword_matches") else "",
        raw_data=raw.extra or {},
    )


def fetch_and_store(
    *,
    province: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    tender_type: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    all_turkiye: bool = False,
    limit: int = 100,
) -> TenderFetchLog:
    """Run a controlled fetch and persist new tenders. Always returns a log."""
    prov = normalize_province(province)
    all_tr = all_turkiye or is_all_turkiye(province)

    log = TenderFetchLog.objects.create(
        started_at=timezone.now(),
        status=TenderFetchLog.STATUS_RUNNING,
        province="" if all_tr else (prov or ""),
        district=district or "",
    )

    adapter = get_adapter()
    log.source = adapter.name

    params = FetchParams(
        province=None if all_tr else prov,
        district=district,
        category=category,
        tender_type=tender_type,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to,
        all_turkiye=all_tr,
        limit=limit,
    )

    keywords = _active_keywords()

    try:
        raw_records = adapter.fetch(params)
        log.total_found = len(raw_records)

        new_count = 0
        dup_count = 0
        from .tender_upsert import upsert_tender

        for r in raw_records:
            tender_cleaner.clean_raw_tender(r)
            _, created, _ = upsert_tender(r, keywords)
            if created:
                new_count += 1
            else:
                dup_count += 1

        log.new_records = new_count
        log.duplicate_records = dup_count
        log.status = TenderFetchLog.STATUS_SUCCESS
        logger.info(
            "Fetch ok: found=%s new=%s dup=%s province=%s",
            log.total_found, log.new_records, log.duplicate_records,
            log.province or "Tüm Türkiye",
        )
    except NotImplementedError as exc:
        log.status = TenderFetchLog.STATUS_FAILED
        log.error_message = str(exc)
        logger.warning("Fetch not implemented: %s", exc)
    except Exception as exc:  # noqa: BLE001
        log.status = TenderFetchLog.STATUS_FAILED
        log.error_message = f"{type(exc).__name__}: {exc}"
        logger.exception("Fetch failed")
    finally:
        log.finished_at = timezone.now()
        log.save()

    return log
