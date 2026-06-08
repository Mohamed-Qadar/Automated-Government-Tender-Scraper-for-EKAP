from django.test import TestCase, override_settings

from tenders import constants
from tenders.models import Tender
from tenders.services import excel_exporter


class ExcelExporterTests(TestCase):
    def setUp(self):
        for i in range(3):
            Tender.objects.create(
                tender_no=f"E{i}", title=f"Test {i}", province="Elazığ",
                tender_type=constants.TENDER_TYPE_YAPIM,
                category="yapim_ihaleleri", source=constants.SOURCE_MOCK,
                official_url="https://ekap.kik.gov.tr/EKAP/",
            )

    def test_export_to_bytes_nonempty(self):
        data = excel_exporter.export_to_bytes(
            Tender.objects.all(), filters={"province": "Elazığ"}
        )
        self.assertTrue(len(data) > 1000)
        # XLSX files are zip archives -> start with PK
        self.assertEqual(data[:2], b"PK")

    def test_export_to_file_created(self):
        path = excel_exporter.export_to_file(
            Tender.objects.all(), filters={"province": "Elazığ"}
        )
        self.assertTrue(path.exists())
        self.assertTrue(path.name.endswith(".xlsx"))


@override_settings(USE_MOCK_TENDER_SOURCE=True)
class FetchLogTests(TestCase):
    def test_fetch_creates_log_and_records(self):
        from tenders.models import TenderFetchLog
        from tenders.services.tender_fetcher import fetch_and_store

        log = fetch_and_store(province="Elazığ")
        self.assertEqual(TenderFetchLog.objects.count(), 1)
        self.assertEqual(log.status, TenderFetchLog.STATUS_SUCCESS)
        self.assertTrue(Tender.objects.filter(province="Elazığ").exists())
