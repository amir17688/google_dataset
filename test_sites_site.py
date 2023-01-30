#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import TestCase

from unittest import expectedFailure


class SiteTests(TestCase):
    @expectedFailure
    def test_fails(self):
        self.assertTrue(False)
