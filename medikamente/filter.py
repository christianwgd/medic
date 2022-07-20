from django_filters import FilterSet, AllValuesFilter, CharFilter

from medikamente.models import Medikament


class MedikamentFilter(FilterSet):
    class Meta:
        model = Medikament
        fields = ['name', ]

    name = CharFilter(lookup_expr='icontains')
