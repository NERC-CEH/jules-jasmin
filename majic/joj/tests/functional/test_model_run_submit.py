# Header
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.model import User
from joj.model import Session
from joj.utils import constants
from joj.services.general import DatabaseService
from joj.services.model_run_service import ModelRunService
from joj.services.user import UserService
from pylons import config
from joj.model import meta


class TestModelRunSummaryController(TestController):

    def setUp(self):
        super(TestModelRunSummaryController, self).setUp()
        self.clean_database()

    def test_GIVEN_no_defining_model_WHEN_navigate_to_summary_THEN_redirect_to_create_model_run(self):

        self.login()

        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")


    def test_GIVEN_model_run_and_parameters_WHEN_view_submit_THEN_page_is_shown_and_contains_model_run_summary(self):

        user = self.login()

        model_run_service = ModelRunService()
        expected_model_name="test model name"
        model_run_service.update_model_run(user, expected_model_name, 1)
        expected_value = 123456789
        model_run_service.store_parameter_values({'1': expected_value}, user)

        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.normal_body, contains_string("<h2>Submit</h2>"))
        assert_that(response.normal_body, contains_string(expected_model_name))
        assert_that(response.normal_body, contains_string("timestep_len"))
        assert_that(response.normal_body, contains_string(str(expected_value)))

    def test_GIVEN_select_previous_WHEN_post_THEN_redirect_to_parameters_page(self):

        user = self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)
        model_run_service.store_parameter_values({'1': 12}, user)

        response = self.app.post(
            url=url(controller='model_run', action='submit'),
            params={
                'submit': u'Previous'
            }
        )

        assert_that(response.status_code, is_(302), "Respose is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='parameters')), "url")

    def test_GIVEN_select_submit_WHEN_post_THEN_redirect_to_index_page_job_submitted(self):

        user = self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)
        model_run_service.store_parameter_values({'1': 12}, user)

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
            """
        ).one()
        assert_that(row.name, is_(constants.MODEL_RUN_STATUS_SUBMIT_FAILED), "model run status")

