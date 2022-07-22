from django_filters import FilterSet, AllValuesFilter, CharFilter

from medikamente.models import Medicament


class MedikamentFilter(FilterSet):
    class Meta:
        model = Medicament
        fields = ['name', ]

    name = CharFilter(lookup_expr='icontains')
