# Header
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from model import User
from joj.model import Session
from joj.utils import constants
from services.general import DatabaseService
from services.model_run_service import ModelRunService
from services.user import UserService
from pylons import config
from joj.model import meta

class TestModelRunParametersController(TestController):

    def setUp(self):
        super(TestModelRunParametersController, self).setUp()
        self.clean_database()

    def test_GIVEN_no_defining_model_WHEN_navigate_to_parameters_THEN_redirect_to_create_model_run(self):

        self.login()

        response = self.app.get(
            url(controller='model_run', action='parameters'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")


    def test_GIVEN_model_run_WHEN_view_THEN_parameter_for_code_version_is_shown(self):

        self.login()

        model_run_service = ModelRunService()
        model_run_service.update_model_run("test", 1)

        response = self.app.post(
            url=url(controller='model_run', action='parameters')
        )

        assert_that(response.normal_body, contains_string("timestep_len"))

    def test_GIVEN_parameter_blank_WHEN_post_THEN_error_shown(self):

        self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run("test", 1)

        response = self.app.post(
            url=url(controller='model_run', action='parameters'),
            params={
                'submit': 'Next',
                'param1': ''
            }
        )

        assert_that(response.normal_body, contains_string("Please enter a value"))

    def test_GIVEN_details_are_correct_WHEN_post_THEN_new_parameters_saved_and_redirect_to_summary_page(self):

        expected_parameter = u'2'

        self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run("test", 1)

        response = self.app.post(
            url=url(controller='model_run', action='parameters'),
            params={
                'param1': expected_parameter,
                'submit': u'Next'
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='summary')), "url")

        self.assert_parameter_of_model_being_created_is_a_value(1, expected_parameter)

    def test_GIVEN_already_have_details_WHEN_post_THEN_new_parameters_overwrite_old_details(self):

        expected_parameter = u'2'

        self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run("test", 1)
        model_run_service.store_parameter_values({'1': 1})

        response = self.app.post(
            url=url(controller='model_run', action='parameters'),
            params={
                'param1': expected_parameter,
                'submit': u'Next'
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='summary')), "url")

        self.assert_parameter_of_model_being_created_is_a_value(1, expected_parameter)
