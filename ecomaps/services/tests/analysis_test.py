from mock import MagicMock, ANY
from ecomaps.model import Analysis
from ecomaps.services.tests.base import BaseTest
from ecomaps.services.analysis import AnalysisService
from ecomaps.model import Dataset
import os

__author__ = 'Chirag Mistry (Tessella)'

class AnalysisServiceTest(BaseTest):

    sample_analysis = None

    def setUp(self):

        super(AnalysisServiceTest, self).setUp()

        self.sample_analysis = Analysis()
        self.sample_analysis.name = 'Test User'
        self.sample_analysis.user_id  = 1
        self.sample_analysis.point_data_dataset_id = 2
        self.sample_analysis.coverage_dataset_ids = ['1_LandCover','3_LandCover']
        self.sample_analysis.parameters = []
        self.sample_analysis.id = 12
        self.sample_analysis.input_hash = 12345
        self.sample_analysis.model_id = 1
        self.sample_analysis.description = 'Analysis for testing purposes'

        results_dataset = Dataset()
        results_dataset.type = 'Result'
        results_dataset.viewable_by_user_id = 1
        results_dataset.name = 'Example Results Dataset 1'

        self.sample_analysis.result_dataset = results_dataset


    def test_create_analysis(self):
        # Important - don't instantiate the mock class,
        # as the session creation function in the service
        # will do that for us

        self._mock_session.add = MagicMock()
        self._mock_session.commit = MagicMock()
        time_indicies = {}

        analysis_service = AnalysisService(self._mock_session)
        analysis_service.create(self.sample_analysis.name,
                                self.sample_analysis.point_data_dataset_id,
                                self.sample_analysis.coverage_dataset_ids,
                                self.sample_analysis.user_id,
                                self.sample_analysis.unit_of_time,
                                self.sample_analysis.random_group,
                                self.sample_analysis.model_variable,
                                self.sample_analysis.data_type,
                                self.sample_analysis.model_id,
                                self.sample_analysis.description,
                                self.sample_analysis.input_hash,
                                time_indicies)

        self._mock_session.add.assert_called_once_with(ANY)
        self._mock_session.commit.assert_called_once_with()

    def test_publish_analysis(self):

        mock_query_result = MagicMock()
        mock_query_result.one = MagicMock(return_value=self.sample_analysis)

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        analysis_service = AnalysisService(self._mock_session)
        analysis_service.publish_analysis(self.sample_analysis.id)

        self.assertEqual(self.sample_analysis.viewable_by, None)
        self.assertEqual(self.sample_analysis.result_dataset.viewable_by_user_id, None)

    def test_get_ncdf_file(self):

        url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'
        analysis_service = AnalysisService()
        results_file = analysis_service.get_netcdf_file(url)

        # Check HTTP status code of the object returned:
        #    200 indicates a successful request.
        self.assertEqual(results_file.getcode(), 200)

    def test_delete_private_analysis(self):

        mock_query_result = MagicMock()
        mock_query_result.one = MagicMock(return_value=self.sample_analysis)

        mock_query = MagicMock()
        mock_query.filter = MagicMock()
        mock_query.filter.return_value = mock_query_result

        self._mock_session.query = MagicMock()
        self._mock_session.query.return_value = mock_query

        analysis_service = AnalysisService(self._mock_session)
        analysis_service.delete_private_analysis(self.sample_analysis.id)

        self.assertEqual(self.sample_analysis.deleted, True)