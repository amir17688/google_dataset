#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from djangobmf.permissions import ModuleViewPermission
from djangobmf.views.mixins import BaseViewMixin

import re


class ViewMixinMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ViewMixinMetaclass, cls).__new__
        parents = [
            b for b in bases if isinstance(b, ViewMixinMetaclass) and
            not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        new_cls = super_new(cls, name, bases, attrs)

        # validation
        if not hasattr(new_cls, 'model'):
            raise ImproperlyConfigured('No model attribute defined in %s.' % new_cls)

        if not hasattr(new_cls, 'slug'):
            raise ImproperlyConfigured('No slug attribute defined in %s.' % new_cls)

        if not hasattr(new_cls, 'name'):
            raise ImproperlyConfigured('No name attribute defined in %s.' % new_cls)

        if not re.match('^[\w-]+$', new_cls.slug):
            raise ImproperlyConfigured('The slug attribute defined in %s contains invalid chars.' % new_cls)

        # we add a key to add a unique identifier
        # the key is equal to the slug (for now) but this
        # gives us the opportunity to add i18n urls later
        if not hasattr(new_cls, 'key'):
            new_cls.key = new_cls.slug

        return new_cls


class ViewMixin(six.with_metaclass(ViewMixinMetaclass, BaseViewMixin)):
    """
    This class acts a an mixin for the REST-API and the view, which is
    rendering the table.
    """
    default_permission_classes = [ModuleViewPermission]
    manager = None
    date_resolution = None
    permissions = None
    template_name = None
