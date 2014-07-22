# header
from hamcrest import *
from mock import Mock

from joj.model import session_scope, Session, ModelRun, Dataset
from joj.utils import constants
from joj.services.model_run_service import ModelRunService
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.services.dap_client import DapClientException


class TestJobDataUpdaterCreation(TestWithFullModelRun):
    """
    Test for the JobDataUpdater
    """

    def setUp(self):
        super(TestJobDataUpdaterCreation, self).setUp()

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

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_dap_client_not_availiable_THEN_model_run_status_is_not_updated(self):

        self.dap_client_factory.get_dap_client = Mock(side_effect=DapClientException("trouble"))
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

        model_run = model_run_service.get_model_by_id(self.user, model_run.id)
        assert_that(model_run.status.name, is_(constants.MODEL_RUN_STATUS_RUNNING), "model status")
        with session_scope() as session:
            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == False)\
                .all()
            assert_that(len(datasets), is_(0), "Number of output datasets")

            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == True)\
                .all()
            assert_that(len(datasets), is_(0), "Number of input datasets")