from django_filters import FilterSet, DateTimeFromToRangeFilter
from django_filters.widgets import RangeWidget
from django.utils.translation import gettext_lazy as _

from measurement.models import Measurement


class MeasurementFilter(FilterSet):
    class Meta:
        model = Measurement
        fields = ['date']

    date = DateTimeFromToRangeFilter(
        label=_('Time range'),
        widget=RangeWidget(
            attrs={'type': 'date'},
        ),
    )
