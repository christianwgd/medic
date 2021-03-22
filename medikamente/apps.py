from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MedikamenteConfig(AppConfig):
    name = 'medikamente'
    verbose_name = _('Medicaments')