# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import auth
from django.dispatch import receiver
from django.utils import formats
from django.utils.translation import gettext as _


User = auth.get_user_model()


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

    def get_active_prescription(self, for_user):
        # pylint: disable=no-member
        return self.prescriptions.active(for_user=for_user).first()

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
    stock = models.DecimalField(
        verbose_name=_('Stock'), max_digits=6, decimal_places=2,
        default=0.0
    )
    last_calc = models.DateField(
        verbose_name=_('Last stock calculation'),
        auto_now_add=False, null=True
    )


REASON_CHOICES = (
    ('00', _('Consumption (-)')),
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
        ordering = ['-date']

    def __str__(self):
        return str(self.medicament)

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


@receiver(models.signals.post_save, sender=StockChange)
def update_medicament_stock(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
        Function to update the medicament stock.
        sender is the model class that sends the signal,
        while instance is an actual instance of that class
    """

    medicament = instance.medicament
    if instance.reason in ['00', '04', '99']:  # Amount is negative
        medicament.stock -= instance.amount
    else:
        medicament.stock += instance.amount
    medicament.save()
