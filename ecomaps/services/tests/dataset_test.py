from mock import MagicMock, ANY
from ecomaps.model import Dataset, DatasetType
from ecomaps.services.dataset import DatasetService
from ecomaps.services.tests.base import BaseTest

__author__ = 'Phil Jenkins (Tessella)'


class DatasetServiceTest(BaseTest):

    def test_get_datasets_for_user(self):

        mock_query_result = MagicMock()
        mock_query_result.all = MagicMock()

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        service = DatasetService(self._mock_session)
        service.get_datasets_for_user(1234, dataset_type_id=1)

        self._mock_session.query.assert_called_once_with(Dataset)
        mock_query.filter.assert_called_once_with(ANY, ANY)
        mock_query_result.all.assert_called_once_with()

    def test_get_dataset_types(self):

        mock_query = MagicMock()
        mock_query.all = MagicMock()

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        service = DatasetService(self._mock_session)
        service.get_dataset_types()

        self._mock_session.query.assert_called_once_with(DatasetType)
        mock_query.all.assert_called_once_with()