"""
# Header
"""
from urlparse import urlparse
import datetime

from hamcrest import *
from joj.tests import *
from joj.model import Session
from joj.utils import constants
from joj.services.model_run_service import ModelRunService
from joj.services.dataset import DatasetService


class TestModelRunSummaryController(TestController):
    def setUp(self):
        super(TestModelRunSummaryController, self).setUp()
        self.clean_database()
        self.user = self.login()
        self.model_run_service = ModelRunService()

    def test_GIVEN_no_defining_model_WHEN_navigate_to_summary_THEN_redirect_to_create_model_run(self):
        response = self.app.get(
            url(controller='model_run', action='submit'))

        assert_that(response.status_code, is_(302), "Response is redirect")
        assert_that(urlparse(response.response.location).path, is_(url(controller='model_run', action='create')), "url")

    def test_GIVEN_select_previous_WHEN_post_THEN_redirect_to_output_page(self):
        self.model_run_service.update_model_run(self.user, "test", 1)
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

    def test_GIVEN_select_submit_WHEN_post_THEN_redirect_to_index_page_job_submitted(self):
        self.model_run_service.update_model_run(self.user, "test", 1)
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

        output_variable_1 = self.model_run_service.get_output_variable_by_id(1)
        output_variable_10 = self.model_run_service.get_output_variable_by_id(10)
        assert_that(response.normal_body, contains_string(str(output_variable_1.name)))
        assert_that(response.normal_body, contains_string(str(output_variable_10.name)))

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

    def create_model_run_ready_for_submit(self):
        # Set up the model as if we'd gone through all the previous pages
        # The Create page
        self.model_name = u'name'
        self.model_description = u'This is a description'
        self.science_config = self.model_run_service.get_scientific_configurations()[0]
        model_science_config_id = self.science_config['id']
        self.app.post(url=url(controller='model_run', action='create'),
                      params={
                          'name': self.model_name,
                          'science_configuration': str(model_science_config_id),
                          'description': self.model_description
                      })
        # The Driving Data page
        self.create_two_driving_datasets()
        dataset_service = DatasetService()
        self.driving_data = dataset_service.get_driving_datasets()[0]
        ds_id = self.driving_data.id
        self.app.post(url(controller='model_run', action='driving_data'),
                      params={
                          'driving_dataset': ds_id,
                          'submit': u'Next'
                      })
        # The Extents page
        self.lat_n, self.lat_s = 40, 0
        self.lon_w, self.lon_e = -15, 15
        self.date_start = datetime.datetime(1980, 1, 1, 0, 0, 0)
        self.date_end = datetime.datetime(1980, 1, 1, 0, 0, 0)
        self.app.post(url(controller='model_run', action='extents'),
                      params={
                          'submit': u'Next',
                          'lat_n': self.lat_n,
                          'lat_s': self.lat_s,
                          'lon_e': self.lon_e,
                          'lon_w': self.lon_w,
                          'start_date': self.date_start.strftime("%Y-%m-%d"),
                          'end_date': self.date_end.strftime("%Y-%m-%d")
                      })
        # The Output Variables page
        self.app.post(url(controller='model_run', action='output'),
                      params={
                          'submit': u'Next',
                          'ov_select_1': 1,
                          'ov_timestep_1': 1,
                          'ov_select_10': 1,
                          'ov_yearly_10': 1,
                          'ov_monthly_10': 1
                      })

    def create_alternate_model_run(self):
        # Set up the model as if we'd gone through all the previous pages
        # (but differently to the other model)
        # The Create page
        self.model_name = u'alternate name'
        self.model_description = u'This is a description of another model_run'
        self.science_config = self.model_run_service.get_scientific_configurations()[2]
        model_science_config_id = self.science_config['id']
        self.app.post(url=url(controller='model_run', action='create'),
                      params={
                          'name': self.model_name,
                          'science_configuration': str(model_science_config_id),
                          'description': self.model_description
                      })
        # The Driving Data page
        self.create_two_driving_datasets()
        dataset_service = DatasetService()
        self.driving_data = dataset_service.get_driving_datasets()[1]
        ds_id = self.driving_data.id
        self.app.post(url(controller='model_run', action='driving_data'),
                      params={
                          'driving_dataset': ds_id,
                          'submit': u'Next'
                      })
        # The Extents page
        self.lat_n, self.lat_s = 80, -75
        self.lon_w, self.lon_e = -100, 120
        self.date_start = datetime.datetime(1907, 1, 1, 0, 0, 0)
        self.date_end = datetime.datetime(1914, 1, 1, 0, 0, 0)
        self.app.post(url(controller='model_run', action='extents'),
                      params={
                          'submit': u'Next',
                          'lat_n': self.lat_n,
                          'lat_s': self.lat_s,
                          'lon_e': self.lon_e,
                          'lon_w': self.lon_w,
                          'start_date': self.date_start.strftime("%Y-%m-%d"),
                          'end_date': self.date_end.strftime("%Y-%m-%d")
                      })
        # The Output Variables page
        self.app.post(url(controller='model_run', action='output'),
                      params={
                          'submit': u'Next',
                          'ov_select_6': 1,
                          'ov_timestep_6': 1,
                          'ov_monthly_6': 1,
                          'ov_select_11': 1,
                          'ov_yearly_11': 1,
                          'ov_monthly_11': 1
                      })
