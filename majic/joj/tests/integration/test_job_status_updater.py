# header
from hamcrest import assert_that, is_
from mock import Mock
from pylons import config

from joj.tests import TestController
from joj.model import session_scope, Session, ModelRun, Dataset
from joj.services.job_status_updater import JobStatusUpdaterService
from joj.services.email_service import EmailService
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient


class TestJobDataUpdater(TestController):
    """
    Test for the JobDataUpdater
    """

    def setUp(self):
        super(TestJobDataUpdater, self).setUp()
        self.clean_database()
        self.running_job_client = JobRunnerClient(None)
        self.email_service = EmailService()
        self.email_service.send_email = Mock()
        self.job_status_updater = JobStatusUpdaterService(
            job_runner_client=self.running_job_client,
            config=config,
            email_service=self.email_service)
        self.user = self.login()

    def create_model(self, status_pending):
        with session_scope(Session) as session:
            model_run = ModelRun()
            model_run.user = self.user
            model_run.change_status(session, status_pending)

        return model_run

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_THEN_model_run_is_set_to_complete_and_email_sent(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_PENDING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_COMPLETED)
        assert_that(self.email_service.send_email.called, is_(True), "An email has been sent")

    def test_GIVEN_no_pending_jobs_in_the_database_WHEN_update_THEN_job_client_is_not_called(self):
        self.running_job_client.get_run_model_statuses = \
            Mock(side_effect=AssertionError("get_run_model_statuses should not be called for no jobs"))

        self.job_status_updater.update()
        assert_that(self.email_service.send_email.called, is_(False), "An email has been sent")

    def test_GIVEN_one_pending_job_in_the_database_and_job_service_returns_two_WHEN_update_THEN_model_run_is_set_to_complete(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_PENDING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id + 1,
                           'status': constants.MODEL_RUN_STATUS_UNKNOWN,
                           'error_message': ''
                           },
                          {'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_COMPLETED)

    def test_GIVEN_two_job_in_the_database_and_job_service_returns_one_running_one_complete_WHEN_update_THEN_models_are_set_correctly(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_PENDING)
        model_run2 = self.create_model(constants.MODEL_RUN_STATUS_RUNNING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run2.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           },
                          {'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_FAILED,
                           'error_message': 'error'
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_FAILED)
        self.assert_model_run_status_and_return(model_run2.id, constants.MODEL_RUN_STATUS_COMPLETED)

    def test_GIVEN_one_submitted_job_in_the_database_and_job_service_returns_error_WHEN_update_THEN_model_run_is_set_to_error_with_messsage(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_SUBMITTED)
        expected_error = "error"

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_FAILED,
                           'error_message': expected_error
                           }])

        self.job_status_updater.update()

        model_run = self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_FAILED)
        assert_that(model_run.error_message, is_(expected_error), "error message")
        assert_that(self.email_service.send_email.called, is_(True), "An email has been sent")

    def test_GIVEN_one_pending_job_in_the_database_which_has_become_running_WHEN_update_THEN_model_run_is_set_to_running_and_no_email_sent(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_PENDING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_RUNNING,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_RUNNING)
        assert_that(self.email_service.send_email.called, is_(False), "An email has been sent")

    def test_GIVEN_one_pending_job_in_the_database_which_has_become_unknown_WHEN_update_THEN_model_run_is_set_to_unknown_and_email_sent(self):
        model_run = self.create_model(constants.MODEL_RUN_STATUS_PENDING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_UNKNOWN,
                           'error_message': 'error'
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_UNKNOWN)
        assert_that(self.email_service.send_email.called, is_(True), "An email has been sent")