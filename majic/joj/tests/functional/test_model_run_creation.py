# Header
from urlparse import urlparse

from hamcrest import *
from joj.tests import *
from joj.services.model_run_service import ModelRunService
from pylons import config
from joj.utils import constants


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
                'description': u'a description'
            }
        )

        assert_that(response.normal_body, contains_string("Code version is not recognised"))

    def test_GIVEN_name_is_duplicate_WHEN_post_THEN_error_thrown(self):

        duplicate_name = u'duplicate name'
        user = self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, duplicate_name, 1, "description which is unique")
        model_run = model_run_service.get_model_run_being_created_or_default(user)
        with model_run_service.transaction_scope() as session:
            model_run.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)

        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': duplicate_name,
                'code_version': u'1',
                'description': u'a description'
            }
        )

        assert_that(response.normal_body, contains_string("Name can not be the same as another model run"))

    def test_GIVEN_name_is_duplicate_but_run_is_owned_by_another_user_WHEN_post_THEN_success(self):

        duplicate_name = u'duplicate name'
        user = self.login("test_different")
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, duplicate_name, 1, "description which is unique")
        model_run = model_run_service.get_model_run_being_created_or_default(user)
        with model_run_service.transaction_scope() as session:
            model_run.change_status(session, constants.MODEL_RUN_STATUS_COMPLETED)

        user = self.login("test")
        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': duplicate_name,
                'code_version': u'1',
                'description': u'a description'
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='parameters')), "url")

    def test_GIVEN_details_are_correct_WHEN_post_THEN_new_model_run_created_and_redirect_to_parameters_page(self):

        expected_name = u'name'
        expected_code_version = 1
        expected_description = u'This is a description'
        self.login()
        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': expected_name,
                'code_version': str(expected_code_version),
                'description': expected_description
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='parameters')), "url")

        self.assert_model_definition(self.login_username, expected_code_version, expected_name, expected_description)

    def test_GIVEN_model_already_being_created_WHEN_navigate_to_create_run_THEN_model_data_filled_in(self):

        user = self.login()

        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, 'test', 1, "description which is unique")

        response = self.app.get(
            url(controller='model_run', action='create'))

        assert_that(response.normal_body, contains_string("test"))
        assert_that(response.normal_body, contains_string(config['default_code_version']))
        assert_that(response.normal_body, contains_string("description which is unique"))

    def test_GIVEN_model_already_being_created_WHEN_update_THEN_model_data_overwritten(self):

        user = self.login()
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, 'not test', 2, "a different description")

        expected_name = u'name'
        expected_code_version = 1
        expected_description = u'descr'

        response = self.app.post(
            url=url(controller='model_run', action='create'),
            params={
                'name': expected_name,
                'code_version': str(expected_code_version),
                'description': expected_description
            }
        )

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='parameters')), "url")

        self.assert_model_definition(self.login_username, expected_code_version, expected_name,expected_description)

