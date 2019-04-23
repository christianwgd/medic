# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.db.models import Min
from django.utils import timezone

from werte.models import Wert


def get_min_date():
    try:
        min = minval['date__min'].strftime("%Y-%m-%d")
    except:
        min = timezone.now().strftime("%Y-%m-%d")
        import traceback
        traceback.print_exc()
    return min


def get_min_val():
    try:
        min = Wert.objects.all().aggregate(Min('date'))
    except:
        min = None
    return min

class TimeForm(forms.Form):
    minval = get_min_val()
    minDate = get_min_date()
    maxDate = timezone.now().strftime("%Y-%m-%d")
    vonDate = forms.DateField(
        label='von',
        widget=DatePickerInput(options={
          "format": "DD.MM.YYYY",
          "minDate": minDate,
          "locale": "de"
        })
    )
    bisDate = forms.DateField(
        label='bis',
        widget=DatePickerInput(options={
          "format": "DD.MM.YYYY",
          "maxDate": maxDate,
          "locale": "de"
        })
    )