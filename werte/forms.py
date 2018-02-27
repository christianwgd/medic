# -*- coding: utf-8 -*-
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.db.models import Min
from django.utils import timezone

from werte.models import Wert


class TimeForm(forms.Form):
    minval = Wert.objects.all().aggregate(Min('date'))
    minDate = minval['date__min'].strftime("%Y-%m-%d")
    maxDate = timezone.now().strftime("%Y-%m-%d")
    vonDate = forms.DateField(label='von',
                              widget=DateTimePicker(options={
                                  "format": "DD.MM.YYYY",
                                  "minDate": minDate,
                                  "locale": "de"
                              }))
    bisDate = forms.DateField(label='bis',
                              widget=DateTimePicker(options={
                                  "format": "DD.MM.YYYY",
                                  "maxDate": maxDate,
                                  "locale": "de"
                              }))