from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsrProfileConfig(AppConfig):
    name = 'usrprofile'
    verbose_name = _("User profile")