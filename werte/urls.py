from django.urls import path, re_path

from . import  views

app_name = 'werte'
urlpatterns = [
    path('werte/', views.werte, name='werte'),
    re_path(r'^minmax/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.minmax, name='minmax'),
    re_path(r'^mail/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.emailwerte, name='email'),
    path('new/', views.new, name='neu'),
    re_path(r'^edit/(?P<wert_id>\d+)/$', views.edit, name='edit'),
    re_path(r'^diagram/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.diagram, name='diagram'),
    re_path(r'^delwert/(?P<delwert_id>\d+)/$', views.delwert, name='delwert'),
]