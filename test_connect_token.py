from mock import Mock
import unittest

from contextio.lib.resources.account import Account
from contextio.lib.resources.user import User
from contextio.lib.resources.connect_token import ConnectToken

class TestConnectToken(unittest.TestCase):
    def test_constructor_creates_connect_token_object_with_all_attributes_in_keys_list(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token"})

        self.assertTrue(hasattr(connect_token, "token"))
        self.assertTrue(hasattr(connect_token, "email"))
        self.assertTrue(hasattr(connect_token, "created"))
        self.assertTrue(hasattr(connect_token, "used"))
        self.assertTrue(hasattr(connect_token, "expires"))
        self.assertTrue(hasattr(connect_token, "callback_url"))
        self.assertTrue(hasattr(connect_token, "first_name"))
        self.assertTrue(hasattr(connect_token, "last_name"))
        self.assertTrue(hasattr(connect_token, "account"))
        self.assertTrue(hasattr(connect_token, "user"))

    def test_constructor_creates_Account_resource_on_ConnectToken_instance_if_account_is_dict_with_id(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token", "account": {"id": "fake_id"}})

        self.assertIsInstance(connect_token.account, Account)

    def test_constructor_creates_Account_resource_on_ConnectToken_instance_if_account_is_string(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token", "account": "fake_id"})

        self.assertIsInstance(connect_token.account, Account)
        self.assertEqual(connect_token.account.id, "fake_id")
        self.assertIsNone(connect_token.user)

    def test_constructor_creates_User_resource_on_ConnectToken_instance_if_user_is_not_None(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token", "user": {"id": "fake_id"}})

        self.assertIsInstance(connect_token.user, User)
        self.assertEqual(connect_token.user.id, "fake_id")
        self.assertIsNone(connect_token.account)

    def test_constructor_sets_account_attribute_to_none_if_empty_dict(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token", "account": {}})

        self.assertEqual(None, connect_token.account)

    def test_constructor_sets_user_attribute_to_none_if_not_in_response(self):
        connect_token = ConnectToken(Mock(spec=[]), {"token": "fake_token"})

        self.assertEqual(None, connect_token.account)
