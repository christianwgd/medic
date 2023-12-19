
from django import forms
from django.forms import TextInput
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from usrprofile.models import UserProfile


lang = getattr(settings, "LANGUAGE_CODE", 'en')
date_format = getattr(settings, "MOMENT_DATE_FORMAT", 'MM/DD/YYYY')


class UsrProfForm(ModelForm):
    first_name = forms.CharField(
        label=_('first name'), required=False,
        widget=TextInput(attrs={"autofocus": "autofocus"}),
    )
    last_name = forms.CharField(
        label=_('last name'), required=False,
    )
    email = forms.EmailField(
        label=_('email adress'), required=False,
    )

    class Meta:
        model = UserProfile
        fields = [
            'warn_days_before', 'medicaments_items_per_page',
            'show_measurement_days', 'measurements_items_per_page',
            'doc_can_see_msm', 'doc_can_see_med', 'email_arzt',
            'my_start_page', 'gebdat',
        ]
        widgets = {
            'warn_days_before': forms.NumberInput(attrs={'step': 1.0, 'min': 0}),
            'show_measurement_days': forms.NumberInput(attrs={'step': 10.0, 'min': 0}),
            'gebdat': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
            ),
        }
