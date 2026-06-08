"""Create demo users with profiles + subscriptions for testing.

Idempotent: re-running updates passwords/subscriptions instead of duplicating.
Prints a username/password table at the end.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import UserProfile

# (username, password, is_superuser, company, city, status, days, package)
DEMO_USERS = [
    ("admin",    "Admin.2026!",    True,  "Sistem Yöneticisi",  "Ankara",   UserProfile.STATUS_ACTIVE, 3650, "Yönetici"),
    ("demo",     "Demo.2026!",     False, "Demo İnşaat A.Ş.",   "Elazığ",   UserProfile.STATUS_ACTIVE,  365, "Yıllık"),
    ("elazig",   "Elazig.2026!",   False, "Elazığ Yapı Ltd.",   "Elazığ",   UserProfile.STATUS_ACTIVE,   30, "Aylık"),
    ("istanbul", "Istanbul.2026!", False, "Marmara Tedarik",    "İstanbul", UserProfile.STATUS_ACTIVE,   30, "Aylık"),
    ("deneme",   "Deneme.2026!",   False, "Deneme Kullanıcı",   "İzmir",    UserProfile.STATUS_TRIAL,    14, "Deneme"),
    ("suresidolmus", "Suresi.2026!", False, "Pasif Firma",      "Bursa",    UserProfile.STATUS_EXPIRED,  -5, "Aylık"),
]


class Command(BaseCommand):
    help = "Test için demo kullanıcılar ve abonelikler oluşturur."

    def handle(self, *args, **options):
        today = timezone.localdate()
        rows = []
        for username, pwd, is_su, company, city, status, days, package in DEMO_USERS:
            user, _ = User.objects.get_or_create(username=username)
            user.set_password(pwd)
            user.is_superuser = is_su
            user.is_staff = is_su
            user.email = f"{username}@example.com"
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.company_name = company
            profile.city = city
            profile.subscription_status = status
            profile.subscription_start_date = today
            profile.subscription_end_date = today + timedelta(days=days)
            profile.package_name = package
            profile.save()

            role = "Süper Kullanıcı" if is_su else "Normal Kullanıcı"
            rows.append((username, pwd, role, profile.get_subscription_status_display(),
                         profile.subscription_end_date.strftime("%d.%m.%Y")))

        self.stdout.write(self.style.SUCCESS(f"{len(rows)} kullanıcı hazır.\n"))
        h = ("Kullanıcı", "Şifre", "Rol", "Abonelik", "Bitiş")
        widths = [max(len(str(r[i])) for r in rows + [h]) for i in range(5)]
        line = "  ".join(h[i].ljust(widths[i]) for i in range(5))
        self.stdout.write(line)
        self.stdout.write("-" * len(line))
        for r in rows:
            self.stdout.write("  ".join(str(r[i]).ljust(widths[i]) for i in range(5)))
