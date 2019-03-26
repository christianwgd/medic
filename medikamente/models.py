# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

EINHEIT_CHOICES = (
        ('mg', 'Milligramm'),
        ('µg', 'Microgramm'),
        ('g', 'Gramm'),
        ('IE', 'Intern. Einheiten')
    )


@python_2_unicode_compatible
class Medikament (models.Model):
    
    class Meta(object):
        verbose_name = "Medikament"
        verbose_name_plural = "Medikamente"
        ordering = ['name', 'staerke']
        
    def __str__(self):
        return ('{} {:8.2f} {}'.format(self.name, self.staerke, self.einheit)).replace('.', ',')
        
    name = models.CharField(verbose_name="Bezeichnung", max_length=50)
    hersteller = models.CharField(verbose_name="Hersteller", max_length=50, null=True, blank=True)
    wirkstoff = models.CharField(verbose_name="Wirkstoff", max_length=50, null=True, blank=True)
    packung = models.IntegerField(verbose_name="Packungsgröße", help_text=" Tabletten")
    staerke = models.DecimalField(verbose_name="Dosis", max_digits=8, decimal_places=2)
    einheit = models.CharField(verbose_name="Einheit", max_length=2, choices=EINHEIT_CHOICES)
    bestand = models.DecimalField(verbose_name='Bestand', max_digits=5, decimal_places=2)
    bestand_vom = models.DateField(verbose_name='Bestandsänderung vom', auto_now_add=True)
    ref_usr = models.ForeignKey(User)


@python_2_unicode_compatible
class Verordnung (models.Model):
    
    class Meta(object):
        verbose_name = "Verordnung"
        verbose_name_plural = "Verordnungen"
        
    def __str__(self):
        return '{}'.format(self.ref_medikament)
        
    ref_medikament = models.ForeignKey(Medikament, verbose_name='Medikament')
    morgen = models.DecimalField(verbose_name='Morgen', max_digits=3, decimal_places=2, null=True, blank=True)
    mittag = models.DecimalField(verbose_name='Mittag', max_digits=3, decimal_places=2, null=True, blank=True)
    abend = models.DecimalField(verbose_name='Abend', max_digits=3, decimal_places=2, null=True, blank=True)
    nacht = models.DecimalField(verbose_name='Nacht', max_digits=3, decimal_places=2, null=True, blank=True)
    mo = models.BooleanField(verbose_name='Mo', default=False)
    di = models.BooleanField(verbose_name='Di', default=False)
    mi = models.BooleanField(verbose_name='Mi', default=False)
    do = models.BooleanField(verbose_name='Do', default=False)
    fr = models.BooleanField(verbose_name='Fr', default=False)
    sa = models.BooleanField(verbose_name='Sa', default=False)
    so = models.BooleanField(verbose_name='So', default=False)
    ref_usr = models.ForeignKey(User, verbose_name='Benutzer')


@python_2_unicode_compatible
class VrdFuture (models.Model):

    class Meta(object):
        verbose_name = "Terminierte Verordnung"
        verbose_name_plural = "Terminierte Verordnungen"

    def __str__(self):
        return ('{}-{}-{}-{}-{}'.format(self.ref_medikament, self.morgen, self.mittag,
                                        self.abend, self.nacht))

    ref_medikament = models.ForeignKey(Medikament, verbose_name='Medikament')
    ref_usr = models.ForeignKey(User, verbose_name='Benutzer')
    morgen = models.DecimalField(verbose_name='Morgen', max_digits=3, decimal_places=2,
                                 null=True, blank=True, help_text=" Tabl.")
    mittag = models.DecimalField(verbose_name='Mittag', max_digits=3, decimal_places=2,
                                 null=True, blank=True, help_text=" Tabl.")
    abend = models.DecimalField(verbose_name='Abend', max_digits=3, decimal_places=2,
                                null=True, blank=True, help_text=" Tabl.")
    nacht = models.DecimalField(verbose_name='Nacht', max_digits=3, decimal_places=2,
                                null=True, blank=True, help_text=" Tabl.")
    mo = models.BooleanField(verbose_name='Mo', default=False)
    di = models.BooleanField(verbose_name='Di', default=False)
    mi = models.BooleanField(verbose_name='Mi', default=False)
    do = models.BooleanField(verbose_name='Do', default=False)
    fr = models.BooleanField(verbose_name='Fr', default=False)
    sa = models.BooleanField(verbose_name='Sa', default=False)
    so = models.BooleanField(verbose_name='So', default=False)
    gueltig_ab = models.DateField(verbose_name='gültig ab')
    erledigt = models.BooleanField(verbose_name='erledigt', default=False)


GRUND_CHOICES = (
        ('', u'wählen...'),
        ('01', u'Neue Packung (+)'),
        ('02', u'Einnhame vergessen (+)'),
        ('03', u'Einnahme ausgesetzt (+)'),
        ('04', u'Verfallsdatum erreicht (-)'),
        ('05', u'Dosis erhöht (-)'),
        ('98', u'Sonstige Korrektur (+)'),
        ('99', u'Sonstige Korrektur (-)'),
    )


@python_2_unicode_compatible
class Bestandsveraenderung(models.Model):
    
    class Meta(object):
        verbose_name = "Bestandsveränderung"
        verbose_name_plural = "Bestandsveränderungen"
        
    def __str__(self):
        return self.ref_medikament

    ref_medikament = models.ForeignKey(Medikament)
    date = models.DateTimeField(verbose_name='Datum', auto_now_add=False)
    menge = models.DecimalField(verbose_name='Menge', max_digits=5, decimal_places=2)
    grund = models.CharField(verbose_name="Einheit", max_length=2, choices=GRUND_CHOICES)
    text = models.CharField(verbose_name='Anmerkung', max_length=50, null=True, blank=True)
    ref_usr = models.ForeignKey(User)
