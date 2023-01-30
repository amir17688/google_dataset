import unittest
from mock import Mock

from contextio.lib.resources.oauth_provider import OauthProvider


class TestOauthProvider(unittest.TestCase):
    def test_constructor_creates_message_object_with_all_attributes_in_keys_list(self):
        oauth_provider = OauthProvider(Mock(), {"provider_consumer_key": "foobar"})

        self.assertTrue(hasattr(oauth_provider, "type"))
        self.assertTrue(hasattr(oauth_provider, "provider_consumer_key"))
        self.assertTrue(hasattr(oauth_provider, "provider_consumer_secret"))
        self.assertTrue(hasattr(oauth_provider, "resource_url"))
