from django.urls import path

from . import  views

app_name = 'werte'
urlpatterns = [
    path('werte/', views.werte, name='werte'),
    path('minmax/<str:von>/<str:bis>/', views.minmax, name='minmax'),
    path('mail/<str:von>/<str:bis>/', views.emailwerte, name='email'),
    path('new/', views.new, name='neu'),
    path('edit/<int:wert_id>/', views.edit, name='edit'),
    path('diagram/<str:von>/<str:bis>/', views.diagram, name='diagram'),
    path('delwert/<int:delwert_id>)/', views.delwert, name='delwert'),
]