from hamcrest import *
from crowd.crowd_client_factory import CrowdClientFactory
from joj.crowd.client import ClientException, CrowdClient
from joj.model import session_scope
from mock import *
from joj.model import User
from joj.services.tests.base import BaseTest
from joj.services.user import UserService
from joj.tests import TestController
from joj.services.email_service import EmailService
from joj.services.general import ServiceException

class UserServiceTest(TestController):

    _mock_session = None

    def setUp(self):
        super(UserServiceTest, self).setUp()
        self._mock_session = Mock

    def test_create_user(self):

        # Important - don't instantiate the mock class,
        # as the session creation function in the service
        # will do that for us

        sample_user = User()
        sample_user.username = 'testuser'
        sample_user.name = 'Test User'
        sample_user.email = 'testuser@test.com'
        sample_user.access_level = 'External'
        sample_user.first_name = "first_name"
        sample_user.last_name = "last_name"
        sample_user.storage_quota_in_gb = 89

        self._mock_session.add = MagicMock()
        self._mock_session.commit = MagicMock()

        user_service = UserService(self._mock_session)
        user_service.create(sample_user.username,
                            sample_user.first_name,
                            sample_user.last_name,
                            sample_user.email,
                            sample_user.access_level)

        self._mock_session.add.assert_called_once_with(ANY)
        self._mock_session.commit.assert_called_once_with()

    def test_get_user_by_username(self):

        mock_query_result = MagicMock()
        mock_query_result.one = MagicMock()

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        username = 'testuser'

        user_service = UserService(self._mock_session)
        user_service.get_user_by_username(username)

        self._mock_session.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once_with(ANY)
        mock_query_result.one.assert_called_once_with()

    def test_get_all_users(self):

        mock_query = MagicMock()

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        user_service = UserService(self._mock_session)
        user_service.get_all_users()

        self._mock_session.query.assert_called_once_with(User)

    def test_GIVEN_user_WHEN_forget_password_THEN_password_forgotten_set(self):

        user = self.login()
        email_service = Mock(EmailService)
        user_service = UserService(email_service=email_service)

        link = user_service.set_forgot_password(user.id)

        with session_scope() as session:
            user = session.query(User).get(user.id)
            assert_that(user.forgotten_password_uuid, is_not(None), "forgotten password uuid set")
            assert_that(user.forgotten_password_expiry_date, is_not(None), "forgotten password expiry date set")
            assert_that(link, contains_string(user.forgotten_password_uuid), "UUID is in link")
            assert_that(email_service.send_email.called, is_(False), "email sent")

    def test_GIVEN_user_WHEN_forget_password_and_send_mail_THEN_password_forgotten_set_and_email_sent(self):

        user = self.login()
        email_service = Mock(EmailService)
        user_service = UserService(email_service=email_service)

        link = user_service.set_forgot_password(user.id, send_email=True)

        with session_scope() as session:
            user = session.query(User).get(user.id)
            assert_that(user.forgotten_password_uuid, is_not(None), "forgotten password uuid set")
            assert_that(user.forgotten_password_expiry_date, is_not(None), "forgotten password expiry date set")
            assert_that(link, contains_string(user.forgotten_password_uuid), "UUID is in link")
            assert_that(link, contains_string(str(user.id)), "user id")
            assert_that(email_service.send_email.called, is_(True), "email sent")

    def test_GIVEN_user_and_non_matching_password_WHEN_password_set_THEN_error(self):

        user = self.login()
        user_service = UserService()

        with self.assertRaises(ServiceException, msg="Should have thrown a ServiceException exception"):
            user_service.reset_password(user.id, "password", "not password")

    def test_GIVEN_no_user_and_matching_password_WHEN_password_set_THEN_error(self):

        user_service = UserService()
        password = "password long"

        with self.assertRaises(ServiceException, msg="Should have thrown a ServiceException exception"):
            user_service.reset_password(-90, password, password)

    def test_GIVEN_user_and_short_password_WHEN_password_set_THEN_error(self):
        user = self.login()
        user_service = UserService()
        password = "123456789"

        with self.assertRaises(ServiceException, msg="Should have thrown a ServiceException exception"):
            user_service.reset_password(user.id, password, password)

    def test_GIVEN_user_and_password_WHEN_password_set_THEN_password_call_made_to_crowd_and_forgotten_password_blanked(self):
        user = self.login()
        crowd_client = Mock(CrowdClient)
        crowd_client_factory = CrowdClientFactory()
        crowd_client_factory.get_client = Mock(return_value=crowd_client)
        user_service = UserService(crowd_client_factory=crowd_client_factory)
        user_service.set_forgot_password(user.id)
        password = "1234567890"

        user_service.reset_password(user.id, password, password)

        assert_that(crowd_client.update_users_password.called, is_(True), "Crowd called to update user")
        user = user_service.get_user_by_id(user.id)
        assert_that(user.forgotten_password_uuid, is_(None), "uuid")
        assert_that(user.forgotten_password_expiry_date, is_(None), "expiry date")

    def test_GIVEN_user_and_password_WHEN_password_set_and_crowd_client_raises_THEN_forgotten_password_not_blanked_error(self):
        user = self.login()
        crowd_client = Mock(CrowdClient)
        crowd_client.update_users_password = Mock(side_effect=ClientException())
        crowd_client_factory = CrowdClientFactory()
        crowd_client_factory.get_client = Mock(return_value=crowd_client)
        user_service = UserService(crowd_client_factory=crowd_client_factory)
        user_service.set_forgot_password(user.id)
        password = "1234567890"

        with self.assertRaises(ServiceException, msg="Service exception not raise"):
            user_service.reset_password(user.id, password, password)

        user = user_service.get_user_by_id(user.id)
        assert_that(user.forgotten_password_uuid, is_not(None), "uuid")
        assert_that(user.forgotten_password_expiry_date, is_not(None), "expiry date")