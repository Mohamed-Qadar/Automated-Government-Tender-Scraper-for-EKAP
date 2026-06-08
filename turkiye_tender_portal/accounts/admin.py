from django.contrib import admin
from django.utils import timezone

from .models import SubscriptionPackage, UserProfile
from .services.subscription_checker import activate_subscription, suspend_subscription


@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_price", "yearly_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.action(description="Aboneliği 30 gün uzat / aktifleştir")
def extend_30_days(modeladmin, request, queryset):
    for profile in queryset:
        activate_subscription(profile, days=30)
    modeladmin.message_user(request, f"{queryset.count()} abonelik 30 gün uzatıldı.")


@admin.action(description="Aboneliği 365 gün uzat / aktifleştir")
def extend_365_days(modeladmin, request, queryset):
    for profile in queryset:
        activate_subscription(profile, days=365)
    modeladmin.message_user(request, f"{queryset.count()} abonelik 365 gün uzatıldı.")


@admin.action(description="Aboneliği askıya al")
def suspend(modeladmin, request, queryset):
    for profile in queryset:
        suspend_subscription(profile)
    modeladmin.message_user(request, f"{queryset.count()} abonelik askıya alındı.")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "company_name",
        "subscription_status",
        "subscription_start_date",
        "subscription_end_date",
        "days_remaining_display",
        "package_name",
    )
    list_filter = ("subscription_status", "package_name")
    search_fields = ("user__username", "user__email", "company_name", "phone", "city")
    readonly_fields = ("created_at", "updated_at")
    actions = [extend_30_days, extend_365_days, suspend]
    autocomplete_fields = ("user",)
    fieldsets = (
        ("Kullanıcı", {"fields": ("user", "company_name", "phone", "city")}),
        (
            "Abonelik",
            {
                "fields": (
                    "subscription_status",
                    "package_name",
                    "subscription_start_date",
                    "subscription_end_date",
                )
            },
        ),
        ("Zaman Damgaları", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Kalan Gün")
    def days_remaining_display(self, obj):
        d = obj.days_remaining
        return "Süresiz" if d is None else f"{d} gün"
