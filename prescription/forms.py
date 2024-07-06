from bitfield.forms import BitFieldCheckboxSelectMultiple
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.utils.translation import gettext as _

from prescription.models import Prescription


class WeekdaysBitFieldCheckboxSelectMultiple(BitFieldCheckboxSelectMultiple):
    template_name = "prescription/widgets/multi_input.html"
    option_template_name = "prescription/widgets/checkbox_option.html"


class PrescriptionForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['morning'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['noon'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['evening'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['night'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})

    class Meta:
        model = Prescription
        fields = [
            'medicament', 'morning', 'noon', 'evening', 'night',
            'weekdays', 'valid_from', 'valid_until',
        ]
        widgets = {
            'weekdays': WeekdaysBitFieldCheckboxSelectMultiple,
            'valid_from': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
            ),
            'valid_until': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
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
