"""
header
"""
import datetime
from mock import Mock
from joj.tests import *
from joj.services.dataset import DatasetService
from joj.services.model_run_service import ModelRunService
from joj.services.job_status_updater import JobStatusUpdaterService
from joj.services.email_service import EmailService
from joj.services.job_runner_client import JobRunnerClient
from pylons import config


class TestWithFullModelRun(TestController):
    """
    Test class which includes a way of submiting the whole model run
    """

    def setUp(self):
        super(TestWithFullModelRun, self).setUp()
        self.running_job_client = JobRunnerClient([])
        self.email_service = EmailService()
        self.email_service.send_email = Mock()

        self.job_status_updater = JobStatusUpdaterService(
            job_runner_client=self.running_job_client,
            config=config,
            email_service=self.email_service,
            dap_client_factory=self.create_mock_dap_factory_client())

        self.clean_database()
        self.user = self.login()
        self.model_run_service = ModelRunService()

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
                          'site': u'multi',
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
                          'site': u'single',
                          'lat': self.lat_n,
                          'lon': self.lon_e,
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