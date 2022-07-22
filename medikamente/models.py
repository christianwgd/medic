# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Manager, Q
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _

EINHEIT_CHOICES = (
        ('mg', _('Milligram')),
        ('µg', _('Microgram')),
        ('g', _('Gram')),
        ('IE', _('Intern. units')),
    )


class Medicament(models.Model):

    class Meta:
        verbose_name = _('Medicament')
        verbose_name_plural = _('Medicaments')
        ordering = ['name', 'staerke']

    def __str__(self):
        dose = formats.localize(self.staerke, use_l10n=True)
        return '{name} {dose} {unit}'.format(
                name=self.name,
                dose=dose,
                unit=self.einheit
        )

    name = models.CharField(
        verbose_name=_('Denomination'), max_length=50
    )
    hersteller = models.CharField(
        verbose_name=_('Manufacturer'), max_length=50,
        null=True, blank=True
    )
    wirkstoff = models.CharField(
        verbose_name=_('Active ingredient'), max_length=50,
        null=True, blank=True
    )
    packung = models.PositiveIntegerField(
        verbose_name=_('Package size'), help_text=_(' Tablets')
    )
    staerke = models.DecimalField(
        verbose_name=_('Dose'), max_digits=8, decimal_places=2
    )
    einheit = models.CharField(
        verbose_name=_('Unit'), max_length=2, choices=EINHEIT_CHOICES
    )
    bestand = models.DecimalField(
        verbose_name=_('Inventory'), max_digits=5, decimal_places=2
    )
    bestand_vom = models.DateField(
        verbose_name=_('Inventory change'), auto_now_add=True
    )
    ref_usr = models.ForeignKey(User, on_delete=models.PROTECT)


class ActivePrescriptionManager(Manager):

    def active(self, for_user):
        return self.filter(
            Q(ref_usr=for_user) &
            Q(valid_from__lte=timezone.now()) &
            Q(valid_until__gt=timezone.now()) | Q(valid_until=None)
        ).order_by('valid_from')


class Prescription(models.Model):

    class Meta(object):
        verbose_name = _('Prescription')
        verbose_name_plural = _('Prescriptions')
        ordering = ['ref_medikament__name', 'ref_medikament__staerke']

    def __str__(self):
        return '{}'.format(self.ref_medikament)

    def save(self, *args, **kwargs):
        # TODO: Check for overlapping periods of same medicament!
        existing = self.objects.filter(
            Q(valid_until__gte=self.valid_from) | Q(valid_from__lte=self.valid_until),
            ref_medikament=self.ref_medikament,
        )
        super().save(*args, **kwargs)

    objects = ActivePrescriptionManager()

    ref_medikament = models.ForeignKey(
        Medicament, verbose_name=_('Medicament'),
        on_delete=models.PROTECT, related_name='prescriptions'
    )
    morgen = models.DecimalField(
        verbose_name=_('Morning'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    mittag = models.DecimalField(
        verbose_name=_('Noon'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    abend = models.DecimalField(
        verbose_name=_('Evening'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    nacht = models.DecimalField(
        verbose_name=_('Night'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    mo = models.BooleanField(verbose_name=_('Mo'), default=True)
    di = models.BooleanField(verbose_name=_('Tu'), default=True)
    mi = models.BooleanField(verbose_name=_('We'), default=True)
    do = models.BooleanField(verbose_name=_('Th'), default=True)
    fr = models.BooleanField(verbose_name=_('Fr'), default=True)
    sa = models.BooleanField(verbose_name=_('Sa'), default=True)
    so = models.BooleanField(verbose_name=_('Su'), default=True)
    ref_usr = models.ForeignKey(
        User, verbose_name='Benutzer', on_delete=models.PROTECT
    )
    valid_from = models.DateField(verbose_name=_('Valid from'), null=True, blank=True)
    valid_until = models.DateField(verbose_name=_('Valid until'), null=True, blank=True)


class VrdFuture (models.Model):

    class Meta:
        verbose_name = _('Scheduled prescription')
        verbose_name_plural = _('Scheduled prescriptions')

    def __str__(self):
        return '{}-{}-{}-{}-{}'.format(
            self.ref_medikament,
            self.morgen,
            self.mittag,
            self.abend,
            self.nacht
        )

    ref_medikament = models.ForeignKey(Medicament, verbose_name='Medikament', on_delete=models.PROTECT)
    ref_usr = models.ForeignKey(User, verbose_name='Benutzer', on_delete=models.PROTECT)
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
        verbose_name = _('Change of inventory')
        verbose_name_plural = _('Changes of inventory')

    def __str__(self):
        return self.ref_medikament

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
    ref_usr = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('User'),
    )
