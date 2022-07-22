# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import formats, timezone
from django.utils.translation import gettext as _


UNIT_CHOICES = (
    ('mg', _('Milligram')),
    ('µg', _('Microgram')),
    ('g', _('Gram')),
    ('IE', _('Intern. units')),
)


class Medicament(models.Model):

    class Meta:
        verbose_name = _('Medicament')
        verbose_name_plural = _('Medicaments')
        ordering = ['name', 'strength']

    def __str__(self):
        dose = formats.localize(self.strength, use_l10n=True)
        return f'{self.name} {dose} {self.unit}'

    name = models.CharField(
        verbose_name=_('Denomination'), max_length=50
    )
    producer = models.CharField(
        verbose_name=_('Producer'), max_length=50,
        null=True, blank=True
    )
    ingredient = models.CharField(
        verbose_name=_('Active ingredient'), max_length=50,
        null=True, blank=True
    )
    package = models.PositiveIntegerField(
        verbose_name=_('Package size'), help_text=_('Tablets')
    )
    strength = models.DecimalField(
        verbose_name=_('Strength'), max_digits=8, decimal_places=2
    )
    unit = models.CharField(
        verbose_name=_('Unit'), max_length=2, choices=UNIT_CHOICES,
    )
    owner = models.ForeignKey(
        User, verbose_name=_('Owner'), on_delete=models.PROTECT
    )


REASON_CHOICES = (
    ('', _('choose ...')),
    ('01', _('New Package (+)')),
    ('02', _('Intake missed (+)')),
    ('03', _('Intake skipped (+)')),
    ('04', _('Expiry date reached (-)')),
    ('05', _('Dose increased (-)')),
    ('98', _('Other (+)')),
    ('99', _('Other (-)')),
)


class StockChange(models.Model):

    class Meta:
        verbose_name = _('Stock change')
        verbose_name_plural = _('Stock changes')

    def __str__(self):
        return self.medicament

    medicament = models.ForeignKey(
        Medicament, on_delete=models.PROTECT, verbose_name=_('Medicament'),
    )
    date = models.DateField(verbose_name=_('Date'), auto_now_add=False)
    amount = models.DecimalField(
        verbose_name=_('Amount'), max_digits=5, decimal_places=2
    )
    reason = models.CharField(
        verbose_name=_('Reason'), max_length=2, choices=REASON_CHOICES
    )
    text = models.CharField(
        verbose_name=_('Note'), max_length=50, null=True, blank=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('Owner'),
    )
