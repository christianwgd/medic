from django.conf.urls import url

from . import  views

app_name = 'werte'
urlpatterns = [
    url(r'^werte/$', views.werte, name='werte'),
    url(r'^minmax/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.minmax, name='minmax'),
    url(r'^mail/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.emailwerte, name='email'),
    url(r'^new/$', views.new, name='neu'),
    url(r'^edit/(?P<wert_id>\d+)/$', views.edit, name='edit'),
    url(r'^diagram/(?P<von>[0-9.]{10})/(?P<bis>[0-9.]{10})/$', views.diagram, name='diagram'),
    url(r'^delwert/(?P<delwert_id>\d+)/$', views.delwert, name='delwert'),
]