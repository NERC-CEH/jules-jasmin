"""
header
"""
from hamcrest import assert_that, is_
from mock import MagicMock
from joj.services.tests.base import BaseTest
from joj.utils.land_cover_controller_helper import LandCoverControllerHelper
from joj.model import ModelRun, DrivingDataset, LandCoverRegion, LandCoverRegionCategory, LandCoverValue, \
    LandCoverAction
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
        self.model_run.driving_dataset_id = 1

        self.land_cover_service = LandCoverService()
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region
        self.land_cover_service.get_land_cover_values = self._mock_get_land_cover_values
        self.land_cover_service.get_land_cover_categories = self._mock_get_land_cover_categories
        self.land_cover_service.save_land_cover_actions_for_model = MagicMock()
        self.land_cover_service.get_land_cover_actions_for_model = self._mock_lcs_get_actions_for_model_run
        self.land_cover_service.save_fractional_land_cover_for_model = MagicMock()
        self.land_cover_service.get_default_fractional_cover = self._mock_lcs_get_default_fractional_cover

        self.land_cover_helper = LandCoverControllerHelper(land_cover_service=self.land_cover_service)

    class Context(object):
        """
        Mock context object
        """
        pass

    @staticmethod
    def _mock_get_land_cover_values(return_ice=False):
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
        region2.name = "Itchen"
        region2.category_id = 1
        region2.category = cat1

        cat1.regions = [region1, region2]

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

        cat2.regions = [region3, region4]

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

    @staticmethod
    def _mock_lcs_get_actions_for_model_run(model_run):
        cat = LandCoverRegionCategory()
        cat.id = 1
        cat.name = "Countries"
        cat.driving_dataset_id = 1

        region = LandCoverRegion()
        region.id = 1
        region.name = "Wales"
        region.category = cat

        action = LandCoverAction()
        action.id = 1
        action.region = region
        action.value_id = 1

        return [action]

    @staticmethod
    def _mock_lcs_get_actions_for_model_run_wrong_dataset(model_run):
        cat = LandCoverRegionCategory()
        cat.id = 1
        cat.name = "Countries"
        cat.driving_dataset_id = 2

        region = LandCoverRegion()
        region.id = 1
        region.name = "Wales"
        region.category = cat

        action = LandCoverAction()
        action.id = 1
        action.region = region
        action.value_id = 1

        return [action]

    @staticmethod
    def _mock_lcs_get_actions_for_model_run_no_actions(model_run):
        return []

    @staticmethod
    def _mock_lcs_get_default_fractional_cover(model_run):
        return [0.02, 0.11, 0.02, 0.05, 0.35, 0.19, 0.22, 0.04, 0.0]

    @staticmethod
    def _mock_lcs_get_awkward_default_fractional_cover(model_run):
        return [0.0102193951607, 0.0, 0.361101979017, 0.0344029143453, 0.0, 0.369327515364, 0.0, 0.124948188663, 0.0]

    @staticmethod
    def _mock_lcs_get_missing_default_fractional_cover(model_run):
        return 9 * [-9999.99]

    def test_GIVEN_single_action_WHEN_save_land_cover_THEN_land_cover_action_saved(self):
        values = {'action_1_region': u'1',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        self.land_cover_helper.save_land_cover_actions(values, {}, self.model_run)
        called_land_cover_actions = self.land_cover_service.save_land_cover_actions_for_model.call_args[0][1]

        lca1 = called_land_cover_actions[0]
        assert_that(lca1.region_id, is_(1))
        assert_that(lca1.value_id, is_(8))

    def test_GIVEN_two_actions_WHEN_save_land_cover_THEN_both_saved_with_correct_order(self):
        values = {'action_1_region': u'1',
                  'action_1_value': u'8',
                  'action_1_order': u'1',
                  'action_2_region': u'3',
                  'action_2_value': u'7',
                  'action_2_order': u'2'}
        self.land_cover_helper.save_land_cover_actions(values, {}, self.model_run)
        called_land_cover_actions = self.land_cover_service.save_land_cover_actions_for_model.call_args[0][1]

        lca1 = called_land_cover_actions[0]
        assert_that(lca1.region_id, is_(1))
        assert_that(lca1.value_id, is_(8))
        assert_that(lca1.order, is_(1))

        lca2 = called_land_cover_actions[1]
        assert_that(lca2.region_id, is_(3))
        assert_that(lca2.value_id, is_(7))
        assert_that(lca2.order, is_(2))

    def test_GIVEN_invalid_region_WHEN_save_land_cover_THEN_error_returned(self):
        # In this test, the region is for another dataset
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region_wrong_dataset

        values = {'action_1_region': u'10',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_cover_actions(values, errors, self.model_run)

        assert_that(len(errors), is_(1))

    def test_GIVEN_invalid_region_WHEN_save_land_cover_THEN_land_covers_not_saved(self):
        # In this test, the region is for another dataset
        self.land_cover_service.get_land_cover_region_by_id = self._mock_lcs_get_land_cover_region_wrong_dataset

        values = {'action_1_region': u'10',
                  'action_1_value': u'8',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_cover_actions(values, errors, self.model_run)

        assert not self.land_cover_service.save_land_cover_actions_for_model.called

    def test_GIVEN_invalid_land_cover_value_WHEN_save_land_cover_THEN_error_returned(self):
        # In this test, the land cover value doesn't exist
        values = {'action_1_region': u'1',
                  'action_1_value': u'77',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_cover_actions(values, errors, self.model_run)

        assert_that(len(errors), is_(1))

    def test_GIVEN_invalid_land_cover_value_WHEN_save_land_cover_THEN_land_covers_not_saved(self):
        # In this test, the land cover value doesn't exist
        values = {'action_1_region': u'1',
                  'action_1_value': u'77',
                  'action_1_order': u'1'}
        errors = {}
        self.land_cover_helper.save_land_cover_actions(values, errors, self.model_run)

        assert not self.land_cover_service.save_land_cover_actions_for_model.called

    def test_GIVEN_valid_values_WHEN_save_fractional_land_cover_THEN_values_saved_to_file(self):
        values = {'submit': u'Next',
                  'fractional_cover': u'1',
                  'land_cover_value_1': u'20',
                  'land_cover_value_2': u'20',
                  'land_cover_value_3': u'10',
                  'land_cover_value_4': u'10',
                  'land_cover_value_5': u'10',
                  'land_cover_value_6': u'10',
                  'land_cover_value_7': u'10',
                  'land_cover_value_8': u'10'}
        errors = {}

        self.land_cover_helper.save_fractional_land_cover(values, errors, self.model_run)
        assert_that(len(errors), is_(0))

        called_save_frac_cover = self.land_cover_service.save_fractional_land_cover_for_model.call_args_list[0][0][1]
        assert_that(called_save_frac_cover, is_("0.2\t0.2\t0.1\t0.1\t0.1\t0.1\t0.1\t0.1\t0"))

    def test_GIVEN_values_dont_add_up_WHEN_save_fractional_land_cover_THEN_error_and_values_not_saved_to_file(self):
        values = {'submit': u'Next',
                  'fractional_cover': u'1',
                  'land_cover_value_1': u'20',
                  'land_cover_value_2': u'25',
                  'land_cover_value_3': u'10',
                  'land_cover_value_4': u'10',
                  'land_cover_value_5': u'10',
                  'land_cover_value_6': u'10',
                  'land_cover_value_7': u'10',
                  'land_cover_value_8': u'15'}
        errors = {}

        self.land_cover_helper.save_fractional_land_cover(values, errors, self.model_run)
        assert_that(errors['land_cover_frac'], is_("The sum of all the land cover fractions must be 100%"))

        assert not self.land_cover_service.save_fractional_land_cover_for_model.called

    def test_GIVEN_empty_values_WHEN_save_fractional_land_cover_THEN_error_returned(self):
        values = {'submit': u'Next',
                  'fractional_cover': u'1',
                  'land_cover_value_1': u'20',
                  'land_cover_value_2': u'25',
                  'land_cover_value_3': u'10',
                  'land_cover_value_4': u'',
                  'land_cover_value_5': u'10',
                  'land_cover_value_6': u'10',
                  'land_cover_value_7': u'10',
                  'land_cover_value_8': u'15'}
        errors = {}

        self.land_cover_helper.save_fractional_land_cover(values, errors, self.model_run)
        assert_that(errors['land_cover_value_4'], is_("Please enter a number"))

        assert not self.land_cover_service.save_fractional_land_cover_for_model.called

    def test_GIVEN_negative_value_WHEN_save_fractional_land_cover_THEN_error_returned(self):
        values = {'submit': u'Next',
                  'fractional_cover': u'1',
                  'land_cover_value_1': u'20',
                  'land_cover_value_2': u'20',
                  'land_cover_value_3': u'20',
                  'land_cover_value_4': u'-25',
                  'land_cover_value_5': u'20',
                  'land_cover_value_6': u'20',
                  'land_cover_value_7': u'10',
                  'land_cover_value_8': u'15'}
        errors = {}

        self.land_cover_helper.save_fractional_land_cover(values, errors, self.model_run)
        assert_that(errors['land_cover_value_4'], is_("Please enter a positive number"))

        assert not self.land_cover_service.save_fractional_land_cover_for_model.called

    def test_GIVEN_ice_chosen_WHEN_save_fractional_land_cover_THEN_values_saved_to_file(self):
        values = {'submit': u'Next',
                  'land_cover_ice': u'1'}
        errors = {}

        self.land_cover_helper.save_fractional_land_cover(values, errors, self.model_run)
        assert_that(len(errors), is_(0))

        called_save_frac_cover = self.land_cover_service.save_fractional_land_cover_for_model.call_args_list[0][0][1]
        assert_that(called_save_frac_cover, is_("0\t0\t0\t0\t0\t0\t0\t0\t1"))

    def test_GIVEN_no_land_cover_actions_saved_WHEN_add_to_context_THEN_no_errors_returned(self):
        self.land_cover_service.save_land_cover_actions_for_model = self._mock_lcs_get_actions_for_model_run
        errors = {}
        self.land_cover_helper.add_land_covers_to_context(self.Context(), errors, self.model_run)
        assert_that(len(errors), is_(0))

    def test_GIVEN_driving_data_has_categories_WHEN_add_to_context_THEN_context_contains_land_cover_categories(self):
        context = self.Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_categories), is_(2))

    def test_GIVEN_nothing_saved_WHEN_add_to_context_THEN_context_contains_land_cover_values(self):
        context = self.Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_values), is_(9))

    def test_GIVEN_land_cover_actions_saved_WHEN_add_to_context_THEN_context_contains_actions(self):
        context = self.Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_actions), is_(1))

    def test_GIVEN_invalid_land_cover_actions_saved_WHEN_add_to_context_THEN_errors_returned(self):
        self.land_cover_service.get_land_cover_actions_for_model = self._mock_lcs_get_actions_for_model_run_wrong_dataset
        errors = {}
        self.land_cover_helper.add_land_covers_to_context(self.Context(), errors, self.model_run)

        assert_that(len(errors), is_(1))

    def test_GIVEN_invalid_land_cover_actions_saved_WHEN_add_to_context_THEN_no_actions_returned(self):
        self.land_cover_service.get_land_cover_actions_for_model = self._mock_lcs_get_actions_for_model_run_wrong_dataset

        context = self.Context()
        self.land_cover_helper.add_land_covers_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_actions), is_(0))

    def test_GIVEN_nothing_WHEN_add_fractional_cover_to_context_THEN_cover_types_added(self):
        self.model_run.land_cover_frac = "0\t0\t0\t0\t0\t0\t0\t0\t1"

        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_values), is_(9))

    def test_GIVEN_fractional_land_cover_saved_WHEN_add_fractional_cover_to_context_THEN_cover_values_added(self):
        self.model_run.land_cover_frac = "0\t0\t0\t0\t0\t0\t0\t0\t1"

        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)

        assert_that(len(context.land_cover_values), is_(9))
        assert_that(context.land_cover_values["land_cover_ice"], is_(1))

    def test_GIVEN_nothing_WHEN_add_fractional_cover_to_context_THEN_ice_index_added(self):
        self.model_run.land_cover_frac = "0\t0\t0\t0\t0\t0\t0\t0\t1"

        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)

        assert_that(context.ice_index, is_(9))

    def test_GIVEN_no_fractional_land_cover_saved_WHEN_add_fractional_cover_to_context_THEN_defaults_returned(self):
        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)
        context_vals = [context.land_cover_values[key] for key in sorted(context.land_cover_values)]
        assert_that(context_vals, is_([2.0, 11.0, 2.0, 5.0, 35.0, 19.0, 22.0, 4.0]))

    def test_GIVEN_awkward_default_fractional_cover_WHEN_add_cover_to_context_THEN_truncated_and_adds_to_one(self):
        # Sometimes the default fractional cover retrieved from the netCDF file is awkward in that the
        # fractions are long (11 decimal places) and don't add up to precisely 1.0
        self.land_cover_service.get_default_fractional_cover = self._mock_lcs_get_awkward_default_fractional_cover

        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)
        context_vals = [context.land_cover_values[key] for key in sorted(context.land_cover_values) if 'land_cover_value' in key]
        assert sum(context_vals) - 100.0 < 0.00000001

    def test_GIVEN_missing_fractional_cover_WHEN_add_cover_to_context_THEN_zeros_returned(self):
        self.land_cover_service.get_default_fractional_cover = self._mock_lcs_get_missing_default_fractional_cover

        context = self.Context()
        self.land_cover_helper.add_fractional_land_cover_to_context(context, {}, self.model_run)
        for value in context.land_cover_values.values():
            assert_that(value, is_(0.0))

