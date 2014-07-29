"""
# header
"""
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from pylons import config
from joj.model import session_scope, Session, User, AccountRequest


class TestAdminUserCreatedFromRequest(TestController):

    def setUp(self):
        super(TestAdminUserCreatedFromRequest, self).setUp()
        self.clean_database()

    def _create_account_request(self):
        with session_scope() as session:
            self.account_request = AccountRequest()
            self.account_request.email = "test@test.com"
            self.account_request.institution = "institution"
            self.account_request.name = "name"
            self.account_request.usage = "usage"
            session.add(self.account_request)

    def test_GIVEN_not_logged_in_WHEN_edit_THEN_redirects(self):
        response = self.app.get(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )
        assert_that(response.status_code, is_(302), "Response is redirect")

    def test_GIVEN_non_admin_WHEN_edit_THEN_returns_error(self):
        self.login()
        response = self.app.get(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )
        assert_that(response.normal_body, contains_string("Not found"))

    def test_GIVEN_admin_and_no_requests_WHEN_view_THEN_page_shows_none(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        response = self.app.get(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )

        assert_that(response.normal_body, contains_string("Account Requests"))
        assert_that(response.normal_body, contains_string("No requests outstanding"))

    def test_GIVEN_admin_and_one_requests_WHEN_view_THEN_page_shows_request(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        self._create_account_request()


        response = self.app.get(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )

        assert_that(response.normal_body, contains_string(self.account_request.usage))
        assert_that(response.normal_body, contains_string(self.account_request.name))
        assert_that(response.normal_body, contains_string(self.account_request.institution))
        assert_that(response.normal_body, contains_string(self.account_request.email))
