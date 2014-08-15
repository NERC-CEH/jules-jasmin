"""
#header
"""

import os
import unittest
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.services.job_service import JobService, ServiceException
from pylons import config
from job_runner.utils.constants import *


class TestJobService(TestController):

    def setUp(self):
        self.model_run_id = 201
        self.run_dir = config['run_dir'] + '/run201'
        self.user_id = 1
        self.user_name = "test"
        self.user_email = "email@test.ac.uk"
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)

        self.job_service = JobService()

        self.model_run = \
            {
                'model_run_id': self.model_run_id,
                'code_version': 'Jules v3.4.1',
                JSON_USER_ID: self.user_id,
                JSON_USER_EMAIL: self.user_email,
                JSON_USER_NAME: self.user_name,
                'namelist_files':
                    [
                        {'filename': 'timesteps.nml',
                        'namelists': \
                            [
                                {
                                    'name': 'JULES_TIME',
                                    JSON_MODEL_NAMELIST_INDEX: 1,
                                    'parameters': {'timestep_len': '1800'}
                                }
                            ]
                        }
                    ]
            }

    def test_GIVEN_model_run_WHEN_submit_job_is_submitted_THEN_directory_and_files_are_setup(self):

        result = self.job_service.submit(self.model_run)

        assert_that(os.path.exists(self.run_dir), is_(True), "directory '%s' exists" % self.run_dir)
        assert_that(os.path.exists(self.run_dir + '/jules_run.sh'), is_(True), 'jules_run.sh in run directory')
        assert_that(os.path.exists(self.run_dir + '/data'), is_(True), 'data in run directory')
        assert_that(os.path.exists(self.run_dir + '/timesteps.nml'), is_(True), 'timesteps.nml in run directory')
        assert_that(result, greater_than(0), "PID is greater than 0")

        last_line = ""
        f = file(os.path.join(config['run_dir'], 'jobs_run.log'))
        for line in f:
            last_line = line
        assert_that(last_line, contains_string(str(result)))
        assert_that(last_line, contains_string(str(self.user_id)))
        assert_that(last_line, contains_string(self.user_name))
        assert_that(last_line, contains_string(str(self.model_run_id)))
        assert_that(last_line, contains_string(self.user_email))

    def test_GIVEN_model_id_is_not_an_integer_WHEN_submit_job_is_submitted_THEN_exception(self):
        self.model_run['model_run_id'] = '../201'
        with self.assertRaises(AssertionError):
            self.job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_doesnt_submit_job_but_runs_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceException):
            VALID_CODE_VERSIONS['invalid_script'] = 'invalid_script.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_doesnt_exist_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceException):
            VALID_CODE_VERSIONS['invalid_script'] = 'doesnt exist.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_errors_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceException):
            VALID_CODE_VERSIONS['invalid_script'] = 'error_submit.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)