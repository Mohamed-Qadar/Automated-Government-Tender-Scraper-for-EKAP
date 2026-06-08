"""Seed demo keywords and initialize database."""
from django.core.management.base import BaseCommand

from tenders.models import Keyword


DEMO_KEYWORDS = [
    "yapım", "asfalt", "yazılım", "temizlik", "güvenlik", "akaryakıt",
    "tıbbi", "danışmanlık", "elektrik", "gıda", "eğitim", "su",
]


class Command(BaseCommand):
    help = "Demo anahtar kelimeler üretir. Örnek ihale verisi üretimi temizlenmiştir."

    def add_arguments(self, parser):
        parser.add_argument("--provinces", nargs="*", default=["Elazığ", "İstanbul", "Ankara", "İzmir"])

    def handle(self, *args, **options):
        for kw in DEMO_KEYWORDS:
            Keyword.objects.get_or_create(name=kw)
        self.stdout.write(self.style.SUCCESS(f"{len(DEMO_KEYWORDS)} anahtar kelime hazır."))
        self.stdout.write(self.style.WARNING("Örnek (MOCK) ihale verisi üretimi veri temizliği kapsamında devre dışı bırakılmıştır. Lütfen gerçek verileri çekmek için ekap_veri_cek.bat dosyasını kullanın."))
