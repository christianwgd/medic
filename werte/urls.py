from django.urls import path

from . import  views

app_name = 'werte'
urlpatterns = [
    path('werte/', views.MeasurementListView.as_view(), name='werte'),
    path('minmax/<str:von>/<str:bis>/', views.minmax, name='minmax'),
    path('mail/<str:von>/<str:bis>/', views.emailwerte, name='email'),
    path('new/', views.MeasurementCreateView.as_view(), name='neu'),
    path('edit/<int:pk>/', views.MeasurementUpdateView.as_view(), name='edit'),
    path('diagram/<str:von>/<str:bis>/', views.diagram, name='diagram'),
    path('delwert/<int:delwert_id>)/', views.delwert, name='delwert'),
]
