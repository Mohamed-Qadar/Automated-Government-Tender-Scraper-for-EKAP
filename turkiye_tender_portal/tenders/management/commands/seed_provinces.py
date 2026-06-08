"""Seed all 81 Turkish provinces (and sample districts for demo provinces)."""
from django.core.management.base import BaseCommand

from tenders import constants
from tenders.models import District, Province


class Command(BaseCommand):
    help = "81 ili ve örnek ilçeleri veritabanına ekler."

    def handle(self, *args, **options):
        created = 0
        for plate, name in constants.PROVINCES:
            obj, was_created = Province.objects.update_or_create(
                plate_code=plate, defaults={"name": name, "is_active": True}
            )
            created += int(was_created)

        d_created = 0
        for prov_name, districts in constants.SAMPLE_DISTRICTS.items():
            try:
                province = Province.objects.get(name=prov_name)
            except Province.DoesNotExist:
                continue
            for d in districts:
                _, dc = District.objects.get_or_create(province=province, name=d)
                d_created += int(dc)

        self.stdout.write(self.style.SUCCESS(
            f"İller: {Province.objects.count()} (yeni {created}). "
            f"Örnek ilçeler eklendi (yeni {d_created})."
        ))
