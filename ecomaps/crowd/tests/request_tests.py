import unittest
from ecomaps.crowd.models import UserRequest

__author__ = 'Phil Jenkins (Tessella)'


class RequestTests(unittest.TestCase):

    def test_user_request_produces_valid_json(self):

        req = UserRequest()
        req.username = "Test User"
        req.password = "Password"
        req.remote_address = "127.0.0.1"

        self.assertEqual(req.to_json(),
                         '{"username": "%s", "password": "%s", '
                         '"validation-factors": {"validationFactors": [{"name": "remote_address", "value": "%s"}]}}'
                         % (req.username,req.password,req.remote_address),
                         'JSON does not match')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
