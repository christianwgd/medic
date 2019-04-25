# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.db.models import Min
from django.utils import timezone

from werte.models import Wert


class TimeForm(forms.Form):
    vonDate = forms.DateField(
        label='von',
        widget=DatePickerInput(options={
          "format": "DD.MM.YYYY",
          "locale": "de"
        })
    )
    bisDate = forms.DateField(
        label='bis',
        widget=DatePickerInput(options={
          "format": "DD.MM.YYYY",
          "locale": "de"
        })
    )