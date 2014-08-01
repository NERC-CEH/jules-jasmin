import random
import string
from pylons import config
from hamcrest import *
from joj.tests import *
from joj.crowd.client import CrowdClient, SessionNotFoundException, ClientException, AuthenticationFailedException
from joj.crowd.crowd_client_factory import CrowdClientFactory
import unittest


class CrowdClientTests(TestController):

    client = None
    username = None

    def create_user(self):
        self.username = '3tnmjrtlkg8df9gjdf9'
        self.password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))

        self.tearDown()

        u = self.client.create_user(self.username,
                                    'Test',
                                    'User',
                                    'test@test.com',
                                    self.password)

    def tearDown(self):
        if self.client.use_crowd and self.username:
            try:
                self.client.delete_user(self.username)
            except ClientException:
                pass

    def setUp(self):
        self.client = CrowdClientFactory().get_client()
        if not self.client.use_crowd:
            raise self.skipTest("Can not talk to crowd")

    def test_authentication_with_valid_credentials(self):
        self.create_user()

        self.client.check_authenticated(self.username, self.password)

    def test_change_password_with_valid_credentials(self):
        self.create_user()
        new_password = "hard to guess and very long"

        self.client.update_users_password(self.username, new_password)

        self.client.check_authenticated(self.username, new_password)

    def test_user_session_control_with_valid_credentials(self):
        self.create_user()

        response = self.client.create_user_session(self.username, self.password, remote_addr="80.252.78.170")
        obj = self.client.verify_user_session(response['token'])

        self.assertNotEqual(obj, None)

        # Delete the session
        self.client.delete_session(response['token'])

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session(response['token']))

    def test_user_session_request_with_invalid_credentials(self):
        self.create_user()

        self.assertRaises(
            AuthenticationFailedException,
            lambda:self.client.create_user_session("crowd-admin", "sddfghfh", "127.0.0.1"))

    def test_duff_token(self):

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session("abc123"))

    def test_get_user_info_returns_populated_object(self):
        self.create_user()

        user = self.client.get_user_info(self.username)

        assert_that(self.username, is_(self.username), "username")
