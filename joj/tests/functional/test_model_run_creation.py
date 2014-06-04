# Header
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from model import User
from joj.model import Session
from services.general import DatabaseService
from services.user import UserService
from pylons import config
from joj.model import meta

class TestModelRunController(TestController):

    def setUp(self):
        super(TestModelRunController, self).setUp()
        self.clean_database()

    def test_GIVEN_nothing_WHEN_navigate_to_create_run_THEN_create_run_page_shown(self):

        self.login()

        response = self.app.get(
            url(controller='model_run', action='create'))
        assert_that(response.normal_body, contains_string("Create Model Run"))
        assert_that(response.normal_body, contains_string("Name"))
        assert_that(response.normal_body, contains_string("Code"))
        assert_that(response.normal_body, contains_string(config['default_code_version']))

        assert_that(response.normal_body, contains_string("Next"))

    def test_GIVEN_model_run_has_no_name_WHEN_post_THEN_error_thrown(self):

        self.login()

        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': u'',
                'code_version': u'a version',
            }
        )

        assert_that(response.normal_body, contains_string("Please enter a value"))

    def test_GIVEN_code_version_is_blank_WHEN_post_THEN_error_thrown(self):

        self.login()
        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': u'name',
                'code_version': u'',
            }
        )

        assert_that(response.normal_body, contains_string("Please enter a value"))

    def test_GIVEN_code_version_is_invalid_WHEN_post_THEN_error_thrown(self):

        self.login()
        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': u'name',
                'code_version': u'-10',
            }
        )

        assert_that(response.normal_body, contains_string("Code version is not recognised"))

    def test_GIVEN_details_are_correct_WHEN_post_THEN_new_model_run_created_and_redirect_to_parameters_page(self):

        expected_name = u'name'
        expected_code_version = 1
        self.login()
        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': expected_name,
                'code_version': str(expected_code_version)
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='parameters')), "url")

        session = Session()
        row = session.query("name", "code_version_id").from_statement(
            """
            SELECT m.name, m.code_version_id
            FROM model_runs m
            JOIN model_run_statuses s on s.id = m.status_id
            WHERE s.name=:status
            """
        ).params(status="Defining").one()

        assert_that(row.name, is_(expected_name), "model run name")
        assert_that(row.code_version_id, is_(expected_code_version), "code version")


