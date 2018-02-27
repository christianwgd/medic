# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from medikamente.models import Verordnung

register = template.Library()

@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    vo = Verordnung.objects.get(pk=vo_id)
    dosis = vo.ref_medikament.staerke * value
    return ("{:10.2f} {} ".format(dosis, vo.ref_medikament.einheit).replace('.', ','))