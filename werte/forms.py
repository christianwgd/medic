# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.db.models import Min
from django.utils import timezone
from django.conf import settings

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