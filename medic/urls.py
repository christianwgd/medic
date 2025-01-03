from django.urls import path, include, reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.utils.translation import gettext_lazy as _
from two_factor.urls import urlpatterns as tf_urls

from . import  views

admin.site.site_header = _('medic')

urlpatterns = [
    path('', include(tf_urls)),
    path('admin/', admin.site.urls),

    # Startseite
    path('index/', views.index, name='index'),  # Inhaltsverzeichnis anzeigen

    # dynamische Startseite
    path('startpage/', views.startpage, name='startpage'),
    path('', views.startpage, name='startpage'),  # Index auch bei leerer Adresse

    path('login/', RedirectView.as_view(url='/account/login/'), name='medic_login'),
    path(
        'pwd_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='medic_reg/password_change_form.html',
            success_url=reverse_lazy('pwd_change_done'),
        ),
        name='pwd_change',
    ),
    path(
        'pwd_change_done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='medic_reg/password_change_done_form.html',
        ),
        name='pwd_change_done',
    ),
    path('logoff/', views.log_off, name='logoff'),

    path('measurement/', include('measurement.urls')),
    path('medicament/', include('medicament.urls')),
    path('prescription/', include('prescription.urls')),
    path('order/', include('order.urls')),
    path('usrprofile/', include('usrprofile.urls')),
    path("select2/", include("django_select2.urls")),
]
