"""
header
"""

from hamcrest import *
from mock import Mock
from datetime import datetime
import pytz
from job_runner.model.job_status import JobStatus
from job_runner.tests import TestController
from job_runner.utils import constants
from job_runner.services.job_service import JobService
from job_runner.services.service_exception import ServiceException
from job_runner.model.log_file_parser import LogFileParser


class TestJobRunnerClient(TestController):

    def setUp(self):
        self.job_service = JobService()
        self.model_run_id = 1
        self.job_status = JobStatus(self.model_run_id)

    def test_GIVEN_run_folder_does_not_WHEN_get_job_status_THEN_job_status_failed(self):
        self.job_service.exists_run_dir = Mock(return_value=False)

        self.job_status.check(self.job_service, None)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_SUBMIT_FAILED), "Job status")

    def test_GIVEN_run_folder_does_exist_but_no_job_id_WHEN_get_job_status_THEN_job_status_failed(self):
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=None)

        self.job_status.check(self.job_service, None)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_SUBMIT_FAILED), "Job status")
        assert_that(self.job_status.error_message, is_(constants.ERROR_MESSAGE_NO_JOB_ID), "Error message")

    def test_GIVEN_job_is_pending_WHEN_get_job_status_THEN_job_status_pending(self):

        bsub_id = 10
        bjobs_list = {bsub_id: constants.MODEL_RUN_STATUS_PENDING}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        self.job_service.get_running_jobs = Mock(return_value=bjobs_list)

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_PENDING), "Job status")

    def test_GIVEN_job_is_running_WHEN_get_job_status_THEN_job_status_running(self):

        bsub_id = 10
        bjobs_list = {bsub_id: constants.MODEL_RUN_STATUS_RUNNING}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        self.job_service.get_running_jobs = Mock(return_value=bjobs_list)

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_RUNNING), "Job status")

    def test_GIVEN_job_is_not_in_list_and_log_has_success_in_WHEN_get_job_status_THEN_job_status_complete(self):

        bsub_id = 10
        bjobs_list = {}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        result = LogFileParser(None)
        result.status = constants.MODEL_RUN_STATUS_COMPLETED
        self.job_service.get_output_log_result = Mock(return_value=result)

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_COMPLETED), "Job status")

    def test_GIVEN_job_is_not_in_list_and_log_has_failed_in_WHEN_get_job_status_THEN_job_status_faield(self):

        expected_error_msg = "error"
        bsub_id = 10
        bjobs_list = {}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        result = LogFileParser(None)
        result.status = constants.MODEL_RUN_STATUS_FAILED
        result.error_message = expected_error_msg
        self.job_service.get_output_log_result = Mock(return_value=result)

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.job_status.error_message, is_(expected_error_msg), "Error message")

    def test_GIVEN_job_is_not_in_list_and_log_files_does_not_exist_WHEN_get_job_status_THEN_job_status_failed(self):

        expected_error_msg = "error"
        bsub_id = 10
        bjobs_list = {}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        self.job_service.get_output_log_result = Mock(side_effect=ServiceException(expected_error_msg))

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.job_status.error_message, is_(expected_error_msg), "Error message")

    def test_GIVEN_job_is_not_in_list_and_log_has_success_and_time_and_storage_in_WHEN_get_job_status_THEN_json_contains_storage_and_start_end_times(self):

        bsub_id = 10
        expected_storage = 1234

        bjobs_list = {}
        self.job_service.exists_run_dir = Mock(return_value=True)
        self.job_service.get_bsub_id = Mock(return_value=bsub_id)
        result = LogFileParser(None)
        result.status = constants.MODEL_RUN_STATUS_COMPLETED
        result.storage_in_mb = expected_storage
        result.start_time = datetime(2012, 01, 10, 11, 12, 13, tzinfo=pytz.utc)
        result.end_time = datetime(2013, 02, 11, 12, 1, 14, tzinfo=pytz.utc)
        self.job_service.get_output_log_result = Mock(return_value=result)

        self.job_status.check(self.job_service, bjobs_list)

        assert_that(self.job_status.start_time, is_(result.start_time), "start time")
        assert_that(self.job_status.end_time, is_(result.end_time), "start time")
        assert_that(self.job_status.storage_in_mb, is_(result.storage_in_mb), "start time")