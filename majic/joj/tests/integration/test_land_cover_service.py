"""
header
"""
from hamcrest import assert_that, is_
from joj.services.land_cover_service import LandCoverService
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from model import session_scope, LandCoverRegionCategory
from services.model_run_service import ModelRunService


class TestLandCoverService(TestWithFullModelRun):

    def setUp(self):
        self.land_cover_service = LandCoverService()
        self.model_run_service = ModelRunService()
        self.clean_database()
        self.user = self.login()
        self.create_model_run_ready_for_submit()

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
