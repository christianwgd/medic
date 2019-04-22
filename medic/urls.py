# encoding: utf-8
from __future__ import absolute_import
from django.urls import path, include

from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import index, log_off, startpage

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),

    # Startseite
    path('index/', index, name='index'),  # Inhaltsverzeichnis anzeigen

    # dynamische Startseite
    path('startpage/', startpage, name='startpage'),
    path('', startpage),  # Index auch bei leerer Adresse

    path('login/', auth_views.LoginView.as_view(),
         {'template_name': '/login.html'}, name='medic_login'),
    path('logoff/', log_off, name='logoff'),

    path('werte/', include('werte.urls')),
    path('medikamente/', include('medikamente.urls')),
    path('usrprofile/', include('usrprofile.urls')),
]
