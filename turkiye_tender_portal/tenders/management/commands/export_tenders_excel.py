"""Export tenders to an Excel file under exports/excel/."""
from django.core.management.base import BaseCommand, CommandError

from tenders.services import excel_exporter
from tenders.services.province_filter import filter_tenders, normalize_province


class Command(BaseCommand):
    help = "Seçilen il veya tüm Türkiye için ihaleleri Excel'e aktarır."

    def add_arguments(self, parser):
        parser.add_argument("--province", type=str, default=None)
        parser.add_argument("--category", type=str, default=None)
        parser.add_argument("--all-turkiye", action="store_true")

    def handle(self, *args, **options):
        if not options["province"] and not options["all_turkiye"]:
            raise CommandError("--province veya --all-turkiye belirtin.")

        province = None if options["all_turkiye"] else options["province"]
        qs = filter_tenders(
            province=province, category=options["category"]
        ).order_by("-announcement_date")

        filters = {
            "province": normalize_province(province) or "Tüm Türkiye",
            "category_label": options["category"] or "",
        }
        path = excel_exporter.export_to_file(qs, filters=filters)
        self.stdout.write(self.style.SUCCESS(
            f"{qs.count()} kayıt dışa aktarıldı: {path}"
        ))
