# header
from hamcrest import *
from pylons import url

from tests import TestController


class AccountRequestControllerTest(TestController):

    def setUp(self):
        self.app.extra_environ['REMOTE_USER'] = str("username")

    def test_GIVEN_empty_name_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'',
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter a name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))


    def test_GIVEN_missing_name_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter a name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_email_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter an email"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_email_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter an email"))

    def test_GIVEN_invalid_email_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'this.is.not.an.email',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter a valid email"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_institution_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'institution': u'',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter your institution"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_institution_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'usage': u'usage',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please enter your institution"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_usage_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'usage': u'',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please describe how you will use Majic"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_usage_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'license': u'1'
            }
        )
        assert_that(response.normal_body, contains_string("Please describe how you will use Majic"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_unaccepted_license_WHEN_submitted_THEN_returns_error(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'institution': u'hydrology',
            }
        )
        assert_that(response.normal_body, contains_string("You must agree to the Majic license"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_valid_parameters_WHEN_submitted_THEN_redirected(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params={
                'name': u'name',
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
            }
        )
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Account Requested"))