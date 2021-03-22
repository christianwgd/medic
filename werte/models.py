# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _


class Wert (models.Model):
    
    class Meta:
        verbose_name = _('Measurement')
        verbose_name_plural = _('Measurements')

    def __str__(self):
        return ('{date}'.format(date=date_format(self.date)))

    date = models.DateTimeField(
        db_index=True, verbose_name=_('Date'), 
        auto_now_add=True
    )
    rrsys = models.DecimalField(
        verbose_name=_('RR sys'), max_digits=3, 
        decimal_places=0, null=True, blank=True
    )
    rrdia = models.DecimalField(
        verbose_name=_('RR dia'), max_digits=3, 
        decimal_places=0, null=True, blank=True
    )
    puls = models.DecimalField(
        verbose_name=_('Pulse'), max_digits=3, 
        decimal_places=0, null=True, blank=True
    )
    temp = models.DecimalField(
        verbose_name=_('Temp.'), max_digits=3, 
        decimal_places=1, null=True, blank=True
    )
    gew = models.DecimalField(
        verbose_name=_('Weight'), max_digits=3, 
        decimal_places=1, null=True, blank=True
    )
    bemerkung = models.CharField(
        verbose_name=_('Peculiarity'), max_length=50, 
        null=True, blank=True
    )
    ref_usr = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('user')
    )
