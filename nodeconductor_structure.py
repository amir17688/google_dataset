from collections import OrderedDict
from django import template
from django.utils.lru_cache import lru_cache

from nodeconductor.structure import SupportedServices
from nodeconductor.structure.serializers import BaseServiceSerializer


register = template.Library()


@lru_cache(maxsize=1)
@register.inclusion_tag('structure/service_settings_description.html')
def service_settings_description():
    services = []
    for cls in BaseServiceSerializer.__subclasses__():
        if cls.Meta.model is NotImplemented:
            continue
        if not SupportedServices._is_active_model(cls.Meta.model):
            continue
        name = SupportedServices.get_name_for_model(cls.Meta.model)
        fields, extra_fields = get_fields(cls)
        services.append((name, {
            'fields': fields,
            'extra_fields': extra_fields
        }))
    return {'services': sorted(services)}


def get_fields(serializer_class):
    fields = OrderedDict()
    extra_fields = OrderedDict()

    field_names = serializer_class.SERVICE_ACCOUNT_FIELDS
    if field_names is NotImplemented:
        field_names = []

    extra_field_names = serializer_class.SERVICE_ACCOUNT_EXTRA_FIELDS
    if extra_field_names is NotImplemented:
        extra_field_names = []

    for name, field in serializer_class().get_fields().items():
        data = {
            'label': field.label,
            'help_text': field.help_text,
            'required': field.required
        }
        if name in field_names:
            fields[name] = data
        if name in extra_field_names:
            extra_fields[name] = data

    return (fields, extra_fields)
