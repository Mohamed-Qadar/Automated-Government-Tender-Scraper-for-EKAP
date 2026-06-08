from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tenders/", views.tender_list, name="tender_list"),
    path("tenders/<int:pk>/", views.tender_detail, name="tender_detail"),
    path("export/excel/", views.export_excel, name="export_excel"),
    path("fetch/", views.fetch_now, name="fetch_now"),
    path("api/districts/", views.districts_api, name="districts_api"),
]
