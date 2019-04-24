# -*- coding: utf-8 -*-
from builtins import object
from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.forms import EmailInput
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from usrprofile.models import UserProfile


class UsrProfForm(ModelForm):
    email = forms.EmailField(
        label=_('email adress'), required=False,
        widget=EmailInput(attrs={"autofocus": "autofocus"})
    )

    class Meta(object):
        model = UserProfile
        fields = ['warnenTageVorher', 'werteLetzteTage', 'zeigeArztWerte',
                  'zeigeArztMed', 'email_arzt', 'myStartPage', 'gebdat']
        widgets = {
            'warnenTageVorher': forms.NumberInput(attrs={'step': 1.0, 'min': 0}),
            'werteLetzteTage': forms.NumberInput(attrs={'step': 10.0, 'min': 0}),
            'gebdat': DatePickerInput(options={
                "format": "DD.MM.YYYY",
                "locale": "de"
            })
        }


class MailForm(forms.Form):
    mailadr = forms.EmailField(label=_("to"))
    subject = forms.CharField(max_length=80, label=_("Subject"))
    text = forms.CharField(
        max_length=500, required=False,
        label="Text", widget=forms.Textarea(attrs={'cols': 80, 'rows': 4})
    )
