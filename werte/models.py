# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.formats import date_format
from future.utils import python_2_unicode_compatible


@python_2_unicode_compatible
class Wert (models.Model):
    
    class Meta:
        verbose_name = "Messwert"
        verbose_name_plural = "Messwerte"

    def __str__(self):
        return ('{date}'.format(date_format(self.date)))

    date = models.DateTimeField(db_index=True, verbose_name='Datum', auto_now_add=True)
    # date = models.DateTimeField(verbose_name='Datum')
    rrsys = models.DecimalField(verbose_name='RR-Sys', max_digits=3, decimal_places=0, null=True, blank=True)
    rrdia = models.DecimalField(verbose_name='RR-Dia', max_digits=3, decimal_places=0, null=True, blank=True)
    puls = models.DecimalField(verbose_name='Puls', max_digits=3, decimal_places=0, null=True, blank=True)
    temp = models.DecimalField(verbose_name='Temp', max_digits=3, decimal_places=1, null=True, blank=True)
    gew = models.DecimalField(verbose_name='Gewicht', max_digits=3, decimal_places=1, null=True, blank=True)
    bemerkung = models.CharField(verbose_name='Besonderheiten', max_length=50, null=True, blank=True)
    ref_usr = models.ForeignKey(User)
