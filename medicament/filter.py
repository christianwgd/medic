from django_filters import FilterSet, AllValuesFilter, CharFilter

from medicament.models import Medicament, StockChange


class MedicamentFilter(FilterSet):
    class Meta:
        model = Medicament
        fields = ['name', ]

    name = CharFilter(lookup_expr='icontains')


class StockChangeFilter(FilterSet):

    class Meta:
        model = StockChange
        fields = ['reason']
