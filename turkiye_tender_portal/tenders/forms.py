from django import forms

from . import constants
from .models import Province


class TenderFilterForm(forms.Form):
    """All list-page filters. Province is highlighted in the UI."""

    province = forms.ChoiceField(label="İl", required=False)
    district = forms.CharField(label="İlçe", required=False)
    search = forms.CharField(label="Arama", required=False)
    title = forms.CharField(label="İhale Başlığı", required=False)
    authority_name = forms.CharField(label="İdare Adı", required=False)
    tender_type = forms.ChoiceField(
        label="İhale Türü", required=False,
        choices=[("", "Tümü")] + constants.TENDER_TYPE_CHOICES,
    )
    status = forms.ChoiceField(
        label="Durum", required=False,
        choices=[("", "Tümü")] + constants.STATUS_CHOICES,
    )
    category = forms.ChoiceField(
        label="Kategori", required=False,
        choices=[("", "Tümü")] + constants.CATEGORY_CHOICES,
    )
    keyword = forms.CharField(label="Anahtar Kelime", required=False)
    date_from = forms.DateField(
        label="Başlangıç Tarihi", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Bitiş Tarihi", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    today_only = forms.BooleanField(label="Bugünkü İhaleler", required=False)
    this_week_only = forms.BooleanField(label="Bu Haftaki İhaleler", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        provinces = list(
            Province.objects.filter(is_active=True).values_list("name", flat=True)
        )
        choices = [(constants.ALL_TURKIYE, "Tüm Türkiye")] + [
            (p, p) for p in provinces
        ]
        self.fields["province"].choices = choices
        # Bootstrap styling
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
