#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.sites import Dashboard
from djangobmf.sites import Category
from djangobmf.sites import Module
from djangobmf.sites import ViewMixin
from djangobmf.sites import register

from .models import TestView


class TestDashboard(Dashboard):
    name = 'Test'
    slug = 'test'


@register
class TaskModule(Module):
    model = TestView
    default = True


class TestCategory(Category):
    name = 'Test'
    slug = 'test'
    dashboard = TestDashboard


@register(category=TestCategory)
class TestListView(ViewMixin):
    model = TestView
    slug = 'test'
    name = 'test'
