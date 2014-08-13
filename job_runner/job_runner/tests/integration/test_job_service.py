"""
header
"""
from mock import MagicMock

import os
import shutil
from hamcrest import *
from pylons import config
from job_runner.tests import *
from job_runner.services.job_service import JobService
from job_runner.utils.constants import *
from job_runner.services.service_exception import ServiceException
from job_runner.utils.land_cover_editor import LandCoverEditor


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
                JSON_LAND_COVER: {},
                'namelist_files':
                [
                    {'filename': 'timesteps.nml',
                     'namelists':
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
        assert_that(os.path.exists(self.run_dir + '/submit_jules_3_4_1.sh'), is_(True),
                    'submit_jules_3_4_1.sh in run directory')
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

    def test_GIVEN_land_cover_actions_WHEN_submit_job_THEN_land_cover_editor_called_correctly(self):
        land_cover_dict = {JSON_LAND_COVER_BASE_FILE: 'data/ancils/frac.nc',
                           JSON_LAND_COVER_BASE_KEY: 'frac',
                           JSON_LAND_COVER_ACTIONS: [{JSON_LAND_COVER_MASK_FILE: 'data/masks/mask1.nc',
                                                      JSON_LAND_COVER_VALUE: '9',
                                                      JSON_LAND_COVER_ORDER: '2'},
                                                     {JSON_LAND_COVER_MASK_FILE: 'data/masks/mask2.nc',
                                                      JSON_LAND_COVER_VALUE: '5',
                                                      JSON_LAND_COVER_ORDER: '1'}]}
        model_run_json = self.model_run
        model_run_json[JSON_LAND_COVER] = land_cover_dict

        expected_copied_base_path = self.run_dir + '/user_edited_land_cover_fractional_file.nc'

        land_cover_editor = LandCoverEditor()
        land_cover_editor.copy_land_cover_base_map = MagicMock(return_value=expected_copied_base_path)
        land_cover_editor.apply_land_cover_action = MagicMock()

        job_service = JobService(land_cover_editor=land_cover_editor)
        job_service.submit(model_run_json)

        # Check that the file was called to copy correctly
        called_base_file, called_run_directory = land_cover_editor.copy_land_cover_base_map.call_args_list[0][0]
        assert_that(called_base_file, is_('data/ancils/frac.nc'))
        assert_that(called_run_directory, is_(self.run_dir))

        # Check that the apply action was called correctly the first time
        called_base, called_mask, called_value = land_cover_editor.apply_land_cover_action.call_args_list[0][0]
        assert_that(called_base, is_(expected_copied_base_path))
        assert_that(called_mask, is_(self.run_dir + '/data/masks/mask2.nc'))
        assert_that(called_value, is_('5'))

        # Check that the apply actions was called correctly the second time
        called_base, called_mask, called_value = land_cover_editor.apply_land_cover_action.call_args_list[1][0]
        assert_that(called_base, is_(expected_copied_base_path))
        assert_that(called_mask, is_(self.run_dir + '/data/masks/mask1.nc'))
        assert_that(called_value, is_('9'))