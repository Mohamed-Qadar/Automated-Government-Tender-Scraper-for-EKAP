"""Fetch tenders for a province or all of Türkiye via the configured adapter."""
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from tenders.services.tender_fetcher import fetch_and_store


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


class Command(BaseCommand):
    help = "Seçilen il veya tüm Türkiye için ihale çeker."

    def add_arguments(self, parser):
        parser.add_argument("--province", type=str, default=None)
        parser.add_argument("--district", type=str, default=None)
        parser.add_argument("--category", type=str, default=None)
        parser.add_argument("--keyword", type=str, default=None)
        parser.add_argument("--date-from", type=str, default=None)
        parser.add_argument("--date-to", type=str, default=None)
        parser.add_argument("--all-turkiye", action="store_true")
        parser.add_argument("--limit", type=int, default=50,
                            help="Çekilecek maksimum kayıt (varsayılan 50)")
        parser.add_argument("--clear-mock", action="store_true",
                            help="Çekimden önce demo (MOCK) kayıtları siler")

    def handle(self, *args, **options):
        if not options["province"] and not options["all_turkiye"]:
            raise CommandError("--province veya --all-turkiye belirtin.")

        if options["clear_mock"]:
            from tenders.models import Tender
            from tenders import constants as c
            n = Tender.objects.filter(source=c.SOURCE_MOCK).delete()[0]
            self.stdout.write(self.style.WARNING(f"{n} demo (MOCK) kayıt silindi."))

        log = fetch_and_store(
            province=options["province"],
            district=options["district"],
            category=options["category"],
            keyword=options["keyword"],
            date_from=_parse_date(options["date_from"]),
            date_to=_parse_date(options["date_to"]),
            all_turkiye=options["all_turkiye"],
            limit=options["limit"],
        )
        scope = "Tüm Türkiye" if options["all_turkiye"] else options["province"]
        if log.status == log.STATUS_SUCCESS:
            self.stdout.write(self.style.SUCCESS(
                f"[{scope}] Bulunan: {log.total_found}, Yeni: {log.new_records}, "
                f"Tekrar: {log.duplicate_records}"
            ))
        else:
            self.stdout.write(self.style.ERROR(f"[{scope}] Hata: {log.error_message}"))
