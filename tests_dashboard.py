#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

# from django.test import TestCase
# from django.utils.translation import ugettext_lazy as _

# from djangobmf.core.dashboard import Dashboard
# from djangobmf.core.category import Category

# from collections import OrderedDict


# class ClassTests(TestCase):

#   def setUp(self):  # noqa

#       class TestCategory1(Category):
#           name = "test1"
#           slug = "test1"

#       class TestCategory2(Category):
#           name = "test2"
#           slug = "test2"

#       self.cat1 = TestCategory1()
#       self.cat2 = TestCategory2()

#       super(ClassTests, self).setUp()

#   def test_init_empty(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard()

#       self.assertEqual(td.data, OrderedDict([]))

#   def test_init_data1(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard(self.cat1)

#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#       ]))

#   def test_init_data2(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard(self.cat1, self.cat2)

#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#           (self.cat2.key, self.cat2),
#       ]))

#   def test_init_data3(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard(self.cat2, self.cat1)

#       self.assertEqual(td.data, OrderedDict([
#           (self.cat2.key, self.cat2),
#           (self.cat1.key, self.cat1),
#       ]))

#   def test_add_category(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard()

#       td.add_category(self.cat1)
#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#       ]))

#       td.add_category(self.cat1)
#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#       ]))

#       td.add_category(self.cat2)
#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#           (self.cat2.key, self.cat2),
#       ]))

#       td.add_category(self.cat1)
#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#           (self.cat2.key, self.cat2),
#       ]))

#       td.add_category(self.cat2)
#       self.assertEqual(td.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#           (self.cat2.key, self.cat2),
#       ]))

#   def test_key(self):
#       class TestDashboard(Dashboard):
#           name = "Test"
#           slug = "test"
#       td = TestDashboard()
#       self.assertEqual(td.key, "test")

#   def test_merge(self):
#       class TestDashboard1(Dashboard):
#           name = "Test1"
#           slug = "test1"
#       class TestDashboard2(Dashboard):
#           name = "Test1"
#           slug = "test1"

#       td1 = TestDashboard1()
#       td2 = TestDashboard2()
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict())

#       td1 = TestDashboard1()
#       td2 = TestDashboard2(self.cat1)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#       ]))

#       td1 = TestDashboard1(self.cat1)
#       td2 = TestDashboard2(self.cat2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           (self.cat1.key, self.cat1),
#           (self.cat2.key, self.cat2),
#       ]))

#       td1 = TestDashboard1(self.cat2)
#       td2 = TestDashboard2(self.cat2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           (self.cat2.key, self.cat2),
#       ]))

#       td1 = TestDashboard1(self.cat2, self.cat1)
#       td2 = TestDashboard2(self.cat2)
#       td1.merge(td2)
#       self.assertEqual(td1.data, OrderedDict([
#           (self.cat2.key, self.cat2),
#           (self.cat1.key, self.cat1),
#       ]))

#   def test_bool(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard()
#       self.assertFalse(td)
#       td.add_category(self.cat1)
#       self.assertTrue(td)

#   def test_len(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"

#       td = TestDashboard()
#       self.assertEqual(len(td), 0)

#       td = TestDashboard(self.cat1, self.cat2)
#       self.assertEqual(len(td), 2)

#   def test_eq(self):
#       class TestDashboard1(Dashboard):
#           name = "test1"
#           slug = "test1"
#       class TestDashboard2(Dashboard):
#           name = "test2"
#           slug = "test2"
#       class TestDashboard3(Dashboard):
#           name = "test1"
#           slug = "test1"

#       td1 = TestDashboard1()
#       td2 = TestDashboard2()
#       td3 = TestDashboard3()

#       self.assertEqual(td1, td3)
#       self.assertNotEqual(td1, td2)
#       self.assertNotEqual(td1, self.cat1)

#   def test_contains(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard(self.cat1)
#       self.assertFalse('test2' in td)
#       self.assertFalse(self.cat2 in td)
#       self.assertTrue('test1' in td)
#       self.assertTrue(self.cat1 in td)

#   def test_getitem(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"
#       td = TestDashboard(self.cat1, self.cat2)

#       self.assertEqual(td['test1'], self.cat1)
#       self.assertEqual(td['test2'], self.cat2)

#       with self.assertRaises(KeyError):
#           test = td['test3']

#   def test_iter(self):
#       class TestDashboard(Dashboard):
#           name = "test"
#           slug = "test"

#       td = TestDashboard(self.cat1, self.cat2)
#       self.assertEqual([i for i in td], [self.cat1, self.cat2])

#       td = TestDashboard(self.cat2, self.cat1)
#       self.assertEqual([i for i in td], [self.cat2, self.cat1])
