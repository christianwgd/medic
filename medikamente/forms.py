from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import Verordnung, Medikament


lang = getattr(settings, "LANGUAGE_CODE", 'en')
date_format = getattr(settings, "MOMENT_DATE_FORMAT", 'MM/DD/YYYY')


class VrdForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(VrdForm, self).__init__(*args, **kwargs)
        self.fields['morgen'].widget = forms.NumberInput(attrs={'step':1.0, 'min': 0})
        self.fields['mittag'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['abend'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['nacht'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})

    class Meta:
        model = Verordnung
        fields = [
            'ref_medikament', 'morgen', 'mittag', 'abend', 'nacht', 
            'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'
        ]

    def clean(self):
        cleaned_data = super(VrdForm, self).clean()
        if (
            not cleaned_data['morgen'] and not cleaned_data['mittag'] and
            not cleaned_data['abend'] and not cleaned_data['nacht']
        ):
            raise ValidationError(_('No values entered.'), code='no_values')
        return cleaned_data


class MedForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(MedForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput({"autofocus": "autofocus"})

    class Meta:
        model = Medikament
        fields = ['name', 'hersteller', 'wirkstoff', 'packung', 'staerke', 'einheit']


# class vrdFutForm(forms.ModelForm):
#     # class vrdForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(vrdFutForm, self).__init__(*args, **kwargs)
#         self.fields['morgen'].widget = forms.TextInput()
#         self.fields['mittag'].widget = forms.TextInput()
#         self.fields['abend'].widget = forms.TextInput()
#         self.fields['nacht'].widget = forms.TextInput()
#
#     class Meta(object):
#         model = VrdFuture
#         fields = [
#             'ref_medikament', 'morgen', 'mittag', 'abend', 'nacht',
#             'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so',
#             'gueltig_ab'
#         ]
#
# class bestEditForm(forms.ModelForm):
#     class Meta(object):
#         model = Bestandsveraenderung
#         fields = ['date', 'grund', 'menge', 'text', ]
#
#     date = forms.DateField(
#         label=_('Date'),
#         widget=DatePickerInput(options={
#             "format": date_format,
#             "locale": lang
#         })
#     )
#     menge = forms.DecimalField(help_text=" Tablet(s)")
#     grund = forms.ChoiceField(choices=GRUND_CHOICES)
#     text = forms.CharField(max_length=50, required=False, label=_("Note"))
