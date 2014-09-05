import datetime
from mock import Mock
from pylons import config
from hamcrest import *
from joj.tests import *
from joj.services.file_server_client import FileServerClient
from joj.model.non_database.driving_data_file_location_validator import DrivingDataFileLocationValidator

EXISTING_FILE = "model_runs/data/WATCH_2D/driving/Wind_WFD/Wind_WFD.ncml"
NON_EXISTING_FILE = "this_doesntexist"


class TestDrivingDataFileLocationChecker(TestController):

    def setUp(self):
        self.file_server_client = FileServerClient()
        self.errors = {}
        self.driving_data_file_location_validator = DrivingDataFileLocationValidator(self.errors, self.file_server_client)

    def test_GIVEN_no_parameters_WHEN_check_THEN_no_errors(self):
        params = {}

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(0), "results count")

    def test_GIVEN_valid_land_frac_file_WHEN_check_THEN_no_errors_and_land_frac_file_returned(self):
        self.file_server_client.file_exists = Mock(return_value=True)
        expected_url = "expected base url"
        params = {'land_frac_file': expected_url}

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(1), "results count")
        assert_that(result[0].base_url, is_(expected_url), "url")

    def test_GIVEN_invalid_land_frac_file_WHEN_check_THEN_errors_and_no_land_frac_file_returned(self):
        params = {'land_frac_file': "invalid"}
        self.file_server_client.file_exists = Mock(return_value=False)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(1), "Errors count")
        assert_that(self.errors['land_frac_file'], is_("Please check, file does not exist"), "Error")
        assert_that(len(result), is_(0), "results count")

    def test_GIVEN_invalid_anc_and_mask_files_WHEN_check_THEN_errors_and_locations_file_returned(self):
        params = {
            'land_frac_file': "invalid",
            'latlon_file': "invalid",
            'frac_file': "invalid",
            'soil_props_file': "invalid",
            'region-4.path': "invalid",
            'region-2.path': "invalid"}

        self.file_server_client.file_exists = Mock(return_value=False)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(6), "Errors count")
        assert_that(len(result), is_(0), "results count")

    def test_GIVEN_valid_driving_data_file_variable_templating_only_WHEN_check_THEN_no_errors_and_locations_returned(self):
        template = "template"
        drive_file = "valid{0}_{0}"
        params = {
            'drive_file': drive_file.format("%vv"),
            'drive_var_-2.templates': template}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(1), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(template)), "results count")

    def test_GIVEN_valid_driving_data_file_variable_templating_only_with_dates_WHEN_check_THEN_no_errors_and_locations_returned(self):
        template = "template"
        drive_file = "valid{0}_{0}"
        params = {
            'drive_file': drive_file.format("%vv"),
            'drive_var_-2.templates': template,
            'driving_data_start': datetime.datetime(2000, 1, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2002, 1, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(1), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(template)), "results count")


    def test_GIVEN_valid_driving_data_file_time_in_years_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{0}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y4"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 1, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2002, 1, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(3), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 2000)), "url 0")
        assert_that(result[1].base_url, is_(drive_file.format(var_template, 2001)), "url 1")
        assert_that(result[2].base_url, is_(drive_file.format(var_template, 2002)), "url 2")

    def test_GIVEN_valid_driving_data_file_time_in_2_year_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{0}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 1, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2002, 1, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(3), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 00)), "url 0")
        assert_that(result[1].base_url, is_(drive_file.format(var_template, 01)), "url 1")
        assert_that(result[2].base_url, is_(drive_file.format(var_template, 02)), "url 2")

    def test_GIVEN_valid_driving_data_file_time_with_year_and_month_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2", "%m2"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 9, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2000, 11, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(3), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 00, "09")), "url 0")
        assert_that(result[1].base_url, is_(drive_file.format(var_template, 00, 10)), "url 1")
        assert_that(result[2].base_url, is_(drive_file.format(var_template, 00, 11)), "url 2")

    def test_GIVEN_valid_driving_data_file_time_with_no_year_and_month_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned_but_months_not_templated(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "2000", "%m2"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 9, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2000, 11, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(1), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 2000, "%m2")), "url 0")

    def test_GIVEN_invalid_driving_data_file_time_in_years_and_variable_templating_WHEN_check_THEN_one_errors_and_no_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{0}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y4"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 1, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2002, 1, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=False)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(1), "Errors count")
        assert_that(self.errors['drive_var_-2.templates'], is_("Please check, file does not exist"), "Error")
        assert_that(len(result), is_(0), "results count")

    def test_GIVEN_valid_driving_data_file_time_with_year_and_month1_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2", "%m1"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(2000, 9, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2000, 11, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(3), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 00, "9")), "url 0")
        assert_that(result[1].base_url, is_(drive_file.format(var_template, 00, 10)), "url 1")
        assert_that(result[2].base_url, is_(drive_file.format(var_template, 00, 11)), "url 2")

    def test_GIVEN_valid_driving_data_file_time_with_year_and_month_c_and_variable_templating_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2", "%mc"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(1999, 12, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2000, 2, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(3), "results count")
        assert_that(result[0].base_url, is_(drive_file.format(var_template, 99, "dec")), "url 0")
        assert_that(result[1].base_url, is_(drive_file.format(var_template, 00, "jan")), "url 1")
        assert_that(result[2].base_url, is_(drive_file.format(var_template, 00, "feb")), "url 2")

    def test_GIVEN_valid_driving_data_file_time_with_year_and_month_c_and_variable_templating_over_couple_of_years_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2", "%mc"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(1999, 1, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2001, 12, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(36), "results count")

    def test_GIVEN_valid_driving_data_file_time_with_year_and_month_c_and_variable_templating_over_couple_of_years_WHEN_check_THEN_no_errors_and_locations_returned(self):
        time_template = "time template"
        var_template = "var template"
        drive_file = "valid_{1}_{0}_{2}_{1}"
        params = {
            'drive_file': drive_file.format("%vv", "%y2", "%mc"),
            'drive_var_-2.templates': var_template,
            'driving_data_start': datetime.datetime(1999, 4, 1, 2, 1, 1),
            'driving_data_end': datetime.datetime(2001, 4, 1, 2, 1, 1)}

        self.file_server_client.file_exists = Mock(return_value=True)

        result = self.driving_data_file_location_validator.get_file_locations(params)

        assert_that(len(self.errors), is_(0), "Errors count")
        assert_that(len(result), is_(25), "results count")