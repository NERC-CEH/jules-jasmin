"""
# header
"""
from urlparse import urlparse
from hamcrest import *
from joj.tests import *
from joj.utils import constants, utils
from pylons import config
from joj.model import session_scope, Session, User, AccountRequest


class TestAdminUserCreatedFromRequest(TestController):

    def setUp(self):
        super(TestAdminUserCreatedFromRequest, self).setUp()
        self.clean_database()

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
        self.create_account_request()


        response = self.app.get(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )

        assert_that(response.normal_body, contains_string(self.account_request.usage))
        assert_that(response.normal_body, contains_string(self.account_request.first_name))
        assert_that(response.normal_body, contains_string(self.account_request.last_name))
        assert_that(response.normal_body, contains_string(self.account_request.institution))
        assert_that(response.normal_body, contains_string(self.account_request.email))

    def test_GIVEN_admin_and_post_reject_no_id_WHEN_view_THEN_redirect_nothing_changes(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        self.create_account_request()
        response = self.app.post(
            url=url(controller='user', action='requests'),
            expect_errors=True
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).count(), is_(1), "Number of user accounts")

    def test_GIVEN_admin_and_post_reject_with_id_no_accept_or_reject_WHEN_view_THEN_redirect_nothing_changes(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).count(), is_(1), "Number of user accounts")

    def test_GIVEN_admin_and_id_but_not_accept_or_reject_or_ignore_WHEN_view_THEN_redirect_nothing_changes(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True,
            params={'action': 'not accept'}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).count(), is_(1), "Number of user accounts")

    def test_GIVEN_admin_WHEN_reject_THEN_redirect_user_account_not_setup_request_deleted(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id_to_keep = self.create_account_request()
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True,
            params={
                'action': u'reject',
                'reason': u'a reason'}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).one().id, is_(request_id_to_keep), "Id left is one to keep")
            assert_that(session.query(User).count(), is_(2), "Only two users core and test in the users table")

    def test_GIVEN_admin_and_no_reason_WHEN_reject_THEN_redirect_user_account_no_request_deleted(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True,
            params={
                'action': u'reject',
                'reason': u'  '}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).one().id, is_(request_id), "Request is kept")
            assert_that(session.query(User).count(), is_(2), "Only two users core and test in the users table")

    def test_GIVEN_admin_and_non_existant_id_WHEN_reject_THEN_redirect_user_account_no_request_deleted(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id + 200),
            expect_errors=True,
            params={
                'action': u'reject',
                'reason': u'A valid reason'}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).one().id, is_(request_id), "Request is kept")

    def test_GIVEN_admin_and_already_existing_account_WHEN_accept_THEN_redirect_user_account_exists(self):
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id = self.create_account_request(user.username)

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True,
            params={
                'action': u'accept',
                'reason': u'  '}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).count(), is_(0), "Request is deleted")
            user = session.query(User).filter(User.username == self.account_request.email).one()

    def test_GIVEN_admin_WHEN_ignore_THEN_redirect_user_account_not_setup_request_deleted(self):
        self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)
        request_id_to_keep = self.create_account_request()
        request_id = self.create_account_request()

        response = self.app.post(
            url=url(controller='user', action='requests', id=request_id),
            expect_errors=True,
            params={
                'action': u'ignore',
                'reason': u''}
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='user', action='requests')), "url")
        with session_scope() as session:
            assert_that(session.query(AccountRequest).one().id, is_(request_id_to_keep), "Id left is one to keep")
            assert_that(session.query(User).count(), is_(2), "Only two users core and test in the users table")
