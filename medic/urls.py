# encoding: utf-8
from __future__ import absolute_import
from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import index, log_off, startpage

admin.autodiscover()

urlpatterns = [
    # Startseite
    url(r'^index/$', index, name='index'),  # Inhaltsverzeichnis anzeigen

    # dynamische Startseite
    url(r'^startpage/$', startpage, name='startpage'),
    url(r'^$', startpage),  # Index auch bei leerer Adresse

    # An- und Abmeldung
    # url(r'^login/$', log_in, name='login'),
    # url(r'^logon/$', log_in),
    # url(r'^logoff/$', log_off, name='logoff'),
    # url(r'^logout/$', log_off),

    url(r'^login/$', auth_views.login,
         {'template_name': 'login.html'}, name='kas_login'),
    url(r'^logoff/$', log_off, name='logoff'),

    url(r'^werte/', include('werte.urls')),
    url(r'^medikamente/', include('medikamente.urls')),
    url(r'^usrprofile/', include('usrprofile.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
