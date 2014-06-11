# header

from mock import MagicMock, ANY

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User
from joj.services.model_run_service import ModelRunService


class ModelRunServiceTest(BaseTest):

    def setUp(self):

        super(ModelRunServiceTest, self).setUp()

        self._mock_session.query = MagicMock()
        self.model_run_service = ModelRunService(self._mock_session)

    def test_GIVEN_no_model_runs_WHEN_get_model_list_THEN_empty_list_returned(self):

        mock_query_result = MagicMock()
        mock_query_result.all = MagicMock(return_value=[])

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result
        self._mock_session.query.return_value = mock_query

        user = User()
        models = self.model_run_service.get_models_for_user(user)

        assert_that(len(models), is_(0), "There should be no model for the user")
