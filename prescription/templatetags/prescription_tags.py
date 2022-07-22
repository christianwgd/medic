# -*- coding: utf-8 -*-
from django import template
from django.utils import formats

from prescription.models import Prescription


register = template.Library()


@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    vo = Prescription.objects.get(pk=vo_id)
    dose = formats.localize(round(vo.medicament.strength * value, 2), use_l10n=True)
    return f'{dose}{vo.medicament.unit}'
