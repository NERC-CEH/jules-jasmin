# header
from hamcrest import *
from mock import Mock

from pylons import config
from joj.tests import TestController
from joj.model import session_scope, Session, ModelRun, Dataset
from joj.services.job_status_updater import JobStatusUpdaterService
from joj.services.email_service import EmailService
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.services.model_run_service import ModelRunService
from joj.utils import output_controller_helper
from joj.tests.functional.test_model_run_submit import TestModelRunSummaryController
from joj.services.dap_client import DapClient
from joj.services.dap_client_factory import DapClientFactory


class TestJobDataUpdaterCreation(TestModelRunSummaryController):
    """
    Test for the JobDataUpdater
    """

    def setUp(self):
        super(TestJobDataUpdaterCreation, self).setUp()
        self.running_job_client = JobRunnerClient(None)
        self.email_service = EmailService()
        self.email_service.send_email = Mock()
        self.dap_client = Mock()
        self.dap_client.get_longname = Mock(return_value="long_name")
        self.dap_client.get_data_range = Mock(return_value=[10, 12])
        dap_client_factory = DapClientFactory()
        dap_client_factory.get_dap_client = Mock(return_value=self.dap_client)
        
        self.job_status_updater = JobStatusUpdaterService(
            job_runner_client=self.running_job_client,
            config=config,
            email_service=self.email_service,
            dap_client_factory=dap_client_factory)

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_THEN_model_run_data_is_in_datasets(self):

        self.create_model_run_ready_for_submit()
        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_run_being_created_or_default(self.user)
        with session_scope(Session) as session:
            model_run.change_status(session, constants.MODEL_RUN_STATUS_RUNNING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        with session_scope() as session:
            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == False)\
                .all()
            assert_that(len(datasets), is_(3), "Number of output datasets")

            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == True)\
                .all()
            assert_that(len(datasets), is_(2), "Number of input datasets")
