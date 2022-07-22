from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicamentConfig(AppConfig):
    name = 'medicament'
    verbose_name = _('Medicament')
