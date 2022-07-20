from django.urls import path
from django.urls.converters import StringConverter, register_converter

from . import views


class NullStringConverter(StringConverter):
    """ String converter, that allows empty string """

    regex = "[-a-zA-Z0-9_]*"


register_converter(NullStringConverter, "null-str")


app_name = 'werte'
urlpatterns = [
    path('werte/', views.MeasurementListView.as_view(), name='werte'),
    path('new/', views.MeasurementCreateView.as_view(), name='neu'),
    path('edit/<int:pk>/', views.MeasurementUpdateView.as_view(), name='edit'),
    path('minmax/<null-str:von>/<null-str:bis>/', views.MeasurementMinMaxView.as_view(), name='minmax'),
    path('diagram/<null-str:von>/<null-str:bis>/', views.MeasurementDiagramView.as_view(), name='diagram'),
]
