"""
header
"""
from hamcrest import assert_that, is_
from mock import MagicMock
from joj.services.tests.base import BaseTest
from joj.utils.land_cover_controller_helper import LandCoverControllerHelper
from joj.model import ModelRun, DrivingDataset, LandCoverRegion, LandCoverRegionCategory, LandCoverValue
from joj.services.model_run_service import ModelRunService
from joj.services.land_cover_service import LandCoverService


class TestLandCoverControllerHelper(BaseTest):
    def setUp(self):
        driving_data = DrivingDataset()
        driving_data.name = "Driving1"
        driving_data.id = 1

        self.return_dd_id = 10

        self.model_run = ModelRun()
        self.model_run.name = "Model Run1"
        self.model_run.driving_dataset = driving_data

        self.land_cover_service = LandCoverService()
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region
        self.land_cover_service.get_land_cover_values = self._mock_get_land_cover_values
        self.land_cover_service.get_land_cover_categories = self._mock_get_land_cover_categories

        self.model_run_service = ModelRunService()
        self.model_run_service.save_land_cover_actions_for_model = MagicMock()
        self.land_cover_helper = LandCoverControllerHelper(model_run_service=self.model_run_service,
                                                           land_cover_service=self.land_cover_service)

    @staticmethod
    def _mock_get_land_cover_values():
        land_cover_values = []
        types = {1: 'BT', 2: 'NT', 3: 'C3G', 4: 'C4G', 5: 'Shrub', 6: 'Urban', 7: 'Lake', 8: 'Soil',
                 9: 'Ice'}
        for index in types:
            land_cover_value = LandCoverValue()
            land_cover_value.id = index
            land_cover_value.index = index
            land_cover_value.name = types[index]
            land_cover_values.append(land_cover_value)
        return land_cover_values

    @staticmethod
    def _mock_get_land_cover_categories(driving_data_id):
        cat1 = LandCoverRegionCategory()
        cat1.driving_dataset_id = driving_data_id
        cat1.name = "Rivers"
        cat1.id = 1

        region1 = LandCoverRegion()
        region1.id = 1
        region1.name = "Thames"
        region1.category_id = 1
        region1.category = cat1

        region2 = LandCoverRegion()
        region2.id = 2
        region2.name = "Thames"
        region2.category_id = 1
        region2.category = cat1

        cat1.land_cover_regions = [region1, region2]

        cat2 = LandCoverRegionCategory()
        cat2.driving_dataset_id = driving_data_id
        cat2.name = "Counties"
        cat2.id = 2

        region3 = LandCoverRegion()
        region3.id = 3
        region3.name = "Hampshire"
        region3.category_id = 2
        region3.category = cat2

        region4 = LandCoverRegion()
        region4.id = 4
        region4.name = "Oxfordshire"
        region4.category_id = 2
        region4.category = cat2

        cat2.land_cover_regions = [region3, region4]

        return [cat1, cat2]


    @staticmethod
    def _mock_lcs_get_land_cover_region(id):
        dds = DrivingDataset()
        dds.id = 1

        land_cover_type = LandCoverRegionCategory()
        land_cover_type.id = 1
        land_cover_type.driving_dataset_id = 1
        land_cover_type.driving_dataset = dds

        land_cover_region = LandCoverRegion()
        land_cover_region.id = id
        land_cover_region.name = "Sand"
        land_cover_region.category = land_cover_type

        return land_cover_region

    @staticmethod
    def _mock_lcs_get_land_cover_region_wrong_dataset(id):
        dds = DrivingDataset()
        dds.id = 7

        land_cover_type = LandCoverRegionCategory()
        land_cover_type.id = 1
        land_cover_type.driving_dataset_id = 7
        land_cover_type.driving_dataset = dds

        land_cover_region = LandCoverRegion()
        land_cover_region.id = id
        land_cover_region.name = "Sand"
        land_cover_region.category = land_cover_type

        return land_cover_region

    def test_GIVEN_single_action_WHEN_save_land_cover_THEN_land_cover_action_saved(self):
        values = {'action_1_region': u'1',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        self.land_cover_helper.save_land_covers(values, {}, self.model_run)
        called_land_cover_actions = self.model_run_service.save_land_cover_actions_for_model.call_args[0][1]

        lca1 = called_land_cover_actions[0]
        assert_that(lca1.region_id, is_(1))
        assert_that(lca1.value, is_(8))

    def test_GIVEN_two_actions_WHEN_save_land_cover_THEN_both_saved_with_correct_order(self):
        values = {'action_1_region': u'1',
                  'action_1_value': u'8',
                  'action_1_order': u'1',
                  'action_2_region': u'3',
                  'action_2_value': u'7',
                  'action_2_order': u'2'}
        self.land_cover_helper.save_land_covers(values, {}, self.model_run)
        called_land_cover_actions = self.model_run_service.save_land_cover_actions_for_model.call_args[0][1]

        lca1 = called_land_cover_actions[0]
        assert_that(lca1.region_id, is_(1))
        assert_that(lca1.value, is_(8))
        assert_that(lca1.order, is_(1))

        lca2 = called_land_cover_actions[1]
        assert_that(lca2.region_id, is_(3))
        assert_that(lca2.value, is_(7))
        assert_that(lca2.order, is_(2))

    def test_GIVEN_invalid_region_WHEN_save_land_cover_THEN_error_returned(self):
        # In this test, the region is for another dataset
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region_wrong_dataset

        values = {'action_1_region': u'10',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_covers(values, errors, self.model_run)

        assert_that(len(errors), is_(1))

    def test_GIVEN_invalid_region_WHEN_save_land_cover_THEN_land_covers_not_saved(self):
        # In this test, the region is for another dataset
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region_wrong_dataset

        values = {'action_1_region': u'10',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_covers(values, errors, self.model_run)

        assert not self.model_run_service.save_land_cover_actions_for_model.called

    def test_GIVEN_invalid_land_cover_value_WHEN_save_land_cover_THEN_error_returned(self):
        # In this test, the land cover value doesn't exist
        values = {'action_1_region': u'1',
                  'action_1_value': u'77',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_covers(values, errors, self.model_run)

        assert_that(len(errors), is_(1))

    def test_GIVEN_invalid_land_cover_value_WHEN_save_land_cover_THEN_land_covers_not_saved(self):
        # In this test, the land cover value doesn't exist
        values = {'action_1_region': u'1',
                  'action_1_value': u'77',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_covers(values, errors, self.model_run)

        assert not self.model_run_service.save_land_cover_actions_for_model.called

    def test_GIVEN_no_land_cover_actions_saved_WHEN_add_to_context_THEN_no_errors_returned(self):
        errors = {}
        self.land_cover_helper.add_land_covers_to_context(object, errors, self.model_run)
        assert_that(len(errors), is_(0))

    def test_GIVEN_no_land_cover_actions_saved_WHEN_add_to_context_THEN_context_contains_land_cover_categories(self):
        class Context(object):
            pass
        context = Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_categories), is_(2))

    def test_GIVEN_no_land_cover_actions_saved_WHEN_add_to_context_THEN_context_contains_land_cover_values(self):
        class Context(object):
            pass
        context = Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_values), is_(9))

    # TODO  Test that we can add existing saved land cover actions to the context, and validate errors.
