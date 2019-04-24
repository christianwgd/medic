from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsrProfileConfig(AppConfig):
    name = 'usrprofile'
    verbose_name = _("User profile")