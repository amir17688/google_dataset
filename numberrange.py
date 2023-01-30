#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.timezone import get_default_timezone
from django.utils.timezone import is_aware
from django.utils.timezone import localtime

from djangobmf.models import NumberRange as NumberRangeModel

import re
import datetime

import logging
logger = logging.getLogger(__name__)


class NumberRangeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(NumberRangeMetaclass, cls).__new__
        parents = [
            b for b in bases if isinstance(b, NumberRangeMetaclass) and
            not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        new_cls = super_new(cls, name, bases, attrs)

        # validation
        if not getattr(new_cls, 'template', None):
            raise ImproperlyConfigured('No template attribute defined in %s.' % new_cls)

        new_cls._template = new_cls.settings and getattr(settings, new_cls.settings, None) or new_cls.template
        new_cls.validate_template()
        new_cls.get_type()

        return new_cls


class NumberRange(six.with_metaclass(NumberRangeMetaclass, object)):
    _MATCH_YEAR = r'{year}'
    _MATCH_MONTH = r'{month}'
    _MATCH_COUNTER = r'{counter:0[1-9]+[0-9]*d}'
    _TYPE_RANGE_MONTH = 'm'
    _TYPE_RANGE_YEAR = 'y'
    _TYPE_COUNTER = 'c'

    settings = None
    lookup = {}

    def name(self, obj, time_field="created"):
        ct = ContentType.objects.get_for_model(obj)

        if self.type == self._TYPE_COUNTER:
            date = None
            number = self.get_object(ct)
            if self.lookup:
                counter = obj._base_manager.filter(**self.lookup).count() + number.counter
            else:
                counter = obj.pk
        else:
            date = self.from_time(getattr(obj, time_field))
            number = self.get_object(ct, date)

            lookup = self.lookup
            lookup.update({
                '%s__gte' % time_field: number.period_start,
                'pk__lt': obj.pk,
            })

            counter = obj._base_manager.filter(**lookup).count() + number.counter

        return self.generate_name(date, counter)

    def delete(self, obj, time_field="created"):
        ct = ContentType.objects.get_for_model(obj)
        date = self.from_time(getattr(obj, time_field))

        number = self.get_object(ct, date)
        number.counter += 1
        number.save()

    def get_object(self, ct, date=None):
        if self.type == self._TYPE_COUNTER:
            start = None
            final = None
        else:
            start, final = self.get_period(date)

        obj, created = NumberRangeModel.objects.get_or_create(
            ct=ct, period_start=start, period_final=final,
        )
        return obj

    @classmethod
    def validate_template(cls):
        y = re.findall(cls._MATCH_YEAR, cls._template)
        m = re.findall(cls._MATCH_MONTH, cls._template)
        c = re.findall(cls._MATCH_COUNTER, cls._template)

        if len(y) > 1:
            raise ValidationError('{year} can only be used once')
        if len(m) > 1:
            raise ValidationError('{month} can only be used once')
        if len(m) == 1 and len(y) == 0:
            raise ValidationError('{month} can only be used while {year} is present')
        if len(c) > 1:
            raise ValidationError('{counter:0Nd} can only be used once')
        if len(c) == 0:
            raise ValidationError('{counter:0Nd} must be used once')

        try:
            cls._template.format(year=1999, month=11, counter=1)
        except KeyError:
            raise ValidationError('The string has the wrong format')

    @classmethod
    def get_type(cls):
        if (re.search(cls._MATCH_MONTH, cls._template)):
            cls.type = cls._TYPE_RANGE_MONTH
        elif (re.search(cls._MATCH_YEAR, cls._template)):
            cls.type = cls._TYPE_RANGE_YEAR
        else:
            cls.type = cls._TYPE_COUNTER

    def from_time(self, time):
        if is_aware(time):
            localtime(time, get_default_timezone())
        return datetime.date(time.year, time.month, time.day)

    def generate_name(self, date, counter):

        if self.type == self._TYPE_COUNTER:
            return self._template.format(counter=counter)

        date = self.get_period(date, as_range=False)

        return self._template.format(
            year=date.strftime('%Y'),
            month=date.strftime('%m'),
            counter=counter,
        )

    def get_period(self, date, as_range=True):
        start = date
        end = date

        if self.type == self._TYPE_RANGE_MONTH:
            start = datetime.date(date.year, date.month, 1)
            if date.month == 12:
                end = datetime.date(date.year + 1, 1, 1) - datetime.timedelta(1)
            else:
                end = datetime.date(date.year, date.month + 1, 1) - datetime.timedelta(1)

        if self.type == self._TYPE_RANGE_YEAR:
            start = datetime.date(date.year, 1, 1)
            end = datetime.date(date.year, 12, 31)

        if as_range:
            return start, end
        return start
