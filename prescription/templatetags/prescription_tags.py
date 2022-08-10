# -*- coding: utf-8 -*-
from django import template
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from prescription.models import Prescription

register = template.Library()


@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    prescription = Prescription.objects.get(pk=vo_id)
    dose = formats.localize(round(prescription.medicament.strength * value, 2), use_l10n=True)
    return f'{dose}{prescription.medicament.unit}'


@register.inclusion_tag('prescription/includes/weekdays.html')
def weekday_disp(weekdays):
    wds = [(_(wd[0].capitalize()), wd[1]) for wd in weekdays]
    return {'weekdays': wds}


@register.simple_tag(name='calc_days')
def calc_days(prescription, user):
    if prescription.medicament.stock > 28:
        badge_class = 'bg-success'
    elif prescription.medicament.stock > 14:
        badge_class = 'bg-warning'
    else:
        badge_class = 'bg-danger'
    remaining = prescription.get_days_before_empty(user)
    return mark_safe(f'<span class="badge {badge_class}">{remaining}</span>')
