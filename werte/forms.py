# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from werte.models import Wert

lang = getattr(settings, "LANGUAGE_CODE", 'en')
date_format = getattr(settings, "MOMENT_DATE_FORMAT", 'MM/DD/YYYY')


class TimeForm(forms.Form):
    vonDate = forms.DateField(
        label='von',
        widget=DatePickerInput(options={
          "format": date_format,
          "locale": lang
        })
    )
    bisDate = forms.DateField(
        label='bis',
        widget=DatePickerInput(options={
          "format": date_format,
          "locale": lang
        })
    )


class MesswertForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(MesswertForm, self).__init__(*args, **kwargs)
        self.fields['gew'].localize = True
        self.fields['temp'].localize = True

    class Meta:
        model = Wert
        fields = ['rrsys', 'rrdia', 'puls', 'temp', 'gew', 'bemerkung']
        widgets = {
            'rrsys': forms.NumberInput(attrs={'min': 0, "autofocus": "autofocus"}),
            'rrdia': forms.NumberInput(attrs={'min': 0}),
            'puls': forms.NumberInput(attrs={'min': 0}),
            'temp': forms.NumberInput(attrs={'min': 0}),
            'gew': forms.NumberInput(attrs={'min': 0}),
        }

    def clean(self):
        cleaned_data = super(MesswertForm, self).clean()
        if (
            not cleaned_data['rrsys'] and not cleaned_data['rrdia'] and
            not cleaned_data['puls'] and not cleaned_data['temp'] and
            not cleaned_data['gew']
        ):
            raise ValidationError(_('No values entered.'), code='no_values')
        return cleaned_data
