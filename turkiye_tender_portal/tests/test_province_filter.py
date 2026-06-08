from django.test import TestCase

from tenders import constants
from tenders.models import Tender
from tenders.services.province_filter import (
    filter_tenders,
    is_all_turkiye,
    normalize_province,
)


class ProvinceFilterTests(TestCase):
    def setUp(self):
        Tender.objects.create(tender_no="1", title="a", province="Elazığ",
                              category="yapim_ihaleleri", source="MOCK")
        Tender.objects.create(tender_no="2", title="b", province="İstanbul",
                              category="mal_alimi", source="MOCK")
        Tender.objects.create(tender_no="3", title="c", province="Ankara",
                              category="yapim_ihaleleri", source="MOCK")

    def test_normalize_all_turkiye(self):
        self.assertIsNone(normalize_province("ALL"))
        self.assertIsNone(normalize_province(""))
        self.assertTrue(is_all_turkiye("Tüm Türkiye"))
        self.assertEqual(normalize_province("Elazığ"), "Elazığ")

    def test_province_filter_single(self):
        qs = filter_tenders(province="Elazığ")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().province, "Elazığ")

    def test_all_turkiye_returns_everything(self):
        qs = filter_tenders(province="ALL")
        self.assertEqual(qs.count(), 3)

    def test_category_filter(self):
        qs = filter_tenders(province="ALL", category="yapim_ihaleleri")
        self.assertEqual(qs.count(), 2)
