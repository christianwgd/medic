# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus.widgets import DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from werte.models import Wert


class MesswertForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        cleaned_data = super().clean()
        if (
            not cleaned_data['rrsys'] and not cleaned_data['rrdia'] and
            not cleaned_data['puls'] and not cleaned_data['temp'] and
            not cleaned_data['gew']
        ):
            raise ValidationError(_('No values entered.'), code='no_values')
        return cleaned_data
