"""
header
"""
from hamcrest import is_, assert_that, contains_string
from pylons import url
from sqlalchemy.orm import subqueryload
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from joj.model import session_scope, LandCoverRegionCategory, ModelRun, LandCoverRegion
from joj.services.dataset import DatasetService
from joj.utils import constants


# noinspection PyProtectedMember
from services.land_cover_service import LandCoverService


class TestModelRunLandCover(TestController):
    def setUp(self):
        self.clean_database()
        self.user = self.login()
        self.create_two_driving_datasets()
        dds = DatasetService().get_driving_datasets()[0]
        with session_scope() as session:
            model_run = ModelRun()
            model_run.name = "model run"
            model_run.change_status(session, constants.MODEL_RUN_STATUS_CREATED)
            model_run.user = self.user
            model_run.driving_dataset_id = dds.id
            session.add(model_run)
            session.commit()
            self.model_run_service = ModelRunService()
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
        self.add_land_cover_region(model_run)

    def test_GIVEN_land_cover_actions_WHEN_post_THEN_land_cover_action_saved_in_database(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
        categories = LandCoverService().get_land_cover_categories(dds.id)
        # Need to know the region IDs
        self.app.post(
            url(controller='model_run', action='land_cover'),
            params={
                'submit': u'Next',
                'action_1_region': str(categories[0].land_cover_regions[0].id),
                'action_1_value': u'8',
                'action_1_order': u'1',
                'action_2_region': str(categories[0].land_cover_regions[0].id),
                'action_2_value': u'7',
                'action_2_order': u'2'
            })
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)

        actions = model_run.land_cover_actions
        assert_that(len(actions), is_(2))
        for action in actions:
            if action.value_id == 8:
                assert_that(action.order, is_(1))
            elif action.value_id == 7:
                assert_that(action.order, is_(2))
            else:
                assert False

    def test_GIVEN_invalid_land_cover_actions_WHEN_post_THEN_error_shown_and_stay_on_page(self):
        # Add some regions to another driving dataset
        dds = DatasetService().get_driving_datasets()[1]
        with session_scope() as session:
            land_cat = LandCoverRegionCategory()
            land_cat.driving_dataset = dds
            land_cat.name = "Category2"

            land_region = LandCoverRegion()
            land_region.name = "Region1"
            land_region.category = land_cat
            session.add(land_region)

        response = self.app.post(
            url(controller='model_run', action='land_cover'),
            params={
                'submit': u'Next',
                'action_1_region': str(land_region.id),
                'action_1_value': u'8',
                'action_1_order': u'1'
            })
        assert_that(response.normal_body, contains_string("Land Cover"))  # Check still on page
        assert_that(response.normal_body, contains_string("Your chosen land cover choices are not valid for your"
                                                          " chosen driving dataset"))

    def test_GIVEN_land_cover_values_and_regions_exist_WHEN_get_THEN_regions_and_categories_rendered(self):
        with session_scope() as session:
            model_run = self.model_run_service._get_model_run_being_created(session, self.user)
            dds = model_run.driving_dataset
            session.add_all(self.generate_categories_with_regions(dds))

        response = self.app.get(url(controller='model_run', action='land_cover'))

        assert_that(response.normal_body, contains_string("Rivers"))
        assert_that(response.normal_body, contains_string("Thames"))
        assert_that(response.normal_body, contains_string("Itchen"))
        assert_that(response.normal_body, contains_string("Counties"))
        assert_that(response.normal_body, contains_string("Hampshire"))
        assert_that(response.normal_body, contains_string("Oxfordshire"))

    def test_GIVEN_nothing_WHEN_get_THEN_values_rendered(self):
        response = self.app.get(url(controller='model_run', action='land_cover'))

        values = LandCoverService().get_land_cover_values()
        for value in values:
            assert_that(response.normal_body, contains_string(str(value.name)))

    def test_GIVEN_land_cover_actions_already_saved_WHEN_get_THEN_actions_rendered(self):
        assert False #todo

    def generate_categories_with_regions(self, driving_dataset):
            # Add categories
            cat1 = LandCoverRegionCategory()
            cat1.driving_dataset_id = driving_dataset.id
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

            cat1.land_cover_regions = [region1, region2]

            cat2 = LandCoverRegionCategory()
            cat2.driving_dataset_id = driving_dataset.id
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