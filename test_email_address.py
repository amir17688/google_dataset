import unittest
from mock import Mock, patch

from contextio.lib.resources.email_address import EmailAddress


class TestEmailAddress(unittest.TestCase):
    def setUp(self):
        self.email_address = EmailAddress(Mock(), {"email": "fake@email.com", "primary": 1})

    def test_constructor_sets_attributes_on_object(self):
        self.assertTrue(hasattr(self.email_address, "email"))
        self.assertTrue(hasattr(self.email_address, "validated"))
        self.assertTrue(hasattr(self.email_address, "primary"))


    def test_constructor_allows_email_address_in_definition(self):
        email_address = EmailAddress(Mock(), {"email_address": "fake@email.com"})

        self.assertEqual("fake@email.com", email_address.email)

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_updates_primary_attribute_in_memory(self, mock_post):
        self.assertEqual(self.email_address.primary, 1)

        self.email_address.post(primary=0)

        self.assertEqual(self.email_address.primary, 0)

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_attempts_to_convert_string_input_to_int(self, mock_post):
        self.assertEqual(self.email_address.primary, 1)

        self.email_address.post(primary="0")

        self.assertEqual(self.email_address.primary, 0)

    def test_post_throws_error_if_unable_to_parse_int(self):
        self.assertEqual(self.email_address.primary, 1)

        with self.assertRaises(ValueError):
            self.email_address.post(primary="not_integer")
