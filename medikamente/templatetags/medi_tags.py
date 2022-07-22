# -*- coding: utf-8 -*-
from django import template
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from medikamente.models import Prescription, Medicament

register = template.Library()

@register.simple_tag(name='calc_dosis')
def calc_dosis(value, vo_id):
    vo = Prescription.objects.get(pk=vo_id)
    dosis = round(vo.ref_medikament.staerke * value, 2)
    dose = formats.localize(dosis, use_l10n=True)
    return "{dose}{unit}".format(
        dose=dose,
        unit=vo.ref_medikament.einheit
    )


@register.inclusion_tag('medikamente/includes/mediheader.html')
def medi_header(med_id, *args, **kwargs):
    try:
        med = Medicament.objects.get(pk=med_id)
        med_detail = '{name} {strength} {unit}'.format(
            name = med.name,
            strength = med.staerke,
            unit = med.einheit,
        )
        in_stock = formats.localize(med.bestand, use_l10n=True)
        med_stock = _('{stock} Tablets').format(
            stock = in_stock
        )
    except Medicament.DoesNotExist:
        med_detail = _('unknown')
        med_stock = _('unknown')
    return {'med_detail': med_detail, 'med_stock': med_stock}
