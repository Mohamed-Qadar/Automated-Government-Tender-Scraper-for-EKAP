from django.conf import settings
from django.db import models
from django.utils import timezone

from . import constants


class Province(models.Model):
    name = models.CharField("İl Adı", max_length=80, unique=True)
    plate_code = models.PositiveSmallIntegerField("Plaka Kodu", unique=True)
    is_active = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "İl"
        verbose_name_plural = "İller"
        ordering = ["plate_code"]

    def __str__(self):
        return f"{self.plate_code:02d} - {self.name}"


class District(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name="İl",
    )
    name = models.CharField("İlçe Adı", max_length=80)
    is_active = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "İlçe"
        verbose_name_plural = "İlçeler"
        ordering = ["province__plate_code", "name"]
        unique_together = ("province", "name")

    def __str__(self):
        return f"{self.name} / {self.province.name}"


class Keyword(models.Model):
    name = models.CharField("Anahtar Kelime", max_length=120, unique=True)
    category = models.CharField(
        "Kategori", max_length=40, choices=constants.CATEGORY_CHOICES,
        blank=True,
    )
    is_active = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "Anahtar Kelime"
        verbose_name_plural = "Anahtar Kelimeler"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tender(models.Model):
    tender_no = models.CharField("İhale Kayıt No", max_length=60, db_index=True)
    title = models.CharField("İhale Başlığı", max_length=500)
    authority_name = models.CharField("İdare Adı", max_length=300, blank=True)
    # Store province/district as clean string fields (as required by spec),
    # with optional FKs kept loose for Türkiye-wide flexibility.
    province = models.CharField("İl", max_length=80, blank=True, db_index=True)
    district = models.CharField("İlçe", max_length=80, blank=True, db_index=True)
    
    # New procurement_type field representing Mal/Hizmet/Yapım/Danışmanlık
    procurement_type = models.CharField(
        "Alım Türü", max_length=20, choices=constants.TENDER_TYPE_CHOICES, blank=True, db_index=True
    )
    tender_type = models.CharField(
        "İhale Türü", max_length=100, blank=True
    )
    category = models.CharField(
        "Kategori", max_length=40, choices=constants.CATEGORY_CHOICES, blank=True,
        db_index=True,
    )
    tender_procedure = models.CharField(
        "İhale Usulü", max_length=100, blank=True
    )
    announcement_date = models.DateField("İlan Tarihi", null=True, blank=True, db_index=True)
    tender_date = models.DateField("İhale Tarihi", null=True, blank=True, db_index=True)
    deadline_date = models.DateField("Son Teklif Tarihi", null=True, blank=True, db_index=True)
    work_location = models.CharField("İşin Yapılacağı Yer", max_length=500, blank=True)
    short_description = models.TextField("Kısa Açıklama", blank=True)
    official_url = models.URLField("Resmî / EKAP Link", max_length=500, blank=True)
    source = models.CharField(
        "Kaynak", max_length=20, choices=constants.SOURCE_CHOICES,
        default=constants.SOURCE_MOCK,
    )
    status = models.CharField(
        "Durum", max_length=40, choices=constants.STATUS_CHOICES,
        default=constants.STATUS_ACTIVE, db_index=True
    )
    keyword_matches = models.CharField(
        "Anahtar Kelime Eşleşmesi", max_length=300, blank=True
    )
    raw_data = models.JSONField("Ham Veri", default=dict, blank=True)
    
    # New tracking fields
    first_seen_at = models.DateTimeField("İlk Görülme", default=timezone.now, db_index=True)
    last_seen_at = models.DateTimeField("Son Görülme", default=timezone.now, db_index=True)
    
    created_at = models.DateTimeField("Sisteme Eklenme", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "İhale"
        verbose_name_plural = "İhaleler"
        ordering = ["-announcement_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tender_no", "source"], name="uniq_tender_no_source"
            )
        ]
        indexes = [
            models.Index(fields=["tender_no"]),
            models.Index(fields=["province"]),
            models.Index(fields=["district"]),
            models.Index(fields=["procurement_type"]),
            models.Index(fields=["announcement_date"]),
            models.Index(fields=["tender_date"]),
            models.Index(fields=["deadline_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.tender_no} - {self.title[:60]}"

    @property
    def is_today(self):
        return self.announcement_date == timezone.localdate()



class TenderFetchLog(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_PARTIAL = "partial"
    STATUS_FAILED = "failed"
    STATUS_RUNNING = "running"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Başarılı"),
        (STATUS_PARTIAL, "Kısmen Başarılı"),
        (STATUS_FAILED, "Başarısız"),
        (STATUS_RUNNING, "Çalışıyor"),
    ]

    started_at = models.DateTimeField("Başlangıç", default=timezone.now)
    finished_at = models.DateTimeField("Bitiş", null=True, blank=True)
    status = models.CharField(
        "Durum", max_length=20, choices=STATUS_CHOICES, default=STATUS_RUNNING
    )
    source = models.CharField("Kaynak", max_length=20, blank=True)
    province = models.CharField("İl", max_length=80, blank=True)
    district = models.CharField("İlçe", max_length=80, blank=True)
    total_found = models.PositiveIntegerField("Bulunan Kayıt", default=0)
    new_records = models.PositiveIntegerField("Yeni Kayıt", default=0)
    duplicate_records = models.PositiveIntegerField("Tekrar Eden", default=0)
    error_message = models.TextField("Hata Mesajı", blank=True)

    class Meta:
        verbose_name = "İhale Çekme Logu"
        verbose_name_plural = "İhale Çekme Logları"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.started_at:%Y-%m-%d %H:%M} - {self.province or 'Tüm Türkiye'} ({self.get_status_display()})"


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        verbose_name="Kullanıcı",
    )
    action = models.CharField("İşlem", max_length=80)
    description = models.TextField("Açıklama", blank=True)
    created_at = models.DateTimeField("Tarih", auto_now_add=True)

    class Meta:
        verbose_name = "Kullanıcı Aktivite Logu"
        verbose_name_plural = "Kullanıcı Aktivite Logları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
