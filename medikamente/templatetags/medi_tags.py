# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import locale

from django import template
from django.utils.translation import ugettext_lazy as _

from medikamente.models import Verordnung, Medikament

register = template.Library()

@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    vo = Verordnung.objects.get(pk=vo_id)
    dosis = vo.ref_medikament.staerke * value
    locale.setlocale(locale.LC_ALL, '')
    dose = locale.format_string('%.2f', dosis)
    return "{dose}{unit}".format(
        dose=dose, 
        unit=vo.ref_medikament.einheit
    )


@register.inclusion_tag('medikamente/includes/mediheader.html')
def medi_header(med_id, *args, **kwargs):
    try:
        med = Medikament.objects.get(pk=med_id)
        med_detail = '{name} {strength} {unit}'.format(
            name = med.name, 
            strength = med.staerke,
            unit = med.einheit,
        )
        locale.setlocale(locale.LC_ALL, '')
        in_stock = locale.format_string('%.2f', med.bestand)
        med_stock = _('{stock} Tablets').format(
            stock = in_stock
        )
    except Medikament.DoesNotExist:
        med_detail = _('unknown')
        med_stock = _('unknown')
    return {'med_detail': med_detail, 'med_stock': med_stock}
