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
from hamcrest import assert_that, is_
import os
from pylons import url, config
from job_runner.tests import TestController
from job_runner.utils import constants
from job_runner.services.job_service import JobService


class TestJobFileController(TestController):
    """
    Test the functionality of the Job File controller
    """

    def setUp(self):
        self.job_service = JobService()
        self.test_filename = 'user_uploaded_driving_data.dat'
        self.model_run_id = 1
        self.directory = self.job_service.get_run_dir(self.model_run_id)
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.path = os.path.join(self.directory, self.test_filename)
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_GIVEN_file_not_exist_WHEN_create_new_THEN_file_created(self):
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id)}
        response = self.app.post_json(url(controller='job_file', action='new'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        assert_that(os.path.isfile(self.path), is_(True))

    def test_GIVEN_file_exists_WHEN_create_new_THEN_file_replaced(self):
        test_contents = 'existing\nlines\nof\ndata\n'

        # Set up file
        f = open(self.path, 'a+')
        f.write(test_contents)
        f.close()

        f = open(self.path, 'r')
        assert_that(f.read(), is_(test_contents))
        f.close()

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id)}
        response = self.app.post_json(url(controller='job_file', action='new'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        assert_that(os.path.isfile(self.path), is_(True))

        f = open(self.path, 'r')
        assert_that(f.read(), is_(''))

    def test_GIVEN_file_exists_but_empty_WHEN_append_THEN_file_contains_text(self):
        test_line = 'line of data into file\n'

        # Set up file
        f = open(self.path, 'w+')

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id),
                     constants.JSON_MODEL_FILE_LINE: test_line}
        response = self.app.post_json(url(controller='job_file', action='append'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        f = open(self.path, 'r')
        assert_that(f.read(), is_(test_line))

    def test_GIVEN_file_exists_with_lines_in_WHEN_append_THEN_file_contains_all_text(self):
        test_contents = 'existing\nlines\nof\ndata\n'
        test_line = 'line of data into file\n'

        # Set up file
        f = open(self.path, 'a+')
        f.write(test_contents)
        f.close()

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id),
                     constants.JSON_MODEL_FILE_LINE: test_line}
        response = self.app.post_json(url(controller='job_file', action='append'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        f = open(self.path, 'r')
        assert_that(f.read(), is_(test_contents + test_line))

    def test_GIVEN_file_not_exist_WHEN_append_THEN_file_created_and_text_added(self):
        test_line = 'line of data into file\n'

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id),
                     constants.JSON_MODEL_FILE_LINE: test_line}
        response = self.app.post_json(url(controller='job_file', action='append'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        f = open(self.path, 'r')
        assert_that(f.read(), is_(test_line))

    def test_GIVEN_file_created_WHEN_delete_THEN_file_removed(self):

        # Set up file
        f = open(self.path, 'w+')
        f.close()

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id)}
        response = self.app.post_json(url(controller='job_file', action='delete'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        assert_that(os.path.exists(self.path), is_(False))

    def test_GIVEN_file_not_exist_WHEN_delete_THEN_nothing_bad_happens(self):

        # Call web service
        json_dict = {constants.JSON_MODEL_FILENAME: self.test_filename,
                     constants.JSON_MODEL_RUN_ID: str(self.model_run_id)}
        response = self.app.post_json(url(controller='job_file', action='delete'),
                                      params=json_dict)

        assert_that(response.status_code, is_(200))
        assert_that(os.path.exists(self.path), is_(False))