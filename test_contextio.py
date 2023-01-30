import unittest
from contextio.contextio import ContextIO

from contextio.lib.v2_0 import V2_0
from contextio.lib.lite import Lite


class TestContextIOFactory(unittest.TestCase):
    def test_ContextIOFactory_returns_v2_0_instance_by_default(self):
        contextio = ContextIO(consumer_key="foo", consumer_secret="bar")

        self.assertIsInstance(contextio, V2_0)

    def test_ContextIOFactory_returns_Lite_instance(self):
        contextio = ContextIO(consumer_key="foo", consumer_secret="bar", api_version="lite")

        self.assertIsInstance(contextio, Lite)
