
from django import template
from django.template.defaultfilters import floatformat
from django.templatetags.l10n import localize

from measurement.models import Value

register = template.Library()


@register.simple_tag(name='format_value')
def format_value(measurement, value_type):
    try:
        val = Value.objects.get(measurement=measurement, value_type__slug=value_type.slug)
        if val.value is not None:
            return localize(floatformat(val.value, value_type.decimals))
    except Value.DoesNotExist:
        pass
    return ''
