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
        response = self.app.post(url=url(controller='model_run', action='create'),
                                 params={
                                     'name': self.model_name,
                                     'science_configuration': str(model_science_config_id),
                                     'description': self.model_description
                                 })
        assert response.status_code == 302
        # The Driving Data page
        self.create_two_driving_datasets()
        dataset_service = DatasetService()
        driving_datasets = dataset_service.get_driving_datasets(self.user)
        self.driving_data = [dds for dds in driving_datasets if dds.name == "driving1"][0]
        response = self.app.post(url(controller='model_run', action='driving_data'),
                                 params={
                                     'driving_dataset': self.driving_data.id,
                                     'submit': u'Next'
                                 })
        assert response.status_code == 302
        # The Extents page
        self.lat_n, self.lat_s = 40, 0
        self.lon_w, self.lon_e = -15, 15
        self.date_start = datetime.datetime(1980, 1, 1, 0, 0, 0)
        self.date_end = datetime.datetime(1980, 1, 1, 0, 0, 0)
        response = self.app.post(url(controller='model_run', action='extents'),
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
        assert response.status_code == 302
        # The Output Variables page
        response = self.app.post(url(controller='model_run', action='output'),
                                 params={
                                     'submit': u'Next',
                                     'ov_select_1': 1,
                                     'ov_timestep_1': 1,
                                     'ov_select_10': 1,
                                     'ov_yearly_10': 1,
                                     'ov_monthly_10': 1
                                 })
        assert response.status_code == 302

    def create_alternate_model_run(self):
        # Set up the model as if we'd gone through all the previous pages
        # (but differently to the other model)
        # The Create page
        self.model_name = u'alternate name'
        self.model_description = u'This is a description of another model_run'
        self.science_config = self.model_run_service.get_scientific_configurations()[2]
        model_science_config_id = self.science_config['id']
        response = self.app.post(url=url(controller='model_run', action='create'),
                                 params={
                                     'name': self.model_name,
                                     'science_configuration': str(model_science_config_id),
                                     'description': self.model_description
                                 })
        assert response.status_code == 302
        # The Driving Data page
        self.create_two_driving_datasets()
        dataset_service = DatasetService()
        driving_datasets = dataset_service.get_driving_datasets(self.user)
        self.driving_data = [dds for dds in driving_datasets if dds.name == "driving2"][0]
        response = self.app.post(url(controller='model_run', action='driving_data'),
                                 params={
                                     'driving_dataset': self.driving_data.id,
                                     'submit': u'Next'
                                 })
        assert response.status_code == 302
        # The Extents page
        self.lat_n, self.lat_s = 80, -75
        self.lon_w, self.lon_e = -100, 120
        self.date_start = datetime.datetime(1907, 1, 1, 0, 0, 0)
        self.date_end = datetime.datetime(1914, 1, 1, 0, 0, 0)
        response = self.app.post(url(controller='model_run', action='extents'),
                                 params={
                                     'submit': u'Next',
                                     'site': u'single',
                                     'lat': self.lat_n,
                                     'lon': self.lon_e,
                                     'start_date': self.date_start.strftime("%Y-%m-%d"),
                                     'end_date': self.date_end.strftime("%Y-%m-%d")
                                 })
        assert response.status_code == 302
        # The Output Variables page
        response = self.app.post(url(controller='model_run', action='output'),
                                 params={
                                     'submit': u'Next',
                                     'ov_select_6': 1,
                                     'ov_timestep_6': 1,
                                     'ov_monthly_6': 1,
                                     'ov_select_11': 1,
                                     'ov_yearly_11': 1,
                                     'ov_monthly_11': 1
                                 })
        assert response.status_code == 302

    def create_model_run_with_user_uploaded_driving_data(self):
        # Set up the model as if we'd gone through all the previous pages
        # and uploaded our own driving data
        # The Create page
        self.model_name = u'Run with my own driving data'
        self.model_description = u'This is a description of a model_run'
        self.science_config = self.model_run_service.get_scientific_configurations()[2]
        model_science_config_id = self.science_config['id']
        response = self.app.post(url=url(controller='model_run', action='create'),
                                 params={
                                     'name': self.model_name,
                                     'science_configuration': str(model_science_config_id),
                                     'description': self.model_description
                                 })
        assert response.status_code == 302
        # The Driving Data page
        self.sample_file_contents = "# solar   long  rain  snow    temp   wind     press      humid\n" \
                                    "# sw_down   lw_down  tot_rain  tot_snow    t   wind     pstar      q\n" \
                                    "# i   i  i  i    i   i     i      i\n" \
                                    "3.3  187.8   0.0   0.0  259.10  3.610  102400.5  1.351E-03\n" \
                                    "89.5  185.8   0.0   0.0  259.45  3.140  102401.9  1.357E-03\n" \
                                    "142.3  186.4   0.0   0.0  259.85  2.890  102401.0  1.369E-03\n" \
                                    "# ----- data for later times ----"
        data_service = DatasetService()
        self.create_two_driving_datasets()
        ds_id = data_service.get_id_for_user_upload_driving_dataset()
        response = self.app.post(
            url(controller='model_run', action='driving_data'),
            params={
                'driving_dataset': ds_id,
                'submit': u'Upload',
                'lat': u'55',
                'lon': u'45',
                'dt_start': u'2000-01-01 00:00',
                'dt_end': u'2000-01-01 02:00'},
            upload_files=[('driving-file', 'file.txt', self.sample_file_contents)]
        )
        assert response.status_code == 302
        # The Extents page
        self.lat_n, self.lat_s = 55, 55
        self.lon_w, self.lon_e = 45, 45
        self.date_start = datetime.datetime(2000, 1, 1, 0, 0, 0)
        self.date_end = datetime.datetime(2000, 1, 1, 0, 2, 0)
        response = self.app.post(url(controller='model_run', action='extents'),
                                 params={
                                     'submit': u'Next',
                                     'site': u'single',
                                     'lat': self.lat_n,
                                     'lon': self.lon_e,
                                     'start_date': self.date_start.strftime("%Y-%m-%d"),
                                     'end_date': self.date_end.strftime("%Y-%m-%d")
                                 })
        assert response.status_code == 302
        # The Output Variables page
        response = self.app.post(url(controller='model_run', action='output'),
                                 params={
                                     'submit': u'Next',
                                     'ov_select_6': 1,
                                     'ov_timestep_6': 1,
                                     'ov_monthly_6': 1,
                                     'ov_select_11': 1,
                                     'ov_yearly_11': 1,
                                     'ov_monthly_11': 1
                                 })
        assert response.status_code == 302