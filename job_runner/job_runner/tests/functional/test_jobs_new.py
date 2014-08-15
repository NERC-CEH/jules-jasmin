"""
# header
"""
import os
from pylons import config
import re
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.utils.constants import *


class TestJobsControllerNew(TestController):

    def setUp(self):
        model_run_id = 101
        self.run_dir = config['run_dir'] + '/run101'
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)

        namelist_files = \
            [
                {'filename': 'file1',
                 JSON_MODEL_NAMELISTS:
                     [
                         {'name': 'a name',
                          JSON_MODEL_NAMELIST_INDEX: 1,
                          'parameters': {
                                            'time_lens': '1'
                                        }
                         },
                         {
                             'name': JULES_PARAM_POINTS_FILE[0],
                             JSON_MODEL_NAMELIST_INDEX: 2,
                             'parameters': {}
                         }
                     ]
                 }
            ]
        self.valid_job_submission = {
            'code_version': 'Jules v3.4.1',
            'model_run_id': model_run_id,
            'namelist_files': namelist_files,
            JSON_USER_NAME: 'name',
            JSON_USER_ID: 2,
            JSON_USER_EMAIL: 'email',
            JSON_LAND_COVER: {}
        }

    def test_GIVEN_nothing_WHEN_get_new_job_THEN_error(self):
        response = self.app.get(
            url(controller='jobs', action='new'),
            expect_errors=True
        )

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_no_job_information_WHEN_post_new_job_THEN_error(self):
        response = self.app.post(
            url(controller='jobs', action='new'),
            params={},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_code_version_is_unknown_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['code_version'] = 'not a valid code version'
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('code version'), "invalid request")

    def test_GIVEN_code_version_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['code_version']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('code version'), "invalid request")

    def test_GIVEN_model_run_id_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['model_run_id']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('model run id'), "invalid request")

    def test_GIVEN_model_run_id_is_blank_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['model_run_id'] = '  '
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('model run id'), "invalid request")

    def test_GIVEN_model_run_id_is_not_a_number_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['model_run_id'] = 'not a number'
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('model run id'), "invalid request")

    def test_GIVEN_namelist_files_are_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('namelist files'), "invalid request")

    def test_GIVEN_namelist_file_has_no_filename_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files'][0]['filename']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('filename'), "invalid request")

    def test_GIVEN_namelist_file_has_blank_filename_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['namelist_files'][0]['filename'] = ''
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('filename'), "invalid request")

    def test_GIVEN_namelist_set_is_empty_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS] = []
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('namelist'), "invalid request")

    def test_GIVEN_namelist_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS]
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('namelist'), "invalid request")

    def test_GIVEN_namelist_has_no_name_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS][0]['name']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('name'), "invalid request")

    def test_GIVEN_namelist_has_blank_name_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS][0]['name'] = ''
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('name'), "invalid request")

    def test_GIVEN_parameter_set_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS][0]['parameters']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('parameters'), "invalid request")

    def test_GIVEN_parameter_name_is_blank_post_new_job_THEN_error(self):
        self.valid_job_submission['namelist_files'][0][JSON_MODEL_NAMELISTS][0]['parameters'][''] = 'val'
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('parameter name'), "invalid request")

    def test_GIVEN_user_id_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['user_id']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('user id'), "invalid request")

    def test_GIVEN_user_name_is_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['user_name']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('user name'), "invalid request")

    def test_GIVEN_user_id_email_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['user_email']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('user email address'), "invalid request")

    def test_GIVEN_valid_job_submission_WHEN_post_new_job_THEN_returns_job_id(self):
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(200), "valid request")
        job_id = re.search("(\d*)", response.normal_body).group(1)
        assert_that(job_id, greater_than(0), "pid")
