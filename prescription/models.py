from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from medicament.models import Medicament


WEEK_DAYS = {
    ('0', 'mo'),
    ('1', 'tu'),
    ('2', 'we'),
    ('3', 'th'),
    ('4', 'fr'),
    ('5', 'sa'),
    ('6', 'su'),
}


def get_weekdays_default():
    return {
        '0': True, '1': True, '2': True, '3': True, '4': True, '5': True, '6': True
    }


class ActivePrescriptionManager(Manager):

    def active(self, for_user):
        return self.filter(
            Q(owner=for_user) &
            Q(valid_from__lte=timezone.now()) &
            Q(valid_until__gt=timezone.now()) | Q(valid_until=None)
        ).order_by('valid_from')


class Prescription(models.Model):

    class Meta(object):
        verbose_name = _('Prescription')
        verbose_name_plural = _('Prescriptions')
        ordering = ['medicament__name', 'medicament__strength']

    def __str__(self):
        return self.medicament.name

    objects = ActivePrescriptionManager()

    medicament = models.ForeignKey(
        Medicament, verbose_name=_('Medicament'),
        on_delete=models.PROTECT, related_name='prescriptions'
    )
    morning = models.DecimalField(
        verbose_name=_('Morning'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    noon = models.DecimalField(
        verbose_name=_('Noon'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    evening = models.DecimalField(
        verbose_name=_('Evening'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    night = models.DecimalField(
        verbose_name=_('Night'), max_digits=3,
        decimal_places=2, null=True, blank=True
    )
    weekdays = models.JSONField(
        verbose_name=_('Weekdays'), default=get_weekdays_default,
        blank=True
    )
    owner = models.ForeignKey(
        User, verbose_name=_('Owner'), on_delete=models.PROTECT
    )
    valid_from = models.DateField(verbose_name=_('Valid from'), null=True, blank=True)
    valid_until = models.DateField(verbose_name=_('Valid until'), null=True, blank=True)
