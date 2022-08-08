from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.utils.translation import gettext as _

from medicament.models import Medicament, StockChange, REASON_CHOICES


class MedicamentForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput({"autofocus": "autofocus"})

    class Meta:
        model = Medicament
        fields = ['name', 'producer', 'ingredient', 'package', 'strength', 'unit']


class StockChangeForm(BSModalModelForm):
    class Meta(object):
        model = StockChange
        fields = ['date', 'reason', 'amount', 'text']

    date = forms.DateField(
        label=_('Date'),
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}
        )
    )
    amount = forms.DecimalField(help_text=" Tablet(s)")
    reason = forms.ChoiceField(choices=REASON_CHOICES)
    text = forms.CharField(max_length=50, required=False, label=_("Note"))
