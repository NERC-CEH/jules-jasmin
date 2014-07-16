"""
#header
"""
from urlparse import urlparse
from hamcrest import assert_that, contains_string, is_
from pylons import url
from joj.tests import TestController
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService


class TestModelRunDrivingData(TestController):

    def setUp(self):
        super(TestModelRunDrivingData, self).setUp()
        self.clean_database()
        self.user = self.login()

    def _add_model_run_being_created(self):
        model_run_service = ModelRunService()
        model_run_service.update_model_run(self.user, "test", 1)

    def test_GIVEN_no_model_being_created_WHEN_page_get_THEN_redirect_to_create_model_run(self):
        response = self.app.get(
            url(controller='model_run', action='driving_data'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_two_driving_datasets_WHEN_get_THEN_select_driving_data_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string("Select Driving Data"))
        self.assert_model_run_creation_action(self.user, 'driving_data')

    def test_GIVEN_two_driving_datasets_WHEN_get_THEN_driving_datasets_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.get(
            url(controller='model_run', action='driving_data'))
        assert_that(response.normal_body, contains_string("driving1"))
        assert_that(response.normal_body, contains_string("driving2"))

    def test_GIVEN_invalid_driving_data_chosen_WHEN_post_THEN_error_returned(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': -100,
                'submit': u'Next'
            })

        assert_that(response.normal_body, contains_string("Driving data not recognised"))

    def test_GIVEN_valid_driving_data_chosen_WHEN_post_THEN_next_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='extents')), "url")

    def test_GIVEN_user_quota_exceeded_WHEN_navigate_post_to_driving_data_THEN_navigate_to_error_page(self):
        """
        On a post of data the quota should not be checked, he data should just be saved as normal
        """
        user = self.login()
        self.create_run_model(storage=user.storage_quota_in_gb * 1024 + 1, name="big_run", user=user)

        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='index')), "url")


    def test_GIVEN_valid_driving_data_chosen_WHEN_go_back_THEN_create_page_rendered(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Back'
            })

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path,
                    is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_valid_driving_data_chosen_WHEN_post_THEN_driving_data_stored_against_model_run(self):
        self._add_model_run_being_created()
        self.create_two_driving_datasets()

        dataset_service = DatasetService()
        driving_data = dataset_service.get_driving_datasets()
        ds_id = driving_data[0].id
        self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Next'
            })

        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_being_created_with_non_default_parameter_values(self.user)
        param_val = model_run.get_python_parameter_value(["JULES_DRIVE", "file"])
        assert_that(param_val, is_('testFileName'))