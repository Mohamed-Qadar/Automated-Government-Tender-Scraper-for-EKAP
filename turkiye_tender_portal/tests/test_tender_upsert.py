from django.test import TestCase
from django.utils import timezone
from tenders import constants
from tenders.models import Tender
from tenders.services.public_source_adapter import RawTender
from tenders.services.tender_upsert import upsert_tender


class TenderUpsertTests(TestCase):
    def setUp(self):
        self.keywords = ["laboratuvar", "sarf"]

    def _raw(self, no, title="laboratuvar sarf alımı", url=""):
        return RawTender(
            tender_no=no,
            title=title,
            authority_name="Test Hastanesi",
            province="Elazığ",
            district="Merkez",
            tender_type=constants.TENDER_TYPE_MAL,
            category="mal_alimi",
            tender_procedure="Açık",
            announcement_date=timezone.localdate(),
            tender_date=timezone.localdate(),
            deadline_date=timezone.localdate(),
            work_location="Elazığ",
            short_description="Açıklama",
            official_url=url,
            source=constants.SOURCE_EKAP,
            status=constants.STATUS_ACTIVE,
        )

    def test_upsert_creates_new(self):
        raw = self._raw("2026/940121", url="https://ekapv2.kik.gov.tr/ekap/search/ihale-detay/123")
        tender, created, updated = upsert_tender(raw, self.keywords)
        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertEqual(Tender.objects.count(), 1)
        self.assertEqual(tender.tender_no, "2026/940121")
        self.assertEqual(tender.keyword_matches, "laboratuvar, sarf")

    def test_upsert_idempotent_no_changes(self):
        raw = self._raw("2026/940121", url="https://ekapv2.kik.gov.tr/ekap/search/ihale-detay/123")
        tender1, created1, updated1 = upsert_tender(raw, self.keywords)
        self.assertTrue(created1)
        
        # Upsert again with same data
        tender2, created2, updated2 = upsert_tender(raw, self.keywords)
        self.assertFalse(created2)
        self.assertFalse(updated2)
        self.assertEqual(Tender.objects.count(), 1)
        self.assertEqual(tender2.pk, tender1.pk)

    def test_upsert_updates_changed_fields(self):
        raw1 = self._raw("2026/940121", title="eski baslik", url="https://ekapv2.kik.gov.tr/ekap/search/ihale-detay/123")
        tender1, created1, updated1 = upsert_tender(raw1, self.keywords)
        self.assertTrue(created1)
        
        raw2 = self._raw("2026/940121", title="yeni baslik", url="https://ekapv2.kik.gov.tr/ekap/search/ihale-detay/123")
        tender2, created2, updated2 = upsert_tender(raw2, self.keywords)
        self.assertFalse(created2)
        self.assertTrue(updated2)
        self.assertEqual(Tender.objects.count(), 1)
        self.assertEqual(tender2.title, "yeni baslik")
