import stat
import os
from pylons import config
import re
import shutil
from job_runner.tests import *
from hamcrest import *
from job_runner.utils import constants


class TestJobFileControllerDuplicate(TestController):

    def setUp(self):
        self.model_run_id = 102
        self.run_dir = config['run_dir'] + '/run102'
        if os.path.exists(self.run_dir):
            os.chmod(self.run_dir, stat.S_IRWXU)
            shutil.rmtree(self.run_dir)
        os.mkdir(self.run_dir)
        f = open(os.path.join(self.run_dir, "user_uploaded_driving_data.dat"), 'w')
        self.orginal_contents = "hi there please delete me"
        f.write(self.orginal_contents)
        f.close()

        self.final_model_run_id = 202
        self.final_run_dir = config['run_dir'] + '/run202'
        if os.path.exists(self.final_run_dir):
            shutil.rmtree(self.final_run_dir)

    def test_GIVEN_nothing_WHEN_duplicate_file_THEN_error(self):
        response = self.app.get(
            url(controller='job_file', action='duplicate'),
            expect_errors=True
        )

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_no_file_information_WHEN_post_duplicate_THEN_error(self):
        response = self.app.post(
            url(controller='job_file', action='duplicate'),
            params={},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")

    def test_GIVEN_model_run_id_is_not_an_integer_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={'model_run_id': 'nan'},
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('model run id'), "invalid request")

    def test_GIVEN_model_run_id_to_copy_from_is_not_an_integer_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.model_run_id,
                'model_run_to_duplicate_from': 'nan'
            },
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('model run id to duplicate from'), "invalid request")

    def test_GIVEN_filename_is_present_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.model_run_id + 1,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': None
            },
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('filename'), "invalid request")

    def test_GIVEN_filename_is_not_on_whitelist_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.model_run_id + 1,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': 'rubbish'
            },
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('Filename'), "invalid request")

    def test_GIVEN_model_run_dir_doesnt_exist_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.model_run_id + 1,
                'model_run_to_duplicate_from': 10000,
                'filename': "user_uploaded_driving_data.dat"
            },
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('Can not duplicate file Model run directory to duplicate from does not exist'), "invalid request")

    def test_GIVEN_file_doesnt_exist_WHEN_duplicate_THEN_error(self):
        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.model_run_id + 1,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': "fractional.dat"
            },
            expect_errors=True)

        assert_that(response.status_code, is_(400), "invalid request")
        assert_that(response.normal_body, contains_string('Can not duplicate file, it does not exist'), "invalid request")

    def test_GIVEN_destination_dir_does_not_exist_WHEN_duplicate_THEN_create_dir_and_copy_file(self):
        assert_that(os.path.exists(self.final_run_dir), is_(False), "Precondition: dir exists")

        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.final_model_run_id,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': "user_uploaded_driving_data.dat"
            },
            expect_errors=True)

        assert_that(response.status_code, is_(200), "request status")

        filepath = os.path.join(self.final_run_dir, "user_uploaded_driving_data.dat")
        file_exists = os.path.exists(filepath)
        assert_that(file_exists, is_(True), "file exists")

    def test_GIVEN_destination_dir_does_exist_WHEN_duplicate_THEN_copy_file(self):
        os.mkdir(self.final_run_dir)
        assert_that(os.path.exists(self.final_run_dir), is_(True), "Precondition: dir exists")

        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.final_model_run_id,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': "user_uploaded_driving_data.dat"
            },
            expect_errors=True)

        assert_that(response.status_code, is_(200), "request status")

        filepath = os.path.join(self.final_run_dir, "user_uploaded_driving_data.dat")
        file_exists = os.path.exists(filepath)
        assert_that(file_exists, is_(True), "file exists")

    def test_GIVEN_destination_file_does_exist_WHEN_duplicate_THEN_copy_file(self):
        os.mkdir(self.final_run_dir)
        assert_that(os.path.exists(self.final_run_dir), is_(True), "Precondition: dir exists")
        f = open(os.path.join(self.final_run_dir, "user_uploaded_driving_data.dat"), 'w')
        contents = "To overwrite"
        f.write(contents)
        f.close()


        response = self.app.post_json(
            url(controller='job_file', action='duplicate'),
            params={
                'model_run_id': self.final_model_run_id,
                'model_run_to_duplicate_from': self.model_run_id,
                'filename': "user_uploaded_driving_data.dat"
            },
            expect_errors=True)

        assert_that(response.status_code, is_(200), "request status")

        filepath = os.path.join(self.final_run_dir, "user_uploaded_driving_data.dat")
        file_exists = os.path.exists(filepath)
        assert_that(file_exists, is_(True), "file exists")

        f = open(os.path.join(self.final_run_dir, "user_uploaded_driving_data.dat"), 'r')
        final_contents = f.read()
        f.close()
        assert_that(final_contents, is_(self.orginal_contents), "File contents")
