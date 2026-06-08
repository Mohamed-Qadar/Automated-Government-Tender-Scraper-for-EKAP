from django.test import TestCase

from tenders import constants
from tenders.models import Tender
from tenders.services.duplicate_checker import filter_new, is_duplicate
from tenders.services.public_source_adapter import RawTender


class DuplicateCheckerTests(TestCase):
    def _raw(self, no, url=""):
        return RawTender(
            tender_no=no, title="x", source=constants.SOURCE_MOCK, official_url=url
        )

    def test_is_duplicate_by_tender_no(self):
        Tender.objects.create(tender_no="A1", title="x", source=constants.SOURCE_MOCK)
        self.assertTrue(is_duplicate(self._raw("A1")))
        self.assertFalse(is_duplicate(self._raw("A2")))

    def test_filter_new_dedupes_db_and_batch(self):
        Tender.objects.create(tender_no="A1", title="x", source=constants.SOURCE_MOCK)
        records = [self._raw("A1"), self._raw("A2"), self._raw("A2")]
        new, dups = filter_new(records)
        self.assertEqual(len(new), 1)       # only A2 once
        self.assertEqual(len(dups), 2)      # A1 (db) + duplicate A2 (batch)
        self.assertEqual(new[0].tender_no, "A2")
