"""
# Header
"""
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.model import Session, session_scope, LandCoverRegion, LandCoverRegionCategory, LandCoverAction
from joj.utils import constants


class TestModelRunSummaryController(TestWithFullModelRun):
    def setUp(self):
        super(TestModelRunSummaryController, self).setUp()

    def test_GIVEN_no_defining_model_WHEN_navigate_to_summary_THEN_redirect_to_create_model_run(self):
        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_select_previous_WHEN_post_THEN_redirect_to_output_page(self):
        self.model_run_service.update_model_run(self.user, "test", constants.DEFAULT_SCIENCE_CONFIGURATION)
        self.model_run_service.store_parameter_values({'1': 12}, self.user)

        response = self.app.post(
            url=url(controller='model_run', action='submit'),
            params={
                'submit': u'Previous'
            }
        )

        assert_that(response.status_code, is_(302), "Respose is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='output')), "url")

    def test_GIVEN_select_previous_and_user_over_quota_WHEN_post_THEN_redirect_to_index_page(self):
        self.create_run_model(storage_in_mb=self.user.storage_quota_in_gb * 1024 + 1, name="big_run", user=self.user)
        self.model_run_service.update_model_run(self.user, "test", constants.DEFAULT_SCIENCE_CONFIGURATION)
        self.model_run_service.store_parameter_values({'1': 12}, self.user)

        response = self.app.post(
            url=url(controller='model_run', action='submit'),
            params={
                'submit': u'Previous'
            }
        )

        assert_that(response.status_code, is_(302), "Respose is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='index')), "url")

    def test_GIVEN_select_submit_WHEN_post_THEN_redirect_to_index_page_job_submitted(self):
        self.model_run_service.update_model_run(self.user, "test", constants.DEFAULT_SCIENCE_CONFIGURATION)
        self.model_run_service.store_parameter_values({'1': 12}, self.user)

        response = self.app.post(
            url=url(controller='model_run', action='submit'),
            params={
                'submit': u'Submit'
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

        session = Session()
        row = session.query("name").from_statement(
            """
                SELECT s.name
                FROM model_runs m
                JOIN model_run_statuses s on s.id = m.status_id
                WHERE m.user_id = :userid
                """) \
            .params({'userid': self.user.id}) \
            .one()
        assert_that(row.name, is_(constants.MODEL_RUN_STATUS_SUBMIT_FAILED), "model run status")

    def test_GIVEN_select_submit_and_user_over_quota_WHEN_post_THEN_redirect_to_index_page_job_not_submitted(self):
        big_model_run = self.create_run_model(storage_in_mb=self.user.storage_quota_in_gb * 1024 + 1, name="big_run", user=self.user)
        self.model_run_service.update_model_run(self.user, "test", constants.DEFAULT_SCIENCE_CONFIGURATION)
        self.model_run_service.store_parameter_values({'1': 12}, self.user)

        response = self.app.post(
            url=url(controller='model_run', action='submit'),
            params={
                'submit': u'Submit'
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='index')), "url")

        session = Session()
        row = session.query("name").from_statement(
            """
                SELECT s.name
                FROM model_runs m
                JOIN model_run_statuses s on s.id = m.status_id
                WHERE m.user_id = :userid AND m.id != :model_run_id
                """) \
            .params({'userid': self.user.id, 'model_run_id': big_model_run.id}) \
            .one()
        assert_that(row.name, is_(constants.MODEL_RUN_STATUS_CREATED), "model run status")

    def test_GIVEN_model_run_and_parameters_WHEN_view_submit_THEN_page_is_shown_and_contains_model_run_summary(self):
        self.create_model_run_ready_for_submit()
        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.normal_body, contains_string("<h1>Submit Model Run</h1>"))
        assert_that(response.normal_body, contains_string(str(self.model_name)))
        assert_that(response.normal_body, contains_string(str(self.model_description)))
        assert_that(response.normal_body, contains_string(str(self.science_config['name'])))

        assert_that(response.normal_body, contains_string(str(self.driving_data.name)))

        assert_that(response.normal_body, contains_string(str(self.lat_n)))
        assert_that(response.normal_body, contains_string(str(self.lat_s)))
        assert_that(response.normal_body, contains_string(str(self.lon_w)))
        assert_that(response.normal_body, contains_string(str(self.lon_e)))
        assert_that(response.normal_body, contains_string(str(self.date_start.strftime("%Y-%m-%d"))))
        assert_that(response.normal_body, contains_string(str(self.date_end.strftime("%Y-%m-%d"))))

        assert_that(response.normal_body, contains_string("No land cover edits made"))

        output_variable_1 = self.model_run_service.get_output_variable_by_id(1)
        output_variable_10 = self.model_run_service.get_output_variable_by_id(10)
        assert_that(response.normal_body, contains_string(str(output_variable_1.description)))
        assert_that(response.normal_body, contains_string(str(output_variable_10.description)))
        self.assert_model_run_creation_action(self.user, 'submit')

    def test_GIVEN_land_cover_action_saved_WHEN_view_submit_page_THEN_land_cover_action_shown(self):
        self.create_model_run_ready_for_submit()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)

        with session_scope() as session:
            land_cover_cat = LandCoverRegionCategory()
            land_cover_cat.driving_dataset_id = model_run.driving_dataset_id
            land_cover_cat.name = "Rivers"

            land_cover_region = LandCoverRegion()
            land_cover_region.name = "Thames"
            land_cover_region.category = land_cover_cat

            land_cover_action = LandCoverAction()
            land_cover_action.model_run = model_run
            land_cover_action.value_id = 9
            land_cover_action.region = land_cover_region
            land_cover_action.order = 1

            session.add(land_cover_action)

        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.normal_body, contains_string("Change Thames (Rivers) to Ice"))

    def test_GIVEN_alternate_workflow_branch_followed_WHEN_reach_submit_THEN_parameter_values_the_same(self):
        # We create a model run, then simulate going back to the first page and recreating it with different options
        # Finally we again go back to the first page and recreate the original model run to check the end result is
        # the same both paths.
        self.create_model_run_ready_for_submit()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_values_start = model_run.parameter_values
        self.create_alternate_model_run()
        self.create_model_run_ready_for_submit()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_values_end = model_run.parameter_values

        # Sort by param_id
        param_values_start.sort(key=lambda pv: pv.parameter_id)
        param_values_end.sort(key=lambda pv: pv.parameter_id)

        # The two lists should match up
        assert_that(len(param_values_start), is_(len(param_values_end)))
        for i in range(len(param_values_start)):
            assert_that(param_values_start[i].parameter_id, is_(param_values_end[i].parameter_id))
            assert_that(param_values_start[i].value, is_(param_values_end[i].value))
            assert_that(param_values_start[i].group_id, is_(param_values_end[i].group_id))

    def test_GIVEN_workflow_branch_with_user_driving_data_followed_WHEN_reach_submit_THEN_parameter_values_the_same(self):
        # We create a model run, then simulate going back to the first page and recreating it with different options
        # Finally we again go back to the first page and recreate the original model run to check the end result is
        # the same both paths.
        self.create_model_run_ready_for_submit()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_values_start = model_run.parameter_values
        self.create_model_run_with_user_uploaded_driving_data()
        self.create_model_run_ready_for_submit()
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_values_end = model_run.parameter_values

        # Sort by param_id
        param_values_start.sort(key=lambda pv: pv.parameter_id)
        param_values_end.sort(key=lambda pv: pv.parameter_id)

        # The two lists should match up
        assert_that(len(param_values_start), is_(len(param_values_end)))
        for i in range(len(param_values_start)):
            assert_that(param_values_start[i].parameter_id, is_(param_values_end[i].parameter_id))
            assert_that(param_values_start[i].value, is_(param_values_end[i].value))
            assert_that(param_values_start[i].group_id, is_(param_values_end[i].group_id))