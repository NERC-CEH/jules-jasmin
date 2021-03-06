"""
#header
"""
from urlparse import urlparse
import datetime
from hamcrest import assert_that, is_, contains_string, close_to
from pylons import url
from joj.model import DrivingDataset, Session, session_scope, ModelRun, ParameterValue
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from joj.utils.constants import *
from joj.services.dataset import DatasetService


class TestModelRunExtents(TestController):
    def setUp(self):
        super(TestModelRunExtents, self).setUp()
        self.clean_database()
        self.user = self.login()
        self.model_run_service = ModelRunService()
        with session_scope(Session) as session:
            self.driving_data = DrivingDataset()
            self.driving_data.name = "d1"
            self.driving_data.boundary_lat_north = 47.5
            self.driving_data.boundary_lat_south = 13.8
            self.driving_data.boundary_lon_east = 123.1
            self.driving_data.boundary_lon_west = -15.0
            self.driving_data.time_start = datetime.datetime(1901, 1, 1, 0, 0, 0)
            self.driving_data.time_end = datetime.datetime(2001, 1, 1, 0, 0, 0)
            session.add(self.driving_data)
            session.commit()

            self.model_run = ModelRun()
            self.model_run.name = "MR1"
            self.model_run.status = self._status(MODEL_RUN_STATUS_CREATED)
            self.model_run.driving_dataset_id = self.driving_data.id
            self.model_run.user = self.user
            self.model_run.science_configuration_id = 2

            param1 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_INTERP)
            pv1 = ParameterValue()
            pv1.parameter_id = param1.id
            pv1.set_value_from_python(8 * ['nf'])

            param2 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_PERIOD)
            pv2 = ParameterValue()
            pv2.parameter_id = param2.id
            pv2.set_value_from_python(60 * 60)

            self.model_run.parameter_values = [pv1, pv2]
            session.add(self.model_run)

    def set_up_single_cell_user_driving_data(self):
        self.clean_database()
        del self.driving_data
        self.user = self.login()
        user_upload_id = DatasetService().get_id_for_user_upload_driving_dataset()
        with session_scope(Session) as session:
            self.model_run = ModelRun()
            self.model_run.name = "MR1"
            self.model_run.status = self._status(MODEL_RUN_STATUS_CREATED)
            self.model_run.driving_dataset_id = user_upload_id
            self.model_run.user = self.user
            self.model_run.driving_data_lat = 25
            self.model_run.driving_data_lon = 40
            self.model_run.driving_data_rows = 248
            self.model_run.science_configuration_id = 2

            param1 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_INTERP)
            pv1 = ParameterValue()
            pv1.parameter_id = param1.id
            pv1.set_value_from_python(8 * ['nf'])

            param2 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_PERIOD)
            pv2 = ParameterValue()
            pv2.parameter_id = param2.id
            pv2.set_value_from_python(60 * 60)

            param3 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_START)
            pv3 = ParameterValue()
            pv3.parameter_id = param3.id
            pv3.value = "'1901-01-01 00:00:00'"

            param4 = self.model_run_service.get_parameter_by_constant(JULES_PARAM_DRIVE_DATA_END)
            pv4 = ParameterValue()
            pv4.parameter_id = param4.id
            pv4.value = "'1901-01-31 21:00:00'"

            self.model_run.parameter_values = [pv1, pv2, pv3, pv4]
            session.add(self.model_run)

    def test_GIVEN_no_created_model_WHEN_page_get_THEN_redirect_to_create(self):
        self.clean_database()
        self.login()
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_no_driving_dataset_selected_for_model_WHEN_page_get_THEN_redirect_to_driving_data(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        with session_scope(Session) as session:
            model_run.driving_dataset_id = None
            session.add(model_run)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='driving_data')), "url")

    def test_GIVEN_nothing_WHEN_page_get_THEN_extents_page_rendered(self):
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("Specify Model Run Extents"))
        self.assert_model_run_creation_action(self.user, 'extents')

    def test_GIVEN_driving_dataset_selected_for_model_WHEN_page_get_THEN_driving_data_spatial_extents_rendered(self):
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lat_north)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lat_south)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lon_east)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lon_west)))

    def test_GIVEN_driving_dataset_selected_for_model_WHEN_page_get_THEN_driving_data_temporal_extents_rendered(self):
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("1901-01-01"))
        assert_that(response.normal_body, contains_string("1911-01-01"))

    def test_GIVEN_multi_cell_spatial_extents_already_chosen_WHEN_page_get_THEN_existing_extents_rendered(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS, [12.3, 35.5], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS, [50, 70], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, True, self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("12.3"))
        assert_that(response.normal_body, contains_string("35.5"))
        assert_that(response.normal_body, contains_string("50"))
        assert_that(response.normal_body, contains_string("70"))

    def test_GIVEN_single_cell_spatial_extents_already_chosen_WHEN_page_get_THEN_existing_extents_rendered(self):
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, False, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_NPOINTS, 1, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_POINTS_FILE, [55, 12.3], self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("55"))
        assert_that(response.normal_body, contains_string("12.3"))

    def test_GIVEN_temporal_extents_already_chosen_WHEN_page_get_THEN_existing_extents_rendered(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS, [12.3, 35.5], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS, [50, 70], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, True, self.user)
        start_time = datetime.datetime(1935, 3, 5, 17, 12, 11)
        end_time = datetime.datetime(1969, 7, 21, 20, 17, 00)
        self.model_run_service.save_parameter(JULES_PARAM_RUN_START, start_time, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_RUN_END, end_time, self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string(start_time.strftime("%Y-%m-%d")))
        assert_that(response.normal_body, contains_string(end_time.strftime("%Y-%m-%d")))

    def test_GIVEN_invalid_multi_cell_spatial_extents_already_chosen_WHEN_page_get_THEN_errors_shown(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS, [40, 500], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS, [20, 25], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, True, self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("Longitude must be between -180 and 180"))

    def test_GIVEN_invalid_single_cell_spatial_extents_already_chosen_WHEN_page_get_THEN_errors_shown(self):
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, False, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_NPOINTS, 1, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_POINTS_FILE, [55, 593], self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("Longitude must be between -180 and 180"))

    def test_GIVEN_invalid_temporal_extents_already_chosen_WHEN_page_get_THEN_errors_shown(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS, [12.3, 35.5], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS, [50, 70], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_USE_SUBGRID, True, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LATLON_REGION, True, self.user)
        start_time = datetime.datetime(1900, 10, 14, 17, 12, 11)
        end_time = datetime.datetime(1969, 7, 21, 20, 17, 00)
        self.model_run_service.save_parameter(JULES_PARAM_RUN_START, start_time, self.user)
        self.model_run_service.save_parameter(JULES_PARAM_RUN_END, end_time, self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("Start date cannot be earlier than 1901-01-01"))

    def test_GIVEN_invalid_multi_cell_spatial_extents_WHEN_post_THEN_errors_rendered(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'multi',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 500,
                'start_date': '1940-10-13',
                'end_date': '1950-10-13'
            })
        assert_that(response.normal_body, contains_string("Longitude must be between -180 and 180"))

    def test_GIVEN_invalid_single_cell_spatial_extents_WHEN_post_THEN_errors_rendered(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'single',
                'lat': -88,
                'lon': 40,
                'start_date': '1940-10-13',
                'end_date': '1950-10-13'
            })
        assert_that(response.normal_body, contains_string("Latitude (-88 deg N) cannot be south of 13.8 deg N"))

    def test_GIVEN_invalid_temporal_extents_WHEN_post_THEN_errors_rendered(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'multi',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
                'start_date': '1900-10-14',
                'end_date': '1950-10-13'
            })
        assert_that(response.normal_body, contains_string("Start date cannot be earlier than 1901-01-01"))

    def test_GIVEN_valid_multi_cell_extents_WHEN_post_THEN_extents_saved(self):
        self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'multi',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
                'start_date': '1940-10-13',
                'end_date': '1950-10-13'
            })
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        lat_bounds = model_run.get_parameter_values(JULES_PARAM_LAT_BOUNDS)[0].value
        lon_bounds = model_run.get_parameter_values(JULES_PARAM_LON_BOUNDS)[0].value
        use_subgrid = model_run.get_parameter_values(JULES_PARAM_USE_SUBGRID)[0].value
        latlon_region = model_run.get_parameter_values(JULES_PARAM_LATLON_REGION)[0].value
        start_run = model_run.get_parameter_values(JULES_PARAM_RUN_START)[0].value
        end_run = model_run.get_parameter_values(JULES_PARAM_RUN_END)[0].value
        assert_that(lat_bounds, is_("20    25"))
        assert_that(lon_bounds, is_("35    40"))
        assert_that(use_subgrid, is_(".true."))
        assert_that(latlon_region, is_(".true."))
        assert_that(str(start_run), is_("'1940-10-13 00:00:00'"))
        assert_that(str(end_run), is_("'1950-10-13 23:00:00'"))  # Time is moved forward to match the acceptable end

    def test_GIVEN_valid_single_cell_extents_WHEN_post_THEN_extents_saved(self):
        self.set_up_single_cell_user_driving_data()
        self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'single',
                'lat': 25,
                'lon': 40,
                'start_date': '1901-01-4',
                'end_date': '1901-01-13',
                'average_over_cell': 1
            })
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        pointfile = model_run.get_parameter_values(JULES_PARAM_POINTS_FILE)[0].value
        n_points = model_run.get_parameter_values(JULES_PARAM_NPOINTS)[0].value
        use_subgrid = model_run.get_parameter_values(JULES_PARAM_USE_SUBGRID)[0].value
        latlon_region = model_run.get_parameter_values(JULES_PARAM_LATLON_REGION)[0].value
        l_point_data = model_run.get_parameter_values(JULES_PARAM_SWITCHES_L_POINT_DATA)[0].value
        start_run = model_run.get_parameter_values(JULES_PARAM_RUN_START)[0].value
        end_run = model_run.get_parameter_values(JULES_PARAM_RUN_END)[0].value
        assert_that(pointfile, is_("25    40"))
        assert_that(n_points, is_("1"))
        assert_that(use_subgrid, is_(".true."))
        assert_that(latlon_region, is_(".false."))
        assert_that(l_point_data, is_(".false."))
        assert_that(str(start_run), is_("'1901-01-04 00:00:00'"))
        assert_that(str(end_run), is_("'1901-01-13 20:00:00'"))  # Interpolation flag brings us forward an hour

    def test_GIVEN_valid_extents_WHEN_post_THEN_redirect_to_output(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'multi',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
                'start_date': '1940-10-13',
                'end_date': '1950-10-13'
            })
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='land_cover')), "url")

    def test_GIVEN_valid_extents_and_user_over_quota_WHEN_post_THEN_redirect_to_catalogue(self):
        self.create_run_model(storage_in_mb=self.user.storage_quota_in_gb * 1024 + 1, name="big_run", user=self.user)

        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'site': u'multi',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
                'start_date': '1940-10-13',
                'end_date': '1950-10-13'
            })
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_bng_WHEN_bng_to_latlon_service_called_THEN_correct_latlon_returned(self):
        # BNG test values are from http://www.bgs.ac.uk/data/webservices/convertForm.cfm
        bng_easting = 429157
        bng_northing = 623009
        lat = 55.5
        lon = -1.54
        delta = 0.00001
        response = self.app.post(
            url(controller='model_run', action='bng_to_latlon'),
            params={
                'bng_easting': bng_easting,
                'bng_northing': bng_northing
            })
        json = response.json_body
        assert_that(json['lat'], is_(close_to(lat, delta)))
        assert_that(json['lon'], is_(close_to(lon, delta)))

    def test_GIVEN_invalid_bng_WHEN_bng_to_latlon_service_called_THEN_error_returned(self):
        response = self.app.post(
            url(controller='model_run', action='bng_to_latlon'),
            params={
                'bng_easting': u'asd',
                'bng_northing': u'1.1,23413'
            })
        json = response.json_body
        assert_that(json['is_error'], is_(True))