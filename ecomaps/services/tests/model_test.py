from ecomaps.model import Model
from mock import MagicMock, ANY
from ecomaps.services.model import ModelService
from ecomaps.services.tests.base import BaseTest

__author__ = 'Chirag Mistry (Tessella)'

class ModelServiceTest(BaseTest):

    sample_model = None

    def setUp(self):

        super(ModelServiceTest, self).setUp()

        self.sample_model = Model()
        self.sample_model.name = 'Test Model'
        self.sample_model.id = 1
        self.sample_model.description = 'Model for testing'
        self.sample_model.code_path = 'code_path'

    def test_get_model_by_id(self):
        """ Test if model can be found by id. Test just checks that the sqlalchemy is called.
        """

        mock_query_result = MagicMock()
        mock_query_result.one = MagicMock(return_value=self.sample_model)

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        model_service = ModelService(self._mock_session)
        model = model_service.get_model_by_id(1)

        self.assertEqual(model.id, 1)
        self.assertEqual(model.name, 'Test Model')
