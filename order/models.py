from gettext import pgettext

from django.contrib import auth
from django.db import models
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _

from medicament.models import Medicament

User = auth.get_user_model()


class Order(models.Model):

    class Meta:
        verbose_name = pgettext('order', 'Order')
        verbose_name_plural = _('Orders')
        ordering = ['-date']

    def __str__(self):
        return formats.date_format(
            timezone.localtime(self.date),
            format='SHORT_DATETIME_FORMAT',
        )

    def get_absolute_url(self):
        return reverse('order:detail', kwargs={'pk': self.pk})

    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('Owner'),
    )
    medicaments = models.ManyToManyField(
        Medicament, verbose_name=_('Medicaments'),
    )
    date = models.DateTimeField(auto_now_add=True)
    done = models.BooleanField(
        verbose_name=_('Done'), default=False,
    )
