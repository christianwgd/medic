import datetime
from decimal import Decimal

from bitfield import BitField
from django.contrib import auth
from django.db import models
from django.db.models import Manager, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from medicament.models import Medicament


User = auth.get_user_model()


def daterange(start_date, end_date):
    for index in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(index)


class ActivePrescriptionManager(Manager):

    def active(self, for_user):
        return self.filter(
            Q(owner=for_user) &
            Q(valid_from__lte=timezone.now()) &
            Q(valid_until__gt=timezone.now()) | Q(valid_until=None)
        ).order_by('valid_from')


class Prescription(models.Model):

    class Meta:
        verbose_name = _('Prescription')
        verbose_name_plural = _('Prescriptions')
        ordering = ['medicament__name', 'medicament__strength']

    def __str__(self):
        return str(self.medicament)

    def active(self, date, for_user):
        valid_from = True
        if self.valid_from is not None:
            valid_from = self.valid_from <= date
        valid_until = True
        if self.valid_until is not None:
            valid_until = date <= self.valid_until
        return valid_from and valid_until and self.owner == for_user

    def get_dose_per_day(self, date, user):
        # pylint: disable=no-member
        if self.active(date, user) and self.weekdays.items()[date.weekday()][1]:
            return self.morning + self.noon + self.evening + self.night
        return 0.0

    def get_default_dose(self):
        # Find first intake to get default dose
        if self.morning:
            return self.morning
        if self.noon:
            return self.noon
        if self.evening:
            return self.evening
        if self.night:
            return self.night
        return None

    def get_amount_for_time(self, start_date, end_date, user):
        needed = Decimal(0.0)
        for day in daterange(start_date, end_date):
            dpd = self.get_dose_per_day(day, user)
            needed += Decimal(dpd)
        return needed

    def get_days_before_empty(self, user):
        amount = self.medicament.stock
        date = timezone.now().date()
        if not self.active(date, user):
            return 0
        days = 0
        while amount > 0:
            amount -= Decimal(self.get_dose_per_day(date, user))
            date += datetime.timedelta(days=1)
            days += 1
        return days

    objects = ActivePrescriptionManager()

    medicament = models.ForeignKey(
        Medicament, verbose_name=_('Medicament'),
        on_delete=models.PROTECT, related_name='prescriptions'
    )
    morning = models.DecimalField(
        verbose_name=_('Morning'), max_digits=3,
        decimal_places=2, default=0.0, blank=True
    )
    noon = models.DecimalField(
        verbose_name=_('Noon'), max_digits=3,
        decimal_places=2, default=0.0, blank=True
    )
    evening = models.DecimalField(
        verbose_name=_('Evening'), max_digits=3,
        decimal_places=2, default=0.0, blank=True
    )
    night = models.DecimalField(
        verbose_name=_('Night'), max_digits=3,
        decimal_places=2, default=0.0, blank=True
    )
    weekdays = BitField(flags=('mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'), default=0)
    owner = models.ForeignKey(
        User, verbose_name=_('Owner'), on_delete=models.PROTECT,
        related_name='prescriptions'
    )
    valid_from = models.DateField(verbose_name=_('Valid from'), null=True, blank=True)
    valid_until = models.DateField(verbose_name=_('Valid until'), null=True, blank=True)
