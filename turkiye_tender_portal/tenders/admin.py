from django.contrib import admin

from .models import (
    District,
    Keyword,
    Province,
    Tender,
    TenderFetchLog,
    UserActivityLog,
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("plate_code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "plate_code")
    ordering = ("plate_code",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "province", "is_active")
    list_filter = ("is_active", "province")
    search_fields = ("name", "province__name")
    autocomplete_fields = ("province",)


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name",)


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "tender_no",
        "title_short",
        "province",
        "district",
        "tender_type",
        "category",
        "status",
        "announcement_date",
        "source",
    )
    list_filter = (
        "tender_type",
        "category",
        "status",
        "source",
        "province",
        "announcement_date",
    )
    search_fields = (
        "tender_no",
        "title",
        "authority_name",
        "work_location",
        "keyword_matches",
    )
    date_hierarchy = "announcement_date"
    readonly_fields = ("created_at", "updated_at", "raw_data")
    ordering = ("-announcement_date",)

    @admin.display(description="İhale Başlığı")
    def title_short(self, obj):
        return obj.title[:70]


@admin.register(TenderFetchLog)
class TenderFetchLogAdmin(admin.ModelAdmin):
    list_display = (
        "started_at",
        "finished_at",
        "status",
        "source",
        "province",
        "total_found",
        "new_records",
        "duplicate_records",
    )
    list_filter = ("status", "source", "province")
    readonly_fields = [f.name for f in TenderFetchLog._meta.fields]
    ordering = ("-started_at",)

    def has_add_permission(self, request):
        return False


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "action", "description")
    readonly_fields = ("user", "action", "description", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False
