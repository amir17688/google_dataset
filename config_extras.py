from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def escapenewline(value): # Only one argument.
    return value.replace('\r\n', '\\n').replace('\n', '\\n')
