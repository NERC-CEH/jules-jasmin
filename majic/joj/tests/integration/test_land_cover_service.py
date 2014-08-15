"""
header
"""
from hamcrest import assert_that, is_
from pylons import config
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.model import session_scope, LandCoverRegionCategory, LandCoverRegion
from joj.services.land_cover_service import LandCoverService
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService
from joj.services.dap_client import DapClientException
from joj.services.dap_client_factory import DapClientFactory
from joj.utils import constants
from joj.services.general import ServiceException


class MockLandCoverDapClient(object):
    """
    Mock Dap client for land cover
    """

    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.return_values = {}

        if self.url == config['thredds.server_url'] + "dodsC/model_runs/data/driving1/frac.nc" and self.key == 'frac':
            self.return_values[(0, 0)] = [0.02, 0.11, 0.02, 0.05, 0.35, 0.19, 0.22, 0.04, 0.0]
        elif self.url == config['thredds.server_url'] + "dodsC/model_runs/data/driving2/frac.nc" and self.key == 'frac2':
            self.return_values[(70, 0)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            self.return_values[(80, 120)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        else:
            raise DapClientException("URL not found")

    def get_fractional_cover(self, lat, lon):
        """
        Mock get fractional cover method
        :param lat:
        :param lon:
        """
        return self.return_values[(lat, lon)]


class TestLandCoverService(TestWithFullModelRun):
    def setUp(self):
        dap_client_factory = DapClientFactory()
        dap_client_factory.get_land_cover_dap_client = self._mock_get_land_cover_dap_client
        self.land_cover_service = LandCoverService(dap_client_factory=dap_client_factory)
        self.model_run_service = ModelRunService()
        self.dataset_service = DatasetService()
        self.clean_database()
        self.user = self.login()
        self.create_model_run_ready_for_submit()

    @staticmethod
    def _mock_get_land_cover_dap_client(url, key):
        return MockLandCoverDapClient(url, key)

    def test_GIVEN_land_cover_regions_exist_WHEN_get_land_cover_region_by_id_THEN_land_cover_region_returned(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        id = land_cover_region.id

        returned_region = self.land_cover_service.get_land_cover_region_by_id(id)
        assert_that(returned_region.id, is_(id))
        assert_that(returned_region.name, is_("Wales"))

    def test_GIVEN_land_cover_categories_WHEN_get_land_cover_region_THEN_returned_region_has_category_loaded(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        id = land_cover_region.id

        with session_scope() as session:
            land_cover_cat = LandCoverRegionCategory()
            land_cover_cat.name = "River Catchments"
            land_cover_cat.driving_dataset_id = model_run.driving_dataset_id
            session.add(land_cover_cat)

        returned_region = self.land_cover_service.get_land_cover_region_by_id(id)
        assert_that(returned_region.category.name, is_("Countries"))

    def test_GIVEN_land_cover_values_WHEN_get_land_cover_values_THEN_land_cover_values_returned(self):
        lc_values = self.land_cover_service.get_land_cover_values()
        assert_that(len(lc_values), is_(9))
        names = [lc_value.name for lc_value in lc_values]
        assert 'Urban' in names
        assert 'Ice' in names

    def test_GIVEN_multiple_land_cover_categories_WHEN_get_categories_THEN_correct_categories_returned(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        datasets = self.dataset_service.get_driving_datasets()

        with session_scope() as session:
            cat1 = LandCoverRegionCategory()
            cat1.name = "Countries"
            cat1.driving_dataset_id = model_run.driving_dataset_id

            region1 = LandCoverRegion()
            region1.mask_file = "filepath"
            region1.name = "Wales"
            region1.category = cat1

            cat2 = LandCoverRegionCategory()
            cat2.name = "Rivers"
            cat2.driving_dataset_id = datasets[1].id

            region2 = LandCoverRegion()
            region2.mask_file = "filepath2"
            region2.name = "Thames"
            region2.category = cat2

            session.add_all([region1, region2])

        categories = self.land_cover_service.get_land_cover_categories(model_run.driving_dataset_id)
        assert_that(len(categories), is_(1))
        assert_that(categories[0].name, is_("Countries"))

    def test_GIVEN_categories_have_land_cover_regions_WHEN_get_categories_THEN_category_has_regions_loaded(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        with session_scope() as session:
            cat1 = LandCoverRegionCategory()
            cat1.name = "Countries"
            cat1.driving_dataset_id = model_run.driving_dataset_id

            region1 = LandCoverRegion()
            region1.mask_file = "filepath"
            region1.name = "Wales"
            region1.category = cat1

            cat2 = LandCoverRegionCategory()
            cat2.name = "Rivers"
            cat2.driving_dataset_id = model_run.driving_dataset_id

            region2 = LandCoverRegion()
            region2.mask_file = "filepath2"
            region2.name = "Thames"
            region2.category = cat2

            session.add_all([region1, region2])

        categories = self.land_cover_service.get_land_cover_categories(model_run.driving_dataset_id)
        assert_that(len(categories[0].regions), is_(1))
        assert_that(categories[0].regions[0].name, is_("Wales"))

    def test_GIVEN_land_cover_actions_WHEN_save_land_cover_actions_THEN_land_cover_actions_saved(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1), (2, 3)], self.land_cover_service)

        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
        actions = model_run.land_cover_actions
        assert_that(len(actions), is_(2))

    def test_GIVEN_existing_land_cover_actions_WHEN_save_land_cover_actions_THEN_land_cover_actions_overwritten(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1), (2, 3)], self.land_cover_service)

        self.add_land_cover_actions(land_cover_region, model_run, [(2, 4)], self.land_cover_service)

        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
        actions = model_run.land_cover_actions
        assert_that(len(actions), is_(1))
        assert_that(actions[0].value_id, is_(2))
        assert_that(actions[0].order, is_(4))

    def test_GIVEN_no_land_cover_actions_WHEN_save_land_cover_actions_THEN_all_land_cover_actions_removed(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1), (2, 3)], self.land_cover_service)

        self.add_land_cover_actions(land_cover_region, model_run, [], self.land_cover_service)

        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
        actions = model_run.land_cover_actions
        assert_that(len(actions), is_(0))

    def test_GIVEN_land_cover_actions_saved_on_model_run_WHEN_get_land_cover_actions_THEN_actions_returned(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1), (2, 3)], self.land_cover_service)

        actions = self.land_cover_service.get_land_cover_actions_for_model(model_run)
        assert_that(len(actions), is_(2))
        assert_that(actions[0].value_id, is_(1))
        assert_that(actions[0].order, is_(1))
        assert_that(actions[1].value_id, is_(2))
        assert_that(actions[1].order, is_(3))

    def test_GIVEN_land_cover_actions_saved_WHEN_get_actions_THEN_actions_have_regions_and_categories_loaded(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1)], self.land_cover_service)

        action = self.land_cover_service.get_land_cover_actions_for_model(model_run)[0]
        assert_that(action.region.name, is_("Wales"))
        assert_that(action.region.category.name, is_("Countries"))

    def test_GIVEN_land_cover_actions_saved_WHEN_get_actions_THEN_actions_have_values_loaded(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        land_cover_region = self.add_land_cover_region(model_run)
        self.add_land_cover_actions(land_cover_region, model_run, [(1, 1)], self.land_cover_service)

        action = self.land_cover_service.get_land_cover_actions_for_model(model_run)[0]
        assert_that(action.value.name, is_("Broad-leaved Tree"))

    def test_GIVEN_fractional_string_WHEN_save_fractional_land_cover_for_model_THEN_fractional_cover_saved(self):
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        assert_that(model_run.land_cover_frac, is_(None))

        fractional_string = "0\t0\t0\t0\t0\t0\t0\t0\t1"
        self.land_cover_service.save_fractional_land_cover_for_model(model_run, fractional_string)

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        assert_that(model_run.land_cover_frac, is_(fractional_string))

    def test_GIVEN_user_uploaded_driving_data_WHEN_get_default_fractional_cover_THEN_fractional_cover_returned(self):
        self.clean_database()
        self.user = self.login()
        self.create_model_run_with_user_uploaded_driving_data()

        model_run = self.set_model_run_latlon(self.user, 70, 0)

        fractional_vals = self.land_cover_service.get_default_fractional_cover(model_run)
        assert_that(fractional_vals, is_([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]))

    def test_GIVEN_two_matching_datasets_WHEN_get_default_cover_THEN_higher_priority_fractional_cover_returned(self):
        self.clean_database()
        self.user = self.login()
        self.create_model_run_with_user_uploaded_driving_data()

        model_run = self.set_model_run_latlon(self.user, 0, 0)
        fractional_vals = self.land_cover_service.get_default_fractional_cover(model_run)
        assert_that(fractional_vals, is_([0.02, 0.11, 0.02, 0.05, 0.35, 0.19, 0.22, 0.04, 0.0]))

    def test_GIVEN_no_matching_datasets_WHEN_get_default_cover_THEN_zeros_returned(self):
        self.clean_database()
        self.user = self.login()
        self.create_model_run_with_user_uploaded_driving_data()

        model_run = self.set_model_run_latlon(self.user, 88, 0)
        fractional_vals = self.land_cover_service.get_default_fractional_cover(model_run)
        assert_that(fractional_vals, is_([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))

    def test_GIVEN_thredds_not_working_WHEN_get_default_cover_THEN_zeros_returned(self):
        self.clean_database()
        self.user = self.login()
        self.create_model_run_with_user_uploaded_driving_data()

        def _get_broken_dap_client(url, key):
            return MockLandCoverDapClient("broken_url", key)

        dap_client_factory = DapClientFactory()
        dap_client_factory.get_land_cover_dap_client = _get_broken_dap_client
        self.land_cover_service = LandCoverService(dap_client_factory=dap_client_factory)

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        fractional_vals = self.land_cover_service.get_default_fractional_cover(model_run)
        assert_that(fractional_vals, is_([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))

    def test_GIVEN_using_provided_driving_data_WHEN_get_default_fractional_cover_THEN_fractional_cover_returned(self):
        self.clean_database()
        self.user = self.login()
        self.create_alternate_model_run()

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        fractional_vals = self.land_cover_service.get_default_fractional_cover(model_run)
        assert_that(fractional_vals, is_([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]))

    def test_GIVEN_multicell_model_run_WHEN_get_default_fractional_cover_THEN_ServiceException_raised(self):
        self.clean_database()
        self.user = self.login()
        self.create_model_run_ready_for_submit()

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        with self.assertRaises(ServiceException):
            self.land_cover_service.get_default_fractional_cover(model_run)

    def set_model_run_latlon(self, user, lat, lon):
        params_to_save = [[constants.JULES_PARAM_POINTS_FILE, [lat, lon]]]
        params_to_del = constants.JULES_PARAM_POINTS_FILE
        self.model_run_service.save_new_parameters(params_to_save, params_to_del, user)

        return self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
