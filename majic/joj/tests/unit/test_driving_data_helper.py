"""
header
"""
import datetime
from hamcrest import assert_that, is_
from mock import Mock
from joj.services.job_runner_client import JobRunnerClient
from joj.services.tests.base import BaseTest
from joj.utils.driving_data_controller_helper import DrivingDataParsingException, DrivingDataControllerHelper


class TestDrivingDataHelper(BaseTest):
    def setUp(self):
        super(TestDrivingDataHelper, self).setUp()
        self.mock_job_runner_client = Mock(JobRunnerClient)
        self.mock_job_runner_client.open_file = Mock()
        self.mock_job_runner_client.append_to_file = Mock()
        self.mock_job_runner_client.delete_file = Mock()
        self.mock_job_runner_client.close_file = Mock()
        self.driving_data_helper = DrivingDataControllerHelper(job_runner_client=self.mock_job_runner_client)
        self.start_date = datetime.datetime(2012, 1, 1, 0, 0, 0)
        self.end_date = datetime.datetime(2012, 1, 1, 2, 0, 0)

    def test_GIVEN_valid_file_WHEN_parse_THEN_accepted_and_properties_correct(self):
        file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                        "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n",
                        "# i   i  i  i    i   i     i      i\n",
                        "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                        "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                        "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                        "# ----- data for later times ----"]

        self.driving_data_helper._process_driving_data_file(file_content, self.start_date, self.end_date, 1)

        assert_that(self.driving_data_helper.var_list, is_(['sw_down', 'lw_down', 'tot_rain',
                                                            'tot_snow', 't', 'wind', 'pstar', 'q']))
        assert_that(self.driving_data_helper.n_lines, is_(3))
        assert_that(self.driving_data_helper.interp_list, is_(8 * ['i']))

        assert self.driving_data_helper.job_runner_client.start_new_file.called
        assert self.driving_data_helper.job_runner_client.append_to_file.called
        assert self.driving_data_helper.job_runner_client.close_file.called

    def test_GIVEN_file_with_missing_header_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)

    def test_GIVEN_file_with_too_few_interps_in_header_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n",
                                "# i   i  i  i    i   i     i\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)

    def test_GIVEN_file_with_invalid_interps_in_header_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n",
                                "# i   i  i  i    i   i  x   i\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)

    def test_GIVEN_file_with_invalid_vars_in_header_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "# sw_down   lw_down  xxx  tot_snow    t   wind     pstar      q\n",
                                "# i   i  i  i    i   i   i   i\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)

    def test_GIVEN_file_with_two_few_numbers_in_row_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n",
                                "# i   i  i  i    i   i     i      i\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)

    def test_GIVEN_file_with_invalid_number_in_data_WHEN_parse_THEN_raises_DrivingDataParsingException(self):
        with self.assertRaises(DrivingDataParsingException):
            bad_file_content = ["# solar   long  rain  snow    temp   wind     press      humid\n",
                                "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n",
                                "# i   i  i  i    i   i     i      i\n",
                                "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n",
                                "89.5  185.8   0.0   0.0  259.45  apple  102401.9  1.357E-03\n",
                                "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n",
                                "# ----- data for later times ----"]
            self.driving_data_helper._process_driving_data_file(bad_file_content, self.start_date, self.end_date, 1)
