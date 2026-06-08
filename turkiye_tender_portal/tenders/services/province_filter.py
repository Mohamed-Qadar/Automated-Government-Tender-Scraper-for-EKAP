"""Province / district helpers and Tender queryset filtering."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from django.db.models import Q
from django.utils import timezone

from .. import constants
from ..models import Tender


def normalize_province(value: Optional[str]) -> Optional[str]:
    """Return a clean province name, or None for 'Tüm Türkiye'/empty."""
    if not value or value in (constants.ALL_TURKIYE, "Tüm Türkiye", "tum_turkiye"):
        return None
    return value.strip()


def is_all_turkiye(value: Optional[str]) -> bool:
    return normalize_province(value) is None


def filter_tenders(
    queryset=None,
    *,
    province: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None,
    title: Optional[str] = None,
    authority_name: Optional[str] = None,
    tender_type: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    today_only: bool = False,
    this_week_only: bool = False,
):
    """Apply all list-page filters to a Tender queryset."""
    qs = Tender.objects.all() if queryset is None else queryset

    prov = normalize_province(province)
    if prov:
        qs = qs.filter(province__iexact=prov)
    if district:
        qs = qs.filter(district__iexact=district.strip())
    if tender_type:
        qs = qs.filter(tender_type=tender_type)
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if title:
        qs = qs.filter(title__icontains=title.strip())
    if authority_name:
        qs = qs.filter(authority_name__icontains=authority_name.strip())
    if keyword:
        qs = qs.filter(
            Q(keyword_matches__icontains=keyword.strip())
            | Q(title__icontains=keyword.strip())
            | Q(short_description__icontains=keyword.strip())
        )
    if search:
        s = search.strip()
        qs = qs.filter(
            Q(title__icontains=s)
            | Q(authority_name__icontains=s)
            | Q(tender_no__icontains=s)
            | Q(work_location__icontains=s)
            | Q(short_description__icontains=s)
        )

    today = timezone.localdate()
    if today_only:
        qs = qs.filter(announcement_date=today)
    if this_week_only:
        start = today - timedelta(days=today.weekday())
        qs = qs.filter(announcement_date__gte=start, announcement_date__lte=today)
    if date_from:
        qs = qs.filter(announcement_date__gte=date_from)
    if date_to:
        qs = qs.filter(announcement_date__lte=date_to)

    return qs
