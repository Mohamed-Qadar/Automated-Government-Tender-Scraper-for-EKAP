"""
Public source adapter interface.

This defines a clean, swappable contract for fetching PUBLIC tender data.
The MVP ships with a MockPublicSourceAdapter so the whole application works
end-to-end. A real EKAP adapter can be added later by implementing the same
`fetch()` signature WITHOUT changing any caller code.

Legal / technical notes:
  * Only publicly available official data may be fetched.
  * Do NOT bypass login, e-signature, mobile signature, CAPTCHA or paywalls.
  * Use controlled requests with delays, retries, timeouts and logging.
  * Never overload source websites.
"""
from __future__ import annotations

import abc
import logging
import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from django.conf import settings
from django.utils import timezone

from .. import constants

logger = logging.getLogger("tenders")


@dataclass
class FetchParams:
    """Normalized parameters passed to any adapter."""

    province: Optional[str] = None      # province name or None / ALL for Türkiye
    district: Optional[str] = None
    category: Optional[str] = None
    tender_type: Optional[str] = None
    keyword: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    all_turkiye: bool = False
    limit: int = 100

    @property
    def is_all_turkiye(self) -> bool:
        return self.all_turkiye or self.province in (None, "", constants.ALL_TURKIYE)


@dataclass
class RawTender:
    """Source-neutral raw record. `extra` is stored in Tender.raw_data."""

    tender_no: str
    title: str
    authority_name: str = ""
    province: str = ""
    district: str = ""
    tender_type: str = ""
    category: str = ""
    tender_procedure: str = ""
    announcement_date: Optional[date] = None
    tender_date: Optional[date] = None
    deadline_date: Optional[date] = None
    work_location: str = ""
    short_description: str = ""
    official_url: str = ""
    source: str = constants.SOURCE_MOCK
    status: str = constants.STATUS_ACTIVE
    extra: dict = field(default_factory=dict)


class BasePublicSourceAdapter(abc.ABC):
    """Contract every concrete source adapter must implement."""

    name = "base"

    @abc.abstractmethod
    def fetch(self, params: FetchParams) -> list[RawTender]:
        """Return a list of RawTender for the given params."""
        raise NotImplementedError


# --------------------------------------------------------------------------- #
#  EKAP Adapter Factory                                                       #
# --------------------------------------------------------------------------- #

def get_adapter() -> BasePublicSourceAdapter:
    """Factory: returns the configured real EKAP scraper adapter."""
    from .ekap_scraper import EkapPublicAdapter
    return EkapPublicAdapter()
