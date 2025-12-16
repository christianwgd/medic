
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.utils.translation import gettext as _

from measurement.models import Measurement


class MeasurementForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for idx, value_type in enumerate(self.user.profile.active_value_types.all()):
            self.fields[value_type.slug] = forms.DecimalField(
                label=value_type.name,
                max_digits=5,
                decimal_places=2,
                required=False,
            )
            self.fields[value_type.slug].localize = True
            self.fields[value_type.slug].widget = forms.NumberInput(
                attrs={'min': 0},
            )
            if idx == 0:
                self.fields[value_type.slug].widget.attrs.update({'autofocus': 'autofocus'})

    def clean(self):
        cleaned_data = super().clean()
        no_value = True
        for value_type in self.user.profile.active_value_types.all():
            if cleaned_data[value_type.slug]:
                no_value = False
        if no_value:
            raise forms.ValidationError(_('No values entered.'))
        return cleaned_data

    class Meta:
        model = Measurement
        fields = ['comment']
