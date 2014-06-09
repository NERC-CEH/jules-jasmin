from job_runner.tests import *
from hamcrest import *



class TestJobsController(TestController):

    def setUp(self):
        namelist_files = ['file1']
        self.valid_job_submission = {
            'code_version': 'Jules v3.4.1',
            'model_run_id': '101',
            'namelist_files': namelist_files
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

    def test_GIVEN_namelist_files_are_not_present_WHEN_post_new_job_THEN_error(self):
        del self.valid_job_submission['namelist_files']
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('namelist files'), "invalid request")

    def test_GIVEN_namelist_file_set_is_empty_WHEN_post_new_job_THEN_error(self):
        self.valid_job_submission['namelist_files'] = []
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('namelist files'), "invalid request")




    def test_GIVEN_valid_job_submission_WHEN_post_new_job_THEN_returns_job_id(self):
        response = self.app.post_json(
            url(controller='jobs', action='new'),
            params=self.valid_job_submission,
            expect_errors=True)

        assert_that(response.status_code, is_(200), "invalid request")
        assert_that(response.normal_body, contains_string('100'), "invalid request")
