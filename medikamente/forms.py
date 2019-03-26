from __future__ import absolute_import
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms


from .models import Verordnung, VrdFuture, Medikament, Bestandsveraenderung, GRUND_CHOICES


class vrdForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(vrdForm, self).__init__(*args, **kwargs)
        self.fields['morgen'].widget = forms.NumberInput(attrs={'step':1.0, 'min': 0})
        self.fields['mittag'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['abend'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})
        self.fields['nacht'].widget = forms.NumberInput(attrs={'step': 1.0, 'min': 0})

    class Meta:
        model = Verordnung
        fields = ['ref_medikament', 'morgen', 'mittag', 'abend', 'nacht', 'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']


class vrdFutForm(forms.ModelForm):
    # class vrdForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(vrdFutForm, self).__init__(*args, **kwargs)
        self.fields['morgen'].widget = forms.TextInput()
        self.fields['mittag'].widget = forms.TextInput()
        self.fields['abend'].widget = forms.TextInput()
        self.fields['nacht'].widget = forms.TextInput()

    class Meta:
        model = VrdFuture
        fields = ['ref_medikament', 'morgen', 'mittag', 'abend', 'nacht', 'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so',
                  'gueltig_ab']


class medForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(medForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput({"autofocus": "autofocus"})

    class Meta:
        model = Medikament
        fields = ['name', 'hersteller', 'wirkstoff', 'packung', 'staerke', 'einheit']


class bestEditForm(forms.ModelForm):
    class Meta:
        model = Bestandsveraenderung
        fields = ['date', 'grund', 'menge', 'text', ]

    date = forms.DateField(label='Datum',
                           widget=DateTimePicker(options={
                               "format": "DD.MM.YYYY",
                                "locale": "de"
                           }))
    menge = forms.DecimalField(help_text=" Tablette(n)")
    grund = forms.ChoiceField(choices=GRUND_CHOICES)
    text = forms.CharField(max_length=50, required=False, label="Anmerkung")
