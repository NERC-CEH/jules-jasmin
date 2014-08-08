# header
from datetime import datetime
import pytz

from hamcrest import *
from mock import Mock
from job_runner.model.job_status import JobStatus
from job_runner.tests import TestController
from job_runner.utils import constants
from job_runner.services.job_service import JobService
from job_runner.model.log_file_parser import LogFileParser

class TestJulesLogFileParser(TestController):

    def setUp(self):
        self.lines = []
        self.parser = LogFileParser(self.lines)


    def test_GIVEN_empty_file_WHEN_parse_THEN_job_status_failed(self):

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, is_(constants.ERROR_MESSAGE_OUTPUT_IS_EMPTY), "error message")

    def test_GIVEN_file_contains_success_WHEN_parse_THEN_job_status_success(self):
        self.lines.extend(['random line', 'blah', ' foo' + constants.JULES_RUN_COMPLETED_MESSAGE + 'bah', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_COMPLETED), "Job status")

    def test_GIVEN_file_does_not_contain_success_WHEN_parse_THEN_job_status_failed(self):
        self.lines.extend(['random line', 'blah', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, is_(constants.ERROR_MESSAGE_UNKNOWN_JULES_ERROR), "error message")

    def test_GIVEN_file_does_not_contain_success_AND_HAS_fatal_error_inWHEN_parse_THEN_job_status_failed_error_message_is_fatal_error(self):
        expected_error = 'init_output: Output directory does not exist'
        self.lines.extend(['random line', '[FATAL ERROR] ' + expected_error, 'foo again'])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, is_("Jules error:" + expected_error), "error message")

    def test_GIVEN_file_does_not_contain_success_and_has_multiple_fatal_error_inWHEN_parse_THEN_job_status_failed_error_message_is_fatal_error(self):
        expected_error1 = 'init_output:'
        expected_error2 = 'Output directory does not exist'
        self.lines.extend(['random line', '[FATAL ERROR] ' + expected_error1, '[FATAL ERROR] ' + expected_error2,'foo again'])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, is_("Jules error:" + expected_error1 + ', ' + expected_error2), "error message")

    def test_GIVEN_file_contains_start_time_WHEN_parse_THEN_start_time_included(self):
        self.lines.extend(['random line', 'blah', 'Start Time: 2014-07-16 16:33:30 +0000', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.start_time, is_(datetime(2014, 07, 16, 16, 33, 30, tzinfo=pytz.utc)), "start time")

    def test_GIVEN_file_contains_invalid_start_time_WHEN_parse_THEN_start_time_is_none(self):
        self.lines.extend(['random line', 'blah', 'Start Time: 2014-blah-16 16:33:30 +0000', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.start_time, is_(None), "start time")

    def test_GIVEN_file_contains_end_time_WHEN_parse_THEN_start_time_included(self):
        self.lines.extend(['random line', 'blah', 'End Time: 2014-07-16 16:33:30 +0000', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.end_time, is_(datetime(2014, 07, 16, 16, 33, 30, tzinfo=pytz.utc)), "end time")

    def test_GIVEN_file_contains_invalid_end_time_WHEN_parse_THEN_start_time_is_none(self):
        self.lines.extend(['random line', 'blah', 'End Time: 2014-blah-16 16:33:30 +0000', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.end_time, is_(None), "end time")

    def test_GIVEN_file_contains_storage_WHEN_parse_THEN_storage_set(self):
        self.lines.extend(['random line', 'blah', 'Storage MB: 256   .', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.storage_in_mb, is_(256), "storage")

    def test_GIVEN_file_contains_invalid_storage_WHEN_parse_THEN_storage_is_0(self):
        self.lines.extend(['random line', 'blah', 'Storage MB: nan   .', 'foo again'])

        self.parser.parse()

        assert_that(self.parser.storage_in_mb, is_(0), "storage")

    def test_GIVEN_file_does_not_contain_success_and_has_multiple_fatal_errors_from_different_processors_WHEN_parse_THEN_job_status_failed_error_message_is_fatal_error(self):
        expected_error = 'init_output'
        self.lines.extend(['random line', '{MPI Task 1}[FATAL ERROR] ' + expected_error,
                           '{MPI Task 0}[FATAL ERROR] ' + expected_error, 'foo again'])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, is_("Jules error:" + expected_error + ', ' + expected_error), "error message")

    def test_GIVEN_file_contains_success_and_post_processing_error_WHEN_parse_THEN_job_status_failed(self):
        expected_error = "error line"
        self.lines.extend(['blah', ' foo' + constants.JULES_RUN_COMPLETED_MESSAGE + 'bah', 'foo again', '{MPI}'+ constants.JULES_POST_PROCESS_ERROR_PREFIX + expected_error])

        self.parser.parse()

        assert_that(self.parser.status, is_(constants.MODEL_RUN_STATUS_FAILED), "Job status")
        assert_that(self.parser.error_message, contains_string(expected_error), "error line")
