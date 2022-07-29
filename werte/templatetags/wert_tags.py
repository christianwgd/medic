# -*- coding: utf-8 -*-
from django import template

from werte.models import Value

register = template.Library()


@register.simple_tag(name='format_value')
def format_value(measurement, value_type):
    try:
        val = Value.objects.get(measurement=measurement, value_type__slug=value_type.slug)
        if val.value is not None:
            return f'{val.value:.{value_type.decimals}f}'
    except Value.DoesNotExist:
        pass
    return ''
