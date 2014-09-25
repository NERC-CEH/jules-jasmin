"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from mock import Mock, MagicMock

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
        try:
            VALID_CODE_VERSIONS['invalid_script'] = 'invalid_script.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)
        except ServiceException as ex:
            assert_that(ex.message, is_("Problem submitting job, unexpected output."), "error message does not contain details")
            return
        self.fail("Should have thrown an exception")

    def test_GIVEN_code_version_script_doesnt_exist_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        try:
            VALID_CODE_VERSIONS['invalid_script'] = 'doesnt exist.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)
        except ServiceException as ex:
            assert_that(ex.message, is_("Problem submitting job."), "error message does not contain details")
            return
        self.fail("Should have thrown an exception")

    def test_GIVEN_code_version_script_errors_WHEN_submit_job_is_submitted_THEN_error_thrown(self):
        try:
            VALID_CODE_VERSIONS['invalid_script'] = 'error_submit.sh'
            local_job_service = JobService(VALID_CODE_VERSIONS)
            self.model_run['code_version'] = 'invalid_script'

            local_job_service.submit(self.model_run)
        except ServiceException as ex:
            assert_that(ex.message, is_("Problem submitting job, unknown error."), "error message does not contain details")
            return
        self.fail("Should have thrown an exception")

    def test_GIVEN_land_cover_actions_WHEN_submit_job_THEN_land_cover_editor_called_correctly(self):
        land_cover_dict = {JSON_LAND_COVER_BASE_FILE: 'data/ancils/frac.nc',
                           JSON_LAND_COVER_BASE_KEY: 'frac',
                           JSON_LAND_COVER_ICE_INDEX: 9,
                           JSON_LAND_COVER_ACTIONS: [{JSON_LAND_COVER_MASK_FILE: 'data/masks/mask1.nc',
                                                      JSON_LAND_COVER_VALUE: '9',
                                                      JSON_LAND_COVER_ORDER: '2'},
                                                     {JSON_LAND_COVER_MASK_FILE: 'data/masks/mask2.nc',
                                                      JSON_LAND_COVER_VALUE: '5',
                                                      JSON_LAND_COVER_ORDER: '1'}],
                           JSON_LAND_COVER_POINT_EDIT: {}}
        model_run_json = self.model_run
        model_run_json[JSON_LAND_COVER] = land_cover_dict

        expected_copied_base_path = self.run_dir + '/user_edited_land_cover_fractional_file.nc'

        land_cover_editor = LandCoverEditor()
        land_cover_editor.copy_land_cover_base_map = Mock(return_value=expected_copied_base_path)
        land_cover_editor.apply_land_cover_action = Mock()

        job_service = JobService(land_cover_editor=land_cover_editor)
        job_service.submit(model_run_json)

        # Check that the file was called to copy correctly
        called_base_file, called_run_directory = land_cover_editor.copy_land_cover_base_map.call_args_list[0][0]
        assert_that(called_base_file, is_('data/ancils/frac.nc'))
        assert_that(called_run_directory, is_(self.run_dir))

        # Check that the apply action was called correctly the first time
        called_base, called_mask, called_value, ice = land_cover_editor.apply_land_cover_action.call_args_list[0][0]
        assert_that(called_base, is_(expected_copied_base_path))
        assert_that(called_mask, is_(self.run_dir + '/data/masks/mask2.nc'))
        assert_that(called_value, is_('5'))

        # Check that the apply actions was called correctly the second time
        called_base, called_mask, called_value, ice = land_cover_editor.apply_land_cover_action.call_args_list[1][0]
        assert_that(called_base, is_(expected_copied_base_path))
        assert_that(called_mask, is_(self.run_dir + '/data/masks/mask1.nc'))
        assert_that(called_value, is_('9'))

    def test_GIVEN_single_point_land_cover_edit_WHEN_submit_job_THEN_land_cover_editor_called_correctly(self):
        land_cover_dict = {JSON_LAND_COVER_BASE_FILE: 'data/ancils/frac.nc',
                           JSON_LAND_COVER_BASE_KEY: 'frac',
                           JSON_LAND_COVER_ACTIONS: [],
                           JSON_LAND_COVER_POINT_EDIT: {JSON_LAND_COVER_LAT: 51.75,
                                                        JSON_LAND_COVER_LON: -0.25,
                                                        JSON_LAND_COVER_FRACTIONAL_VALS: 8 * [0.0] + [1.0]}}
        model_run_json = self.model_run
        model_run_json[JSON_LAND_COVER] = land_cover_dict

        expected_copied_base_path = self.run_dir + '/user_edited_land_cover_fractional_file.nc'

        land_cover_editor = LandCoverEditor()
        land_cover_editor.copy_land_cover_base_map = MagicMock(return_value=expected_copied_base_path)
        land_cover_editor.apply_land_cover_action = MagicMock()
        land_cover_editor.apply_single_point_fractional_cover = MagicMock()

        job_service = JobService(land_cover_editor=land_cover_editor)
        job_service.submit(model_run_json)

        c_path, c_vals, c_lat, c_lon, c_key = land_cover_editor.apply_single_point_fractional_cover.call_args_list[0][0]
        assert_that(c_path, is_(expected_copied_base_path))
        assert_that(c_lat, is_(51.75))
        assert_that(c_lon, is_(-0.25))
        assert_that(c_vals, is_(8 * [0.0] + [1.0]))
