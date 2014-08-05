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
        self.land_cover_service.get_land_cover_types = self._mock_get_land_cover_types

        self.model_run_service = ModelRunService()
        self.model_run_service.save_land_cover_actions_for_model = MagicMock()
        self.land_cover_helper = LandCoverControllerHelper(model_run_service=self.model_run_service,
                                                           land_cover_service=self.land_cover_service)

    @staticmethod
    def _mock_get_land_cover_types():
        land_cover_types = []
        types = {1: 'BT', 2: 'NT', 3: 'C3G', 4: 'C4G', 5: 'Shrub', 6: 'Urban', 7: 'Lake', 8: 'Soil',
                 9: 'Ice'}
        for index in types:
            land_cover_type = LandCoverValue()
            land_cover_type.id = index
            land_cover_type.index = index
            land_cover_type.name = types[index]
            land_cover_types.append(land_cover_type)
        return land_cover_types

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
        land_cover_region.type = land_cover_type

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
        land_cover_region.type = land_cover_type

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
