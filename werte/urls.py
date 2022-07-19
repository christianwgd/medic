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
    path('minmax/<null-str:von>/<null-str:bis>/', views.MeasurementMinMaxView.as_view(), name='minmax'),
    path('mail/<str:von>/<str:bis>/', views.emailwerte, name='email'),
    path('new/', views.MeasurementCreateView.as_view(), name='neu'),
    path('edit/<int:pk>/', views.MeasurementUpdateView.as_view(), name='edit'),
    path('diagram/<str:von>/<str:bis>/', views.diagram, name='diagram'),
]
