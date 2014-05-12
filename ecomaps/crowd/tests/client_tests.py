from ecomaps.crowd.client import CrowdClient, SessionNotFoundException, ClientException, AuthenticationFailedException

__author__ = 'Phil Jenkins (Tessella)'

import unittest

class CrowdClientTests(unittest.TestCase):

    client = None

    def user_credentials(self):

        if self.client.crowd_api == 'http://crowd.ceh.ac.uk:8095/crowd/rest/usermanagement/latest/':
            return 'philip.jenkins@tessella.com', 'DrJ1jZlT62VQUg49]8ez'
        else:
            return 'crowd-admin', 'pa55word'

    def setUp(self):

        self.client = CrowdClient(api_url="http://localhost:8095/crowd/rest/usermanagement/latest/",
                                 app_name="ecomaps",
                                 app_pwd="ecomaps")

        # self.client = CrowdClient(api_url="http://crowd.ceh.ac.uk:8095/crowd/rest/usermanagement/latest/",
        #                           app_name="ecomaps-dev",
        #                           app_pwd="3WY7i1eIhl8Lzy2tr77f")

    def test_client_can_be_instantiated(self):

        self.assertNotEqual(self.client, None)

    def test_authentication_with_valid_credentials(self):

        self.client.check_authenticated(*self.user_credentials())

    def test_user_session_request_with_valid_credentials(self):

        self.client.create_user_session(*self.user_credentials(), remote_addr="80.252.78.170")

    def test_user_session_request_with_invalid_credentials(self):

        self.assertRaises(AuthenticationFailedException, lambda:self.client.create_user_session("crowd-admin", "sddfghfh", "127.0.0.1"))

    def test_duff_token(self):

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session("abc123"))

    def test_proper_token(self):

        response = self.client.create_user_session(*self.user_credentials(), remote_addr="80.252.78.170")
        obj = self.client.verify_user_session(response['token'])

        self.assertNotEqual(obj, None)

    def test_delete_session_invalidates_as_expected(self):

        response = self.client.create_user_session(*self.user_credentials(), remote_addr="80.252.78.170")
        obj = self.client.verify_user_session(response['token'])

        # Delete the session
        self.client.delete_session(response['token'])

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session(response['token']))

    def test_get_user_info_returns_populated_object(self):

        username = self.user_credentials()[0]

        user = self.client.get_user_info(username)

        self.assertEqual(username, user['name'])

    def test_create_user(self):

        username = '3tnmjrtlkg8df9gjdf9'

        try:
            self.client.delete_user(username)
        except ClientException:
            pass

        u = self.client.create_user(username,
                                    'Test',
                                    'User',
                                    'test@test.com',
                                    'pa55word')

        try:
            self.client.delete_user(username)
        except ClientException:
            pass

def main():
    unittest.main()

if __name__ == '__main__':
    main()
