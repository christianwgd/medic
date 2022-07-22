# -*- coding: utf-8 -*-
from django import template
from django.utils import formats
from django.utils.translation import gettext as _, pgettext

from prescription.models import Prescription


register = template.Library()


@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    vo = Prescription.objects.get(pk=vo_id)
    dose = formats.localize(round(vo.medicament.strength * value, 2), use_l10n=True)
    return f'{dose}{vo.medicament.unit}'


@register.simple_tag(name='weekday_name')
def weekday_name(weekdays):
    names = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    result = ''
    all_days = True
    no_days = True
    for key, value in weekdays.items():
        if value:
            result += f'{_(names[int(key)])} '
            no_days = False
        else:
            all_days = False
    if all_days:
        return _('All')
    if no_days:
        return pgettext('medic', 'None')
    return result
