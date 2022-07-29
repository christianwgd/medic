from django.urls import path

from measurement import views


app_name = 'measurement'

urlpatterns = [
    path('list/', views.MeasurementListView.as_view(), name='list'),
    path('new/', views.MeasurementCreateView.as_view(), name='neu'),
    path('edit/<int:pk>/', views.MeasurementUpdateView.as_view(), name='edit'),
    path('minmax/<str:von>/<str:bis>/', views.MeasurementMinMaxView.as_view(), name='minmax'),
    path('chart/<str:von>/<str:bis>/', views.MeasurementDiagramView.as_view(), name='diagram'),
    path('chart-json/<str:type>/<str:von>/<str:bis>/', views.ValuesJSONView.as_view(), name='json-values'),
]
