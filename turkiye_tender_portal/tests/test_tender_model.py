from django.test import TestCase

from tenders import constants
from tenders.models import Tender


class TenderModelTests(TestCase):
    def test_create_and_str(self):
        t = Tender.objects.create(
            tender_no="2026/123456",
            title="Test Yapım İşi",
            province="Elazığ",
            tender_type=constants.TENDER_TYPE_YAPIM,
            category="yapim_ihaleleri",
            source=constants.SOURCE_MOCK,
        )
        self.assertIn("2026/123456", str(t))
        self.assertEqual(t.province, "Elazığ")

    def test_unique_tender_no_source(self):
        Tender.objects.create(tender_no="X1", title="A", source=constants.SOURCE_MOCK)
        from django.db import IntegrityError, transaction

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Tender.objects.create(tender_no="X1", title="B", source=constants.SOURCE_MOCK)
