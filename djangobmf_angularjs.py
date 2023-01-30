#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.template import Library

register = Library()


@register.simple_tag(name='ng')
def angularjs(value):
    return '{{%s}}' % value
