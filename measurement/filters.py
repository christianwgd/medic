from django.utils.translation import gettext_lazy as _
from django_filters import DateTimeFromToRangeFilter, FilterSet
from django_filters.widgets import RangeWidget

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
