from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class SubscriptionPackage(models.Model):
    """Sellable subscription package. Pricing is informational in the MVP;
    activation is performed manually by an admin."""

    name = models.CharField("Paket Adı", max_length=120, unique=True)
    description = models.TextField("Açıklama", blank=True)
    monthly_price = models.DecimalField(
        "Aylık Ücret (TL)", max_digits=10, decimal_places=2, default=0
    )
    yearly_price = models.DecimalField(
        "Yıllık Ücret (TL)", max_digits=10, decimal_places=2, default=0
    )
    is_active = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "Abonelik Paketi"
        verbose_name_plural = "Abonelik Paketleri"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_SUSPENDED = "suspended"
    STATUS_TRIAL = "trial"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Aktif"),
        (STATUS_EXPIRED, "Süresi Dolmuş"),
        (STATUS_SUSPENDED, "Askıya Alınmış"),
        (STATUS_TRIAL, "Deneme"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Kullanıcı",
    )
    company_name = models.CharField("Firma Adı", max_length=200, blank=True)
    phone = models.CharField("Telefon", max_length=30, blank=True)
    city = models.CharField("Şehir", max_length=80, blank=True)
    subscription_status = models.CharField(
        "Abonelik Durumu", max_length=20, choices=STATUS_CHOICES, default=STATUS_TRIAL
    )
    subscription_start_date = models.DateField(
        "Abonelik Başlangıç", null=True, blank=True
    )
    subscription_end_date = models.DateField("Abonelik Bitiş", null=True, blank=True)
    package_name = models.CharField("Paket", max_length=120, blank=True)
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ({self.get_subscription_status_display()})"

    @property
    def is_subscription_active(self):
        """True when the user may use paid features right now."""
        if self.user.is_superuser:
            return True
        if self.subscription_status == self.STATUS_SUSPENDED:
            return False
        if self.subscription_status in (self.STATUS_ACTIVE, self.STATUS_TRIAL):
            if self.subscription_end_date is None:
                return True
            return self.subscription_end_date >= timezone.localdate()
        return False

    @property
    def days_remaining(self):
        if self.subscription_end_date is None:
            return None
        return (self.subscription_end_date - timezone.localdate()).days

    def mark_expired_if_due(self):
        """Flip status to expired when the end date has passed."""
        if (
            self.subscription_end_date
            and self.subscription_end_date < timezone.localdate()
            and self.subscription_status in (self.STATUS_ACTIVE, self.STATUS_TRIAL)
        ):
            self.subscription_status = self.STATUS_EXPIRED
            self.save(update_fields=["subscription_status", "updated_at"])
