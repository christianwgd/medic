
from django.db import models
from django.contrib import auth
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _


User = auth.get_user_model()


class ValueType(models.Model):

    class Meta:
        verbose_name = _('Value Type')
        verbose_name_plural = _('Value Types')
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    name = models.CharField(
        verbose_name=_('Name'), max_length=50,
    )
    unit = models.CharField(
        verbose_name=_('Unit'), max_length=50,
    )
    decimals = models.PositiveIntegerField(
        verbose_name=_('Decimal places'), default=0)
    slug = models.SlugField()
    sort_order = models.PositiveIntegerField(default=0)


class Measurement(models.Model):

    class Meta:
        verbose_name = _('Measurement')
        verbose_name_plural = _('Measurements')
        ordering = ['-date']

    def __str__(self):
        return date_format(self.date)

    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('user'),
    )
    comment = models.CharField(
        verbose_name=_('Comment'), max_length=50,
        null=True, blank=True,
    )
    date = models.DateTimeField(
        db_index=True, verbose_name=_('Date'),
        auto_now_add=True,
    )


class Value(models.Model):

    class Meta:
        verbose_name = _('Value')
        verbose_name_plural = _('Values')

    def __str__(self):
        return f'{self.value_type}-{self.measurement}'

    value_type = models.ForeignKey(
        ValueType, db_index=True, verbose_name=_('Value Type'),
        on_delete=models.CASCADE,
    )
    value = models.DecimalField(
        verbose_name=_('Value'), max_digits=5, decimal_places=2,
        null=True, blank=True,
    )
    measurement = models.ForeignKey(
        Measurement, db_index=True, verbose_name=_('Value'),
        on_delete=models.CASCADE, related_name='values',
    )
