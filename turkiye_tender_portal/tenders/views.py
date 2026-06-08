import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import subscription_required
from accounts.services.subscription_checker import get_profile

from . import constants
from .forms import TenderFilterForm
from .models import District, Province, Tender, TenderFetchLog, UserActivityLog
from .services import excel_exporter
from .services.province_filter import filter_tenders, normalize_province
from .services.tender_fetcher import fetch_and_store

logger = logging.getLogger("tenders")


def _log_activity(user, action, description=""):
    try:
        UserActivityLog.objects.create(user=user, action=action, description=description)
    except Exception:  # noqa: BLE001
        logger.exception("Activity log failed")


def _parse_filters(request):
    """Build kwargs for filter_tenders() + a label dict from GET params."""
    form = TenderFilterForm(request.GET or None)
    data = {}
    if form.is_valid():
        data = form.cleaned_data
    g = request.GET
    province = data.get("province") or g.get("province") or ""
    kwargs = dict(
        province=province,
        district=data.get("district") or g.get("district") or "",
        search=data.get("search") or g.get("search") or "",
        title=data.get("title") or "",
        authority_name=data.get("authority_name") or "",
        tender_type=data.get("tender_type") or g.get("tender_type") or "",
        status=data.get("status") or "",
        category=data.get("category") or g.get("category") or "",
        keyword=data.get("keyword") or "",
        date_from=data.get("date_from"),
        date_to=data.get("date_to"),
        today_only=bool(data.get("today_only")) or g.get("today_only") == "1",
        this_week_only=bool(data.get("this_week_only")) or g.get("this_week_only") == "1",
    )
    return form, kwargs


@subscription_required
def dashboard(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    profile = get_profile(request.user)

    selected_province = request.GET.get("province", "Elazığ")  # demo default
    selected_category = request.GET.get("category", "")

    base = Tender.objects.all()
    if normalize_province(selected_province):
        base_scope = base.filter(province__iexact=selected_province)
    else:
        base_scope = base
    if selected_category:
        base_scope = base_scope.filter(category=selected_category)

    last_log = TenderFetchLog.objects.order_by("-started_at").first()
    last_success_log = TenderFetchLog.objects.filter(status=TenderFetchLog.STATUS_SUCCESS).order_by("-started_at").first()

    # Calculate analytical data for charts
    # 1. Tender Type Distribution (procurement_type mapping)
    type_data = list(base_scope.values("procurement_type").annotate(count=Count("id")))
    type_map = dict(constants.TENDER_TYPE_CHOICES)
    chart_types_labels = []
    chart_types_counts = []
    for item in type_data:
        pt = item["procurement_type"]
        if pt:
            label = type_map.get(pt, pt)
            chart_types_labels.append(label)
            chart_types_counts.append(item["count"])

    # 2. Timeline (Tenders count by date for last 10 days)
    timeline_data = list(base_scope.filter(announcement_date__isnull=False)
                                   .values("announcement_date")
                                   .annotate(count=Count("id"))
                                   .order_by("-announcement_date")[:10])
    timeline_data.reverse()
    chart_dates = [d["announcement_date"].strftime("%d.%m.%Y") for d in timeline_data]
    chart_counts = [d["count"] for d in timeline_data]

    context = {
        "total_tenders": base.count(),
        "scoped_total": base_scope.count(),
        "new_today": base.filter(announcement_date=today).count(),
        "new_week": base.filter(
            announcement_date__gte=week_start, announcement_date__lte=today
        ).count(),
        "last_fetch": last_log,
        "last_success_fetch": last_success_log,
        "ekap_data_mode": settings.EKAP_DATA_MODE,
        "profile": profile,
        "selected_province": selected_province,
        "selected_category": selected_category,
        "category_choices": constants.CATEGORY_CHOICES,
        "provinces": Province.objects.filter(is_active=True),
        "latest_tenders": base_scope.order_by("-announcement_date", "-created_at")[:10],
        "quick_filters": [
            ("Tüm Türkiye", "?province=ALL"),
            ("Bugünkü İhaleler", "?today_only=1"),
            ("Bu Haftaki İhaleler", "?this_week_only=1"),
            ("Sonuç İlanları", "?category=ihale_sonuclari"),
            ("Yapım İhaleleri", "?category=yapim_ihaleleri"),
            ("Mal Alımı", "?category=mal_alimi"),
            ("Hizmet Alımı", "?category=hizmet_alimi"),
        ],
        "chart_types_labels": chart_types_labels,
        "chart_types_counts": chart_types_counts,
        "chart_dates": chart_dates,
        "chart_counts": chart_counts,
    }
    return render(request, "tenders/dashboard.html", context)


@subscription_required
def tender_list(request):
    form, kwargs = _parse_filters(request)
    
    sort_by = request.GET.get("sort")
    direction = request.GET.get("direction", "desc")
    
    sort_fields = {
        "ikn": "tender_no",
        "title": "title",
        "date": "announcement_date",
        "province": "province",
    }
    
    qs_base = filter_tenders(**kwargs)
    if sort_by in sort_fields:
        order_field = sort_fields[sort_by]
        if direction == "desc":
            order_field = f"-{order_field}"
        qs = qs_base.order_by(order_field, "-created_at")
    else:
        qs = qs_base.order_by("-announcement_date", "-created_at")

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))

    # Preserve querystring for pagination links (minus page, sort, direction)
    params = request.GET.copy()
    params.pop("page", None)
    params.pop("sort", None)
    params.pop("direction", None)

    context = {
        "form": form,
        "page_obj": page,
        "total_count": qs.count(),
        "querystring": params.urlencode(),
        "applied_province": kwargs["province"] or "Tüm Türkiye",
    }
    return render(request, "tenders/tender_list.html", context)


@subscription_required
def tender_detail(request, pk):
    tender = get_object_or_404(Tender, pk=pk)
    if request.GET.get("modal") == "1":
        return render(request, "tenders/tender_detail_modal.html", {"tender": tender})
    return render(request, "tenders/tender_detail.html", {"tender": tender})


@subscription_required
def export_excel(request):
    pk = request.GET.get("pk")
    pks = request.GET.get("pks")
    if pk:
        tender = get_object_or_404(Tender, pk=pk)
        qs = [tender]
        filters = {
            "province": tender.province or "Tüm Türkiye",
            "district": tender.district,
            "category_label": dict(constants.CATEGORY_CHOICES).get(tender.category, ""),
            "date_from": "",
            "date_to": "",
        }
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_no = "".join(ch for ch in tender.tender_no if ch.isalnum() or ch in "_-") or "tek"
        filename = f"ihale_raporu_{safe_no}_{stamp}.xlsx"
        path = excel_exporter.export_to_file(qs, filters=filters, user=request.user, filename=filename)
        _log_activity(request.user, "excel_export_single", f"ihale={tender.tender_no}")
    elif pks:
        id_list = [int(x) for x in pks.split(",") if x.isdigit()]
        qs = list(Tender.objects.filter(pk__in=id_list))
        filters = {
            "province": "Seçilen İhaleler",
            "district": "",
            "category_label": "",
            "date_from": "",
            "date_to": "",
        }
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ihale_raporu_secilenler_{stamp}.xlsx"
        path = excel_exporter.export_to_file(qs, filters=filters, user=request.user, filename=filename)
        _log_activity(request.user, "excel_export_bulk", f"adet={len(id_list)}")
    else:
        _, kwargs = _parse_filters(request)
        qs = filter_tenders(**kwargs).order_by("-announcement_date", "-created_at")

        cat_map = dict(constants.CATEGORY_CHOICES)
        filters = {
            "province": normalize_province(kwargs["province"]) or "Tüm Türkiye",
            "district": kwargs["district"],
            "category_label": cat_map.get(kwargs["category"], ""),
            "date_from": kwargs["date_from"].strftime("%d.%m.%Y") if kwargs["date_from"] else "",
            "date_to": kwargs["date_to"].strftime("%d.%m.%Y") if kwargs["date_to"] else "",
        }

        # Save a copy to exports/excel/ and also stream to the user.
        path = excel_exporter.export_to_file(qs, filters=filters, user=request.user)
        _log_activity(
            request.user, "excel_export",
            f"{qs.count()} kayıt, il={filters['province']}",
        )

    data = path.read_bytes()
    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{path.name}"'
    return response


@subscription_required
@require_POST
def fetch_now(request):
    """Manual 'Yeni İlanları Çek' action with basic rate control."""
    cooldown = int(getattr(settings, "FETCH_MANUAL_COOLDOWN", 60))
    last_key = "last_manual_fetch"
    last_ts = request.session.get(last_key)
    now_ts = timezone.now().timestamp()
    if last_ts and (now_ts - last_ts) < cooldown:
        wait = int(cooldown - (now_ts - last_ts))
        messages.warning(
            request, f"Çok sık çekim yapılamaz. Lütfen {wait} saniye sonra tekrar deneyin."
        )
        return redirect(request.POST.get("next") or "dashboard")

    province = request.POST.get("province", "")
    category = request.POST.get("category", "")
    all_tr = normalize_province(province) is None

    log = fetch_and_store(
        province=province,
        category=category or None,
        all_turkiye=all_tr,
    )
    request.session[last_key] = now_ts

    if log.status == TenderFetchLog.STATUS_SUCCESS:
        messages.success(
            request,
            f"Çekim tamamlandı: {log.new_records} yeni, "
            f"{log.duplicate_records} tekrar eden kayıt.",
        )
    else:
        messages.error(request, f"Çekim başarısız: {log.error_message[:200]}")

    _log_activity(request.user, "manual_fetch", f"il={province or 'Tüm Türkiye'}")
    next_url = request.POST.get("next")
    return redirect(next_url or "dashboard")


@subscription_required
def districts_api(request):
    """Return districts for a province (depends-on dropdown)."""
    from django.http import JsonResponse

    province_name = request.GET.get("province", "")
    items = []
    try:
        province = Province.objects.get(name__iexact=province_name)
        items = list(
            District.objects.filter(province=province, is_active=True)
            .values_list("name", flat=True)
        )
    except Province.DoesNotExist:
        pass
    return JsonResponse({"districts": items})
