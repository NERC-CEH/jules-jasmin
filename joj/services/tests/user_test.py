from mock import MagicMock, ANY
from joj.model import User
from joj.services.tests.base import BaseTest
from joj.services.user import UserService


class UserServiceTest(BaseTest):

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