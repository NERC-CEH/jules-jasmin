#header
from urlparse import urlparse
from hamcrest import assert_that, is_, contains_string
from pylons import url
from joj.model import DrivingDataset, Session, session_scope, ModelRun, User
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from joj.utils.constants import JULES_PARAM_LON_BOUNDS, JULES_PARAM_LAT_BOUNDS, JULES_PARAM_LATLON_REGION, \
    JULES_PARAM_USE_SUBGRID, MODEL_RUN_STATUS_CREATED


class TestModelRunExtents(TestController):

    def setUp(self):
        super(TestModelRunExtents, self).setUp()
        self.clean_database()
        self.user = self.login()
        self.model_run_service = ModelRunService()
        with session_scope(Session) as session:
            self.driving_data = DrivingDataset()
            self.driving_data.boundary_lat_north = 47.5
            self.driving_data.boundary_lat_south = 13.8
            self.driving_data.boundary_lon_east = 123.1
            self.driving_data.boundary_lon_west = -15.0
            session.add(self.driving_data)
            session.commit()

            self.model_run = ModelRun()
            self.model_run.name = "MR1"
            self.model_run.status = self._status(MODEL_RUN_STATUS_CREATED)
            self.model_run.driving_dataset_id = self.driving_data.id
            self.model_run.user = self.user
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
        assert_that(response.normal_body, contains_string("Specify Spatial and Temporal Extents"))

    def test_GIVEN_driving_dataset_selected_for_model_WHEN_page_get_THEN_driving_data_spatial_extents_rendered(self):
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lat_north)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lat_south)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lon_east)))
        assert_that(response.normal_body, contains_string(str(self.driving_data.boundary_lon_west)))

    def test_GIVEN_spatial_extents_already_chosen_WHEN_page_get_THEN_existing_extents_rendered(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS[1], JULES_PARAM_LON_BOUNDS[0], [12.3, 35.5], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS[1], JULES_PARAM_LAT_BOUNDS[0], [50, 70], self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))
        assert_that(response.normal_body, contains_string("12.3"))
        assert_that(response.normal_body, contains_string("35.5"))
        assert_that(response.normal_body, contains_string("50"))
        assert_that(response.normal_body, contains_string("70"))

    def test_GIVEN_invalid_spatial_extents_already_chosen_WHEN_page_get_THEN_errors_shown(self):
        self.model_run_service.save_parameter(JULES_PARAM_LON_BOUNDS[1], JULES_PARAM_LON_BOUNDS[0], [40, 500], self.user)
        self.model_run_service.save_parameter(JULES_PARAM_LAT_BOUNDS[1], JULES_PARAM_LAT_BOUNDS[0], [20, 25], self.user)
        response = self.app.get(
            url(controller='model_run', action='extents'))

        assert_that(response.normal_body, contains_string("Longitude must be between -180 and 180"))

    def test_GIVEN_invalid_extents_WHEN_post_THEN_errors_rendered(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 500,
            })
        assert_that(response.normal_body, contains_string("Longitude must be between -180 and 180"))

    def test_GIVEN_valid_extents_WHEN_post_THEN_extents_saved(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
            })
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        lat_bounds = model_run.get_parameter_value(JULES_PARAM_LAT_BOUNDS[1], JULES_PARAM_LAT_BOUNDS[0])
        lon_bounds = model_run.get_parameter_value(JULES_PARAM_LON_BOUNDS[1], JULES_PARAM_LON_BOUNDS[0])
        use_subgrid = model_run.get_parameter_value(JULES_PARAM_USE_SUBGRID[1], JULES_PARAM_USE_SUBGRID[0])
        latlon_region = model_run.get_parameter_value(JULES_PARAM_LATLON_REGION[1], JULES_PARAM_LATLON_REGION[0])
        assert_that(lat_bounds, is_("20.0, 25.0"))
        assert_that(lon_bounds, is_("35.0, 40.0"))
        assert_that(use_subgrid, is_(".true."))
        assert_that(latlon_region, is_(".true."))

    def test_GIVEN_valid_extents_WHEN_post_THEN_redirect_to_parameters(self):
        response = self.app.post(
            url(controller='model_run', action='extents'),
            params={
                'submit': u'Next',
                'lat_n': 25,
                'lat_s': 20,
                'lon_e': 40,
                'lon_w': 35,
            })
        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='parameters')), "url")