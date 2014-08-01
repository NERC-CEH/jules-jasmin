"""
header
"""
import datetime
from hamcrest import is_, assert_that, contains_string
from mock import MagicMock
from joj.model import DrivingDataset, Session, session_scope, DrivingDatasetParameterValue, DrivingDatasetLocation
from joj.tests import TestController
from joj.utils.ascii_download_helper import AsciiDownloadHelper
from joj.utils import constants
from joj.services.model_run_service import ModelRunService
from joj.services.dataset import DatasetService
from joj.services.dap_client import DapClient
from joj.services.dap_client_factory import DapClientFactory


class TestAsciiDownloadHelper(TestController):

    def setUp(self):
        self.start_delta = datetime.timedelta(hours=1)
        self.end_delta = datetime.timedelta(hours=2)

        def _create_mock_dap_client(var_name):

            def _gtia(date):
                return date + self.start_delta

            def _gtib(date):
                return date - self.end_delta

            def _data(lat, lon, date):
                return len(var_name) * lat * lon + date.hour + 24 * date.day

            mock_dap_client = MagicMock()
            mock_dap_client.get_time_immediately_after = _gtia
            mock_dap_client.get_time_immediately_before = _gtib
            mock_dap_client.get_data_at = _data
            return mock_dap_client

        def _create_dap_client(url):
            if "file1" in url:
                return _create_mock_dap_client("variable1")
            elif "file2" in url:
                return _create_mock_dap_client("v2")

        mock_dap_client_factory = DapClientFactory()
        mock_dap_client_factory.get_dap_client = MagicMock(side_effect=_create_dap_client)

        self.download_helper = AsciiDownloadHelper(dap_client_factory=mock_dap_client_factory)
        self.model_run_service = ModelRunService()
        self.nvars = 2
        self.period = 3600
        with session_scope(Session) as session:
            driving_data = DrivingDataset()
            driving_data.name = "Test Driving Dataset"

            pv1 = DrivingDatasetParameterValue(self.model_run_service, driving_data,
                                               constants.JULES_PARAM_DRIVE_DATA_PERIOD, self.period)
            pv2 = DrivingDatasetParameterValue(self.model_run_service, driving_data,
                                               constants.JULES_PARAM_DRIVE_NVARS, self.nvars)
            pv3 = DrivingDatasetParameterValue(self.model_run_service, driving_data,
                                               constants.JULES_PARAM_DRIVE_VAR, "'var1'    'var2'")
            pv4 = DrivingDatasetParameterValue(self.model_run_service, driving_data,
                                               constants.JULES_PARAM_DRIVE_INTERP, "'i'    'nf'")
            ddl1 = DrivingDatasetLocation()
            ddl1.base_url = "data/file1.nc"
            ddl1.var_name = "var1"
            ddl1.driving_dataset = driving_data

            ddl2 = DrivingDatasetLocation()
            ddl2.base_url = "data/file2.nc"
            ddl2.var_name = "var2"
            ddl2.driving_dataset = driving_data

            session.add_all([driving_data])
        self.driving_data = DatasetService().get_driving_dataset_by_id(driving_data.id)

    def test_GIVEN_driving_date_name_etc_WHEN_get_filename_THEN_filename_returned(self):
        lat = 55
        lon = 1.5
        start = datetime.datetime(1900, 1, 1, 0, 0, 0)
        end = datetime.datetime(2000, 1, 1, 0, 0, 0)
        filename = self.download_helper.get_driving_data_filename(self.driving_data, lat, lon, start, end)
        expected_filename = "Test_Driving_Dataset_55_1.5_1900-01-01_2000-01-01"\
                            + constants.USER_DOWNLOAD_DRIVING_DATA_FILE_EXTENSION
        assert_that(filename, is_(expected_filename))

    def test_GIVEN_many_lines_WHEN_get_filesize_THEN_filesize_approximately_correct(self):
        start = datetime.datetime(1900, 1, 1, 0, 0, 0)
        end = datetime.datetime(2000, 1, 1, 0, 0, 0)

        nlines = (end - start).total_seconds() / self.period
        expected_size = 12.5 * self.nvars * nlines

        size = self.download_helper.get_driving_data_filesize(self.driving_data, start, end)
        # Check estimate within reasonable bounds (likely to vary with header etc)
        assert size < expected_size * 1.05
        assert size > expected_size * 0.95

    def test_GIVEN_dataset_locations_WHEN_get_file_gen_THEN_header_has_correct_datetimes(self):
        text = self.get_download_text_lines()
        assert_that(text[0], contains_string("1900-01-01 01:00"))
        assert_that(text[0], contains_string("1900-01-02 22:00"))

    def test_GIVEN_dataset_locations_WHEN_get_file_gen_THEN_header_has_correct_period(self):
        text = self.get_download_text_lines()
        assert_that(text[0], contains_string("3600"))
        assert_that(text[0], contains_string("1900-01-02 22:00"))

    def test_GIVEN_dataset_locations_WHEN_get_file_gen_THEN_header_has_var_names_and_interps(self):
        text = self.get_download_text_lines()
        assert_that(text[0], contains_string("var1\tvar2"))
        assert_that(text[0], contains_string("i\tnf"))

    def test_GIVEN_dataset_locations_WHEN_get_file_gen_THEN_file_has_expected_number_of_points(self):
        text = self.get_download_text_lines()
        actual_start = datetime.datetime(1900, 1, 1, 0, 0, 0) + self.start_delta
        actual_end = datetime.datetime(1900, 1, 3, 0, 0, 0) - self.end_delta
        delta = actual_end - actual_start
        expected_num = divmod(delta.total_seconds(), self.period)[0] + 1
        assert_that(len(text), is_(expected_num + 1))

    def test_GIVEN_dataset_locations_WHEN_get_file_gen_THEN_file_points_are_correct(self):
        # Here we're just checking that they the values returned are for the correct dataset and time,
        # rather than numerically correct since we just made them up in the mock. The mock method
        # dap_client.get_data(lat, lon, date) assures us that the first variable's numbers will be
        # larger than the second variables numbers, and also that both column's values should be
        # increasing with time. If these are true then we are calling the mock correctly.

        text = self.get_download_text_lines()
        for i in range(1, len(text)):
            col1, col2 = text[i].split()
            assert float(col1) > float(col2)
            if i > 1:
                prev_col1, prev_col2 = text[i-1].split()
                assert float(col1) > float(prev_col1)
                assert float(col2) > float(prev_col2)

    def get_download_text_lines(self):
        lat = 55
        lon = 1.5
        start = datetime.datetime(1900, 1, 1, 0, 0, 0)
        end = datetime.datetime(1900, 1, 3, 0, 0, 0)
        file_gen = self.download_helper.get_driving_data_file_gen(self.driving_data, lat, lon, start, end)
        text = []
        for line in file_gen:
            text.append(line)
        return text
