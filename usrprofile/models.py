# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from orderable.models import Orderable

from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MaxValueValidator, MinValueValidator


@python_2_unicode_compatible
class StartUrl(Orderable):

    class Meta:
        verbose_name = "Startseite"
        verbose_name_plural = "Startseiten"

    def __str__(self):
        return self.name

    name = models.CharField(verbose_name='Name', max_length=100)
    url = models.CharField(verbose_name='URL-Pattern', max_length=100)


@python_2_unicode_compatible
class UserProfile(models.Model):
    
    class Meta:
        verbose_name = "Einstellung"
        verbose_name_plural = "Einstellungen"
        
    def __str__(self):
        return self.ref_usr.username

    gebdat = models.DateField(verbose_name="Geburtsdatum", null=True, blank=True)
    warnenTageVorher = models.IntegerField(default=20, verbose_name="Medikamente vorhalten für mindestens",
                                           validators=[MinValueValidator(2), MaxValueValidator(30)],
                                           help_text='Tage')
    werteLetzteTage = models.IntegerField(default=30, verbose_name="Standart Zeitraum Messwerte anzeigen",
                                          validators=[MinValueValidator(10), MaxValueValidator(365)],
                                          help_text='Tage')
    zeigeArztWerte = models.BooleanField(default=False, verbose_name="Arzt darf Messwerte sehen")
    zeigeArztMed = models.BooleanField(default=False, verbose_name="Arzt darf Medikamente sehen")
    ref_usr = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_arzt = models.EmailField(verbose_name="email-Adresse Arzt", null=True, blank=True)
    myStartPage = models.ForeignKey(StartUrl, verbose_name="Meine Startseite", blank=True, null=True)
    @property
    def usrinf(self):
        if self.gebdat is None:
            return '{}, {}'.format(
                self.ref_usr.last_name,
                self.ref_usr.first_name
            )
        else:
            return '{}, {} - {}'.format(
                                    self.ref_usr.last_name,
                                    self.ref_usr.first_name,
                                    self.gebdat.strftime("geb. %d.%m.%Y")
                                 )
