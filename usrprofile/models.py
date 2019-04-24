# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object
from django.db import models
from django.contrib.auth.models import User
from django.utils import formats, dateparse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MaxValueValidator, MinValueValidator

from orderable.models import Orderable


@python_2_unicode_compatible
class StartUrl(Orderable):

    class Meta(object):
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")

    def __str__(self):
        return self.name

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    url = models.CharField(verbose_name=_('URL pattern'), max_length=100)


@python_2_unicode_compatible
class UserProfile(models.Model):
    
    class Meta(object):
        verbose_name = _("User setting")
        verbose_name_plural = _("User settings")
        
    def __str__(self):
        return self.ref_usr.username

    gebdat = models.DateField(
        verbose_name=_("Date of birth"), null=True, blank=True
    )
    warnenTageVorher = models.IntegerField(
        default=20, verbose_name=_("Hold medications for at least"),
        validators=[MinValueValidator(2), MaxValueValidator(30)],
        help_text=_('days')
    )
    werteLetzteTage = models.IntegerField(
        default=30, verbose_name=_("Show readings for"),
        validators=[MinValueValidator(10), MaxValueValidator(365)],
        help_text=_('days')
    )
    zeigeArztWerte = models.BooleanField(
        default=False, verbose_name=_("Doctor is allowed to see readings")
    )
    zeigeArztMed = models.BooleanField(
        default=False, verbose_name=_("Doctor is allowed to see medications")
    )
    ref_usr = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        verbose_name=_("User"), related_name='profile'
    )
    email_arzt = models.EmailField(
        verbose_name=_("Doctor's email address"), null=True, blank=True
    )
    myStartPage = models.ForeignKey(
        StartUrl, on_delete=models.PROTECT, 
        verbose_name=_("My home page"), blank=True, null=True
    )

    @property
    def usrinf(self):
        if self.gebdat is None:
            return '{}, {}'.format(
                self.ref_usr.last_name,
                self.ref_usr.first_name
            )
        else:
            userinf = '{}, {} - {} {}'.format(
                self.ref_usr.last_name,
                self.ref_usr.first_name,
                _('born'),
                formats.date_format(
                    self.gebdat,
                    format='SHORT_DATE_FORMAT',
                    use_l10n=True
                )
            )
            return userinf
