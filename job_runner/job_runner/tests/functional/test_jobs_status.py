import os
from pylons import config
import re
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.utils import constants


class TestJobsControllerStatus(TestController):

    def setUp(self):
        pass

    def test_GIVEN_nothing_WHEN_get_job_status_THEN_error(self):
        response = self.app.post(
            url(controller='jobs', action='status'),
            expect_errors=True
        )

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_empty_jobs_list_WHEN_get_job_status_THEN_empty_list_retutned(self):
        response = self.app.post_json(
            url(controller='jobs', action='status'),
            params=[]
        )

        assert_that(response.status_code, is_(200), "valid request")
        assert_that(response.json_body, is_([]), "containing empty list")

    def test_GIVEN_non_integer_job_id_WHEN_get_job_status_THEN_error(self):
        response = self.app.post_json(
            url(controller='jobs', action='status'),
            params=[12, 'as'],
            expect_errors=True
        )

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_run_folder_not_created_WHEN_get_job_status_THEN_job_status_failed(self):
        model_run_id = 12
        response = self.app.post_json(
            url(controller='jobs', action='status'),
            params=[model_run_id]
        )

        job_statuses = response.json_body
        assert_that(len(job_statuses), is_(1), "Number of job statuses")
        assert_that(job_statuses[0]['id'], is_(model_run_id), "containing empty list")
        assert_that(job_statuses[0]['status'], is_(constants.MODEL_RUN_STATUS_SUBMIT_FAILED), "containing empty list")
        assert_that(job_statuses[0]['error_message'], is_(constants.ERROR_MESSAGE_NO_FOLDER), "containing empty list")

