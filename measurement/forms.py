
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.utils.translation import gettext as _

from measurement.models import ValueType, Measurement


class MeasurementForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.fields = []
        for idx, value_type in enumerate(ValueType.objects.active()):
            self.fields[value_type.slug] = forms.DecimalField(
                label=value_type.name,
                max_digits=5,
                decimal_places=2,
                required=False,
            )
            self.fields[value_type.slug].localize = True
            if idx == 0:
                self.fields[value_type.slug].widget = forms.NumberInput(
                    attrs={'min': 0, "autofocus": "autofocus"},
                )
            else:
                self.fields[value_type.slug].widget = forms.NumberInput(
                    attrs={'min': 0},
                )
            self.Meta.fields.append(value_type.slug)
        self.Meta.fields.append('comment')

    def clean(self):
        cleaned_data = super().clean()
        no_value = True
        # pylint: disable=unused-variable
        for _idx, value_type in enumerate(ValueType.objects.active()):
            if cleaned_data[value_type.slug]:
                no_value = False
        if no_value:
            raise forms.ValidationError(_('No values entered.'))
        return cleaned_data

    class Meta:
        model = Measurement
        fields = ['comment']
