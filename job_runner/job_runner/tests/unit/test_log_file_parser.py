# header
from formencode import Invalid


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
        assert_that(self.parser.error_message, is_("Jules error:" + expected_error1 + ' \n' + expected_error2), "error message")

