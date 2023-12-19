from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms

from medicament.models import Medicament
from order.models import Order


class OrderForm(BSModalModelForm):

    class Meta:
        model = Order
        fields = ['medicaments']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['medicaments'].widget = forms.CheckboxSelectMultiple()
        self.fields['medicaments'].queryset = Medicament.objects.filter(
            id__in=user.prescriptions.values_list('medicament__id', flat=True),
        )
