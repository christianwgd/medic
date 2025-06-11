from allauth.account.decorators import secure_admin_login
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.utils.translation import gettext_lazy as _

from . import  views

admin.autodiscover()
admin.site.site_header = _('medic')
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Startseite
    path('index/', views.index, name='index'),  # Inhaltsverzeichnis anzeigen

    # dynamische Startseite
    path('startpage/', views.startpage, name='startpage'),
    path('', views.startpage, name='startpage'),  # Index auch bei leerer Adresse
    path('accounts/signup/', RedirectView.as_view(url='/', permanent=True)),
    path('accounts/', include('allauth.urls')),

    path('measurement/', include('measurement.urls')),
    path('medicament/', include('medicament.urls')),
    path('prescription/', include('prescription.urls')),
    path('order/', include('order.urls')),
    path('usrprofile/', include('usrprofile.urls')),
    path("select2/", include("django_select2.urls")),
]
