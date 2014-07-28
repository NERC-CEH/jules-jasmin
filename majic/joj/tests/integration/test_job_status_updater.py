# header
from datetime import datetime, timedelta
from hamcrest import *
from mock import Mock
from pylons import config
import pytz

from joj.tests import TestController
from joj.model import session_scope, Session, ModelRun, Dataset
from joj.services.job_status_updater import JobStatusUpdaterService
from joj.services.email_service import EmailService
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.model import session_scope, Session, ModelRun, SystemAlertEmail


class TestJobDataUpdater(TestController):
    """
    Test for the JobDataUpdater
    """

    def setUp(self):
        super(TestJobDataUpdater, self).setUp()
        self.clean_database()
        self.running_job_client = JobRunnerClient([])
        self.email_service = EmailService()
        self.email_service.send_email = Mock()

        self.job_status_updater = JobStatusUpdaterService(
            job_runner_client=self.running_job_client,
            config=config,
            email_service=self.email_service,
            dap_client_factory=self.create_mock_dap_factory_client())
        self.user = self.login()

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_THEN_model_run_is_set_to_complete_and_email_sent(self):
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)

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
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)

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
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)
        model_run2 = self.create_run_model(status=constants.MODEL_RUN_STATUS_RUNNING, name="test", user=self.user, storage_in_mb=10)

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
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_SUBMITTED, name="test", user=self.user, storage_in_mb=10)
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
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_RUNNING,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_RUNNING)
        assert_that(self.email_service.send_email.called, is_(False), "An email has been sent")

    def test_GIVEN_one_pending_job_in_the_database_which_has_become_unknown_WHEN_update_THEN_model_run_is_set_to_unknown_and_email_sent(self):
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_UNKNOWN,
                           'error_message': 'error'
                           }])

        self.job_status_updater.update()

        self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_UNKNOWN)
        assert_that(self.email_service.send_email.called, is_(True), "An email has been sent")

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_THEN_model_runs_start_time_end_time_and_storage_are_set(self):
        model_run = self.create_run_model(status=constants.MODEL_RUN_STATUS_PENDING, name="test", user=self.user, storage_in_mb=10)
        expected_storage = 10

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': '',
                           'start_time': "2014-07-16 16:33:30",
                           'end_time': "2014-07-17 12:07:46",
                           'storage_in_mb': expected_storage
                           }])

        self.job_status_updater.update()

        model_run = self.assert_model_run_status_and_return(model_run.id, constants.MODEL_RUN_STATUS_COMPLETED)
        assert_that(model_run.storage_in_mb, is_(expected_storage), "storage")
        assert_that(model_run.date_started, is_(datetime(2014, 7, 16, 16, 33, 30)), "start time")
        assert_that(model_run.time_elapsed_secs, is_(70456), "time elapsed in s")

    def test_GIVEN_quota_is_exceeded_and_email_not_sent_recently_WHEN_update_THEN_email_sent_and_marked_in_table(self):
        model_run = self.create_run_model(
            status=constants.MODEL_RUN_STATUS_PENDING,
            name="test",
            user=self.user,
            storage_in_mb=10)
        expected_storage = int(config['storage_quota_total_GB']) * 1024 + 1

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_RUNNING,
                           'error_message': '',
                           'start_time': "2014-07-16 16:33:30",
                           'end_time': "2014-07-17 12:07:46",
                           'storage_in_mb': expected_storage
                           }])

        self.job_status_updater.update()

        with session_scope(Session) as session:
            email = session.query(SystemAlertEmail) \
                .filter(SystemAlertEmail.code == SystemAlertEmail.GROUP_SPACE_FULL_ALERT) \
                .one()

        assert_that(email.last_sent, is_not(None), "date email sent")
        assert_that(self.email_service.send_email.called, is_(True), "An email has been sent")

    def test_GIVEN_quota_is_not_exceeded_and_email_not_sent_recently_WHEN_update_THEN_email_not_sent_and_marked_in_table(self):
        model_run = self.create_run_model(
            status=constants.MODEL_RUN_STATUS_PENDING,
            name="test",
            user=self.user,
            storage_in_mb=0)
        expected_storage = 10

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_RUNNING,
                           'error_message': '',
                           'start_time': "2014-07-16 16:33:30",
                           'end_time': "2014-07-17 12:07:46",
                           'storage_in_mb': expected_storage
                           }])

        self.job_status_updater.update()

        with session_scope(Session) as session:
            email = session.query(SystemAlertEmail) \
                .filter(SystemAlertEmail.code == SystemAlertEmail.GROUP_SPACE_FULL_ALERT) \
                .one()

        assert_that(email.last_sent, is_(None), "date email sent")
        assert_that(self.email_service.send_email.called, is_(False), "An email has been sent")

    def test_GIVEN_quota_is_exceeded_and_email_sent_recently_WHEN_update_THEN_email_not_sent(self):
        model_run = self.create_run_model(
            status=constants.MODEL_RUN_STATUS_PENDING,
            name="test",
            user=self.user,
            storage_in_mb=10)
        expected_storage = int(config['storage_quota_total_GB']) * 1024 + 1

        with session_scope(Session) as session:
            email = session.query(SystemAlertEmail) \
                .filter(SystemAlertEmail.code == SystemAlertEmail.GROUP_SPACE_FULL_ALERT) \
                .one()
            email.last_sent = datetime.now() - timedelta(seconds=60)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_RUNNING,
                           'error_message': '',
                           'start_time': "2014-07-16 16:33:30",
                           'end_time': "2014-07-17 12:07:46",
                           'storage_in_mb': expected_storage
                           }])

        self.job_status_updater.update()

        with session_scope(Session) as session:
            email = session.query(SystemAlertEmail) \
                .filter(SystemAlertEmail.code == SystemAlertEmail.GROUP_SPACE_FULL_ALERT) \
                .one()

        assert_that(self.email_service.send_email.called, is_(False), "An email has been sent")
