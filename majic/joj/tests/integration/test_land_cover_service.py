"""
header
"""
from hamcrest import assert_that, is_
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.model import session_scope, LandCoverRegionCategory, LandCoverRegion
from joj.services.land_cover_service import LandCoverService
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService


class TestLandCoverService(TestWithFullModelRun):

    def setUp(self):
        self.land_cover_service = LandCoverService()
        self.model_run_service = ModelRunService()
        self.dataset_service = DatasetService()
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
        assert_that(len(categories[0].land_cover_regions), is_(1))
        assert_that(categories[0].land_cover_regions[0].name, is_("Wales"))
