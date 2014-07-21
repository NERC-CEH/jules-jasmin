import os
import unittest
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.services.job_service import JobService, ServiceError
from pylons import config
from job_runner.utils.constants import *


class TestJobService(TestController):

    def setUp(self):
        model_run_id = 201
        self.run_dir = config['run_dir'] + '/run201'
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)

        self.job_service = JobService()

        self.model_run = \
            {
                'model_run_id': model_run_id,
                'code_version': 'Jules v3.4.1',
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
        assert_that(os.path.exists(self.run_dir + '/submit_jules_3_4_1.sh'), is_(True), 'submit_jules_3_4_1.sh in run directory')
        assert_that(os.path.exists(self.run_dir + '/timesteps.nml'), is_(True), 'timesteps.nml in run directory')
        assert_that(result, greater_than(0), "PID is greater than 0")

    def test_GIVEN_model_id_is_not_an_integer_WHEN_submit_job_is_submitted_THEN_exception(self):
        self.model_run['model_run_id'] = '../201'
        with self.assertRaises(AssertionError):
            self.job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_doesnt_submit_job_but_runs_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceError):
            VALID_CODE_VERSIONS['invalid_script'] = 'invalid_script.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_doesnt_exist_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceError):
            VALID_CODE_VERSIONS['invalid_script'] = 'doesnt exist.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)

    def test_GIVEN_code_version_script_errors_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        with self.assertRaises(ServiceError):
            VALID_CODE_VERSIONS['invalid_script'] = 'error_submit.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)