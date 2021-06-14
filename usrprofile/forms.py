# -*- coding: utf-8 -*-
# from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.forms import EmailInput
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from usrprofile.models import UserProfile


lang = getattr(settings, "LANGUAGE_CODE", 'en')
date_format = getattr(settings, "MOMENT_DATE_FORMAT", 'MM/DD/YYYY')


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
            # 'gebdat': DatePickerInput(options={
            #     "format": date_format,
            #     "locale": lang
            # })
            'gebdat': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }


class MailForm(forms.Form):
    mailadr = forms.EmailField(label=_("Recipient"))
    subject = forms.CharField(max_length=80, label=_("Subject"))
    text = forms.CharField(
        max_length=500, required=False,
        label="Text", widget=forms.Textarea(attrs={'cols': 80, 'rows': 4})
    )
