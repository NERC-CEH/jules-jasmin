# header
from hamcrest import *
from joj.model import session_scope, Session, AccountRequest

from joj.tests import *

class TestAccountRequestController(TestController):

    def setUp(self):
        super(TestAccountRequestController, self).setUp()
        self.clean_database()
        self.account_request = {
                'first_name': u'name',
                'last_name': u'last name',
                'email': u'email@domain.com',
                'institution': u'hydrology',
                'usage': u'usage',
                'license': u'1'
                }

    def test_GIVEN_empty_first_name_WHEN_submitted_THEN_returns_error(self):
        self.account_request['first_name'] = ''
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter a first name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))


    def test_GIVEN_missing_first_name_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['first_name']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter a first name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_last_name_WHEN_submitted_THEN_returns_error(self):
        self.account_request['last_name'] = ''
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter a last name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_last_name_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['last_name']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter a last name"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_email_WHEN_submitted_THEN_returns_error(self):
        self.account_request['email'] = ''
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter an email"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_email_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['email']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter an email"))

    def test_GIVEN_invalid_email_WHEN_submitted_THEN_returns_error(self):
        self.account_request['email'] = 'this.is.not.an.email'
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter a valid email"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_institution_WHEN_submitted_THEN_returns_error(self):
        self.account_request['institution'] = ''
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter your institution"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_institution_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['institution']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please enter your institution"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_empty_usage_WHEN_submitted_THEN_returns_error(self):
        self.account_request['usage'] = ''
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please describe how you will use Majic"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_missing_usage_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['usage']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("Please describe how you will use Majic"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_unaccepted_license_WHEN_submitted_THEN_returns_error(self):
        del self.account_request['license']
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        assert_that(response.normal_body, contains_string("You must agree to the Majic license"))
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Request a Majic Account"))

    def test_GIVEN_valid_parameters_WHEN_submitted_THEN_success(self):
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        # Check we are still on the request account form and have not been redirected
        assert_that(response.normal_body, contains_string("Account Requested"))

    def test_GIVEN_valid_parameters_WHEN_submitted_THEN_request_in_database(self):
        with session_scope(Session) as session:
            session.query(AccountRequest).delete()
        response = self.app.post(
            url=url(controller='request_account', action='request'),
            params=self.account_request
        )
        with session_scope(Session) as session:
            account_requests = session.query(AccountRequest).all()
        assert_that(len(account_requests), is_(1))
        assert_that(account_requests[0].first_name, is_('name'))