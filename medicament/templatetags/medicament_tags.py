# -*- coding: utf-8 -*-
from django import template
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from medicament.models import Medicament


register = template.Library()


@register.inclusion_tag('medicament/includes/mediheader.html')
def medicament_header(med_id, *args, **kwargs):
    try:
        med = Medicament.objects.get(pk=med_id)
        med_detail = f'{med.name} {med.strength} {med.unit}'
        in_stock = formats.localize(med.bestand, use_l10n=True)
        med_stock = _('{stock} Tablets').format(
            stock = in_stock
        )
    except Medicament.DoesNotExist:
        med_detail = _('unknown')
        med_stock = _('unknown')
    return {'med_detail': med_detail, 'med_stock': med_stock}
