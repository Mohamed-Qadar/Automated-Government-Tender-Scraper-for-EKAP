from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from tenders.services.tender_fetcher import fetch_and_store


class Command(BaseCommand):
    help = "EKAP üzerinden canlı ihale verilerini çekip yerel veritabanına kaydeder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--province",
            type=str,
            default=None,
            help="İl adı (Örn: Elazığ)",
        )
        parser.add_argument(
            "--all-turkiye",
            action="store_true",
            help="Tüm Türkiye'den ihaleleri çek",
        )
        parser.add_argument(
            "--procurement-type",
            type=str,
            default=None,
            choices=["MAL", "HIZMET", "YAPIM", "DANISMANLIK", "mal", "hizmet", "yapim", "danismanlik"],
            help="Alım Türü (MAL, HIZMET, YAPIM, DANISMANLIK)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Son kaç günlük ilanları çekmek istediğiniz",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Çekilecek maksimum kayıt (varsayılan 50)",
        )

    def handle(self, *args, **options):
        if not options["province"] and not options["all_turkiye"]:
            raise CommandError("--province veya --all-turkiye parametrelerinden en az birini belirtmelisiniz.")

        date_from = None
        if options["days"] is not None:
            date_from = timezone.localdate() - timedelta(days=options["days"])

        proc_type = options["procurement_type"]
        if proc_type:
            proc_type = proc_type.upper()

        scope = "Tüm Türkiye" if options["all_turkiye"] else options["province"]
        self.stdout.write(f"[{scope}] İhale çekme işlemi başlatılıyor...")

        # Fetch and store
        log = fetch_and_store(
            province=options["province"],
            tender_type=proc_type,
            date_from=date_from,
            all_turkiye=options["all_turkiye"],
            limit=options["limit"],
        )

        if log.status == log.STATUS_SUCCESS:
            self.stdout.write(self.style.SUCCESS(
                f"[{scope}] Çekim Başarılı! Bulunan: {log.total_found}, Yeni: {log.new_records}, "
                f"Tekrar/Güncellenen: {log.duplicate_records}"
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"[{scope}] Çekim Başarısız! Hata: {log.error_message}"
            ))
