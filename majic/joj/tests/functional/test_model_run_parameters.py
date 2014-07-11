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

        user = self.login()

        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", 1)

        response = self.app.get(
            url(controller='model_run', action='parameters'))

        assert_that(response.normal_body, contains_string("timestep_len"))
