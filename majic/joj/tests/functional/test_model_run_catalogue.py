"""
# Header
"""
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.services.model_run_service import ModelRunService
from joj.utils import constants


class TestModelRunCatalogue(TestController):

    def setUp(self):
        super(TestModelRunCatalogue, self).setUp()
        self.clean_database()

    def test_GIVEN_nothing_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_shown(self):

        user = self.login()
        model1_storage = 10101
        model2_storage = 6400
        total = 16.1  # 16501/1024
        percent_used = 16  # 16.1 / 100 (storage for user) rounded
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)
        with model_run_service.transaction_scope() as session:
            model = model_run_service.get_model_run_being_created_or_default(user)
            model.storage_in_mb = model1_storage
            model.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)

        model_run_service.update_model_run(user, "test2", 1)
        with model_run_service.transaction_scope() as session:
            model = model_run_service.get_model_run_being_created_or_default(user)
            model.storage_in_mb = model2_storage
            model.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)

        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("Model Runs"))
        assert_that(response.normal_body, contains_string(str(user.storage_quota_in_gb)))
        assert_that(response.normal_body, contains_string(str(total)))
        assert_that(response.normal_body, contains_string(str(percent_used)))
        assert_that(response.normal_body, contains_string("bar-success"))

    def test_GIVEN_90_percent_of_space_user_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_orange(self):

        user = self.login()
        model1_storage = 90000
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)
        with model_run_service.transaction_scope() as session:
            model = model_run_service.get_model_run_being_created_or_default(user)
            model.storage_in_mb = model1_storage
            model.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)


        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("bar-warning"))

    def test_GIVEN_110_percent_of_space_user_WHEN_navigate_to_run_catalogue_THEN_user_storage_allocation_is_orange(self):

        user = self.login()
        model1_storage = 110000
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)
        with model_run_service.transaction_scope() as session:
            model = model_run_service.get_model_run_being_created_or_default(user)
            model.storage_in_mb = model1_storage
            model.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)


        response = self.app.get(
            url(controller='model_run', action=''))

        assert_that(response.normal_body, contains_string("bar-danger"))