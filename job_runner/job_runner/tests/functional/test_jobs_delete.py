import stat
import os
from pylons import config
import re
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.utils.constants import *


class TestJobsControllerDelete(TestController):

    def setUp(self):
        self.model_run_id = 102
        self.run_dir = config['run_dir'] + '/run102'
        if os.path.exists(self.run_dir):
            os.chmod(self.run_dir, stat.S_IRWXU)
            shutil.rmtree(self.run_dir)
        os.mkdir(self.run_dir)
        f = open(os.path.join(self.run_dir, 'to_delete'), 'w')
        f.write("hi there please delete me")
        f.close()

    def test_GIVEN_nothing_WHEN_get_new_job_THEN_error(self):
        response = self.app.get(
            url(controller='jobs', action='delete'),
            expect_errors=True
        )

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_no_job_information_WHEN_post_new_job_THEN_error(self):
        response = self.app.post(
            url(controller='jobs', action='delete'),
            params={},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_model_run_id_is_not_an_integer_WHEN_delete_THEN_error(self):
        response = self.app.post_json(
            url(controller='jobs', action='delete'),
            params={'model_run_id': 'nan'},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('Model run id'), "invalid request")

    def test_GIVEN_valid_model_run_id_WHEN_delete_THEN_directory_deleted(self):
        response = self.app.post_json(
            url(controller='jobs', action='delete'),
            params={'model_run_id': self.model_run_id},
            expect_errors=True)

        assert_that(response.status_code, is_(200), "valid request")
        assert_that(os.path.exists(self.run_dir), is_(False), "Run dir should be deleted: %s" % self.run_dir)

    def test_GIVEN_non_existant_model_run_id_WHEN_delete_THEN_appears_directory_is_deleted(self):
        response = self.app.post_json(
            url(controller='jobs', action='delete'),
            params={'model_run_id': self.model_run_id + 1},
            expect_errors=True)

        assert_that(response.status_code, is_(200), "valid request")
        assert_that(os.path.exists(self.run_dir), is_(True), "Run dir should not be deleted: %s" % self.run_dir)

    def test_GIVEN_non_deleteable_model_run_directory_WHEN_delete_THEN_error(self):
        os.chmod(self.run_dir, stat.S_IREAD)
        response = self.app.post_json(
            url(controller='jobs', action='delete'),
            params={'model_run_id': self.model_run_id},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "valid request")
        assert_that(response.normal_body, contains_string('Permission denied'), "invalid request")