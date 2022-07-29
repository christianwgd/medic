from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.utils.translation import gettext as _

from prescription.models import Prescription, WEEK_DAYS


class PrescriptionForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['morning'].widget = forms.NumberInput(attrs={'step':1.0, 'min': 0})
        self.fields['noon'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['evening'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['night'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})

        for key, name in WEEK_DAYS.items():
            self.fields[name] = forms.BooleanField(
                label=_(name.capitalize()),
                required=False
            )
            self.Meta.fields.append(name)
            self.fields[name].initial = self.instance.weekdays[key]

    class Meta:
        model = Prescription
        fields = [
            'medicament', 'morning', 'noon', 'evening', 'night',
            'valid_from', 'valid_until'
        ]
        widgets = {
            'valid_from': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'valid_until': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        if (
            not cleaned_data['morning'] and not cleaned_data['noon'] and
            not cleaned_data['evening'] and not cleaned_data['night']
        ):
            raise forms.ValidationError(_('No values entered.'))

        return cleaned_data
